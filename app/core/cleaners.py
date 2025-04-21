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


def extract_blocks(text: str):
    blocks = re.findall(r"\[.*?\]", text)
    return blocks


def extract_lead_info(text: str) -> str:
    blocks = extract_blocks(text)
    if not blocks or blocks[0] not in ["[TESTE]", "[PRE ESCALA]"]:
        return ""
    if len(blocks) < 6:
        return ""
    return f"{blocks[1]}{blocks[4]}{blocks[5]}"


def extract_lead_block(text: str) -> str:
    blocks = extract_blocks(text)
    if not blocks or blocks[0] not in ["[TESTE]", "[PRE ESCALA]"]:
        return ""
    if len(blocks) < 2:
        return ""
    return blocks[1][1:-1]


def extract_ad_block(text: str) -> str:
    blocks = extract_blocks(text)
    if not blocks or blocks[0] not in ["[TESTE]", "[PRE ESCALA]"]:
        return ""
    if len(blocks) < 5:
        return ""
    return blocks[4][1:-1]


def extract_ad_lead(text: str) -> str:
    blocks = extract_blocks(text)
    if not blocks or blocks[0] not in ["[TESTE]", "[PRE ESCALA]"]:
        return ""
    if len(blocks) < 5:
        return ""
    return f"{blocks[1]}{blocks[4]}"
