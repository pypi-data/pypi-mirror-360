from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QDialog
from .datepicker import JalaliDatePicker
from jalali_calendar import JalaliDate
from .utils import get_font, translate

class JalaliDateEdit(QWidget):
    dateSelected = Signal(JalaliDate)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(get_font(14))
        self._date = JalaliDate.today()
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
        self._popup_button.setIcon(QIcon("src/jalali_calendar_qt/assets/calendar.svg"))
        self._popup_button.setFixedSize(32, 32)
        layout.addWidget(self._popup_button)
        
        self._popup = None
        self._popup_button.clicked.connect(self._show_popup)
        self._update_display()

    def _update_display(self):
        self._line_edit.setText(translate(self._date.strftime("%Y / %m / %d")))

    def _show_popup(self):
        if self._popup is None:
            self._popup = QDialog(self)
            self._popup.setWindowFlags(Qt.Popup)
            layout = QHBoxLayout(self._popup)
            self._datepicker = JalaliDatePicker()
            layout.addWidget(self._datepicker)
            self._datepicker.dateSelected.connect(self._on_date_selected)
        
        self._datepicker.set_date(self._date)
        point = self.mapToGlobal(self.geometry().bottomLeft())
        self._popup.move(point)
        self._popup.show()

    def _on_date_selected(self, date):
        self.set_date(date)
        self._popup.close()

    def set_date(self, date):
        self._date = date
        self._update_display()
        self.dateSelected.emit(self._date)

    def date(self) -> JalaliDate:
        return self._date