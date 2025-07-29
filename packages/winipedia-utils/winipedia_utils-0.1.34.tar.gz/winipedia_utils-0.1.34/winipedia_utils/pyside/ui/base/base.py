"""Base UI module.

This module contains the base UI class for the VideoVault application.
"""

from abc import abstractmethod
from types import ModuleType
from typing import TYPE_CHECKING, Any, Self, cast, final

from PySide6.QtCore import QObject
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QStackedWidget

from winipedia_utils.modules.class_ import (
    get_all_nonabstract_subclasses,
)
from winipedia_utils.modules.package import get_main_package, walk_package
from winipedia_utils.oop.mixins.meta import ABCImplementationLoggingMeta
from winipedia_utils.resources.svgs.svg import get_svg_path
from winipedia_utils.text.string import split_on_uppercase

# Avoid circular import
if TYPE_CHECKING:
    from winipedia_utils.pyside.ui.pages.base.base import Base as BasePage
    from winipedia_utils.pyside.ui.windows.base.base import Base as BaseWindow


class QABCImplementationLoggingMeta(
    ABCImplementationLoggingMeta,
    type(QObject),  # type: ignore[misc]
):
    """Metaclass for the QABCImplementationLoggingMixin."""


class Base(metaclass=QABCImplementationLoggingMeta):
    """Base UI class for a Qt application."""

    @final
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the base UI."""
        super().__init__(*args, **kwargs)
        self.base_setup()
        self.pre_setup()
        self.setup()
        self.post_setup()

    @abstractmethod
    def base_setup(self) -> None:
        """Get the Qt object of the UI."""

    @abstractmethod
    def setup(self) -> None:
        """Setup the UI."""

    @abstractmethod
    def pre_setup(self) -> None:
        """Setup the UI."""

    @abstractmethod
    def post_setup(self) -> None:
        """Setup the UI."""

    @classmethod
    @final
    def get_display_name(cls) -> str:
        """Get the display name of the UI."""
        return " ".join(split_on_uppercase(cls.__name__))

    @classmethod
    @final
    def get_subclasses(cls, package: ModuleType | None = None) -> list[type[Self]]:
        """Get all subclasses of the UI.

        Args:
            package: The package to search for subclasses in.
        """
        if package is None:
            # find the main package
            package = get_main_package()

        _ = list(walk_package(package))

        children = get_all_nonabstract_subclasses(cls)
        return sorted(children, key=lambda cls: cls.__name__)

    @final
    def set_current_page(self, page_cls: type["BasePage"]) -> None:
        """Set the current page."""
        self.get_stack().setCurrentWidget(self.get_page(page_cls))

    @final
    def get_stack(self) -> QStackedWidget:
        """Get the stack of the window."""
        window = cast("BaseWindow", (getattr(self, "window", lambda: None)()))

        return window.stack

    @final
    def get_stack_pages(self) -> list["BasePage"]:
        """Get all the pages."""
        # Import here to avoid circular import

        stack = self.get_stack()
        # get all the pages
        return [cast("BasePage", stack.widget(i)) for i in range(stack.count())]

    @final
    def get_page[T: "BasePage"](self, page_cls: type[T]) -> T:
        """Get the page."""
        page = next(
            page for page in self.get_stack_pages() if page.__class__ is page_cls
        )
        return cast("T", page)

    @classmethod
    @final
    def get_svg_icon(cls, svg_name: str, package: ModuleType | None = None) -> QIcon:
        """Get the Qicon for a svg."""
        return QIcon(str(get_svg_path(svg_name, package=package)))

    @classmethod
    @final
    def get_page_static[T: "BasePage"](cls, page_cls: type[T]) -> T:
        """Get the page."""
        from winipedia_utils.pyside.ui.windows.base.base import Base as BaseWindow

        top_level_widgets = QApplication.topLevelWidgets()
        main_window = next(
            widget for widget in top_level_widgets if isinstance(widget, BaseWindow)
        )
        return main_window.get_page(page_cls)
