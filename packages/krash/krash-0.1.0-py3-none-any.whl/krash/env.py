import os


def _getenv(key: str, default: str):
    return os.getenv(f"KRASH_{key.upper()}", default)


LANGUAGE = _getenv("language", "es")
