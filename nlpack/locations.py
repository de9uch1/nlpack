import os
import sys


def cache_dir(name: str) -> str:
    """Gets the cache directory path.

    * MacOS:    `~/Library/Caches/nlpack/<name>`
    * Unix:     `~/.cache/nlpack/<name>`    (from `XDG_CACHE_HOME`)

    Args:
        name (str): Directory name.

    Returns:
        str: The cache directory path.

    Raises:
        NotImplementedError: Unsupported platform.
    """
    if sys.platform == "darwin":
        path = os.path.expanduser("~/Library/Caches")
    elif sys.platform == "linux":
        path = os.getenv("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))
    else:
        raise NotImplementedError
    path = os.path.join(path, "nlpack", name)
    return path


def data_dir(name: str) -> str:
    """Gets the data directory path.

    * MacOS:    `~/Library/Application Support/nlpack/<name>`
    * Unix:     `~/.local/share/nlpack/<name>`    (from `XDG_DATA_HOME`)

    Args:
        name (str): Directory name.

    Returns:
        str: The data directory path.

    Raises:
        NotImplementedError: Unsupported platform.
    """
    if sys.platform == "darwin":
        path = os.path.expanduser("~/Library/Application Support")
    elif sys.platform == "linux":
        path = os.getenv("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
    else:
        raise NotImplementedError
    path = os.path.join(path, "nlpack", name)
    return path
