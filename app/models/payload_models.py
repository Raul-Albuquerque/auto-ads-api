from pydantic import BaseModel


class UtmifyFilters(BaseModel):
    level: str  # ad | campaign
    report_type: str  # controle_ads | leads | escalados
    period: str  # today | yesterday
    plataform: str  # meta | yt_ads


class AdsControlReport(BaseModel):
    report_type: str  # controle_ads | leads | escalados
    active_offer: str  # all | nome da oferta em maíusculo


class LeadsReport(BaseModel):
    report_type: str  # controle_ads | leads | escalados
    period: str  # today | yesterday
    active_offer: str  # all | nome da oferta em maíusculo


class EscaladosReport(LeadsReport):
    pass


class TrafficControlReport(BaseModel):
    report_type: str  # controle_ads | leads | escalados
    period: str  # today | yesterday
    active_offer: str  # all | nome da oferta em maíusculo
    plataform: str


class VturbFilters(BaseModel):
    period: str  # today | yesterday
    report_type: str
