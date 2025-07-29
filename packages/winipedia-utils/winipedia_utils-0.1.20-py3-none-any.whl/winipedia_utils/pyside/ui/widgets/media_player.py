"""Media player module.

This module contains the media player class.
"""

from functools import partial
from typing import Any

from PySide6.QtCore import QBuffer, QByteArray, Qt, Signal
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLayout,
    QMenu,
    QPushButton,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from winipedia_utils.pyside.ui.base.base import Base as BaseUI


class ClickableWidget(QWidget):
    """Widget that can be clicked."""

    clicked = Signal()

    def mousePressEvent(self, event: Any) -> None:  # noqa: N802
        """Handle mouse press event."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class ClickableVideoWidget(QVideoWidget):
    """Video widget that can be clicked."""

    clicked = Signal()

    def mousePressEvent(self, event: Any) -> None:  # noqa: N802
        """Handle mouse press event."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class MediaPlayer(QMediaPlayer):
    """Media player class."""

    def __init__(self, parent_layout: QLayout, *args: Any, **kwargs: Any) -> None:
        """Initialize the media player."""
        super().__init__(*args, **kwargs)
        self.parent_layout = parent_layout
        self.make_widget()

    def make_widget(self) -> None:
        """Make the widget."""
        self.media_player_widget = QWidget()
        self.media_player_layout = QVBoxLayout(self.media_player_widget)
        self.parent_layout.addWidget(self.media_player_widget)
        self.add_media_controls_above()
        self.make_video_widget()
        self.add_media_controls_below()

    def make_video_widget(self) -> None:
        """Make the video widget."""
        self.video_widget = ClickableVideoWidget()
        self.video_widget.clicked.connect(self.on_video_clicked)
        self.video_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.setVideoOutput(self.video_widget)

        self.audio_output = QAudioOutput()
        self.setAudioOutput(self.audio_output)

        self.media_player_layout.addWidget(self.video_widget)

    def on_video_clicked(self) -> None:
        """Handle video widget click."""
        if self.media_controls_widget_above.isVisible():
            self.hide_media_controls()
            return
        self.show_media_controls()

    def show_media_controls(self) -> None:
        """Show media controls."""
        self.media_controls_widget_above.show()
        self.media_controls_widget_below.show()

    def hide_media_controls(self) -> None:
        """Hide media controls."""
        self.media_controls_widget_above.hide()
        self.media_controls_widget_below.hide()

    def add_media_controls_above(self) -> None:
        """Add media controls above the video."""
        # main above widget
        self.media_controls_widget_above = QWidget()
        self.media_controls_layout_above = QHBoxLayout(self.media_controls_widget_above)
        self.media_player_layout.addWidget(self.media_controls_widget_above)
        # left contorls
        self.left_controls_widget = QWidget()
        self.left_controls_layout = QHBoxLayout(self.left_controls_widget)
        self.media_controls_layout_above.addWidget(
            self.left_controls_widget, alignment=Qt.AlignmentFlag.AlignLeft
        )
        # center contorls
        self.center_controls_widget = QWidget()
        self.center_controls_layout = QHBoxLayout(self.center_controls_widget)
        self.media_controls_layout_above.addWidget(
            self.center_controls_widget, alignment=Qt.AlignmentFlag.AlignCenter
        )
        self.right_controls_widget = QWidget()
        self.right_controls_layout = QHBoxLayout(self.right_controls_widget)
        self.media_controls_layout_above.addWidget(
            self.right_controls_widget, alignment=Qt.AlignmentFlag.AlignRight
        )

        self.add_speed_control()
        self.add_volume_control()
        self.add_playback_control()
        self.add_fullscreen_control()

    def add_media_controls_below(self) -> None:
        """Add media controls below the video."""
        self.media_controls_widget_below = QWidget()
        self.media_controls_layout_below = QHBoxLayout(self.media_controls_widget_below)
        self.media_player_layout.addWidget(self.media_controls_widget_below)
        self.add_progress_control()

    def add_playback_control(self) -> None:
        """Add playback control."""
        self.play_icon = BaseUI.get_svg_icon("play_icon.svg")
        self.pause_icon = BaseUI.get_svg_icon("pause_icon.svg")
        # Pause symbol: ⏸ (U+23F8)
        self.playback_button = QPushButton()
        self.playback_button.setIcon(self.pause_icon)
        self.playback_button.clicked.connect(self.toggle_playback)

        self.center_controls_layout.addWidget(self.playback_button)

    def toggle_playback(self) -> None:
        """Toggle playback."""
        if self.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.pause()
            self.playback_button.setIcon(self.play_icon)
        else:
            self.play()
            self.playback_button.setIcon(self.pause_icon)

    def add_speed_control(self) -> None:
        """Add speed control.

        A button in the top left that on click shows a dropdown to select the speed.
        """
        self.default_speed = 1
        self.speed_options = [0.2, 0.5, self.default_speed, 1.5, 2, 3, 4, 5]
        self.speed_button = QPushButton(f"{self.default_speed}x")
        self.speed_menu = QMenu(self.speed_button)
        for speed in self.speed_options:
            action = self.speed_menu.addAction(f"{speed}x")
            action.triggered.connect(partial(self.change_speed, speed))

        self.speed_button.setMenu(self.speed_menu)
        self.left_controls_layout.addWidget(self.speed_button)

    def change_speed(self, speed: float) -> None:
        """Change playback speed."""
        self.setPlaybackRate(speed)
        self.speed_button.setText(f"{speed}x")

    def add_volume_control(self) -> None:
        """Add volume control."""
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        self.left_controls_layout.addWidget(self.volume_slider)

    def on_volume_changed(self, value: int) -> None:
        """Handle volume slider value change."""
        volume = value / 100.0  # Convert to 0.0-1.0 range
        self.audio_output.setVolume(volume)

    def add_fullscreen_control(self) -> None:
        """Add fullscreen control."""
        self.fullscreen_icon = BaseUI.get_svg_icon("fullscreen_icon.svg")
        self.exit_fullscreen_icon = BaseUI.get_svg_icon("exit_fullscreen_icon.svg")
        self.fullscreen_button = QPushButton()
        self.fullscreen_button.setIcon(self.fullscreen_icon)

        self.parent_widget = self.parent_layout.parentWidget()
        self.other_visible_widgets = [
            w
            for w in set(self.parent_widget.findChildren(QWidget))
            - {
                self.media_player_widget,
                *self.media_player_widget.findChildren(QWidget),
            }
            if w.isVisible() or not (w.isHidden() or w.isVisible())
        ]
        self.fullscreen_button.clicked.connect(self.toggle_fullscreen)

        self.right_controls_layout.addWidget(self.fullscreen_button)

    def toggle_fullscreen(self) -> None:
        """Toggle fullscreen mode."""
        # Get the main window
        main_window = self.media_player_widget.window()
        if main_window.isFullScreen():
            for widget in self.other_visible_widgets:
                widget.show()
            # show the window in the previous size
            main_window.showMaximized()
            self.fullscreen_button.setIcon(self.fullscreen_icon)
        else:
            for widget in self.other_visible_widgets:
                widget.hide()
            main_window.showFullScreen()
            self.fullscreen_button.setIcon(self.exit_fullscreen_icon)

    def add_progress_control(self) -> None:
        """Add progress control."""
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.media_controls_layout_below.addWidget(self.progress_slider)

        # Connect media player signals to update the progress slider
        self.positionChanged.connect(self.update_position)
        self.durationChanged.connect(self.set_duration)

        # Connect slider signals to update video position
        self.progress_slider.sliderMoved.connect(self.set_position)
        self.progress_slider.sliderReleased.connect(self.slider_released)

    def update_position(self, position: int) -> None:
        """Update the progress slider position."""
        # Only update if not being dragged to prevent jumps during manual sliding
        if not self.progress_slider.isSliderDown():
            self.progress_slider.setValue(position)

    def set_duration(self, duration: int) -> None:
        """Set the progress slider range based on media duration."""
        self.progress_slider.setRange(0, duration)

    def set_position(self, position: int) -> None:
        """Set the media position when slider is moved."""
        self.setPosition(position)

    def slider_released(self) -> None:
        """Handle slider release event."""
        self.setPosition(self.progress_slider.value())

    def play_data(self, data: bytes, name: str) -> None:
        """Play the video."""
        self.stop()
        self.buffer = QBuffer()
        self.buffer.setData(QByteArray(data))
        self.buffer.open(QBuffer.OpenModeFlag.ReadOnly)

        self.setSourceDevice(self.buffer, name)

        super().play()
