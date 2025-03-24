import re

def currency_to_int(value: str):
  if not isinstance(value, str) or not value.startswith("R$"):
    return value
  cleaned_value = re.sub(r'[^\d]', '', value)
  return int(cleaned_value) if cleaned_value.isdigit() else value

def str_to_int(value: str):
  if value.isdigit():
    return int(value)
  return value

def percentage_to_float(value: str) -> float:
  if not value or not isinstance(value, str) or not value.replace(",", "").replace(".", "").replace("%", "").isnumeric():
    return value
  value = value.replace("%", "").replace(",", ".")
  return round(float(value) / 100, 4)

# def percentage_to_float_ctr(value: str) -> float:
#   if not value or not isinstance(value, str) or not value.replace(",", "").replace(".", "").replace("%", "").isnumeric():
#     return value
#   value = value.replace("%", "").replace(",", ".")
#   return round(float(value) / 100, 4)

def percentage_to_float_from_utmify_hook(value: str):
  if value == "":
    return 0
  if not isinstance(value, str) or not value.replace(",", "").replace(".", "").replace("%", "").isnumeric():
    return value 
  value = value.replace(",", ".")
  return round(float(value), 4)

def percentage_to_float_from_utmify_ctr(value: str):
  # Verifica se o valor é uma string vazia ou qualquer string não numérica (que não é um número)
    if isinstance(value, str) and (value == "" or not value.replace(',', '.', 1).replace('.', '', 1).isdigit()):
        return value
    
    # Se for um número com vírgula, converte para ponto
    try:
        # Substitui vírgula por ponto para converter para float
        number = float(str(value).replace(',', '.'))
        return round(number / 100, 4)  # Converte para porcentagem e arredonda para 4 casas decimais
    except ValueError:
        return value  # Retorna o valor original se não for um número válido

def int_to_currency(value: int):
  try:
    value = int(value)
    if value == 0:
      return 0.0  # Retorna 0.0 se o valor for 0
    return value / 100.0  # Divide por 100 e retorna como float
  except (ValueError, TypeError):
    # Se não for um número válido, retorna um valor padrão
    return "Invalid input"

# test_list = [
#     "R$ 0,00",
#     "R$ 227,02",
#     "R$ 1.650,75",
#     "R$ 500",
#     "R$ 23,45",
#     "",
#     "Alguma coisa",
#     "R$ 9.999,99",
#     "R$ 100",
#     "Teste sem valor"
# ]

# for item in test_list:
#     print(currency_to_int(item))
