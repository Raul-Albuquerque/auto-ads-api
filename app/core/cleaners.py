import re


def extract_ad_name(ad_name: str) -> str:
    ad_name = ad_name.strip()
    pattern = r"^[A-Z]{3,4}_[A-Z]{3}(_[A-Z0-9]+)*$"

    if re.match(pattern, ad_name):
        return ad_name
    else:
        parts = ad_name.split(" ")[0]
        if re.match(r"^[A-Z]{3,4}_[A-Z]{3}(_[A-Z0-9]+)*$", parts):
            return parts
        return ""


def extract_offer_name(ad_name: str) -> str:
    match = re.match(r"([A-Z0-9]{3,4}_[A-Z0-9]{3})", ad_name)
    if match:
        return match.group(0)
    return ""


def extract_ad_d2d_status(fullname: str):
    if re.search(r"\[PAUSADO\]", fullname, re.IGNORECASE):
        return "paused"
    return "active"


def extract_ad_d2d_name(input_string: str) -> str:
    match = re.match(r"([^\[]+)", input_string)
    return match.group(1).strip() if match else input_string
