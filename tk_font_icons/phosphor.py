"""Load icons from Phosphor zip file."""

from __future__ import annotations

from typing import TYPE_CHECKING
from xml.etree import ElementTree

import defusedxml  # type: ignore[import-untyped]

from tk_font_icons.font_archive import open_archive_resource

if TYPE_CHECKING:
    import os


def load_icon(
    archive: str | os.PathLike,
    name: str,
    *,
    style: str = 'regular',
    flat: bool = False,
    fill: str | None = None,
    stroke: str | None = None,
) -> bytes:
    """Find the icon in `archive` and return the svg as `bytes`.

    :param archive: a Phosphor icon archive (directory or zip file)
    :param name: a Phosphor icon name
    :param fill: a hex color code to use for the icon fill
    :param stroke: a hex color code to use for the icon stroke
    :return: a Phosphor icon svg in bytes
    """
    with open_archive_resource(
        archive,
        f'{"SVGs Flat" if flat else "SVGs"}/{style}/{name}.svg',
    ) as icon_svg:
        svg = defusedxml.ElementTree.parse(icon_svg).getroot()
        if fill:
            svg.attrib['fill'] = fill
        if stroke:
            svg.attrib['stroke'] = stroke
        return ElementTree.tostring(svg)
