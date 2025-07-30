from django import template

register = template.Library()

def to_persian_digits(s):
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    return ''.join(persian_digits[int(c)] if c.isdigit() else c for c in str(s))

def format_with_commas(value):
    return f"{value:,}"

@register.filter
def toman_display(value, postfix="تومان"):
    try:
        value = int(value)
        available_coins = [(1000000000, "میلیارد"), (1000000, "میلیون"), (1000, "هزار"), (1, "")]
        final_coins = []

        for coin, vahed in available_coins:
            count = value // coin

            if count:
                persian_value = to_persian_digits(count)
                value_and_vahed = [persian_value, vahed]

                if not vahed:
                    value_and_vahed.pop()

                final_coins.append(
                    " ".join(value_and_vahed)
                )
                value %= coin

        result = " و ".join(final_coins)

        if postfix:
            result = " ".join([result, postfix])
        
        return result 

    except (ValueError, TypeError):
        return f"۰ {postfix}"


@register.filter
def toman_display_summary(value, postfix="تومان"):
    try:
        value = int(value)
        vahed = ""
        lst_result = []

        if value >= 1_000_000_000:
            value = round(value / 1_000_000_000, 2)
            vahed = "میلیارد"
        elif value >= 1_000_000:
            value = round(value / 1_000_000, 2)
            vahed = "میلیون"
        elif value >= 1_000:
            vahed = "هزار"
            value = round(value / 1_000, 2)

        formated_value = format_with_commas(value)
        persian_value = to_persian_digits(formated_value)

        lst_result.append(persian_value)
        if vahed:
            lst_result.append(vahed)
        if postfix:
            lst_result.append(postfix)
        
        return " ".join(lst_result)

    except (ValueError, TypeError):
        return f"۰ {postfix}"