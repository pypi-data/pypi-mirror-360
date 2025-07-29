import datetime
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QDialog
from .timepicker import AnalogTimePicker
from .utils import get_font, translate

class JalaliTimeEdit(QWidget):
    timeSelected = Signal(datetime.time)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(get_font(14))
        self._time = datetime.datetime.now().time().replace(second=0, microsecond=0)
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._line_edit = QLineEdit()
        self._line_edit.setReadOnly(True)
        self._line_edit.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._line_edit)
        
        self._popup_button = QPushButton()
        self._popup_button.setIcon(QIcon("src/jalali_calendar_qt/assets/clock.svg"))
        self._popup_button.setFixedSize(32, 32)
        layout.addWidget(self._popup_button)
        
        self._popup = None
        self._popup_button.clicked.connect(self._show_popup)
        self._update_display()

    def _update_display(self):
        self._line_edit.setText(translate(self._time.strftime("%H:%M")))

    def _show_popup(self):
        if self._popup is None:
            self._popup = QDialog(self)
            self._popup.setWindowFlags(Qt.Popup)
            layout = QHBoxLayout(self._popup)
            self._timepicker = AnalogTimePicker()
            layout.addWidget(self._timepicker)
            self._timepicker.timeSelected.connect(self._on_time_selected)
            
        self._timepicker.set_time(self._time)
        point = self.mapToGlobal(self.geometry().bottomLeft())
        self._popup.move(point)
        self._popup.show()

    def _on_time_selected(self, t):
        self.set_time(t)
        self._popup.close()

    def set_time(self, t):
        self._time = t.replace(second=0, microsecond=0)
        self._update_display()
        self.timeSelected.emit(self._time)

    def time(self) -> datetime.time:
        return self._time