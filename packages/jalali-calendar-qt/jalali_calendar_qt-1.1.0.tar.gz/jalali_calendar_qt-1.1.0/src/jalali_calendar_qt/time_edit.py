import datetime
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QPushButton, QDialog
)
from .timepicker import AnalogTimePicker
from .utils import get_font, translate, Theme, LANG


class JalaliTimeEdit(QWidget):
    """A widget for selecting a time, showing a popup AnalogTimePicker."""
    timeSelected = Signal(datetime.time)

    def __init__(self, parent=None, theme: Theme = None,
                 scale: float = 1.0, use_12h: bool = False):
        super().__init__(parent)
        self.setFont(get_font(14 * scale))
        self.theme = theme or Theme()
        self.scale = scale
        self.use_12h = use_12h
        self._time = datetime.datetime.now().time().replace(
            second=0, microsecond=0
        )

        self.lineEdit = QLineEdit()
        self.button = QPushButton("...")

        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.lineEdit.setReadOnly(True)
        self.lineEdit.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lineEdit)

        button_size = int(32 * self.scale)
        self.button.setFixedSize(button_size, button_size)
        layout.addWidget(self.button)

        self._popup = None
        self.button.clicked.connect(self._show_popup)
        self._update_display()

    def _update_display(self):
        if self.use_12h:
            h12 = self._time.hour % 12
            h12 = 12 if h12 == 0 else h12
            period = LANG['pm'] if self._time.hour >= 12 else LANG['am']
            text = f"{h12:02d}:{self._time.minute:02d} {period}"
            self.lineEdit.setText(translate(text))
        else:
            self.lineEdit.setText(translate(self._time.strftime("%H:%M")))

    def _show_popup(self):
        if self._popup is None:
            self._popup = QDialog(self)
            self._popup.setWindowFlags(Qt.Popup)
            bg_color = self.theme.widget_bg.name()
            self._popup.setStyleSheet(
                f"QDialog {{ background-color: {bg_color}; "
                f"border: 1px solid #ccc; border-radius: 8px; }}"
            )
            layout = QHBoxLayout(self._popup)
            layout.setContentsMargins(0, 0, 0, 0)
            self._timepicker = AnalogTimePicker(
                theme=self.theme, scale=self.scale, use_12h=self.use_12h
            )
            layout.addWidget(self._timepicker)
            self._timepicker.timeSelected.connect(self._on_time_selected)

        self._timepicker.set_time(self._time)
        point = self.mapToGlobal(self.geometry().bottomLeft())
        self._popup.move(point)
        self._popup.show()

    def _on_time_selected(self, t):
        self.set_time(t)
        if self._popup:
            self._popup.close()

    def set_time(self, t: datetime.time):
        """Sets the widget's time and emits the timeSelected signal."""
        self._time = t.replace(second=0, microsecond=0)
        self._update_display()
        self.timeSelected.emit(self._time)

    def time(self) -> datetime.time:
        """Returns the currently selected time."""
        return self._time