# Persian Jalali Calendar - Qt Widgets

A companion library providing beautiful, modern, scalable, and fully theme-aware Qt (PySide6) widgets for the `persian-jalali-calendar` library.

This library provides a set of professional date and time selection widgets designed for a native Persian user experience, including Right-to-Left layout, Persian numerals, and a custom Persian font.

## Installation

When you install this library, the core `persian-jalali-calendar` will be installed automatically as a dependency.

```bash
pip install jalali-calendar-qt
```
The included `BNazanin.ttf` font file will be used automatically.

## Widgets & Customization

The library provides three main "edit" widgets for easy integration.

- `JalaliDateEdit`: A compact input for selecting a date.
- `JalaliTimeEdit`: For selecting a time. Can be configured for 12-hour or 24-hour mode.
- `JalaliDateTimeEdit`: A combined editor for both date and time.

### Basic Usage

```python
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QFormLayout
from jalali_calendar_qt import (
    JalaliDateEdit, JalaliTimeEdit, JalaliDateTimeEdit
)

# Standard application setup
app = QApplication(sys.argv)
window = QMainWindow()
central_widget = QWidget()
layout = QFormLayout(central_widget)
window.setCentralWidget(central_widget)

# Create the widgets
date_editor = JalaliDateEdit()
time_editor_12h = JalaliTimeEdit(use_12h=True)
datetime_editor = JalaliDateTimeEdit() # Default is 24-hour time

# Add them to the layout
layout.addRow("Date:", date_editor)
layout.addRow("Time (12h):", time_editor_12h)
layout.addRow("Date & Time (24h):", datetime_editor)


# Connect to signals to get the selected values
date_editor.dateSelected.connect(lambda d: print(f"Date selected: {d}"))
time_editor_12h.timeSelected.connect(lambda t: print(f"Time selected: {t}"))
datetime_editor.dateTimeSelected.connect(
    lambda dt: print(f"DateTime selected: {dt}")
)

window.show()
sys.exit(app.exec())
```

### Advanced Customization: Theming & Scaling

All picker widgets can be fully customized using a `Theme` object and a `scale` factor. The `__init__` signature for the edit widgets is:

`JalaliTimeEdit(parent=None, theme: Theme = None, scale: float = 1.0, use_12h: bool = False)`
*(This signature is similar for `JalaliDateEdit` and `JalaliDateTimeEdit`)*

```python
from jalali_calendar_qt import JalaliDateTimeEdit, Theme

# 1. Define a custom theme by overriding default colors
# You can provide any valid hex color string.
fire_theme = Theme(
    widget_bg="#263238",             # Dark Gray
    text="#FFFFFF",
    dimmed_text="#90A4AE",
    calendar_highlight_bg="#FF7043", # Deep Orange
    calendar_highlight_text="#263238",
    clock_hand="#FFC107",            # Amber
    clock_hand_center="#FF8F00",     # Dark Amber
    clock_border="#607D8B",
    clock_tick="#B0BEC5",
    clock_inner_bg="#37474F",
    clock_outer_bg="#455A64",
)

# 2. Create the widget with your custom theme and scale
custom_datetime_edit = JalaliDateTimeEdit(
    theme=fire_theme, # Apply the theme
    scale=1.2,        # Make it 120% larger
    use_12h=True      # Use the 12-hour clock face
)

# The popup will now have your custom "fire" theme!
```

**Customizable `Theme` Attributes:**

- `widget_bg`: The main background of the picker popups.
- `text`: The primary text color (e.g., clock numbers, month names).
- `dimmed_text`: The color for inactive text (e.g., other rings on the 24h clock).
- `calendar_highlight_bg`: The background for the selected day in the calendar.
- `calendar_highlight_text`: The text color for the selected day.
- `clock_hand`: The color of the clock's hands.
- `clock_hand_center`: The color of the small circle in the middle of the clock.
- `clock_tick`: The color of the tick marks around the clock.
- `clock_border`: The color of the borders around the clock faces.
- `clock_inner_bg`: The background color of the inner clock ring (or the whole face in 12h mode).
- `clock_outer_bg`: The background color of the outer 24h clock ring.

## License

This project is licensed under the MIT License.