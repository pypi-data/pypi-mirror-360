from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout, 
    QStackedWidget, QGraphicsOpacityEffect
)
from PySide6.QtGui import QFont
from jalali_calendar import JalaliDate
from .utils import get_font, LANG, translate, to_english_digits

class JalaliDatePicker(QWidget):
    dateSelected = Signal(JalaliDate)

    def __init__(self, parent=None, show_footer=True):
        super().__init__(parent)
        self.show_footer = show_footer
        self.setLayoutDirection(Qt.RightToLeft)
        self.setFont(get_font(14))
        
        self._selected_date = JalaliDate.today()
        self._displayed_date = self._selected_date
        self.animation = None
        
        self._init_ui()
        self._update_ui()

    def selected_date(self) -> JalaliDate:
        return self._selected_date

    def set_date(self, date: JalaliDate):
        self._selected_date = date
        self._displayed_date = date
        self._change_view(0, animate=False)

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        header = QHBoxLayout()
        self._next_btn = QPushButton("›")
        self._prev_btn = QPushButton("‹")
        self._next_btn.clicked.connect(lambda: self._update_displayed_date(1))
        self._prev_btn.clicked.connect(lambda: self._update_displayed_date(-1))
        
        self._header_label = QLabel()
        font = get_font(14, True)
        self._header_label.setFont(font)
        self._header_label.setAlignment(Qt.AlignCenter)
        self._header_label.mousePressEvent = self._on_header_clicked
        self._header_label.setCursor(Qt.PointingHandCursor)
        
        header.addWidget(self._prev_btn)
        header.addWidget(self._header_label, 1)
        header.addWidget(self._next_btn)
        main_layout.addLayout(header)
        
        self._stack = QStackedWidget(self)
        self._views = [QWidget(self) for _ in range(3)]
        self._grids = [QGridLayout(v) for v in self._views]
        for v in self._views:
            self._stack.addWidget(v)
        main_layout.addWidget(self._stack)
        
        if self.show_footer:
            footer = QHBoxLayout()
            self._today_btn = QPushButton(LANG['today'])
            self._today_btn.clicked.connect(self._go_to_today)
            footer.addStretch()
            footer.addWidget(self._today_btn)
            footer.addStretch()
            main_layout.addLayout(footer)

    def _update_ui(self):
        self._update_header()
        self._populate_view()

    def _update_header(self):
        idx = self._stack.currentIndex()
        if idx == 0:
            month_name = LANG['months'][self._displayed_date.month]
            self._header_label.setText(translate(f"{month_name} {self._displayed_date.year}"))
        elif idx == 1:
            self._header_label.setText(translate(str(self._displayed_date.year)))
        else:
            start_y = self._displayed_date.year - 6
            self._header_label.setText(translate(f"{start_y} - {start_y + 11}"))
    
    def _clear_grid(self, grid):
        while grid.count():
            item = grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _populate_view(self):
        idx = self._stack.currentIndex()
        self._clear_grid(self._grids[idx])
        if idx == 0: self._populate_day_view()
        elif idx == 1: self._populate_month_view()
        else: self._populate_year_view()
    
    def _populate_day_view(self):
        grid = self._grids[0]
        names = LANG['weekdays_short']
        for i, name in enumerate(names):
            label = QLabel(translate(name), font=get_font(12, True), alignment=Qt.AlignCenter)
            grid.addWidget(label, 0, i)
        
        first = JalaliDate(self._displayed_date.year, self._displayed_date.month, 1)
        start_wd = first.weekday()
        days_in_m = 31 if first.month <= 6 else (30 if first.month <= 11 else (30 if first.is_leap() else 29))
        r, c = 1, start_wd
        for d in range(1, days_in_m + 1):
            btn = QPushButton(translate(str(d)))
            btn.clicked.connect(self._on_day_clicked)
            cur = JalaliDate(self._displayed_date.year, self._displayed_date.month, d)
            btn.setProperty("style", "Highlight" if cur == self._selected_date else "")
            grid.addWidget(btn, r, c)
            c += 1
            if c > 6: c, r = 0, r + 1

    def _populate_month_view(self):
        grid = self._grids[1]
        r, c = 0, 0
        for i, name in enumerate(LANG['months'][1:]):
            btn = QPushButton(name)
            btn.setProperty("month_num", i + 1)
            btn.clicked.connect(self._on_month_clicked)
            grid.addWidget(btn, r, c)
            c += 1
            if c > 2: c, r = 0, r + 1

    def _populate_year_view(self):
        grid = self._grids[2]
        start_y = self._displayed_date.year - 6
        r, c = 0, 0
        for i in range(12):
            y = start_y + i
            btn = QPushButton(translate(str(y)))
            btn.setProperty("year_num", y)
            btn.clicked.connect(self._on_year_clicked)
            grid.addWidget(btn, r, c)
            c += 1
            if c > 2: c, r = 0, r + 1

    def _change_view(self, new_index, animate=True):
        if not animate or (self.animation and self.animation.state() == QPropertyAnimation.Running):
            self._stack.setCurrentIndex(new_index)
            self._update_ui()
            return
        
        current_widget = self._stack.currentWidget()
        opacity_effect = QGraphicsOpacityEffect(current_widget)
        current_widget.setGraphicsEffect(opacity_effect)
        self.animation = QPropertyAnimation(opacity_effect, b"opacity")
        self.animation.setDuration(150)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(lambda: self._finish_fade(new_index))
        self.animation.start()
    
    def _finish_fade(self, new_index):
        self._stack.setCurrentIndex(new_index)
        self._update_ui()
        new_widget = self._stack.currentWidget()
        opacity_effect = QGraphicsOpacityEffect(new_widget)
        new_widget.setGraphicsEffect(opacity_effect)
        self.animation = QPropertyAnimation(opacity_effect, b"opacity")
        self.animation.setDuration(150)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()

    def _on_header_clicked(self, e):
        self._change_view((self._stack.currentIndex() + 1) % 3)

    def _on_day_clicked(self):
        btn = self.sender()
        day_int = int(to_english_digits(btn.text()))
        self._selected_date = JalaliDate(self._displayed_date.year, self._displayed_date.month, day_int)
        self.dateSelected.emit(self._selected_date)
        self._populate_day_view()

    def _on_month_clicked(self):
        self._displayed_date = JalaliDate(self._displayed_date.year, self.sender().property("month_num"), 1)
        self._change_view(0)

    def _on_year_clicked(self):
        self._displayed_date = JalaliDate(self.sender().property("year_num"), self._displayed_date.month, 1)
        self._change_view(1)

    def _go_to_today(self):
        self.set_date(JalaliDate.today())
        self.dateSelected.emit(self._selected_date)

    def _update_displayed_date(self, d):
        idx, y, m = self._stack.currentIndex(), self._displayed_date.year, self._displayed_date.month
        if idx == 0:
            m += d
            new_y = y if 1 <= m <= 12 else y + d
            new_m = m if 1 <= m <= 12 else (1 if d > 0 else 12)
            self._displayed_date = JalaliDate(new_y, new_m, 1)
        elif idx == 1:
            self._displayed_date = JalaliDate(y + d, m, 1)
        else:
            self._displayed_date = JalaliDate(y + (12 * d), m, 1)
        self._update_ui()