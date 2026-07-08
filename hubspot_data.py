"""
╔══════════════════════════════════════════════════════════════════╗
║  hubspot_data.py · Capa de datos HubSpot (en vivo) para el         ║
║  Dashboard ATC — Opción Yo                                         ║
║                                                                   ║
║  · El token se lee SOLO de Streamlit Secrets (nunca del código).  ║
║      [secrets]  HUBSPOT_TOKEN = "pat-..."                         ║
║  · Todas las llamadas están CACHEADAS (respeta rate limits).      ║
║  · Filtra automáticamente los pipelines marcados [NO USAR].       ║
╚══════════════════════════════════════════════════════════════════╝

Uso desde el dashboard:
    import hubspot_data as hub
    if hub.hubspot_activo():
        tickets = hub.tickets_recientes(dias=30)     # DataFrame
        owners  = hub.owners_map()                    # {ownerId: nombre}
"""

import io
import time
import requests
import pandas as pd
import streamlit as st

API = "https://api.hubapi.com"

# Pipelines VIGENTES (los [NO USAR] se excluyen). Verificado en la cuenta 40159402.
PIPELINES = {
    "111962122": "Problemas técnicos",
    "74974093":  "Fidelización",
    "74755616":  "Administración",
    "58252620":  "Flujo automatizado",
    "705217631": "Consultores",
    "653848881": "Coordinación",
}
PIPELINES_NO_USAR = {"0", "51390113"}   # [NO USAR] Atención al Cliente / Cancelaciones

# Propiedades de ticket que nos interesan (esquema real de la cuenta)
TICKET_PROPS = [
    "subject", "createdate", "hs_lastmodifieddate", "closed_date",
    "hs_pipeline", "hs_pipeline_stage", "hs_ticket_category", "hs_ticket_priority",
    "hs_resolution", "respondido_a_tiempo_o_a_destiempo",
    "rangos_de_tiempo_para_primera_respuesta", "hubspot_owner_id",
    "seguimientos_de_ticket",
]


# ── Autenticación ─────────────────────────────────────────────────
def hubspot_activo() -> bool:
    """True si hay token configurado en Secrets."""
    try:
        return bool(st.secrets.get("HUBSPOT_TOKEN"))
    except Exception:
        return False


def _headers():
    return {"Authorization": f"Bearer {st.secrets['HUBSPOT_TOKEN']}",
            "Content-Type": "application/json"}


# ── Owners (dueños) ───────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def owners_map() -> dict:
    """{ownerId (str): 'Nombre Apellido'} — cacheado 1 h."""
    out, after = {}, None
    for _ in range(20):
        params = {"limit": 100}
        if after:
            params["after"] = after
        r = requests.get(f"{API}/crm/v3/owners/", headers=_headers(),
                         params=params, timeout=20)
        if r.status_code != 200:
            break
        data = r.json()
        for o in data.get("results", []):
            nombre = f"{o.get('firstName','')} {o.get('lastName','')}".strip()
            out[str(o["id"])] = nombre or o.get("email", str(o["id"]))
        after = data.get("paging", {}).get("next", {}).get("after")
        if not after:
            break
    return out


# ── Tickets (en vivo, cacheado) ───────────────────────────────────
@st.cache_data(ttl=300, show_spinner="⏳ Consultando HubSpot…")
def tickets_recientes(dias: int = 30, solo_vigentes: bool = True) -> pd.DataFrame:
    """Tickets creados en los últimos N días. Cacheado 5 min (respeta rate limits).
    Excluye pipelines [NO USAR] si solo_vigentes=True."""
    desde_ms = int((time.time() - dias * 86400) * 1000)
    body = {
        "filterGroups": [{
            "filters": [{"propertyName": "createdate", "operator": "GTE",
                         "value": str(desde_ms)}]
        }],
        "properties": TICKET_PROPS,
        "sorts": [{"propertyName": "createdate", "direction": "DESCENDING"}],
        "limit": 100,
    }
    filas, after, guard = [], None, 0
    while guard < 60:                      # tope de seguridad (6.000 tickets)
        guard += 1
        if after:
            body["after"] = after
        r = requests.post(f"{API}/crm/v3/objects/tickets/search",
                          headers=_headers(), json=body, timeout=30)
        if r.status_code == 429:           # rate limit → esperar y reintentar
            time.sleep(2)
            continue
        if r.status_code != 200:
            st.error(f"HubSpot respondió {r.status_code}. Revisa el token/scopes.")
            break
        data = r.json()
        for t in data.get("results", []):
            filas.append(t.get("properties", {}))
        after = data.get("paging", {}).get("next", {}).get("after")
        if not after:
            break

    df = pd.DataFrame(filas)
    if df.empty:
        return df

    # Enriquecer: nombres de pipeline y owner, fechas
    df["pipeline_nombre"] = df.get("hs_pipeline", pd.Series(dtype=str)).map(
        lambda p: PIPELINES.get(str(p), f"({p})"))
    om = owners_map()
    df["owner_nombre"] = df.get("hubspot_owner_id", pd.Series(dtype=str)).map(
        lambda o: om.get(str(o), "—"))
    for c in ["createdate", "closed_date", "hs_lastmodifieddate"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")

    if solo_vigentes and "hs_pipeline" in df.columns:
        df = df[~df["hs_pipeline"].astype(str).isin(PIPELINES_NO_USAR)]
    return df.reset_index(drop=True)


# ── Resumen rápido (para KPIs) ────────────────────────────────────
def resumen_tickets(df: pd.DataFrame) -> dict:
    if df is None or df.empty:
        return {"total": 0, "sin_respuesta": 0, "a_destiempo": 0, "pct_destiempo": 0}
    total = len(df)
    col = df.get("respondido_a_tiempo_o_a_destiempo", pd.Series(dtype=str)).fillna("")
    a_dest = int(col.str.contains("destiempo", case=False).sum())
    return {
        "total": total,
        "a_destiempo": a_dest,
        "pct_destiempo": round(a_dest / total * 100, 1) if total else 0,
        "pipelines": df["pipeline_nombre"].nunique() if "pipeline_nombre" in df else 0,
    }
