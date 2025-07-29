"""utils for svgs."""

from pathlib import Path
from types import ModuleType

from winipedia_utils.modules.module import to_path
from winipedia_utils.resources import svgs


def get_svg_path(svg_name: str, package: ModuleType | None = None) -> Path:
    """Get the path to a svg."""
    package = package or svgs
    return (to_path(package, is_package=True) / svg_name).with_suffix(".svg")
