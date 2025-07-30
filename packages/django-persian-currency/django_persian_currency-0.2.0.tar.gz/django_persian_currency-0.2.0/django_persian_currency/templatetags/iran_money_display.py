from django import template

register = template.Library()

def format_with_commas(value):
    return f"{value:,}"

def to_persian_digits(s):
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    return ''.join(persian_digits[int(c)] if c.isdigit() else c for c in str(s))

@register.filter
def toman_display(value):
    try:
        value = int(value)

        if value >= 1_000_000_000:
            if value % 1_000_000_000 == 0:
                return f"{to_persian_digits(value // 1_000_000_000)} میلیارد تومان"
        if value >= 1_000_000:
            if value % 1_000_000 == 0:
                return f"{to_persian_digits(value // 1_000_000)} میلیون تومان"
        if value >= 1_000:
            if value % 1_000 == 0:
                return f"{to_persian_digits(value // 1_000)} هزار تومان"

        formatted = format_with_commas(value)
        result = f"{to_persian_digits(formatted)} تومان"

        return f"{result} تومان"

    except (ValueError, TypeError):
        return "۰ تومان"
