from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QPushButton, QDialog
)
from .datepicker import JalaliDatePicker
from jalali_calendar import JalaliDate
from .utils import get_font, translate, Theme


class JalaliDateEdit(QWidget):
    """A widget for selecting a date, showing a popup JalaliDatePicker."""
    dateSelected = Signal(JalaliDate)

    def __init__(self, parent=None, theme: Theme = None, scale: float = 1.0):
        super().__init__(parent)
        self.setFont(get_font(14 * scale))
        self.theme = theme or Theme()
        self.scale = scale
        self._date = JalaliDate.today()

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
        self.lineEdit.setText(translate(self._date.strftime("%Y / %m / %d")))

    def _show_popup(self):
        if self._popup is None:
            self._popup = QDialog(self)
            self._popup.setWindowFlags(Qt.Popup)

            bg_color = self.theme.widget_bg.name()
            self._popup.setStyleSheet(
                f"QDialog {{ "
                f"background-color: {bg_color}; "
                f"border: 1px solid #ccc; "
                f"border-radius: 8px; "
                f"}}"
            )

            layout = QHBoxLayout(self._popup)
            layout.setContentsMargins(0, 0, 0, 0)
            self._datepicker = JalaliDatePicker(
                theme=self.theme, scale=self.scale
            )
            layout.addWidget(self._datepicker)
            self._datepicker.dateSelected.connect(self._on_date_selected)

        self._datepicker.set_date(self._date)
        point = self.mapToGlobal(self.geometry().bottomLeft())
        self._popup.move(point)
        self._popup.show()

    def _on_date_selected(self, date):
        self.set_date(date)
        if self._popup:
            self._popup.close()

    def set_date(self, date: JalaliDate):
        """Sets the widget's date and emits the dateSelected signal."""
        self._date = date
        self._update_display()
        self.dateSelected.emit(self._date)

    def date(self) -> JalaliDate:
        """Returns the currently selected date."""
        return self._date