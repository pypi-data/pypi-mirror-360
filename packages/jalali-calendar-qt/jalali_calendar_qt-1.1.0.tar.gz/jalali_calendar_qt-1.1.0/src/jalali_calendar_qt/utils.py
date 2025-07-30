import sys
import os
from PySide6.QtGui import QFontDatabase, QFont, QColor, QPalette
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QLabel

LANG = {
    "weekdays_short": ["ش", "ی", "د", "س", "چ", "پ", "ج"],
    "months": ["", "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
               "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"],
    "today": "امروز", "now": "اکنون", "back": "‹ بازگشت", "ok": "تایید",
    "cancel": "لغو", "am": "ق.ظ", "pm": "ب.ظ",
}
PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
ENGLISH_DIGITS = "0123456789"
TRANSLATION_TABLE_EN_TO_FA = str.maketrans(ENGLISH_DIGITS, PERSIAN_DIGITS)
TRANSLATION_TABLE_FA_TO_EN = str.maketrans(PERSIAN_DIGITS, ENGLISH_DIGITS)

_CUSTOM_FONT_FAMILY = None


def _initialize_font():
    """Initializes and registers the custom font, returning its family name."""
    global _CUSTOM_FONT_FAMILY
    if _CUSTOM_FONT_FAMILY is None:
        try:
            current_dir = os.path.dirname(__file__)
            font_path = os.path.join(
                current_dir, 'assets', 'BNazanin.ttf'
            )

            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id != -1:
                _CUSTOM_FONT_FAMILY = QFontDatabase.applicationFontFamilies(
                    font_id
                )[0]
            else:
                _CUSTOM_FONT_FAMILY = "Tahoma"
        except Exception as e:
            print(f"Font loading error: {e}")
            _CUSTOM_FONT_FAMILY = "Tahoma"
    return _CUSTOM_FONT_FAMILY


def get_font(size=12, bold=False) -> QFont:
    """Creates a QFont object with the custom font."""
    family = _initialize_font()
    font = QFont(family)
    font.setPixelSize(int(size))
    font.setBold(bold)
    return font


class StyledLabel(QLabel):
    def __init__(self, text: str, size: int, bold: bool = False, *args, **kwargs):
        super().__init__(text, *args, **kwargs)
        self.setFont(get_font(size, bold))
class StyledButton(QPushButton):
    def __init__(self, text: str, size: int, bold: bool = False, *args, **kwargs):
        super().__init__(text, *args, **kwargs)
        self.setFont(get_font(size, bold))
def translate(text: str) -> str:
    return str(text).translate(TRANSLATION_TABLE_EN_TO_FA)
def to_english_digits(text: str) -> str:
    return str(text).translate(TRANSLATION_TABLE_FA_TO_EN)
class Theme:
    def __init__(self, **kwargs):
        p=QPalette();is_dark=p.color(QPalette.ColorRole.Base).lightness()<128
        self.text=p.color(QPalette.ColorRole.Text);self.dimmed_text=QColor(self.text)
        self.dimmed_text.setAlpha(100);self.widget_bg=p.color(QPalette.ColorRole.Base)
        self.calendar_highlight_bg=QColor("#0078d4");self.calendar_highlight_text=QColor("#ffffff")
        self.clock_hand=QColor("#0078d4");self.clock_hand_center=QColor("#0078d4")
        self.clock_tick=QColor(self.text);self.clock_border=QColor(self.text)
        if is_dark:self.clock_inner_bg=QColor("#2c2c2c");self.clock_outer_bg=QColor("#222222");self.calendar_highlight_bg=QColor("#6cb4e8");self.calendar_highlight_text=QColor("#000000")
        else:self.clock_inner_bg=QColor("#ffffff");self.clock_outer_bg=QColor("#f0f0f0")
        for key, value in kwargs.items():
            if hasattr(self, key): setattr(self, key, QColor(value))