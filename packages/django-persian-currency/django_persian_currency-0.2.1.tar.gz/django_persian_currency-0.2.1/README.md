# 🏷️ Toman Display Template Tags for Django

A simple Django template tag library to render integers as Persian currency strings, converting numbers into Persian digits and formatting values with appropriate units like "هزار", "میلیون", and "میلیارد".

## ✨ Features

- Converts integer values to human-readable Persian currency format.
- Supports Persian digit conversion (e.g., `123` → `۱۲۳`).
- Handles values in billions, millions, thousands, and ones.
- Appends a customizable postfix (default: `تومان`).
- Gracefully handles invalid or missing input.

---

## 🚀 Installation

Just drop the Python file into one of your Django app's `templatetags/` directories.

For example:

```
myapp/
├── templatetags/
│   └── toman_display.py
```

Make sure your app is listed in `INSTALLED_APPS` in your `settings.py`.

---

## 🧠 Available Filters

### `toman_display`

Formats numbers using Persian digits and currency breakdown.

#### Example:

```django
{{ 12500000|toman_display }}
```

**Output:**
```
۱۲ میلیون و ۵۰۰ هزار تومان
```

#### With custom postfix:

```django
{{ 12500000|toman_display:"ریال" }}
```

**Output:**
```
۱۲ میلیون و ۵۰۰ هزار ریال
```

---

### `toman_display_summary`

This filter is defined but currently not implemented in the provided code. You can extend it to provide a short summary format if needed (e.g., only the largest unit, like "۱۲ میلیون").

---

### `to_persian_digits` (internal helper)

Converts standard digits to Persian numerals.

```python
to_persian_digits(123456)  # Output: '۱۲۳۴۵۶'
```

---

## 🧪 Error Handling

If a non-numeric or invalid value is passed, the output defaults to:

```
۰ تومان
```

---

## 📄 License

MIT – Feel free to use and modify.
