import base64,shutil,os
from itertools import chain
from datetime import datetime, timedelta, timezone

def get_date(day: str, period: str) -> str:
  br_timezone = timezone(timedelta(hours=-3))
  current_date = datetime.now(br_timezone)
  
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

def get_average_rate(new_rate: float, current_rate: float) -> float:
  if new_rate > 0 and current_rate > 0:
    return round((current_rate + new_rate) / 2, 4)
  if new_rate == 0:
    return current_rate
  elif current_rate == 0:
    return new_rate
  
def delete_reports_folder(folder="email-reports"):
    if os.path.exists(folder):
      shutil.rmtree(folder)
      print(f"Pasta '{folder}' e seus arquivos foram removidos com sucesso.")
    else:
      print(f"Pasta '{folder}' não encontrada.")

def groupy_offer(lista_de_listas, tamanho_grupo=6):
  return [lista_de_listas[i:i+tamanho_grupo] for i in range(0, len(lista_de_listas), tamanho_grupo)]

def groupy_leads(lista_de_listas, bloco_tamanho=8):
    resultado = []
    total_blocos = len(lista_de_listas[0]) // bloco_tamanho  # Assumindo todas do mesmo tamanho
    
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
    final_result[lead_name] = {
      item[7]: item for item in grouped_ads.values()
    }

  return final_result
