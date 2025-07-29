"""Base window module.

This module contains the base window class for the VideoVault application.
"""

from abc import abstractmethod
from collections.abc import Generator
from typing import final

from PySide6.QtWidgets import QMainWindow, QStackedWidget

from winipedia_utils.pyside.ui.base.base import Base as BaseUI
from winipedia_utils.pyside.ui.pages.base.base import Base as BasePage


class Base(BaseUI, QMainWindow):
    """Base window class for the VideoVault application."""

    @classmethod
    @abstractmethod
    def get_start_page_cls(cls) -> type[BasePage]:
        """Get the start page class."""

    @final
    def base_setup(self) -> None:
        """Get the Qt object of the UI."""
        self.setWindowTitle(self.get_display_name())

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.add_pages()

        self.set_start_page()

    @final
    def add_pages(self) -> None:
        """Add the pages to the window."""
        self.pages = list(self.make_pages())
        for page in self.pages:
            self.stack.addWidget(page)

    @final
    def make_pages(self) -> Generator[BasePage, None, None]:
        """Get the pages to add to the window."""
        for page_cls in BasePage.get_subclasses():
            yield page_cls()

    @final
    def set_start_page(self) -> None:
        """Set the start page."""
        self.set_current_page(self.get_start_page_cls())
