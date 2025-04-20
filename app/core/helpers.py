import base64, os, shutil
from datetime import datetime, timedelta

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
