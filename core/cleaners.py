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
