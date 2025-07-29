import math, datetime
from PySide6.QtCore import Qt, QPoint, Signal, QRect
from PySide6.QtGui import QPainter, QBrush, QPolygon, QPen, QPalette, QColor, QRadialGradient
from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QStackedWidget, QLabel
from .utils import get_font, LANG, translate, Theme

VIEW_HOUR, VIEW_MINUTE = 0, 1

class AnalogTimePicker(QWidget):
    timeSelected = Signal(datetime.time)
    def __init__(self, parent=None, show_footer=True, theme: Theme = None):
        super().__init__(parent)
        self.theme = theme or Theme()
        self.setFont(get_font(12))
        self.show_footer = show_footer
        self._time = datetime.datetime.now().time().replace(second=0, microsecond=0)
        self._init_ui()

    def time(self) -> datetime.time: return self._time
    def set_time(self, t: datetime.time):
        self._time = t.replace(second=0, microsecond=0)
        self._hour_view.set_time(self._time)
        self._minute_view.set_time(self._time)
        self._update_digital_display()

    def _init_ui(self):
        self.setMinimumSize(250, 280 if self.show_footer else 250)
        main_layout = QVBoxLayout(self); main_layout.setContentsMargins(5, 5, 5, 5)
        self._digital_display = QLabel(); self._digital_display.setAlignment(Qt.AlignCenter); self._digital_display.setFont(get_font(22, True)); self._digital_display.setObjectName("DigitalDisplay"); main_layout.addWidget(self._digital_display)
        self._stack = QStackedWidget(self)
        self._hour_view = ClockPainter(self, False, self.theme)
        self._minute_view = ClockPainter(self, True, self.theme)
        self._stack.addWidget(self._hour_view); self._stack.addWidget(self._minute_view); main_layout.addWidget(self._stack, 1)
        if self.show_footer:
            footer = QHBoxLayout(); self._back_button = QPushButton(LANG['back']); self._back_button.clicked.connect(self._go_to_hour_view); self._back_button.hide()
            self._now_button = QPushButton(LANG['now']); self._now_button.clicked.connect(self._go_to_now)
            footer.addWidget(self._back_button); footer.addStretch(); footer.addWidget(self._now_button); footer.addStretch(); main_layout.addLayout(footer)
        self._hour_view.time_updated.connect(self._on_time_updated); self._minute_view.time_updated.connect(self._on_time_updated)
        self._hour_view.selection_done.connect(self._go_to_minute_view); self._minute_view.selection_done.connect(self._on_minute_selected)
        self._update_digital_display()
    
    def _update_digital_display(self): self._digital_display.setText(translate(self._time.strftime("%H:%M")))
    def _go_to_hour_view(self):
        if self.show_footer: self._back_button.hide()
        self._stack.setCurrentIndex(0)
    def _go_to_minute_view(self):
        if self.show_footer: self._back_button.show()
        self._stack.setCurrentIndex(1)
    def _go_to_now(self): now = datetime.datetime.now().time(); self.set_time(now); self.timeSelected.emit(self.time()); self._go_to_hour_view()
    def _on_time_updated(self, t): self.set_time(t)
    def _on_minute_selected(self, t): self.set_time(t); self.timeSelected.emit(self.time()); self._go_to_hour_view()

class ClockPainter(QWidget):
    time_updated = Signal(datetime.time)
    selection_done = Signal(datetime.time)
    def __init__(self, parent_picker, is_minute_view=False, theme: Theme = None):
        super().__init__(parent_picker)
        self._is_minute_view = is_minute_view
        self.theme = theme or Theme()
        self._time = datetime.datetime.now().time()
        self.parent_picker = parent_picker
        self._dragging = False
    
    def set_time(self, t): self._time = t; self.update()
    
    def paintEvent(self, e):
        with QPainter(self) as p:
            p.setRenderHint(QPainter.Antialiasing); side = min(self.width(), self.height()); p.translate(self.width() / 2, self.height() / 2); p.scale(side / 250.0, side / 250.0)
            if self._is_minute_view: self._paint_minute_view(p)
            else: self._paint_hour_view(p)
            
    def _paint_hour_view(self, p):
        p.setPen(Qt.NoPen); grad = QRadialGradient(0, 0, 120); grad.setColorAt(0, self.theme.alternate_base.lighter(110)); grad.setColorAt(1, self.theme.alternate_base); p.setBrush(QBrush(grad)); p.drawEllipse(-120, -120, 240, 240)
        grad.setRadius(70); grad.setColorAt(0, self.theme.base.lighter(120)); grad.setColorAt(1, self.theme.base); p.setBrush(QBrush(grad)); p.drawEllipse(-70, -70, 140, 140)
        
        is_inner_active = self._time.hour >= 1 and self._time.hour <= 12
        font_inner = get_font(18, True); font_outer = get_font(15)
        
        p.setPen(self.theme.text if is_inner_active else self.theme.dimmed_text)
        for i in range(1, 13):
            p.setFont(font_inner); angle = math.radians(i * 30 - 90); x, y = 50 * math.cos(angle), 50 * math.sin(angle); p.drawText(QRect(int(x) - 18, int(y) - 18, 36, 36), Qt.AlignCenter, translate(str(i)))
        
        p.setPen(self.theme.text if not is_inner_active else self.theme.dimmed_text)
        for i in range(1, 13):
            p.setFont(font_outer); angle = math.radians(i * 30 - 90); x, y = 95 * math.cos(angle), 95 * math.sin(angle); p.drawText(QRect(int(x) - 18, int(y) - 18, 36, 36), Qt.AlignCenter, translate(str(i + 12 if i != 12 else 24)))
        
        pen = QPen(self.theme.text, 3); pen.setCapStyle(Qt.RoundCap); p.setPen(pen); h = self._time.hour
        hour_for_angle = h % 12 if h % 12 != 0 else 12; angle_h = hour_for_angle * 30
        len_h = 80 if not is_inner_active else 35
        p.save(); p.rotate(angle_h); p.drawConvexPolygon(QPolygon([QPoint(4, 7), QPoint(-4, 7), QPoint(0, -len_h)])); p.restore()
        p.setPen(Qt.NoPen); p.setBrush(QBrush(self.theme.highlight)); p.drawEllipse(-5, -5, 10, 10)

    def _paint_minute_view(self, p):
        p.setPen(Qt.NoPen); grad=QRadialGradient(0,0,120); grad.setColorAt(0,self.theme.base.lighter(120)); grad.setColorAt(1,self.theme.base); p.setBrush(QBrush(grad)); p.drawEllipse(-120,-120,240,240); p.save()
        for i in range(60):
            p.setPen(QPen(self.theme.text,2 if i%5==0 else 1)); p.drawLine(105 if i%5==0 else 110,0,118,0); p.rotate(6)
        p.restore()
        p.setPen(self.theme.text); p.setFont(get_font(15))
        for i in range(12): angle=math.radians(i*30); x,y=90*math.sin(angle),-90*math.cos(angle); p.drawText(QRect(int(x)-18,int(y)-18,36,36),Qt.AlignCenter,translate(f"{i*5 if i!=0 else '00'}"))
        p.setPen(Qt.NoPen); m_angle=self._time.minute*6; minute_hand=QPolygon([QPoint(4,7),QPoint(-4,7),QPoint(0,-85)]); p.setBrush(QBrush(self.theme.text)); p.save(); p.rotate(m_angle); p.drawConvexPolygon(minute_hand); p.restore()
        p.setBrush(QBrush(self.theme.highlight)); p.drawEllipse(-5,-5,10,10)

    def _update_time_from_pos(self, e_pos):
        side = min(self.width(), self.height()); cx, cy = self.width() / 2, self.height() / 2
        pos = e_pos; dx, dy = pos.x() - cx, pos.y() - cy
        angle = math.degrees(math.atan2(dy, dx)) + 90; angle = angle if angle >= 0 else angle + 360
        dist_sq = dx**2 + dy**2
        
        if self._is_minute_view:
            if dist_sq > 20**2: new_m = round(angle / 6.0) % 60; self.time_updated.emit(self._time.replace(minute=new_m))
        else:
            slot = round(angle / 30.0); slot = slot if slot != 0 else 12
            if 30**2 < dist_sq < 80**2:
                new_h = slot
            elif 80**2 < dist_sq < 115**2:
                new_h = 0 if slot == 12 else slot + 12
            else: return
            self.time_updated.emit(self._time.replace(hour=new_h))

    def mousePressEvent(self, e): self._dragging = True; self._update_time_from_pos(e.position().toPoint())
    def mouseMoveEvent(self, e):
        if self._dragging: self._update_time_from_pos(e.position().toPoint())
    def mouseReleaseEvent(self, e): self._dragging = False; self.selection_done.emit(self._time)