# Normalize the slug to generate __package and __module private variables
{{cookiecutter.update({"__package": cookiecutter.slug.lower().replace("_", "-")})}}  # noqa: F821
{{cookiecutter.update({"__module": cookiecutter.slug.lower().replace("-", "_")})}}  # noqa: F821
