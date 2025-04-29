from app.core.numbers_manipulators import str_to_int, int_to_currency


def compute_metrics(
    spend: int,
    revenue: int,
    sales: int,
    uniq_views: int,
    clicks: int,
    impressions: int,
    total_over_pitch: int,
    total_under_pitch: int,
):
    roas = revenue / spend if spend > 0 else 0
    gross_profit = revenue - spend
    total_pitch = total_over_pitch + total_under_pitch
    cpa = int(spend / sales if sales > 0 else 0)
    vsl_conversion = round(sales / uniq_views if uniq_views > 0 else 0, 4)
    arpu = revenue // sales if sales > 0 else 0
    connect_rate = round(uniq_views / clicks if clicks > 0 else 0, 4)
    cpc = int(spend / clicks if clicks > 0 else 0)
    a_cpc = int((vsl_conversion * arpu) // 1.8)
    rpc = int(revenue / clicks if clicks > 0 else 0)
    ctr = round(clicks / impressions if impressions > 0 else 0, 4)
    cpm = int((spend / impressions * 1000) if impressions else 0)
    pitch_retention = total_over_pitch / total_pitch if total_pitch > 0 else 0

    return {
        "roas": round(roas, 2),
        "gross_profit": int_to_currency(gross_profit),
        "total_pitch": total_pitch,
        "cpa": int_to_currency(cpa),
        "vsl_conversion": vsl_conversion,
        "arpu": int_to_currency(arpu),
        "connect_rate": connect_rate,
        "cpc": int_to_currency(cpc),
        "a_cpc": int_to_currency(a_cpc),
        "rpc": int_to_currency(rpc),
        "ctr": ctr,
        "cpm": int_to_currency(cpm),
        "pitch_retention": round(pitch_retention, 4),
    }
