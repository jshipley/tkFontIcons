"""Load icons from Font Awesome zip file."""

from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any
from xml.etree import ElementTree

import defusedxml.ElementTree  # type: ignore[import-untyped]

from tk_font_icons.font_archive import IconNotFoundError, open_archive_resource

if TYPE_CHECKING:
    import os

# required to avoid prefixing ns0: to all xml elements
ElementTree.register_namespace('', 'http://www.w3.org/2000/svg')

ICON_METADATA: dict[str, Any] = {}
SEARCH_MAP: defaultdict[str, set[str]] = defaultdict(set)
ALIAS_MAP: dict[str, str] = {}


def _ensure_fa_icon_metadata(archive: str | os.PathLike) -> None:
    """Load icon metadata and populate the lookup mappings.

    :param archive: a Font Awesome archive (directory or zip file)
    """
    if SEARCH_MAP and ALIAS_MAP:
        return

    with open_archive_resource(
        archive,
        'metadata/icons.json',
    ) as icons_file:
        ICON_METADATA.update(json.load(icons_file))

    for icon_name, metadata in ICON_METADATA.items():
        if metadata['search']['terms']:
            for term in metadata['search']['terms']:
                SEARCH_MAP[term.lower()].add(icon_name)
        if 'aliases' in metadata and 'names' in metadata['aliases']:
            for alias in metadata['aliases']['names']:
                ALIAS_MAP[alias.lower()] = icon_name


def search(archive: str | os.PathLike, term: str) -> list[str]:
    """Search Font Awesome icon metadata.

    Uses search terms from metadata/icons.json to search for icons.
    Also returns any icons with `term` in the filename, or any
    icons that `term` is an alias for.

    :param term: the search term
    :return: a list of icon names that match the search term
    """
    _ensure_fa_icon_metadata(archive)

    results = {icon for icon in ICON_METADATA if term.lower() in icon.lower()}
    if term in SEARCH_MAP:
        results |= SEARCH_MAP[term]
    if term in ALIAS_MAP:
        results.add(ALIAS_MAP[term])

    return sorted(results)


def resolve_icon_path(archive: str | os.PathLike, name: str, style: str | None = None) -> Path:
    """Use icons.json metadata to resolve icon paths.

    :param archive: a Font Awesome archive (directory or zip file)
    :param name: a Font Awesome icon name
    :param style: a Font Awesome icon style
    :return: a list of all Font Awesome icons that match the name and style
    """
    _ensure_fa_icon_metadata(archive)

    icon = f'{ALIAS_MAP.get(name, name)}.svg'
    try:
        available_styles = ICON_METADATA[name]['free']
    except KeyError as err:
        raise IconNotFoundError(name) from err

    resolved_icons = []

    if style and style in available_styles:
        resolved_icons.append(Path('svgs') / style / icon)
    if not style:
        resolved_icons.extend(Path('svgs') / style / icon for style in available_styles)
    if not resolved_icons:
        raise IconNotFoundError(name)

    return resolved_icons[0]


def load_icon(
    archive: str | os.PathLike,
    name: str,
    style: str | None = None,
    fill: str | None = None,
    stroke: str | None = None,
) -> bytes:
    """Find the icon in `archive` and return the svg as `bytes`.

    Most of the free fonts only support fill, not stroke.

    :param archive: a Font Awesome archive (directory or zip file)
    :param name: a Font Awesome icon name
    :param style: a Font Awesome icon style
    :param fill: a hex color code to use for the icon fill
    :param stroke: a hex color code to use for the icon stroke
    :return: a Font Awesome icon svg in bytes
    """
    _ensure_fa_icon_metadata(archive)
    with open_archive_resource(
        archive,
        resolve_icon_path(archive, name, style),
    ) as icon_svg:
        svg = defusedxml.ElementTree.parse(icon_svg).getroot()
        if fill:
            svg.attrib['fill'] = fill
        if stroke:
            svg.attrib['stroke'] = stroke
        return ElementTree.tostring(svg)
