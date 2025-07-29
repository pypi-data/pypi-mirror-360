from pathlib import Path
from typing import IO
import io

import fileex


def open_file(
    source: str | bytes | Path,
    mode: str = 'r',
    encoding: str | None = None
) -> IO[str] | IO[bytes]:
    """Create an open file-like object from content or filepath.

    If `source` is a `str` or `bytes`, returns an in-memory
    file-like object containing that content. If `source` is a
    `pathlib.Path`, opens the file at that path with the
    specified mode.

    Parameters
    ----------
    source
        File content (as string or bytes)
        or path (as string or pathlib.Path).
        If a string is provided, it is first checked
        if it is a valid existing file path.
        If so, the string is treated as a path,
        otherwise as file content.
        Bytes are always treated as content,
        and a `pathlib.Path` is always treated as a file path.
    mode
        Mode (e.g., 'r', 'w', 'rb') to open the file when `source` is a path.
        Ignored when `source` is content.
    encoding
        Encoding to use when opening a text file from a path.
        Ignored when `source` is content or in binary mode.

    Returns
    -------
    A file-like object. For content sources, this will be an
    `io.StringIO` or `io.BytesIO`. For file paths, this returns
    the standard file object.
    You can close the returned object by calling its `close()` method
    when done to release resources.
    """
    if isinstance(source, str):
        if fileex.file.is_path(source):
            return Path(source).open(mode=mode, encoding=encoding)
        return io.StringIO(source)
    if isinstance(source, bytes):
        return io.BytesIO(source)
    if isinstance(source, Path):
        return source.open(mode=mode, encoding=encoding)
    raise TypeError(
        f"Expected str, bytes, or pathlib.Path, got {type(source).__name__}"
    )
