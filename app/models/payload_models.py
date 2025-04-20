from pydantic import BaseModel


class UtmifyFilters(BaseModel):
    level: str  # ad | campaign
    report_type: str  # controle_ads | leads | escalados
    period: str  # today | yesterday
