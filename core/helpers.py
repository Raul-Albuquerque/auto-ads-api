import base64
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