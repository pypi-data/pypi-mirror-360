import datetime
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QPushButton, QDialog,
    QVBoxLayout, QFrame, QDialogButtonBox
)
from jalali_calendar import JalaliDateTime
from .datepicker import JalaliDatePicker
from .timepicker import AnalogTimePicker
from .utils import get_font, LANG, translate, Theme


class JalaliDateTimeEdit(QWidget):
    """A widget for selecting date and time, with a combined popup."""
    dateTimeSelected = Signal(JalaliDateTime)

    def __init__(self, parent=None, theme: Theme = None,
                 scale: float = 1.0, use_12h: bool = False):
        super().__init__(parent)
        self.setFont(get_font(14 * scale))
        self.theme = theme or Theme()
        self.scale = scale
        self.use_12h = use_12h
        self._datetime = JalaliDateTime.now()

        self.lineEdit = QLineEdit()
        self.button = QPushButton("...")

        self._popup = None
        self._popup_datepicker = None
        self._popup_timepicker = None
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

        self.button.clicked.connect(self._show_popup)
        self._update_display()

    def _update_display(self):
        date_str = self._datetime.date().strftime("%Y/%m/%d")
        if self.use_12h:
            h12, period = self._datetime.to_12h()
            time_str = f"{h12:02d}:{self._datetime.minute:02d} {period}"
        else:
            time_str = self._datetime.time().strftime("%H:%M")
        self.lineEdit.setText(translate(f"{date_str}  {time_str}"))

    def _show_popup(self):
        if self._popup is None:
            self._popup = QDialog(self)
            self._popup.setWindowTitle(translate("انتخاب تاریخ و زمان"))
            self._popup.setFont(get_font(14 * self.scale))
            self._popup.setStyleSheet(
                f"QDialog {{ background-color: "
                f"{self.theme.widget_bg.name()}; "
                f"border-radius: 8px; }}"
            )
            self._popup_datepicker = JalaliDatePicker(
                show_footer=False, theme=self.theme, scale=self.scale
            )
            self._popup_timepicker = AnalogTimePicker(
                show_footer=False, theme=self.theme, scale=self.scale,
                use_12h=self.use_12h
            )
            picker_layout = QHBoxLayout()
            picker_layout.addWidget(self._popup_datepicker)
            picker_layout.addWidget(QFrame(frameShape=QFrame.VLine))
            picker_layout.addWidget(self._popup_timepicker)
            bbox = QDialogButtonBox(
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel
            )
            bbox.button(QDialogButtonBox.Ok).setText(LANG['ok'])
            bbox.button(QDialogButtonBox.Cancel).setText(LANG['cancel'])
            now_button = bbox.addButton(LANG['now'], QDialogButtonBox.ActionRole)
            now_button.clicked.connect(self._set_to_now_and_confirm)
            bbox.accepted.connect(self._on_confirm)
            bbox.rejected.connect(self._popup.reject)
            master_layout = QVBoxLayout(self._popup)
            master_layout.addLayout(picker_layout)
            master_layout.addWidget(bbox)

        if self._popup_datepicker.selected_date() != self._datetime.date():
            self._popup_datepicker.set_date(self._datetime.date())
        if self._popup_timepicker.time() != self._datetime.time():
            self._popup_timepicker.set_time(self._datetime.time())
        self._popup.exec()

    def _set_to_now_and_confirm(self):
        self.set_datetime(JalaliDateTime.now())
        if self._popup:
            self._popup.accept()

    def _on_confirm(self):
        new_dt = JalaliDateTime.combine(
            self._popup_datepicker.selected_date(),
            self._popup_timepicker.time()
        )
        self.set_datetime(new_dt)
        if self._popup:
            self._popup.accept()

    def set_datetime(self, dt: JalaliDateTime):
        """Sets the widget's datetime and emits the dateTimeSelected signal."""
        self._datetime = dt
        self._update_display()
        self.dateTimeSelected.emit(self._datetime)

    def datetime(self) -> JalaliDateTime:
        """Returns the currently selected datetime."""
        return self._datetime