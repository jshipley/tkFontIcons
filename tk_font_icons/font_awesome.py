"""Load icons from Font Awesome zip file."""

from __future__ import annotations

from collections import defaultdict
from contextlib import contextmanager
import json
from pathlib import Path
from typing import TYPE_CHECKING, Generator
from xml.etree import ElementTree
import zipfile

import defusedxml.ElementTree  # type: ignore[import-untyped]

if TYPE_CHECKING:
    from io import TextIOWrapper
    import os

ElementTree.register_namespace('', 'http://www.w3.org/2000/svg')

SEARCH_MAP: defaultdict[str, list[str]] = defaultdict(list)
ALIAS_MAP: dict[str, str] = {}


def _resolve_archive_path(
    archive: zipfile._path.Path | Path,
    filename: str,
    style: str | None = None,
) -> zipfile._path.Path | Path | None:
    """Resolve file in zip or directory, using fallbacks to find the right resource.

    If a .svg file needs to be found and there is no style specified, then the .svg
    could be under either "solid" or "brands". If it's not under either, then assume
    it doesn't exist.

    :param parent: The font archive (zip or directory) to search
    :param filename: the name of the file to search for
    :param style: the style of font to search for, only applicable for .svg files
    :return: the .json or .svg file that is found, or None if none are found
    """
    search_paths = []
    if filename.endswith('.json'):
        search_paths.append(f'metadata/{filename}')
    elif style:
        search_paths.append(f'{style}/{filename}')
    else:
        search_paths.append(f'solid/{filename}')
        search_paths.append(f'brands/{filename}')

    for search_path in search_paths:
        found_path = next(archive.glob(f'**/{search_path}'), None)
        if found_path and found_path.exists():
            return found_path
    return None


@contextmanager
def _open_archive_resource(
    archive: str | os.PathLike,
    filename: str,
    style: str | None = None,
) -> Generator[TextIOWrapper, None, None]:
    """Context manager for opening files from directory or zip file."""
    archive_path = Path(archive)
    if not archive_path.exists():
        raise FileNotFoundError(archive_path)
    if not (archive_path.is_dir() or zipfile.is_zipfile(archive_path)):
        raise NotADirectoryError(archive_path)

    resource_contents: TextIOWrapper | None = None
    try:
        zip_archive = None
        resource_path: Path | zipfile._path.Path | None = None
        if zipfile.is_zipfile(archive_path):
            zip_archive = zipfile.ZipFile(archive_path)

        resource_path = _resolve_archive_path(
            zipfile.Path(zip_archive) if zip_archive else archive_path,
            filename,
            style,
        )
        if not resource_path:
            if filename.endswith('.json'):
                message = filename
            elif style:
                message = f'{filename} (style: {style})'
            else:
                message = f'{filename} (style: solid/brands)'
            raise FileNotFoundError(message)

        resource_contents = resource_path.open('r', encoding='utf-8')
        yield resource_contents
    finally:
        if resource_contents:
            resource_contents.close()
        if zip_archive:
            zip_archive.close()


def _ensure_fa_icon_metadata(fa_archive: str | os.PathLike) -> None:
    """Load icon metadata and populate the lookup mappings.

    :param fa_archive: a font awesome archive (directory or zip file)
    """
    if SEARCH_MAP and ALIAS_MAP:
        return

    with _open_archive_resource(
        fa_archive,
        'icons.json',
    ) as icons_file:
        icons_metadata = json.load(icons_file)

    for icon_name, metadata in icons_metadata.items():
        if metadata['search']['terms']:
            for term in metadata['search']['terms']:
                SEARCH_MAP[term.lower()].append(icon_name)
        if 'aliases' in metadata and 'names' in metadata['aliases']:
            for alias in metadata['aliases']['names']:
                ALIAS_MAP[alias.lower()] = icon_name


def search(fa_archive: str | os.PathLike, term: str) -> list[str]:
    """Search Font Awesome icon metadata.

    Uses search terms from metadata/icons.json to search for icons.

    :param term: the search term
    :return: a list of icon names that match the search term
    """
    _ensure_fa_icon_metadata(fa_archive)

    return SEARCH_MAP[term]


def load_icon(
    fa_archive: str | os.PathLike,
    name: str,
    style: str | None = None,
    fill: str | None = None,
) -> bytes:
    """Find the icon in `fa_archive` and return the svg as `bytes`.

    :param fa_archive: a font awesome archive (directory or zip file)
    :param name: a font awesome icon name
    :param style: a font awesome icon style
    :param fill: a hex color code to replace the icon foreground
    :return: a font awesome icon svg in bytes
    """
    _ensure_fa_icon_metadata(fa_archive)
    with _open_archive_resource(
        fa_archive,
        f'{ALIAS_MAP.get(name, name)}.svg',
        style,
    ) as icon_svg:
        svg = defusedxml.ElementTree.parse(icon_svg).getroot()
        if fill:
            svg.attrib['fill'] = fill
        return ElementTree.tostring(svg)
