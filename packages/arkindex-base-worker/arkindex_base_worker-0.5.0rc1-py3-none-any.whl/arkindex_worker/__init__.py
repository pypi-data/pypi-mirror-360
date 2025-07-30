import importlib.metadata
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s/%(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

VERSION = importlib.metadata.version("arkindex-base-worker")
