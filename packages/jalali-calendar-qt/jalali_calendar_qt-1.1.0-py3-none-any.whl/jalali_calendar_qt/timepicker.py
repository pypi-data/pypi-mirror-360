import math
import datetime
from PySide6.QtCore import (
    Qt, QPoint, Signal, QRect, QPropertyAnimation
)
from PySide6.QtGui import QPainter, QBrush, QPen
from PySide6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QStackedWidget, QLabel,
    QGraphicsOpacityEffect, QButtonGroup
)
from .utils import get_font, LANG, translate, Theme, StyledButton


class AnalogTimePicker(QWidget):
    """A widget for selecting a time using an analog clock face."""
    timeSelected = Signal(datetime.time)

    def __init__(self, parent=None, show_footer=True,
                 theme: Theme = None, scale: float = 1.0, use_12h: bool = False):
        super().__init__(parent)
        self.theme = theme or Theme()
        self.scale = scale
        self.use_12h = use_12h
        self.setFont(get_font(12 * self.scale))
        self.show_footer = show_footer
        self._time = datetime.datetime.now().time().replace(
            second=0, microsecond=0
        )
        self.animation = None
        self._init_ui()

    def time(self) -> datetime.time:
        """Returns the currently selected time."""
        return self._time

    def set_time(self, t: datetime.time):
        """Sets the widget's time."""
        self._time = t.replace(second=0, microsecond=0)
        self.update_components()

    def update_components(self):
        """Updates child components with the current time."""
        if hasattr(self, '_hour_view'):
            self._hour_view.set_time(self._time)
            self._minute_view.set_time(self._time)
            self._update_digital_display()
        if self.use_12h and hasattr(self, '_am_button'):
            is_pm = self._time.hour >= 12
            self._pm_button.setChecked(is_pm)
            self._am_button.setChecked(not is_pm)

    def _init_ui(self):
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), self.theme.widget_bg)
        self.setPalette(p)
        min_w = int(250 * self.scale)
        min_h = int(280 * self.scale) if self.show_footer else min_w
        if self.use_12h:
            min_h += int(40 * self.scale)

        self.setMinimumSize(min_w, min_h)
        main_layout = QVBoxLayout(self)
        margins = int(5 * self.scale)
        main_layout.setContentsMargins(margins, margins, margins, margins)

        self._digital_display = QLabel()
        self._digital_display.setAlignment(Qt.AlignCenter)
        self._digital_display.setFont(get_font(28 * self.scale, True))
        main_layout.addWidget(self._digital_display)

        if self.use_12h:
            self._am_pm_layout = QHBoxLayout()
            self._am_button = StyledButton(LANG['am'], 14 * self.scale)
            self._pm_button = StyledButton(LANG['pm'], 14 * self.scale)
            self._am_button.setCheckable(True)
            self._pm_button.setCheckable(True)
            self._am_pm_group = QButtonGroup(self)
            self._am_pm_group.addButton(self._am_button)
            self._am_pm_group.addButton(self._pm_button)
            self._am_pm_group.setExclusive(True)
            self._am_pm_layout.addWidget(self._am_button)
            self._am_pm_layout.addWidget(self._pm_button)
            self._am_button.clicked.connect(
                lambda: self._on_period_change(is_pm=False)
            )
            self._pm_button.clicked.connect(
                lambda: self._on_period_change(is_pm=True)
            )
            main_layout.addLayout(self._am_pm_layout)

        self._stack = QStackedWidget(self)
        self._hour_view = ClockPainter(
            self, False, self.theme, self.scale, self.use_12h
        )
        self._minute_view = ClockPainter(
            self, True, self.theme, self.scale, self.use_12h
        )
        self._stack.addWidget(self._hour_view)
        self._stack.addWidget(self._minute_view)
        main_layout.addWidget(self._stack, 1)

        if self.show_footer:
            footer = QHBoxLayout()
            self._back_button = QPushButton(LANG['back'])
            self._back_button.clicked.connect(self._go_to_hour_view)
            self._back_button.hide()
            self._now_button = QPushButton(LANG['now'])
            self._now_button.clicked.connect(self._go_to_now)
            footer.addWidget(self._back_button)
            footer.addStretch()
            footer.addWidget(self._now_button)
            footer.addStretch()
            main_layout.addLayout(footer)

        self._hour_view.time_updated.connect(self._on_time_updated)
        self._minute_view.time_updated.connect(self._on_time_updated)
        self._hour_view.selection_done.connect(self._go_to_minute_view)
        self._minute_view.selection_done.connect(self._on_minute_selected)
        self.set_time(self._time)

    def _on_period_change(self, is_pm: bool):
        h = self._time.hour
        if is_pm and h < 12:
            h += 12
        elif not is_pm and h >= 12:
            h -= 12
        new_time = self._time.replace(hour=h)
        self._on_time_updated(new_time)

    def _update_digital_display(self):
        if self.use_12h:
            h12 = self._time.hour % 12
            h12 = 12 if h12 == 0 else h12
            period = LANG['pm'] if self._time.hour >= 12 else LANG['am']
            text = f"{h12:02d}:{self._time.minute:02d} {period}"
            self._digital_display.setText(translate(text))
        else:
            self._digital_display.setText(
                translate(self._time.strftime("%H:%M"))
            )

    def _change_view(self, new_index: int):
        if (self.animation and
                self.animation.state() == QPropertyAnimation.Running):
            return

        current_widget = self._stack.currentWidget()
        opacity = QGraphicsOpacityEffect(current_widget)
        current_widget.setGraphicsEffect(opacity)
        anim_out = QPropertyAnimation(opacity, b"opacity")
        anim_out.setDuration(150)
        anim_out.setStartValue(1.0)
        anim_out.setEndValue(0.0)

        def on_finish():
            self._stack.setCurrentIndex(new_index)
            new_widget = self._stack.currentWidget()
            opacity_in = QGraphicsOpacityEffect(new_widget)
            new_widget.setGraphicsEffect(opacity_in)
            anim_in = QPropertyAnimation(opacity_in, b"opacity")
            anim_in.setDuration(150)
            anim_in.setStartValue(0.0)
            anim_in.setEndValue(1.0)
            self.animation = anim_in
            self.animation.start()

        anim_out.finished.connect(on_finish)
        self.animation = anim_out
        self.animation.start()

    def _go_to_hour_view(self):
        if self._stack.currentIndex() != 0:
            if self.show_footer:
                self._back_button.hide()
            self._change_view(0)

    def _go_to_minute_view(self):
        if self._stack.currentIndex() != 1:
            if self.show_footer:
                self._back_button.show()
            self._change_view(1)

    def _go_to_now(self):
        self.set_time(datetime.datetime.now().time())
        self.timeSelected.emit(self.time())
        self._go_to_hour_view()

    def _on_time_updated(self, t):
        self.set_time(t)

    def _on_minute_selected(self, t):
        self.set_time(t)
        self.timeSelected.emit(self.time())
        self._go_to_hour_view()


class ClockPainter(QWidget):
    time_updated = Signal(datetime.time)
    selection_done = Signal(datetime.time)

    def __init__(self, parent_picker, is_minute_view=False,
                 theme: Theme = None, scale: float = 1.0, use_12h: bool = False):
        super().__init__(parent_picker)
        self._is_minute_view = is_minute_view
        self.theme = theme or Theme()
        self.scale = scale
        self.use_12h = use_12h
        self._time = datetime.datetime.now().time()
        self._visual_time = self._time
        self._dragging = False

    def set_time(self, t):
        self._time = t
        self._visual_time = t
        self.update()

    def paintEvent(self, e):
        with QPainter(self) as p:
            p.setRenderHint(QPainter.Antialiasing)
            side = min(self.width(), self.height())
            p.translate(self.width() / 2, self.height() / 2)
            p.scale(side / 250.0, side / 250.0)
            if self._is_minute_view:
                self._paint_minute_view(p)
            else:
                self._paint_hour_view(p)

    def _paint_hour_view(self, p):
        inner_radius = 80
        p.setPen(Qt.NoPen)
        p.setBrush(self.theme.clock_outer_bg)
        p.drawEllipse(-120, -120, 240, 240)
        if not self.use_12h:
            p.setBrush(self.theme.clock_inner_bg)
            p.drawEllipse(-inner_radius, -inner_radius,
                          inner_radius*2, inner_radius*2)
        border_pen = QPen(self.theme.clock_border, 2)
        p.setPen(border_pen); p.setBrush(Qt.NoBrush)
        p.drawEllipse(-120, -120, 240, 240)
        if not self.use_12h:
            p.drawEllipse(-inner_radius, -inner_radius,
                          inner_radius*2, inner_radius*2)

        p.save(); p.setPen(QPen(self.theme.clock_tick))
        for i in range(12):
            p.setPen(QPen(self.theme.clock_tick, 2)); p.drawLine(110, 0, 118, 0)
            if not self.use_12h:
                p.setPen(QPen(self.theme.clock_tick, 1))
                p.drawLine(inner_radius-7, 0, inner_radius-1, 0)
            p.rotate(30)
        p.restore()
        
        if self.use_12h:
            p.setFont(get_font(20*self.scale,True)); p.setPen(self.theme.text)
            for i in range(1,13):
                angle=math.radians(i*30-90); x=95*math.cos(angle); y=95*math.sin(angle)
                p.drawText(QRect(int(x)-22,int(y)-22,44,44),Qt.AlignCenter,translate(str(i)))
        else:
            is_inner = 1 <= self._visual_time.hour <= 12
            is_outer = 13<=self._visual_time.hour<=23 or self._visual_time.hour==0
            p.setFont(get_font(24*self.scale,True)); p.setPen(self.theme.text if is_inner else self.theme.dimmed_text)
            for i in range(1,13):angle=math.radians(i*30-90);x=(inner_radius-22)*math.cos(angle);y=(inner_radius-22)*math.sin(angle);p.drawText(QRect(int(x)-22,int(y)-22,44,44),Qt.AlignCenter,translate(str(i)))
            p.setFont(get_font(20*self.scale)); p.setPen(self.theme.text if is_outer else self.theme.dimmed_text)
            for i in range(1,13):angle=math.radians(i*30-90);x=100*math.cos(angle);y=100*math.sin(angle);num_str=str(i+12 if i<12 else 0);p.drawText(QRect(int(x)-22,int(y)-22,44,44),Qt.AlignCenter,translate(num_str))

        pen=QPen(self.theme.clock_hand,3);pen.setCapStyle(Qt.RoundCap);p.setPen(pen)
        h=self._visual_time.hour
        if self.use_12h: ha, len_h = h % 12, 85; ha = 12 if ha == 0 else ha
        else:
            if h==0:ha,len_h=12,95
            elif 1<=h<=12:ha,len_h=h,inner_radius-28
            else:ha,len_h=h-12,95
        p.save();p.rotate(ha*30);p.drawLine(0,10,0,-len_h);p.restore()
        p.setBrush(self.theme.clock_hand_center);p.setPen(Qt.NoPen);p.drawEllipse(-5,-5,10,10)
    
    def _paint_minute_view(self, p):
        p.setPen(Qt.NoPen);p.setBrush(self.theme.clock_inner_bg);p.drawEllipse(-120,-120,240,240)
        border_pen=QPen(self.theme.clock_border,2);p.setPen(border_pen);p.setBrush(Qt.NoBrush);p.drawEllipse(-120,-120,240,240)
        p.save()
        for i in range(60):p.setPen(QPen(self.theme.clock_tick,2 if i%5==0 else 1));p.drawLine(105 if i%5==0 else 110,0,118,0);p.rotate(6)
        p.restore();p.setPen(self.theme.text);p.setFont(get_font(20*self.scale))
        for i in range(12):angle=math.radians(i*30);x,y=95*math.sin(angle),-95*math.cos(angle);p.drawText(QRect(int(x)-22,int(y)-22,44,44),Qt.AlignCenter,translate(f"{i*5:02d}"))
        pen=QPen(self.theme.clock_hand,2);pen.setCapStyle(Qt.RoundCap);p.setPen(pen)
        m_angle=self._visual_time.minute*6;p.save();p.rotate(m_angle);p.drawLine(0,10,0,-100);p.restore()
        p.setBrush(self.theme.clock_hand_center);p.setPen(Qt.NoPen);p.drawEllipse(-5,-5,10,10)

    def _update_time_from_pos(self,e_pos):
        cx,cy=self.width()/2,self.height()/2;dx,dy=e_pos.x()-cx,e_pos.y()-cy;angle=math.degrees(math.atan2(dy,dx))+90;angle=angle if angle>=0 else angle+360
        dist_from_center=(dx**2+dy**2)**0.5
        
        if self._is_minute_view:
            if dist_from_center>20*(self.width()/250.0):self._visual_time=self._time.replace(minute=round(angle/6.0)%60)
        else: # Hour view
            slot=round(angle/30.0); slot=12 if slot==0 else slot
            if self.use_12h:
                if dist_from_center > 30*(self.width()/250.0):
                    is_pm=self._time.hour>=12;new_hour_12h=slot
                    new_hour_24h = new_hour_12h if new_hour_12h != 12 else 0
                    if is_pm and new_hour_12h != 12: new_hour_24h += 12
                    self._visual_time=self._time.replace(hour=new_hour_24h)
                else: self._visual_time=self._time
            else: # 24h logic
                inner_r=80*(self.width()/250.0)
                if dist_from_center<30*(self.width()/250.0): self._visual_time=self._time
                elif dist_from_center<inner_r: self._visual_time=self._time.replace(hour=slot)
                else: self._visual_time=self._time.replace(hour=0 if slot==12 else slot+12)
        
        self.update()

    def mousePressEvent(self,e): self._dragging=True;self._update_time_from_pos(e.position().toPoint())
    def mouseMoveEvent(self,e):
        if self._dragging:self._update_time_from_pos(e.position().toPoint())
    def mouseReleaseEvent(self,e):
        self._dragging=False
        if self._visual_time!=self._time: self._time=self._visual_time; self.time_updated.emit(self._time)
        self.selection_done.emit(self._time)