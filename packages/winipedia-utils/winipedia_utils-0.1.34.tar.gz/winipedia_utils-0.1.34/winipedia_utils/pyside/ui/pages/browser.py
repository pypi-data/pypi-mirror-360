"""Add downloads page module.

This module contains the add downloads page class for the VideoVault application.
"""

from typing import final

from winipedia_utils.pyside.ui.pages.base.base import Base as BasePage
from winipedia_utils.pyside.ui.widgets.browser import Browser as BrowserWidget


class Browser(BasePage):
    """Add downloads page for the VideoVault application."""

    @final
    def setup(self) -> None:
        """Setup the UI."""
        # add a download button in the top right
        self.add_brwoser()

    @final
    def add_brwoser(self) -> None:
        """Add a browser to surfe the web."""
        self.browser = BrowserWidget(self.v_layout)
