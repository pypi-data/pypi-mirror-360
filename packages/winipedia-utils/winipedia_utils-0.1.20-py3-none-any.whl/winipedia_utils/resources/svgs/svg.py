"""utils for svgs."""

from pathlib import Path

from winipedia_utils.modules.module import to_path
from winipedia_utils.resources import svgs


def get_svg_path(svg_name: str) -> Path:
    """Get the path to a svg."""
    return to_path(svgs, is_package=True) / svg_name
