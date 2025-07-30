import io
import pathlib

from qcogclient.httpclient import ReadableFile


def load(file: pathlib.Path | str | ReadableFile) -> ReadableFile:
    if isinstance(file, ReadableFile):
        return file

    if isinstance(file, str):
        raise NotImplementedError("Loading from string is not supported")

    if isinstance(file, pathlib.Path):
        with open(str(file), "rb") as f:
            return io.BytesIO(f.read())

    else:
        raise ValueError(
            "Invalid file type - must be a pathlib.Path, a file-like object or a string"
        )
