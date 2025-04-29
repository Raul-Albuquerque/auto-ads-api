import base64, os, shutil
from typing import List, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict

from config import TIMEZONE


def get_date(day: str, period: str) -> str:
    current_date = datetime.now(TIMEZONE)

    if day == "yesterday":
        current_date -= timedelta(days=1)

    if period == "start":
        target_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "end":
        target_date = current_date.replace(hour=23, minute=59, second=59, microsecond=0)
    else:
        raise ValueError("O parâmetro 'period' deve ser 'start' ou 'end'.")

    return target_date.isoformat()


def generate_basic_token(username: str, password: str) -> str:
    credentials = f"{username}:{password}"
    token_bytes = base64.b64encode(credentials.encode("utf-8"))
    token = f"Basic {token_bytes.decode('utf-8')}"

    return token


def delete_reports_folder(folder="email-reports"):
    if os.path.exists(folder):
        shutil.rmtree(folder)
        print(f"Pasta '{folder}' e seus arquivos foram removidos com sucesso.")
    else:
        print(f"Pasta '{folder}' não encontrada.")


def groupy_offer(lista_de_listas, tamanho_grupo=6):
    return [
        lista_de_listas[i : i + tamanho_grupo]
        for i in range(0, len(lista_de_listas), tamanho_grupo)
    ]


def to_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


def deduplicate_leads_group(leads_group):
    final_result = {}

    for lead_name, campaigns in leads_group.items():
        grouped_ads = {}
        for entry in campaigns:
            if len(entry) < 8:
                continue

            campaign_name = entry[6]
            ad_name = entry[7]
            key = (campaign_name, ad_name)

            approved = to_int(entry[1])
            spend = to_int(entry[4])
            revenue = to_int(entry[3]) if spend > 0 else 0  # Revenue only if spend > 0

            if key not in grouped_ads:
                new_entry = entry.copy()
                new_entry[1] = approved
                new_entry[3] = revenue
                new_entry[4] = spend
                grouped_ads[key] = new_entry
            else:
                grouped_ads[key][1] += approved
                grouped_ads[key][3] += revenue
                grouped_ads[key][4] += spend  # Always add spend

            # Convert to dict using ad name as the key
        final_result[lead_name] = {item[7]: item for item in grouped_ads.values()}

    return final_result


def groupy_leads(lista_de_listas, bloco_tamanho=8):
    resultado = []
    total_blocos = (
        len(lista_de_listas[0]) // bloco_tamanho
    )  # Assumindo todas do mesmo tamanho

    for i in range(total_blocos):
        grupo = []
        for filha in lista_de_listas:
            inicio = i * bloco_tamanho
            fim = inicio + bloco_tamanho
            grupo.append(filha[inicio:fim])  # Agora adiciona a sublista
        resultado.append(grupo)

    return resultado


def ungroup_leads(grupos):
    num_listas = len(grupos[0])  # Quantidade de listas filhas
    listas_reconstruidas = [[] for _ in range(num_listas)]

    for grupo in grupos:
        for i, bloco in enumerate(grupo):
            listas_reconstruidas[i].extend(bloco)

    return listas_reconstruidas


def get_date_range(period: str) -> dict:
    if period == "today":
        target_date = datetime.now()
    elif period == "yesterday":
        target_date = datetime.now() - timedelta(days=1)
    else:
        raise ValueError("Período inválido. Use 'today' ou 'yesterday'.")

    start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end = target_date.replace(hour=23, minute=59, second=59, microsecond=0)

    return {
        "start_date": start.strftime("%Y-%m-%d %H:%M:%S"),
        "end_date": end.strftime("%Y-%m-%d %H:%M:%S"),
    }


def convert_stats_to_list(data: List[Dict[str, Any]]) -> List[List[Any]]:
    return [
        [
            item["player_id"],
            item["name"].strip(),
            item["totalUniqDeviceEvents"],
            item["total_over_pitch"],
            item["total_under_pitch"],
            item["error"],
        ]
        for item in data
        if not item.get("error")
    ]


def get_all_players_id(players_by_offer: dict):
    players_id_list = []
    for players in players_by_offer.values():
        players_id_list.extend(players)
    return players_id_list


def process_data(raw_data):
    result = {}

    for ad_name, entries in raw_data.items():
        if ad_name == "":  # ignora entradas sem nome
            continue

        platforms = defaultdict(
            lambda: {
                "sum_total_uniq": 0,
                "sum_over_pitch": 0,
                "sum_under_pitch": 0,
                "ad_name": ad_name,
                "platform": "",
            }
        )

        for entry in entries:
            _, _, total_uniq, over, under, _, platform = entry

            platforms[platform]["sum_total_uniq"] += int(total_uniq)
            platforms[platform]["sum_over_pitch"] += int(over)
            platforms[platform]["sum_under_pitch"] += int(under)
            platforms[platform]["platform"] = platform

        result[ad_name] = platforms

    return result


def formatted_date(day: str = "today") -> str:
    week_days = ["seg.", "ter.", "qua.", "qui.", "sex.", "sáb.", "dom."]
    months = [
        "jan.",
        "fev.",
        "mar.",
        "abr.",
        "mai.",
        "jun.",
        "jul.",
        "ago.",
        "set.",
        "out.",
        "nov.",
        "dez.",
    ]

    today = datetime.now()

    if day == "today":
        date = today
    elif day == "yesterday":
        date = today - timedelta(days=1)
    else:
        raise ValueError("Parâmetro 'day' deve ser 'today' ou 'yesterday'.")

    week_day = week_days[date.weekday()]
    d = date.day
    month = months[date.month - 1]

    return f"{week_day} {d:02d} {month}"
