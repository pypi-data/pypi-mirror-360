from PySide6.QtGui import QFontDatabase, QFont, QColor, QPalette

LANG = {
    "weekdays_short": ["ش", "ی", "د", "س", "چ", "پ", "ج"],
    "months": ["", "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور", "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"],
    "today": "امروز", "now": "اکنون", "back": "‹ بازگشت", "ok": "تایید", "cancel": "لغو",
}
PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
ENGLISH_DIGITS = "0123456789"
TRANSLATION_TABLE_EN_TO_FA = str.maketrans(ENGLISH_DIGITS, PERSIAN_DIGITS)
TRANSLATION_TABLE_FA_TO_EN = str.maketrans(PERSIAN_DIGITS, ENGLISH_DIGITS)

_CUSTOM_FONT_FAMILY = None

def get_font(size=12, bold=False):
    global _CUSTOM_FONT_FAMILY
    if _CUSTOM_FONT_FAMILY is None:
        try:
            font_id = QFontDatabase.addApplicationFont("src/jalali_calendar_qt/assets/BNazanin.ttf")
            _CUSTOM_FONT_FAMILY = QFontDatabase.applicationFontFamilies(font_id)[0] if font_id != -1 else "Tahoma"
        except Exception: _CUSTOM_FONT_FAMILY = "Tahoma"
    font = QFont(_CUSTOM_FONT_FAMILY); font.setPixelSize(size); font.setBold(bold)
    return font

def translate(text: str) -> str:
    """Translates a string's numerals to Persian. The to_english parameter is removed."""
    return str(text).translate(TRANSLATION_TABLE_EN_TO_FA)

def to_english_digits(text: str) -> str:
    """A dedicated function to convert Persian numerals back to English for logic."""
    return str(text).translate(TRANSLATION_TABLE_FA_TO_EN)

class Theme:
    def __init__(self, **kwargs):
        p = QPalette(); self.base = p.color(QPalette.Base); self.text = p.color(QPalette.WindowText)
        self.highlight = p.color(QPalette.Highlight); self.highlight_text = p.color(QPalette.HighlightedText)
        self.alternate_base = QColor(self.base).darker(115) if self.base.lightness() > 127 else QColor(self.base).lighter(115)
        self.dimmed_text = QColor(self.text); self.dimmed_text.setAlpha(100)
        self.__dict__.update(kwargs)