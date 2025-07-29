# Persian Jalali Calendar - PyQt Widgets

A companion library providing beautiful, modern, and theme-aware PyQt (PySide6) widgets for the `persian-jalali-calendar` library.

This library provides a set of professional date and time selection widgets designed for a native Persian user experience, including Right-to-Left layout, Persian numerals, and a custom Persian font.

## Installation

When you install this library, the core `persian-jalali-calendar` will be installed automatically as a dependency.

```bash
pip install jalali-calendar-qt
```
You will also need to provide the `BNazanin.ttf` font file in a folder like `src/jalali_calendar_qt/assets/` for the custom font to work.

## Widgets

### `JalaliDateEdit`
A compact input field that shows a popup `JalaliDatePicker`.

```python
from jalali_calendar_qt import JalaliDateEdit

date_editor = JalaliDateEdit()
```

### `JalaliTimeEdit`
A compact input field that shows a popup `AnalogTimePicker`.

```python
from jalali_calendar_qt import JalaliTimeEdit

time_editor = JalaliTimeEdit()
```

### `JalaliDateTimeEdit`
A compact input field that shows a combined popup with both date and time pickers.

```python
from jalali_calendar_qt import JalaliDateTimeEdit

datetime_editor = JalaliDateTimeEdit()
```

## Example Usage

```python
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from jalali_calendar_qt import JalaliDateEdit, JalaliTimeEdit, JalaliDateTimeEdit
from jalali_calendar_qt.utils import get_font, translate # For styling

# --- Main Application Window ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # ... setup window ...
        
        # Create the widgets
        date_edit = JalaliDateEdit()
        time_edit = JalaliTimeEdit()
        datetime_edit = JalaliDateTimeEdit()

        # Connect to their signals
        date_edit.dateSelected.connect(self.on_date_selected)
        time_edit.timeSelected.connect(self.on_time_selected)
        datetime_edit.dateTimeSelected.connect(self.on_datetime_selected)
        
        # ... add widgets to layout ...
        
    def on_date_selected(self, jdate):
        print(f"Date selected: {jdate}")
        
# ... (rest of standard application code) ...
```

## License

This project is licensed under the MIT License.