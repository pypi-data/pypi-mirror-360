from PySide6.QtCore import (
    Qt, Signal, QPropertyAnimation, QPoint, QParallelAnimationGroup
)
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout,
    QStackedWidget, QGraphicsOpacityEffect
)
from jalali_calendar import JalaliDate
from .utils import (
    get_font, LANG, translate, to_english_digits, Theme,
    StyledLabel, StyledButton
)


class JalaliDatePicker(QWidget):
    """A widget for picking a Jalali date from a calendar grid view."""
    dateSelected = Signal(JalaliDate)

    def __init__(self, parent=None, show_footer=True,
                 theme: Theme = None, scale: float = 1.0):
        super().__init__(parent)
        self.theme = theme or Theme()
        self.scale = scale
        self.show_footer = show_footer
        self.setLayoutDirection(Qt.RightToLeft)
        self.setFont(get_font(14 * self.scale))
        self._selected_date = JalaliDate.today()
        self._displayed_date = self._selected_date
        self.animation_group = None
        self._init_ui()
        self._update_ui()

    def selected_date(self) -> JalaliDate:
        """Returns the currently selected JalaliDate."""
        return self._selected_date

    def set_date(self, date: JalaliDate):
        """Sets the date of the widget and updates the view."""
        self._selected_date = date
        self._displayed_date = date
        self._change_view(0, animate=False)

    def _init_ui(self):
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), self.theme.widget_bg)
        self.setPalette(p)

        min_w = int(280 * self.scale)
        min_h = int(300 * self.scale) if self.show_footer else int(270 * self.scale)
        self.setMinimumSize(min_w, min_h)

        margins = int(5 * self.scale)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(margins, margins, margins, margins)

        header = QHBoxLayout()
        self._prev_btn = StyledButton("›", 16 * self.scale)
        self._next_btn = StyledButton("‹", 16 * self.scale)
        self._prev_btn.clicked.connect(
            lambda: self._slide_view(1)
        )
        self._next_btn.clicked.connect(
            lambda: self._slide_view(-1)
        )
        self._header_label = StyledLabel("", 16 * self.scale, bold=True)
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
            self._today_btn = StyledButton(LANG['today'], 14 * self.scale)
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
        y, m = self._displayed_date.year, self._displayed_date.month
        if idx == 0:
            month_name = LANG['months'][m]
            text = f"{month_name} {y}"
            self._header_label.setText(translate(text))
        elif idx == 1:
            self._header_label.setText(translate(str(y)))
        else:
            start_y = y - (y % 10)
            text = f"{start_y} - {start_y + 9}"
            self._header_label.setText(translate(text))

    def _clear_grid(self, grid):
        while grid.count():
            item = grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _populate_view(self):
        idx = self._stack.currentIndex()
        self._clear_grid(self._grids[idx])
        if idx == 0:
            self._populate_day_view()
        elif idx == 1:
            self._populate_month_view()
        else:
            self._populate_year_view()

    def _populate_day_view(self):
        grid = self._grids[0]
        names = LANG['weekdays_short']
        for i, name in enumerate(names):
            label = StyledLabel(translate(name), 13 * self.scale, bold=True,
                                alignment=Qt.AlignCenter)
            grid.addWidget(label, 0, i)
        first = JalaliDate(
            self._displayed_date.year, self._displayed_date.month, 1
        )
        start_wd = first.weekday()
        days_in_m = (31 if first.month <= 6 else (
            30 if first.month <= 11 else (30 if first.is_leap() else 29))
        )
        r, c = 1, start_wd
        for d in range(1, days_in_m + 1):
            btn = StyledButton(translate(str(d)), 14 * self.scale)
            btn.clicked.connect(self._on_day_clicked)
            btn.setMinimumHeight(int(32 * self.scale))
            cur = JalaliDate(
                self._displayed_date.year, self._displayed_date.month, d
            )
            if cur == self._selected_date:
                bg = self.theme.calendar_highlight_bg.name()
                fg = self.theme.calendar_highlight_text.name()
                btn.setStyleSheet(f"background-color: {bg}; color: {fg};")
            grid.addWidget(btn, r, c)
            c += 1
            if c > 6:
                c, r = 0, r + 1

    def _populate_month_view(self):
        grid = self._grids[1]
        r, c = 0, 0
        for i, name in enumerate(LANG['months'][1:]):
            btn = StyledButton(name, 14 * self.scale)
            btn.setProperty("month_num", i + 1)
            btn.clicked.connect(self._on_month_clicked)
            grid.addWidget(btn, r, c)
            c += 1
            if c > 2:
                c, r = 0, r + 1

    def _populate_year_view(self):
        grid = self._grids[2]
        start_y = self._displayed_date.year - \
            (self._displayed_date.year % 10)
        r, c = 0, 0
        for i in range(10):
            y = start_y + i
            btn = StyledButton(translate(str(y)), 14 * self.scale)
            btn.setProperty("year_num", y)
            btn.clicked.connect(self._on_year_clicked)
            grid.addWidget(btn, r, c)
            c += 1
            if c > 2:
                c, r = 0, r + 1

    def _animate_view_change(self, direction: int, new_index: int):
        if (self.animation_group and
                self.animation_group.state() == QPropertyAnimation.Running):
            return

        current_widget = self._stack.currentWidget()
        w = current_widget.width()
        current_opacity = QGraphicsOpacityEffect(current_widget)
        current_widget.setGraphicsEffect(current_opacity)

        anim_fade_out = QPropertyAnimation(current_opacity, b"opacity")
        anim_fade_out.setDuration(150); anim_fade_out.setEndValue(0.0)

        anim_slide_out = QPropertyAnimation(current_widget, b"pos")
        anim_slide_out.setDuration(150)
        anim_slide_out.setEndValue(QPoint(w * -direction, 0))

        anim_group_out = QParallelAnimationGroup()
        anim_group_out.addAnimation(anim_fade_out)
        anim_group_out.addAnimation(anim_slide_out)

        def on_finish():
            self._stack.setCurrentIndex(new_index)
            self._update_ui()
            new_widget = self._stack.currentWidget()
            new_widget.move(w * direction, 0)

            opacity_in = QGraphicsOpacityEffect(new_widget)
            new_widget.setGraphicsEffect(opacity_in)
            anim_fade_in = QPropertyAnimation(opacity_in, b"opacity")
            anim_fade_in.setDuration(150); anim_fade_in.setEndValue(1.0)
            
            anim_slide_in = QPropertyAnimation(new_widget, b"pos")
            anim_slide_in.setDuration(150); anim_slide_in.setEndValue(QPoint(0,0))

            anim_group_in = QParallelAnimationGroup()
            anim_group_in.addAnimation(anim_fade_in)
            anim_group_in.addAnimation(anim_slide_in)
            self.animation_group = anim_group_in
            self.animation_group.start()

        anim_group_out.finished.connect(on_finish)
        self.animation_group = anim_group_out
        self.animation_group.start()

    def _change_view(self, new_index, animate=True):
        current_index = self._stack.currentIndex()
        if not animate or current_index == new_index:
            self._stack.setCurrentIndex(new_index)
            self._update_ui()
            return
        direction = 1 if new_index > current_index else -1
        self._animate_view_change(direction, new_index)

    def _slide_view(self, direction: int):
        y, m = self._displayed_date.year, self._displayed_date.month
        idx = self._stack.currentIndex()

        if idx == 0:
            m += direction; new_y,new_m=(y,m) if 1<=m<=12 else (y+direction,1 if direction>0 else 12)
        elif idx == 1:
            new_y,new_m = y+direction,m
        else:
            new_y,new_m = y+(direction*10),m
        self._displayed_date = JalaliDate(new_y, new_m, 1)
        self._animate_view_change(direction, idx)

    def _on_header_clicked(self, e):
        self._change_view((self._stack.currentIndex() + 1) % 3)

    def _on_day_clicked(self):
        btn = self.sender()
        day_int = int(to_english_digits(btn.text()))
        self._selected_date = JalaliDate(
            self._displayed_date.year, self._displayed_date.month, day_int
        )
        self.dateSelected.emit(self._selected_date)
        self._populate_day_view()

    def _on_month_clicked(self):
        month = self.sender().property("month_num")
        self._displayed_date = JalaliDate(
            self._displayed_date.year, month, 1
        )
        self._change_view(0)

    def _on_year_clicked(self):
        year = self.sender().property("year_num")
        self._displayed_date = JalaliDate(
            year, self._displayed_date.month, 1
        )
        self._change_view(1)

    def _go_to_today(self):
        self.set_date(JalaliDate.today())
        self.dateSelected.emit(self._selected_date)