from pydantic import BaseModel


class UtmifyFilters(BaseModel):
    level: str  # ad | campaign
    report_type: str  # controle_ads | leads | escalados
    period: str  # today | yesterday


class AdsLevasReport(BaseModel):
    active_offer: str  # all | nome da oferta em maíusculo
