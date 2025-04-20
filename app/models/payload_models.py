from pydantic import BaseModel


class UtmifyFilters(BaseModel):
    level: str  # ad | campaign
    report_type: str  # controle_ads | leads | escalados
    period: str  # today | yesterday


class AdsControlReport(BaseModel):
    report_type: str  # ads_levas | ads_agregado
    active_offer: str  # all | nome da oferta em maíusculo
