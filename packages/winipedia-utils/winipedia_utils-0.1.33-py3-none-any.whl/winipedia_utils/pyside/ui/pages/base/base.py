"""Base page module.

This module contains the base page class for the VideoVault application.
"""

from functools import partial
from typing import final

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLayout,
    QMenu,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from winipedia_utils.pyside.ui.base.base import Base as BaseUI


class Base(BaseUI, QWidget):
    """Base page class for the VideoVault application."""

    @final
    def base_setup(self) -> None:
        """Get the Qt object of the UI."""
        self.v_layout = QVBoxLayout()
        self.setLayout(self.v_layout)

        # add a horizontal layout for the top row
        self.h_layout = QHBoxLayout()
        self.v_layout.addLayout(self.h_layout)

        self.add_menu_dropdown_button()

    @final
    def add_menu_dropdown_button(self) -> None:
        """Add a dropdown menu that leadds to each page."""
        self.menu_button = QPushButton("Menu")
        self.menu_button.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum
        )
        self.h_layout.addWidget(
            self.menu_button,
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
        )
        self.menu_dropdown = QMenu(self.menu_button)
        self.menu_button.setMenu(self.menu_dropdown)

        for page_cls in Base.get_subclasses():
            action = self.menu_dropdown.addAction(page_cls.get_display_name())
            action.triggered.connect(partial(self.set_current_page, page_cls))

    @final
    def add_to_page_button(
        self, to_page_cls: type["Base"], layout: QLayout
    ) -> QPushButton:
        """Add a button to go to the page."""
        button = QPushButton(to_page_cls.get_display_name())

        # connect to open page on click
        button.clicked.connect(lambda: self.set_current_page(to_page_cls))

        # add to layout
        layout.addWidget(button)

        return button
