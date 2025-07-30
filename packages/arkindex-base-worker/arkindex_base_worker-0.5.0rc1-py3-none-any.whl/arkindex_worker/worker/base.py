"""
The base class for all Arkindex workers.
"""

import argparse
import json
import logging
import os
import shutil
from pathlib import Path
from tempfile import mkdtemp

import gnupg
import yaml

from arkindex import options_from_env
from arkindex.exceptions import ErrorResponse
from arkindex_worker import logger
from arkindex_worker.cache import (
    check_version,
    create_tables,
    create_version_table,
    init_cache_db,
    merge_parents_cache,
)
from arkindex_worker.utils import close_delete_file, extract_tar_zst_archive
from arkindex_worker.worker.process import ProcessMode
from teklia_toolbox.requests import get_arkindex_client


class ExtrasDirNotFoundError(Exception):
    """
    Exception raised when the path towards the extras directory is invalid
    """


class BaseWorker:
    """
    Base class for Arkindex workers.
    """

    def __init__(
        self,
        description: str | None = "Arkindex Base Worker",
        support_cache: bool | None = False,
    ):
        """
        Initialize the worker.

        :param description: Description shown in the ``worker-...`` command line tool.
        :param support_cache: Whether or not this worker supports the cache database.
           Override the constructor and set this parameter to start using the cache database.
        """

        self.parser = argparse.ArgumentParser(description=description)
        self.parser.add_argument(
            "-c",
            "--config",
            help="Alternative configuration file when running without a Worker Run ID",
            type=open,
        )
        self.parser.add_argument(
            "-d",
            "--database",
            help="Alternative SQLite database to use for worker caching",
            type=Path,
            default=None,
        )
        self.parser.add_argument(
            "-v",
            "--verbose",
            "--debug",
            help="Display more information on events and errors",
            action="store_true",
            default=False,
        )
        self.parser.add_argument(
            "--dev",
            help=(
                "Run worker in developer mode. "
                "Worker will be in read-only state even if a worker run is supplied. "
            ),
            action="store_true",
            default=False,
        )
        # To load models, datasets, etc, locally
        self.parser.add_argument(
            "--extras-dir",
            help=(
                "The path to a local directory to store extra files like models, datasets, etc (development only)."
            ),
            type=Path,
        )

        # Call potential extra arguments
        self.add_arguments()

        # Setup workdir either in Ponos environment or on host's home
        if os.environ.get("PONOS_DATA"):
            self.work_dir = Path(os.environ["PONOS_DATA"], "current")
        else:
            # We use the official XDG convention to store file for developers
            # https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
            xdg_data_home = os.environ.get("XDG_DATA_HOME", "~/.local/share")
            self.work_dir = Path(xdg_data_home, "arkindex").expanduser()
            self.work_dir.mkdir(parents=True, exist_ok=True)

        # Store task ID and chunk index. This is only available when running in production
        # through a ponos agent
        self.task_id = os.environ.get("PONOS_TASK")
        self.task_chunk = os.environ.get("ARKINDEX_TASK_CHUNK")

        # Store task data directory.
        self.task_data_dir = Path(os.environ.get("PONOS_DATA", "/data"))

        self.worker_run_id = os.environ.get("ARKINDEX_WORKER_RUN_ID")
        if not self.worker_run_id:
            logger.warning(
                "Missing ARKINDEX_WORKER_RUN_ID environment variable, worker is in read-only mode"
            )

        logger.info(f"Worker will use {self.work_dir} as working directory")

        self.process_information = None
        # corpus_id will be updated in configure() using the worker_run's corpus
        # or in configure_for_developers() from the environment
        self._corpus_id = None
        self.user_configuration = {}
        self.model_configuration = {}
        self.support_cache = support_cache
        # use_cache will be updated in configure_cache() if the cache is supported and if
        # there is at least one available sqlite database either given or in the parent tasks
        self.use_cache = False

        # model_version_id will be updated in configure() using the worker_run's model version
        # or in configure_for_developers() from the environment
        self.model_version_id = None
        # model_details will be updated in configure() using the worker_run's model version
        # or in configure_for_developers() from the environment
        self.model_details = {}

        # task_parents will be updated in configure_cache() if the cache is supported,
        # if the task ID is set and if no database is passed as argument
        self.task_parents = []

        # Define API Client
        self.setup_api_client()

        # Known and available classes in processed corpus
        self.classes = {}
        # Known and available entity types in processed corpus
        self.entity_types = {}
        # Known and available element types in processed corpus
        self.corpus_types = {}

    @property
    def corpus_id(self) -> str:
        """
        ID of the corpus on which the worker is executed.
        Has to be set through the `ARKINDEX_CORPUS_ID` variable in **read-only** mode.
        Raises an Exception when trying to access when unset.
        """
        if not self._corpus_id:
            raise Exception("Missing ARKINDEX_CORPUS_ID environment variable")
        return self._corpus_id

    @property
    def process_mode(self) -> ProcessMode | None:
        """Mode of the process being run. Returns None when read-only."""
        if self.is_read_only:
            return
        return ProcessMode(self.process_information["mode"])

    @property
    def is_read_only(self) -> bool:
        """
        Whether or not the worker can publish data.

        False when dev mode is enabled with the ``--dev`` CLI argument,
            when no worker run ID is provided
        """
        return self.args.dev or self.worker_run_id is None

    @property
    def worker_version_id(self):
        """Deprecated property previously used to retrieve the current WorkerVersion ID.

        :raises DeprecationWarning: Whenever `worker_version_id` is used.
        """
        raise DeprecationWarning("`worker_version_id` usage is deprecated")

    def setup_api_client(self):
        """
        Create an ArkindexClient to make API requests towards Arkindex instances.
        """
        # Build Arkindex API client from environment variables
        self.api_client = get_arkindex_client(**options_from_env())
        logger.debug(f"Setup Arkindex API client on {self.api_client.document.url}")

    def configure_for_developers(self):
        """
        Setup the necessary configuration needed when working in `read_only` mode.
        This is the method called when running a worker locally.
        """
        assert self.is_read_only
        # Setup logging level if verbose or if ARKINDEX_DEBUG is set to true
        if self.args.verbose or os.environ.get("ARKINDEX_DEBUG"):
            logger.setLevel(logging.DEBUG)
            logger.debug("Debug output enabled")

        if self.args.config:
            # Load config from YAML file
            self.config = yaml.safe_load(self.args.config)
            self.worker_details = {"name": "Local worker"}
            required_secrets = self.config.get("secrets", [])
            logger.info(
                f"Running with local configuration from {self.args.config.name}"
            )
        else:
            self.config = {}
            self.worker_details = {}
            required_secrets = []
            logger.warning("Running without any extra configuration")

        # Define corpus_id from environment
        self._corpus_id = os.environ.get("ARKINDEX_CORPUS_ID")

        # Define model_version_id from environment
        self.model_version_id = os.environ.get("ARKINDEX_MODEL_VERSION_ID")

        # Define model_details from environment
        self.model_details = {"id": os.environ.get("ARKINDEX_MODEL_ID")}

        # Load all required secrets
        self.secrets = {name: self.load_secret(Path(name)) for name in required_secrets}

    def configure_worker_run(self):
        """
        Setup the necessary configuration needed using CLI args and environment variables.
        This is the method called when running a worker on Arkindex.
        """
        assert not self.is_read_only
        # Setup logging level if verbose or if ARKINDEX_DEBUG is set to true
        if self.args.verbose or os.environ.get("ARKINDEX_DEBUG"):
            logger.setLevel(logging.DEBUG)
            logger.debug("Debug output enabled")

        # Load worker run information
        worker_run = self.api_client.request("RetrieveWorkerRun", id=self.worker_run_id)

        # Load process information
        self.process_information = worker_run["process"]

        # Load corpus id
        self._corpus_id = worker_run["process"]["corpus"]

        # Load worker version information
        worker_version = worker_run["worker_version"]
        self.worker_details = worker_version["worker"]

        logger.info(f"Loaded {worker_run['summary']} from API")

        # Load model version configuration when available
        model_version = worker_run.get("model_version")
        if model_version:
            logger.info("Loaded model version configuration from WorkerRun")
            self.model_configuration.update(model_version["configuration"])

            # Set model_version ID as worker attribute
            self.model_version_id = model_version["id"]

            # Set model details as worker attribute
            self.model_details = model_version["model"]

        # Retrieve initial configuration from API
        self.config = worker_version["configuration"].get("configuration", {})
        if "user_configuration" in worker_version["configuration"]:
            # Add missing values (using the provided default if set) to user_configuration
            for key, value in worker_version["configuration"][
                "user_configuration"
            ].items():
                if key not in self.model_configuration:
                    self.user_configuration[key] = value.get("default")

        # Load all required secrets
        required_secrets = worker_version["configuration"].get("secrets", [])
        self.secrets = {name: self.load_secret(Path(name)) for name in required_secrets}

        # Load worker run configuration when available
        worker_configuration = worker_run.get("configuration")
        if worker_configuration and worker_configuration.get("configuration"):
            logger.info("Loaded user configuration from WorkerRun")
            self.user_configuration.update(worker_configuration.get("configuration"))

        # if debug mode is set to true activate debug mode in logger
        if self.user_configuration.get("debug"):
            logger.setLevel(logging.DEBUG)
            logger.debug("Debug output enabled")

    def configure_cache(self):
        """
        Setup the necessary attribute when using the cache system of `Base-Worker`.
        """
        paths = None
        if self.support_cache and self.args.database is not None:
            self.use_cache = True
        elif self.support_cache and self.task_id:
            task = self.api_client.request("RetrieveTask", id=self.task_id)
            self.task_parents = task["parents"]
            paths = self.find_parents_file_paths(Path("db.sqlite"))
            self.use_cache = len(paths) > 0

        if self.use_cache:
            if self.args.database is not None:
                assert self.args.database.is_file(), (
                    f"Database in {self.args.database} does not exist"
                )
                self.cache_path = self.args.database
            else:
                cache_dir = self.task_data_dir / self.task_id
                assert cache_dir.is_dir(), f"Missing task cache in {cache_dir}"
                self.cache_path = cache_dir / "db.sqlite"
            init_cache_db(self.cache_path)

            if self.args.database is not None:
                check_version(self.cache_path)
            else:
                create_version_table()

            create_tables()

            # Merging parents caches (if there are any) in the current task local cache, unless the database got overridden
            if self.args.database is None and paths is not None:
                merge_parents_cache(paths, self.cache_path)
        else:
            logger.debug("Cache is disabled")

    def configure(self):
        """
        Setup the worker using CLI arguments and environment variables.
        """
        # CLI args are stored on the instance so that implementations can access them
        self.args = self.parser.parse_args()

        if self.is_read_only:
            self.configure_for_developers()
        else:
            self.configure_worker_run()
            self.configure_cache()

        # Retrieve the model configuration
        if self.model_configuration:
            self.config.update(self.model_configuration)
            logger.info("Model version configuration retrieved")

        # Retrieve the user configuration
        if self.user_configuration:
            self.config.update(self.user_configuration)
            logger.info("User configuration retrieved")

    def load_secret(self, name: Path):
        """
        Load a Ponos secret by name.

        :param name: Name of the Ponos secret.
        :raises Exception: When the secret cannot be loaded from the API nor the local secrets directory.
        """
        secret = None

        # Load from the backend
        try:
            resp = self.api_client.request("RetrieveSecret", name=str(name))
            secret = resp["content"]
            logging.info(f"Loaded API secret {name}")
        except ErrorResponse as e:
            logger.warning(f"Secret {name} not available: {e.content}")

        # Load from local developer storage
        base_dir = Path(os.environ.get("XDG_CONFIG_HOME") or "~/.config").expanduser()
        path = base_dir / "arkindex" / "secrets" / name
        if path.exists():
            logging.debug(f"Loading local secret from {path}")

            try:
                gpg = gnupg.GPG()
                with path.open("rb") as gpg_file:
                    decrypted = gpg.decrypt_file(gpg_file)
                assert decrypted.ok, (
                    f"GPG error: {decrypted.status} - {decrypted.stderr}"
                )
                secret = decrypted.data.decode("utf-8")
                logging.info(f"Loaded local secret {name}")
            except Exception as e:
                logger.error(f"Local secret {name} is not available as {path}: {e}")

        if secret is None:
            raise Exception(f"Secret {name} is not available on the API nor locally")

        # Parse secret payload, according to its extension
        try:
            ext = name.suffix.lower()
            if ext == ".json":
                return json.loads(secret)
            elif ext in (".yaml", ".yml"):
                return yaml.safe_load(secret)
        except Exception as e:
            logger.error(f"Failed to parse secret {name}: {e}")

        # By default give raw secret payload
        return secret

    def find_extras_directory(self) -> Path:
        """
        Find the local path to the directory to store extra files. This supports two modes:
        - the worker runs in ponos, the directory is available at `/data/extra_files` (first try) or `/data/current`.
        - the worker runs locally, the developer may specify it using either
           - the `extras_dir` configuration parameter
           - the `--extras-dir` CLI parameter

        :return: Path to the directory for extra files on disk
        """
        if self.task_id:
            # When running in production with ponos, the agent
            # downloads the model and set it either in
            # - `/data/extra_files`
            # - the current task work dir
            extras_dir = self.task_data_dir / "extra_files"
            if extras_dir.exists():
                return extras_dir
            return self.work_dir
        else:
            extras_dir = self.config.get("extras_dir", self.args.extras_dir)
            if extras_dir is None:
                raise ExtrasDirNotFoundError(
                    "No path to the directory for extra files was provided. "
                    "Please provide extras_dir either through configuration "
                    "or as CLI argument."
                )
            extras_dir = Path(extras_dir)
            if not extras_dir.exists():
                raise ExtrasDirNotFoundError(
                    f"The path {extras_dir} does not link to any directory"
                )
            return extras_dir

    def find_parents_file_paths(self, filename: Path) -> list[Path]:
        """
        Find the paths of a specific file from the parent tasks.
        Only works if the task_parents attributes is updated, so if the cache is supported,
        if the task ID is set and if no database is passed as argument

        :param filename: Name of the file to find
        :return: Paths to the parent files
        """
        # Handle possible chunk in parent task name
        # This is needed to support the init_elements databases
        filenames = [
            filename,
        ]
        if self.task_chunk is not None:
            filenames.append(
                f"{filename.name.replace(filename.suffix, '')}_{self.task_chunk}{filename.suffix}"
            )

        # Find all the paths for these files
        return list(
            filter(
                lambda p: p.is_file(),
                [
                    self.task_data_dir / parent_id / name
                    for parent_id in self.task_parents
                    for name in filenames
                ],
            )
        )

    def extract_parent_archives(self, archive_name: Path, dest: Path) -> None:
        """
        Find and extract the paths from a specific file from the parent tasks.
        Only works if the task_parents attributes is updated, so if the cache is supported,
        if the task ID is set and if no database is passed as argument

        :param archive_name: Name of the file to find
        :param dest: Folder to store the extracted files
        """
        base_extracted_path = Path(mkdtemp(suffix="-extracted-data"))
        file_paths = self.find_parents_file_paths(archive_name)

        # Uncompress and extract the archive
        for file_path in file_paths:
            archive_fd, archive_path = extract_tar_zst_archive(
                file_path, base_extracted_path
            )
            # Remove the tar archive
            close_delete_file(archive_fd, archive_path)

            # Move all files in the dest folder
            for tmp_extracted_path in base_extracted_path.rglob("*"):
                if not tmp_extracted_path.is_file():
                    continue

                extracted_file = Path(
                    str(tmp_extracted_path).replace(str(base_extracted_path), str(dest))
                )
                extracted_file.parent.mkdir(parents=True, exist_ok=True)
                # Use shutil to avoid errors when the files are not on the same filesystem
                shutil.move(tmp_extracted_path, extracted_file)

            # Clean up
            shutil.rmtree(base_extracted_path)

    def add_arguments(self):
        """Override this method to add ``argparse`` arguments to this worker"""

    def run(self):
        """Override this method to implement your own process"""
