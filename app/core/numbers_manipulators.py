import re


def currency_to_int(value: str):
    if not isinstance(value, str) or not value.startswith("R$"):
        return value
    cleaned_value = re.sub(r"[^\d]", "", value)
    return int(cleaned_value) if cleaned_value.isdigit() else value


def str_to_int(value: str):
    clean_value = value.replace(".", "").replace(",", "")
    if clean_value.isdigit():
        return int(clean_value)
    return value


def int_to_currency(value: int):
    try:
        value = int(value)
        if value == 0:
            return 0.0
        return value / 100.0
    except (ValueError, TypeError):
        return value
