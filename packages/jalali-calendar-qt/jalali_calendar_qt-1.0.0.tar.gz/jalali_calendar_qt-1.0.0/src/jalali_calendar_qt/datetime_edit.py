import datetime
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QDialog, QVBoxLayout, QFrame, QDialogButtonBox
from jalali_calendar import JalaliDateTime, JalaliDate
from .datepicker import JalaliDatePicker
from .timepicker import AnalogTimePicker
from .utils import get_font, LANG, translate

class JalaliDateTimeEdit(QWidget):
    dateTimeSelected = Signal(JalaliDateTime)
    def __init__(self, parent=None):
        super().__init__(parent); self.setFont(get_font(14)); self._datetime = JalaliDateTime.now(); self._init_ui()
    
    def _init_ui(self):
        layout = QHBoxLayout(self); layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(0)
        self._line_edit = QLineEdit(); self._line_edit.setReadOnly(True); self._line_edit.setAlignment(Qt.AlignCenter); layout.addWidget(self._line_edit)
        self._popup_button = QPushButton(); self._popup_button.setIcon(QIcon("src/jalali_calendar_qt/assets/calendar.svg")); self._popup_button.setFixedSize(32, 32)
        layout.addWidget(self._popup_button)
        self._popup = None
        self._popup_button.clicked.connect(self._show_popup)
        self._update_display()

    def _update_display(self):
        date_str = self._datetime.date().strftime("%Y/%m/%d"); time_str = self._datetime.time().strftime("%H:%M")
        self._line_edit.setText(translate(f"{date_str}  {time_str}"))

    def _show_popup(self):
        if self._popup is None:
            self._popup = QDialog(self); self._popup.setWindowTitle(translate("انتخاب تاریخ و زمان")); self._popup.setFont(get_font(14))
            
            self._popup_datepicker = JalaliDatePicker(show_footer=False)
            self._popup_timepicker = AnalogTimePicker(show_footer=False)
            
            picker_layout = QHBoxLayout(); picker_layout.addWidget(self._popup_datepicker); picker_layout.addWidget(QFrame(frameShape=QFrame.VLine)); picker_layout.addWidget(self._popup_timepicker)
            
            bbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            bbox.button(QDialogButtonBox.Ok).setText(LANG['ok']); bbox.button(QDialogButtonBox.Cancel).setText(LANG['cancel'])
            now_button = bbox.addButton(LANG['now'], QDialogButtonBox.ActionRole)
            now_button.clicked.connect(self._set_to_now_and_confirm)
            
            bbox.accepted.connect(self._on_confirm); bbox.rejected.connect(self._popup.reject)
            
            master_layout = QVBoxLayout(self._popup); master_layout.addLayout(picker_layout); master_layout.addWidget(bbox)
        
        self._popup_datepicker.set_date(self._datetime.date()); self._popup_timepicker.set_time(self._datetime.time())
        self._popup.exec()

    def _set_to_now_and_confirm(self):
        now_dt = JalaliDateTime.now()
        self.set_datetime(now_dt)
        self._popup.accept()

    def _on_confirm(self):
        new_dt = JalaliDateTime.combine(self._popup_datepicker.selected_date(), self._popup_timepicker.time())
        self.set_datetime(new_dt)
        self._popup.accept()

    def set_datetime(self, dt):
        self._datetime = dt; self._update_display(); self.dateTimeSelected.emit(self._datetime)
        
    def datetime(self) -> JalaliDateTime:
        return self._datetime