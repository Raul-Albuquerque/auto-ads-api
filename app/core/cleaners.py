import re


def extract_ad_name(ad_name: str) -> str:
    ad_name = ad_name.strip()
    bracket_match = re.findall(r"\[[^\[\]]+\]", ad_name)
    if len(bracket_match) >= 2:
        return f"{bracket_match[0]} {bracket_match[1]}"
    if not re.match(r"^[A-Z]{3}_[A-Z]{3}", ad_name):
        return ""
    first_part = ad_name.split(" ")[0]
    matches = re.findall(r"[A-Za-z0-9]+(?:\.[0-9]+)?", first_part)

    if not matches:
        return ""

    return "_".join(matches)


def extract_offer_name(ad_name: str) -> str:
    ad_name = ad_name.strip()
    bracket_match = re.findall(r"\[[^\[\]]+\]", ad_name)
    if bracket_match:
        first_block = bracket_match[0][1:-1]
        if "CRST_" in first_block:
            parts = first_block.split("CRST_")
            if len(parts) == 2 and parts[1]:
                return parts[1]
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


def extract_player_plataform(s: str) -> str:
    match = re.search(r"\[(YT|FB)\]\[[A-Z]{3}_[A-Z]{3}\]$", s)
    if match:
        return match.group(1)
    return ""


def extract_player_offer_name(s: str) -> str:
    match = re.search(r"\[(YT|FB)\]\[([A-Z]{3}_[A-Z]{3})\]$", s)
    if match:
        return match.group(2)
    return ""
