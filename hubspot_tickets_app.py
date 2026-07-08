"""
╔══════════════════════════════════════════════════════════════════╗
║  Tickets en vivo · Opción Yo (HubSpot)                             ║
║  Mini-panel para (1) validar la conexión a HubSpot y              ║
║  (2) servir de base al panel de Incidencias.                      ║
║                                                                   ║
║  Requiere en Streamlit → Secrets:                                ║
║      HUBSPOT_TOKEN = "pat-..."                                    ║
║  requirements.txt: streamlit, pandas, plotly, requests            ║
║  Ejecutar:  python -m streamlit run hubspot_tickets_app.py        ║
╚══════════════════════════════════════════════════════════════════╝
"""

import pandas as pd
import plotly.express as px
import streamlit as st
import hubspot_data as hub

# ── Marca / tema ──────────────────────────────────────────────────
OY_TEAL, OY_TEAL_DARK, OY_WARN, OY_OK = "#16B6C2", "#0E7C86", "#E5484D", "#27AE60"
st.set_page_config(page_title="Tickets en vivo · Opción Yo", page_icon="🎫", layout="wide")
st.markdown(f"""
<style>
.block-container{{padding-top:1.4rem;}}
.oy-h{{background:linear-gradient(100deg,{OY_TEAL_DARK},{OY_TEAL} 60%,#27D0DC);
  color:#fff;padding:18px 26px;border-radius:16px;margin-bottom:14px;
  box-shadow:0 8px 22px rgba(22,182,194,.28);}}
.oy-h h1{{margin:0;font-size:1.5rem;color:#fff;}}
.oy-h p{{margin:3px 0 0;font-size:.85rem;color:#EAFCFE;}}
[data-testid="stMetricValue"]{{font-size:1.7rem;font-weight:800;color:#0A4750;}}
</style>
<div class="oy-h"><h1>🎫 Tickets en vivo · Opción Yo</h1>
<p>Datos directos de HubSpot · se actualizan solos (caché 5 min) · pipelines vigentes</p></div>
""", unsafe_allow_html=True)

# ── Verificación de conexión ──────────────────────────────────────
if not hub.hubspot_activo():
    st.error("No encuentro **HUBSPOT_TOKEN** en Secrets. Añádelo en "
             "Settings → Secrets:\n\n```toml\nHUBSPOT_TOKEN = \"pat-...\"\n```")
    st.stop()

# ── Filtros ───────────────────────────────────────────────────────
c1, c2 = st.columns([1, 3])
with c1:
    dias = st.selectbox("Rango", [7, 15, 30, 60, 90], index=2,
                        format_func=lambda d: f"Últimos {d} días")
if st.button("🔄 Actualizar ahora"):
    hub.tickets_recientes.clear()

df = hub.tickets_recientes(dias=dias)

if df.empty:
    st.warning("HubSpot no devolvió tickets en este rango (o el token no tiene los "
               "permisos de tickets). Revisa los scopes del Private App.")
    st.stop()

# Filtro por pipeline
pipes = sorted(df["pipeline_nombre"].dropna().unique())
sel = st.multiselect("Pipeline", pipes, default=pipes)
dfx = df[df["pipeline_nombre"].isin(sel)] if sel else df

# ── KPIs ──────────────────────────────────────────────────────────
res = hub.resumen_tickets(dfx)
k1, k2, k3, k4 = st.columns(4)
k1.metric("Tickets", f"{res['total']:,}")
k2.metric("Pipelines activos", res["pipelines"])
k3.metric("Respondidos a destiempo", f"{res['a_destiempo']:,}")
k4.metric("% a destiempo", f"{res['pct_destiempo']}%")

st.divider()

# ── Gráficos ──────────────────────────────────────────────────────
g1, g2 = st.columns(2)
with g1:
    st.markdown("##### Tickets por pipeline")
    vp = dfx["pipeline_nombre"].value_counts().reset_index()
    vp.columns = ["Pipeline", "Tickets"]
    fig = px.bar(vp, x="Tickets", y="Pipeline", orientation="h",
                 color_discrete_sequence=[OY_TEAL])
    fig.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0),
                      yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)
with g2:
    st.markdown("##### Top categorías")
    if "hs_ticket_category" in dfx.columns:
        vc = (dfx["hs_ticket_category"].fillna("(sin categoría)")
              .value_counts().head(10).reset_index())
        vc.columns = ["Categoría", "Tickets"]
        fig2 = px.bar(vc, x="Tickets", y="Categoría", orientation="h",
                      color_discrete_sequence=[OY_TEAL_DARK])
        fig2.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0),
                           yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig2, use_container_width=True)

# ── Carga por owner ───────────────────────────────────────────────
st.markdown("##### Carga por responsable (owner)")
if "owner_nombre" in dfx.columns:
    vo = dfx["owner_nombre"].value_counts().head(15).reset_index()
    vo.columns = ["Responsable", "Tickets"]
    st.dataframe(vo, use_container_width=True, hide_index=True)

# ── Detalle ───────────────────────────────────────────────────────
st.markdown("##### Tickets recientes (detalle)")
cols = [c for c in ["createdate", "subject", "pipeline_nombre", "hs_ticket_category",
                    "hs_resolution", "respondido_a_tiempo_o_a_destiempo",
                    "owner_nombre"] if c in dfx.columns]
st.dataframe(dfx[cols].head(200), use_container_width=True, hide_index=True)
st.caption(f"Mostrando hasta 200 de {len(dfx):,} tickets · datos en vivo de HubSpot "
           "(caché 5 min). Pulsa 🔄 para forzar actualización.")
