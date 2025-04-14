import re

def extract_ad_name(ad_name: str) -> str:
  ad_name = ad_name.strip()
  pattern = r"^[A-Z]{3,4}_[A-Z]{3}(_[A-Z0-9]+)*$"
  
  if re.match(pattern, ad_name):
    return ad_name
  else:
    parts = ad_name.split(' ')[0]
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
  blocks = re.findall(r'\[.*?\]', text)
  return blocks

def extract_lead_info(text: str) -> str:
  blocks = extract_blocks(text)
  if not blocks or blocks[0] not in ['[TESTE]', '[PRE ESCALA]']:
    return ""
  if len(blocks) < 6:
    return ""
  return f"{blocks[1]}{blocks[4]}{blocks[5]}"

def extract_lead_block(text: str) -> str:
  blocks = extract_blocks(text)
  if not blocks or blocks[0] not in ['[TESTE]', '[PRE ESCALA]']:
    return ""
  if len(blocks) < 2:
    return ""
  return blocks[1][1:-1]

def extract_ad_block(text: str) -> str:
  blocks = extract_blocks(text)
  if not blocks or blocks[0] not in ['[TESTE]', '[PRE ESCALA]']:
    return ""
  if len(blocks) < 5:
    return ""
  return blocks[4][1:-1]

def agrupar_por_tabela(dados, colunas_por_tabela):
  resultado = {nome: [] for nome in colunas_por_tabela}
  for linha in dados:
    for nome, (inicio, fim) in colunas_por_tabela.items():
      resultado[nome].append(linha[inicio:fim])
  return resultado

def extract_ad_lead(text: str) -> str:
  blocks = extract_blocks(text)
  if not blocks or blocks[0] not in ['[TESTE]', '[PRE ESCALA]']:
    return ""
  if len(blocks) < 5:
    return ""
  return f"{blocks[1]}{blocks[4]}"

# test_list = [
#     "LVH_ESP_AD41_H1",
#     "LVH_ESP_AD08_H1_EMP17 1 1",
#     "TNT_ENG_AD10_H1 1",
#     "EMAC_ESP_AD11_H12",
#     "OPA_ESP_AD01_H2",
#     "LVH_ESP_AD44_H9",
#     "LVH_ESP_AD08_H1_EMP16 213212",
#     "Novo anúncio de Engajamento — Cópia",
#     "AQUECIMENTO 4",
#     "Novo anúncio de Engajamento — Cópia"
# ]

# for ad_name in test_list:
#     print(extract_ad_name(ad_name))