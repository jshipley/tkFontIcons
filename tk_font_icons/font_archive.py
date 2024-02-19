"""Common font archive (zip or directory) operations."""

from __future__ import annotations

from contextlib import contextmanager
from io import TextIOWrapper
from pathlib import Path
from typing import IO, TYPE_CHECKING, cast
import zipfile

if TYPE_CHECKING:
    from collections.abc import Iterator
    import os


class IconNotFoundError(LookupError):
    """Icon could not be found in archive."""


@contextmanager
def _get_archive_path(
    archive: str | os.PathLike,
) -> Iterator[Path | zipfile.Path]:
    """Convert `archive` into a Path object that works for directories or zip files.

    :param archive: an archive directory or zip path
    :return: a pathlib or zipfile Path
    """
    if not Path(archive).exists():
        raise FileNotFoundError(archive)
    if not (Path(archive).is_dir() or zipfile.is_zipfile(archive)):
        raise NotADirectoryError(archive)
    archive_zip: zipfile.ZipFile | None = None
    try:
        archive_zip = zipfile.ZipFile(archive)
        archive_path: Path | zipfile.Path = (
            zipfile.Path(archive_zip)
            if zipfile.is_zipfile(archive)
            else Path(archive)
        )
        yield archive_path
    finally:
        if archive_zip:
            archive_zip.close()


@contextmanager
def open_archive_resource(
    archive: str | os.PathLike,
    filename: str | os.PathLike,
) -> Iterator[TextIOWrapper | IO[bytes]]:
    """Context manager for opening files from directory or zip file.

    :param archive: a zip or directory font archive
    :param filename: a file inside the archive
    """
    resource_io: TextIOWrapper | IO[bytes] | None = None
    try:
        with _get_archive_path(archive) as archive_path:
            resource_files = list(archive_path.rglob(str(filename)))
            if not resource_files:
                resource_files = list(archive_path.glob(str(filename)))
            if not resource_files:
                raise FileNotFoundError(filename)
            resource_file: Path | zipfile.Path = resource_files[0]

            resource_io = resource_file.open('r', encoding='utf-8')
            yield cast(TextIOWrapper | IO[bytes], resource_io)
    finally:
        if resource_io:
            resource_io.close()


def _walk_archive(
    archive: Path | zipfile.Path,
) -> Iterator[Path | zipfile.Path]:
    """Iterate over all of the files contained in the archive.

    Similar to os.walk or Path.walk, but also works for zipfile.Path

    :param archive: the archive to walk
    :return: an iterator of paths
    """
    for child in archive.iterdir():
        if child.is_dir():
            yield from _walk_archive(child)
        elif child.name.endswith('.svg'):
            yield child


def list_archive_files(
    archive: str | os.PathLike,
) -> Iterator[Path | zipfile.Path]:
    """List all files inside an archive (zip or directory).

    :param archive: the archive
    :return: an iterator of Path objects
    """
    with _get_archive_path(archive) as archive_path:
        yield from _walk_archive(archive_path)


def search_archive(archive: str | os.PathLike, term: str) -> list[Path | zipfile.Path]:
    """Search for icons with term in name.

    :param archive: a font archive (directory or zip file)
    :param term: the search term
    :return: a list of icon names that match the search term
    """
    return [
        icon
        for icon in list_archive_files(archive)
        if icon.match(f'**/*{term}*') or icon.match(f'*{term}*')
    ]
