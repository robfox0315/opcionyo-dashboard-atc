"""
╔══════════════════════════════════════════════════════════════════╗
║  DASHBOARD GERENCIAL ATC · OPCIÓN YO  ·  v2                        ║
║  Fuente principal : treble.csv  (chats atendidos)                 ║
║  Exports opcionales (Treble): Outbound · Fallas · Inversión ·     ║
║                               HSM · Horarios/Conexión             ║
║  Stack  : Streamlit · Pandas 2.x/3.x · Plotly                     ║
║  Ejecutar: python -m streamlit run dashboard_atc_v2.py            ║
╚══════════════════════════════════════════════════════════════════╝
Mejoras v2 (respecto a v1):
  • Identidad visual Opción Yo (teal/blue, tarjetas KPI, logo, pills).
  • TPR por agente con MEDIANA (antes promedio → outlier de días).
  • Churn de plan separado de Reprogramación de sesión.
  • Rating con cobertura honesta de encuesta (response rate).
  • Loader robusto + uploader + validación de esquema.
  • Guardas en .mode()[0] (no rompe con filtros vacíos).
  • Estructura completa del PDF de Atención al Cliente como pestañas.
  • NUEVO: Comparativo de agente por Semana y por Día.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ════════════════════════════════════════════════════════════════════
#  CONFIGURACIÓN DE PÁGINA
# ════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="ATC · Opción Yo – Gerencia",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Paleta corporativa Opción Yo (tomada del tablero oficial) ────────
OY_TEAL      = "#16B6C2"   # primario de marca
OY_TEAL_DARK = "#0E8E99"   # títulos / bordes
OY_BLUE      = "#2F80ED"   # secundario (outbound)
OY_OK        = "#27AE60"
OY_WARN      = "#E5484D"
OY_AMBER     = "#F2A33C"
OY_INK       = "#16323A"   # texto
COLOR_SEQ    = [OY_TEAL, OY_BLUE, OY_AMBER, "#7E57C2", "#EC4899",
                "#26A69A", "#FF7043", "#42A5F5", "#9CCC65", "#5C6BC0"]
TEAL_SCALE   = [[0, "#E3F6F8"], [0.5, OY_TEAL], [1, OY_TEAL_DARK]]

# ── CSS de marca ─────────────────────────────────────────────────────
st.markdown("""
<style>
:root{
  --oy-teal:#16B6C2; --oy-teal-d:#0E8E99; --oy-blue:#2F80ED;
  --oy-ok:#27AE60; --oy-warn:#E5484D; --oy-amber:#F2A33C; --oy-ink:#16323A;
}
.stApp { background:#FFFFFF; }
.block-container { padding-top:1.0rem; }
h1,h2,h3 { color:var(--oy-teal-d); }
[data-testid="stMetricValue"]{ font-size:1.75rem!important; font-weight:800; color:var(--oy-ink);}
[data-testid="stMetricLabel"]{ font-size:0.80rem!important; color:#5a6b72; font-weight:600;}
[data-testid="stMetricDelta"]{ font-size:0.80rem!important; }

/* Header de marca */
.oy-header{
  display:flex; align-items:center; gap:14px;
  background:linear-gradient(90deg,var(--oy-teal) 0%, #1AC3CF 100%);
  padding:14px 20px; border-radius:14px; margin-bottom:6px;
  box-shadow:0 6px 18px rgba(22,182,194,.25);
}
.oy-logo{ font-weight:800; font-size:1.55rem; letter-spacing:.3px;
  color:#fff; line-height:1; }
.oy-logo .yo{ color:#0A4750; }
.oy-htitle{ color:#fff; font-weight:800; font-size:1.15rem; margin:0;}
.oy-hsub{ color:#E8FBFD; font-size:.82rem; margin:0;}

/* Section pill */
.sec-title{
  background:var(--oy-teal); color:#fff;
  padding:.45rem 1rem; border-radius:8px;
  font-weight:700; margin:.2rem 0 .8rem 0; font-size:1rem;
  display:inline-block;
}
/* Tarjetas KPI estilo Opción Yo */
.kpi-grid{ display:flex; gap:12px; flex-wrap:wrap; margin-bottom:6px;}
.kpi{
  flex:1; min-width:135px;
  background:var(--oy-teal); border-radius:12px; padding:12px 14px; color:#fff;
  box-shadow:0 4px 12px rgba(22,182,194,.20);
}
.kpi.alt{ background:var(--oy-blue); box-shadow:0 4px 12px rgba(47,128,237,.20);}
.kpi.ok{ background:var(--oy-ok);}
.kpi.warn{ background:var(--oy-warn);}
.kpi.amber{ background:var(--oy-amber);}
.kpi .l{ font-size:.74rem; opacity:.92; font-weight:600; text-transform:uppercase; letter-spacing:.4px;}
.kpi .v{ font-size:1.6rem; font-weight:800; margin-top:2px;}
.kpi .d{ font-size:.72rem; opacity:.95; margin-top:2px;}

.critical-box{ background:#FDECEA; border-left:5px solid var(--oy-warn);
  padding:.6rem 1rem; border-radius:6px; margin-bottom:.7rem; color:#7a1f1c;}
.alert-box{ background:#FFF6E6; border-left:5px solid var(--oy-amber);
  padding:.6rem 1rem; border-radius:6px; margin-bottom:.7rem; color:#7a531a;}
.ok-box{ background:#EAF7EF; border-left:5px solid var(--oy-ok);
  padding:.6rem 1rem; border-radius:6px; margin-bottom:.7rem; color:#1d6b3a;}
.info-box{ background:#E9F6F8; border-left:5px solid var(--oy-teal);
  padding:.7rem 1rem; border-radius:6px; margin-bottom:.7rem; color:#0E6873;}

/* Tabs */
.stTabs [data-baseweb="tab-list"]{ gap:4px; flex-wrap:wrap;}
.stTabs [data-baseweb="tab"]{
  background:#F1FAFB; border-radius:8px 8px 0 0; padding:6px 12px;
  font-weight:600; color:var(--oy-teal-d);
}
.stTabs [aria-selected="true"]{ background:var(--oy-teal)!important; color:#fff!important;}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
#  CONTROL DE ACCESO OPCIONAL
#  Se activa SOLO si defines el secret "app_password" en Streamlit Cloud
#  (Settings → Secrets). Sin secret, la app queda abierta (uso local).
# ════════════════════════════════════════════════════════════════════
def _get_secret(key):
    try:
        return st.secrets.get(key)
    except Exception:
        return None


def require_auth():
    pw = _get_secret("app_password")
    if not pw:                       # sin contraseña configurada → abierto
        return
    if st.session_state.get("auth_ok"):
        return
    st.markdown(
        '<div class="oy-header"><div class="oy-logo">opción<span class="yo"> yo</span></div>'
        '<div><p class="oy-htitle">Dashboard ATC · Acceso restringido</p>'
        '<p class="oy-hsub">Introduce la contraseña para continuar</p></div></div>',
        unsafe_allow_html=True)
    with st.form("login_oy"):
        intro = st.text_input("Contraseña", type="password")
        ok = st.form_submit_button("Entrar")
    if ok:
        if intro == pw:
            st.session_state["auth_ok"] = True
            st.rerun()
        st.error("Contraseña incorrecta.")
    st.stop()


require_auth()


# ════════════════════════════════════════════════════════════════════
#  FUNCIONES AUXILIARES
# ════════════════════════════════════════════════════════════════════
def hms_to_min(serie: pd.Series) -> pd.Series:
    """H:MM:SS → minutos decimales. Errores → NaN."""
    def _p(v):
        try:
            p = str(v).strip().split(":")
            return int(p[0]) * 60 + int(p[1]) + float(p[2]) / 60
        except Exception:
            return np.nan
    return serie.apply(_p)


def fmt_min(m) -> str:
    """Minutos decimales → HH:MM:SS."""
    if m is None or (isinstance(m, float) and np.isnan(m)) or m < 0:
        return "–"
    m = float(m)
    return f"{int(m//60):02d}:{int(m%60):02d}:{int((m*60)%60):02d}"


def safe_pct(num, den) -> float:
    return round(float(num) / float(den) * 100, 1) if den else 0.0


def safe_mode(serie, default="–"):
    """mode()[0] a prueba de series vacías."""
    s = serie.dropna()
    return s.mode().iloc[0] if len(s) and len(s.mode()) else default


def semaforo(val, meta, higher_is_better=True) -> str:
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "Sin datos"
    ok = (val >= meta) if higher_is_better else (val <= meta)
    signo = "≥" if higher_is_better else "≤"
    return f"{'✅' if ok else '🔴'} Meta {signo} {meta}"


def motivo_principal(labels_series: pd.Series) -> str:
    flat = labels_series.dropna().str.split(r",\s*").explode().str.strip()
    return flat.mode().iloc[0] if len(flat) and len(flat.mode()) else "–"


def kpi_card(label, value, delta="", kind=""):
    d = f'<div class="d">{delta}</div>' if delta else ""
    return f'<div class="kpi {kind}"><div class="l">{label}</div><div class="v">{value}</div>{d}</div>'


def style_fig(fig, h=320):
    fig.update_layout(
        height=h, margin=dict(t=46, b=10, l=10, r=10),
        font=dict(color=OY_INK, family="Segoe UI, sans-serif"),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        title_font=dict(color=OY_TEAL_DARK, size=15),
    )
    return fig


# ════════════════════════════════════════════════════════════════════
#  METAS GERENCIALES (editar aquí — config central)
# ════════════════════════════════════════════════════════════════════
META_RATING    = 4.85
META_TPR_MED   = 1.0     # min  (00:01:00)
META_SLA2      = 80.0    # %
META_SLA5      = 93.0    # %
META_PCT_CAL   = 50.0    # %  cobertura encuesta
META_CHURN     = 8.0     # %  cancelaciones de PLAN
META_CANCEL    = 15.0    # %  cancelaciones totales
META_RESOL_MED = 90.0    # min (01:30:00)

DIAS_ES = {"Monday":"Lunes","Tuesday":"Martes","Wednesday":"Miércoles",
           "Thursday":"Jueves","Friday":"Viernes","Saturday":"Sábado","Sunday":"Domingo"}
DIAS_ORDER_EN = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

REGION_PREF = {  # prefijo telefónico → región (para segmentación)
    "1":"EE.UU./Canadá","52":"México","57":"Colombia","58":"Venezuela",
    "54":"Argentina","56":"Chile","51":"Perú","593":"Ecuador","591":"Bolivia",
    "507":"Panamá","34":"España","44":"Reino Unido","49":"Alemania","55":"Brasil",
}

REQ_COLS = {"phone","agent","created_at","finished_at","duration","rating","labels",
            "status","agent_first_message_from_allocation"}


# ════════════════════════════════════════════════════════════════════
#  CARGA Y LIMPIEZA  (loader robusto)
# ════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner="⏳ Procesando treble.csv…")
def load_data(file) -> pd.DataFrame:
    try:
        df = pd.read_csv(file, dtype=str)
    except Exception as e:
        st.error(f"No se pudo leer el archivo: {e}")
        st.stop()

    faltan = REQ_COLS - set(df.columns)
    if faltan:
        st.error(f"El CSV no tiene las columnas requeridas: {sorted(faltan)}")
        st.stop()

    df = df.drop(columns=[c for c in ["username"] if c in df.columns])  # columna muerta

    # 1. Fechas
    for c in ["created_at", "assigned_at", "finished_at"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")

    # 2. Tiempos operacionales
    df["tpr_min"] = hms_to_min(df["agent_first_message_from_allocation"])  # 1ra respuesta (agente)
    df["dur_min"] = hms_to_min(df["duration"])                            # interacción

    # 3. Resolución (finished - created)
    df["resol_min"] = ((df["finished_at"] - df["created_at"]).dt.total_seconds() / 60).clip(lower=0)

    # 4. Rating numérico + cobertura
    df["rating_num"] = pd.to_numeric(df["rating"].replace("-", np.nan), errors="coerce")
    df["calificado"] = df["rating_num"].notna()

    # 5. Tiempo
    df["fecha"]      = df["created_at"].dt.date
    df["hora"]       = df["created_at"].dt.hour
    df["dia_nombre"] = df["created_at"].dt.day_name()
    df["semana"]     = df["created_at"].dt.to_period("W").apply(
        lambda p: p.start_time.date() if pd.notna(p) else None)
    df["mes"]        = df["created_at"].dt.to_period("M").apply(
        lambda p: p.start_time.date() if pd.notna(p) else None)

    # 6. SLA flags + outliers
    df["sla_2min"]  = df["tpr_min"] <= 2
    df["sla_5min"]  = df["tpr_min"] <= 5
    df["sla_15min"] = df["tpr_min"] <= 15
    df["sla_30min"] = df["tpr_min"] <= 30
    df["sla_over30"]= df["tpr_min"] > 30
    df["dur_outlier"] = df["dur_min"] > 300  # >5h

    # 7. Cancelaciones — SEPARADAS (bug v1 corregido)
    lbl = df["labels"].fillna("")
    df["es_churn_plan"]     = lbl.str.contains(r"Cancelar plan|Cancelaci[oó]n de plan", case=False, regex=True)
    df["es_reprogramacion"] = lbl.str.contains(r"Cancelaci[oó]n \+24|Cancelaci[oó]n tard|Postergaci|Esp\. cancela", case=False, regex=True)
    df["es_cancelacion"]    = df["es_churn_plan"] | df["es_reprogramacion"]

    # 8. Etiqueta principal + región
    df["label_principal"] = lbl.replace("", "Sin etiqueta").str.split(r",\s*").str[0].str.strip()
    cc = df["phone"].str.extract(r"^\+(\d{1,3})")[0]
    df["region"] = cc.map(REGION_PREF).fillna("Otros")

    return df


@st.cache_data(show_spinner="⏳ Cargando export…")
def load_simple(file) -> pd.DataFrame:
    return pd.read_csv(file, dtype=str)


def build_agent_kpis(data: pd.DataFrame, usar_mediana=True) -> pd.DataFrame:
    """KPIs por agente. usar_mediana=True → robusto a outliers (corrige bug v1)."""
    agg = np.median if usar_mediana else np.mean
    rows = []
    for agent, g in data.groupby("agent"):
        n   = len(g)
        cal = g["rating_num"].dropna(); nc = len(cal)
        tpr = g["tpr_min"].dropna();    nt = len(tpr)
        res = g.loc[g["resol_min"] > 0, "resol_min"].dropna()
        dur = g.loc[~g["dur_outlier"], "dur_min"].dropna()
        rows.append({
            "Agente":           agent,
            "Chats Atendidos":  n,
            "Calificación":     round(float(cal.mean()), 2) if nc else np.nan,
            "% Calificados":    safe_pct(nc, n),
            "Primera respuesta": fmt_min(agg(tpr)) if nt else "–",
            "T. interacción":   fmt_min(agg(dur)) if len(dur) else "–",
            "T. resolución":    fmt_min(agg(res)) if len(res) else "–",
            "TPR val (min)":    round(float(agg(tpr)), 2) if nt else np.nan,
            "% SLA ≤2min":      safe_pct((tpr <= 2).sum(), nt),
            "% SLA ≤5min":      safe_pct((tpr <= 5).sum(), nt),
            "% SLA >30min":     safe_pct((tpr > 30).sum(), nt),
            "% Churn plan":     safe_pct(g["es_churn_plan"].sum(), n),
            "% Reprogram.":     safe_pct(g["es_reprogramacion"].sum(), n),
        })
    return pd.DataFrame(rows).sort_values("Chats Atendidos", ascending=False)


# ════════════════════════════════════════════════════════════════════
#  HEADER DE MARCA
# ════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="oy-header">
  <div class="oy-logo">opción<span class="yo"> yo</span></div>
  <div>
    <p class="oy-htitle">Dashboard de Gestión · Atención al Cliente</p>
    <p class="oy-hsub">Vista Gerencial · powered by Treble · datos de chats atendidos</p>
  </div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
#  SIDEBAR — DATOS + FILTROS
# ════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🟢 Opción Yo · ATC")
    up = st.file_uploader("Fuente principal (treble.csv)", type=["csv"], key="main")
    source = up if up is not None else "treble.csv"
    try:
        df_raw = load_data(source)
    except Exception:
        st.warning("Sube **treble.csv** para comenzar.")
        st.stop()

    st.divider()
    st.markdown("#### 🔍 Filtros")
    fmin = df_raw["created_at"].min().date()
    fmax = df_raw["created_at"].max().date()
    rango = st.date_input("📅 Fechas", value=(fmin, fmax), min_value=fmin, max_value=fmax)
    f_ini = rango[0] if len(rango) == 2 else fmin
    f_fin = rango[1] if len(rango) == 2 else fmax

    agentes_sel = st.multiselect("👤 Agentes", sorted(df_raw["agent"].dropna().unique()),
                                 placeholder="Todos")
    tags_sel    = st.multiselect("📂 Grupo / Cola", sorted(df_raw["tag"].dropna().unique()),
                                 placeholder="Todos")
    region_sel  = st.multiselect("🌎 Región", sorted(df_raw["region"].dropna().unique()),
                                 placeholder="Todas")
    all_labels  = sorted({l.strip() for lst in df_raw["labels"].dropna() for l in lst.split(",")})
    labels_sel  = st.multiselect("🏷️ Etiquetas", all_labels, placeholder="Todas")
    estados_sel = st.multiselect("🔖 Estado", sorted(df_raw["status"].dropna().unique()),
                                 placeholder="Todos")

    st.divider()
    granularidad = st.radio("Evolución por", ["Día", "Semana", "Mes"], index=1, horizontal=True)
    gran_col = {"Día":"fecha", "Semana":"semana", "Mes":"mes"}[granularidad]
    usar_mediana = st.toggle("Usar mediana (robusto a outliers)", value=True,
                             help="Recomendado. Desactívalo para reproducir los promedios del PDF de Treble.")
    st.divider()
    st.markdown("#### 📎 Exports opcionales de Treble")
    up_out  = st.file_uploader("Outbound / Consumo", type=["csv"], key="out")
    up_fail = st.file_uploader("Fallas de envío", type=["csv"], key="fail")
    up_hsm  = st.file_uploader("HSM", type=["csv"], key="hsm")
    up_conx = st.file_uploader("Horarios / Conexión", type=["csv"], key="conx")
    st.caption("Opción Yo · ATC · v2")


# ════════════════════════════════════════════════════════════════════
#  APLICAR FILTROS
# ════════════════════════════════════════════════════════════════════
df = df_raw.copy()
df = df[(df["created_at"].dt.date >= f_ini) & (df["created_at"].dt.date <= f_fin)]
if agentes_sel: df = df[df["agent"].isin(agentes_sel)]
if tags_sel:    df = df[df["tag"].isin(tags_sel)]
if region_sel:  df = df[df["region"].isin(region_sel)]
if estados_sel: df = df[df["status"].isin(estados_sel)]
if labels_sel:
    df = df[df["labels"].fillna("").str.contains("|".join(map(lambda s: s.replace("+","\\+"), labels_sel)), case=False)]

if df.empty:
    st.warning("No hay datos para los filtros seleccionados.")
    st.stop()

# ── KPIs globales ────────────────────────────────────────────────────
total      = len(df)
n_cal      = int(df["calificado"].sum())
pct_cal    = safe_pct(n_cal, total)
rating_prom= df["rating_num"].mean()
tpr_v      = df["tpr_min"].dropna()
tpr_med    = tpr_v.median() if len(tpr_v) else np.nan
res_v      = df.loc[df["resol_min"] > 0, "resol_min"].dropna()
res_med    = res_v.median() if len(res_v) else np.nan
dur_fil    = df.loc[~df["dur_outlier"], "dur_min"].dropna()
dur_med    = dur_fil.median() if len(dur_fil) else np.nan
pct_sla2   = safe_pct(df["sla_2min"].sum(), len(tpr_v)) if len(tpr_v) else 0
pct_sla5   = safe_pct(df["sla_5min"].sum(), len(tpr_v)) if len(tpr_v) else 0
pct_over30 = safe_pct(df["sla_over30"].sum(), len(tpr_v)) if len(tpr_v) else 0
pct_churn  = safe_pct(df["es_churn_plan"].sum(), total)
pct_reprog = safe_pct(df["es_reprogramacion"].sum(), total)
pct_cancel = safe_pct(df["es_cancelacion"].sum(), total)
pct_outlier= safe_pct(df["dur_outlier"].sum(), total)
csat       = safe_pct((df["rating_num"] >= 4).sum(), n_cal) if n_cal else 0
detractor  = safe_pct((df["rating_num"] <= 3).sum(), n_cal) if n_cal else 0
hora_pico  = int(safe_mode(df["hora"], 0))
dia_pico   = DIAS_ES.get(safe_mode(df["dia_nombre"]), "–")

# ── Clientes recurrentes (quién más contacta) ───────────────────────
_contactos     = df.groupby("phone").size()
n_clientes     = int(_contactos.size)
n_recurrentes  = int((_contactos >= 2).sum())
chats_recur    = int(_contactos[_contactos >= 2].sum())
pct_vol_recur  = safe_pct(chats_recur, total)
max_contactos  = int(_contactos.max()) if len(_contactos) else 0


def build_top_clientes(data: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    """Top clientes por frecuencia de contacto, con su motivo principal."""
    rows = []
    for phone, g in data.groupby("phone"):
        rows.append({
            "Teléfono":           phone,
            "Cliente":            safe_mode(g["contact"]),
            "Contactos":          len(g),
            "Motivo principal":   motivo_principal(g["labels"]),
            "Región":             safe_mode(g["region"]),
            "Agente frecuente":   safe_mode(g["agent"]),
            "Calif. prom":        round(float(g["rating_num"].mean()), 2)
                                  if g["rating_num"].notna().any() else np.nan,
            "¿Churn plan?":       "Sí" if g["es_churn_plan"].any() else "No",
            "Última interacción": str(g["created_at"].max().date())
                                  if g["created_at"].notna().any() else "–",
        })
    return (pd.DataFrame(rows).sort_values("Contactos", ascending=False).head(n))


# ════════════════════════════════════════════════════════════════════
#  TABS — estructura espejo del PDF + mejoras
# ════════════════════════════════════════════════════════════════════
(tab_exec, tab_ag, tab_sd, tab_tpr, tab_lab, tab_canc, tab_evo, tab_det,
 tab_out, tab_fail, tab_inv, tab_hsm, tab_conx) = st.tabs([
    "🏠 Resumen Ejecutivo", "📊 Rendimiento Agentes", "📅 Semana / Día",
    "⚡ Primera Respuesta", "🏷️ Etiquetas", "🚨 Cancelaciones & Retención",
    "📈 Evolución", "📋 Métricas Chats",
    "📤 Outbound", "❌ Fallas Envío", "💰 Inversión", "📨 HSM", "🟢 Conexión",
])


# ╔══════════════════════════════════════════════════════════════════╗
#  1 · RESUMEN EJECUTIVO
# ╚══════════════════════════════════════════════════════════════════╝
with tab_exec:
    st.caption(f"**Período:** {f_ini} → {f_fin}  ·  **{total:,}** chats  ·  "
               f"**{df['agent'].nunique()}** agentes  ·  Pico: {dia_pico} {hora_pico:02d}:00h")

    # Alertas automáticas
    if pct_churn > META_CHURN:
        st.markdown(f'<div class="critical-box">🚨 <b>CHURN DE PLAN: {pct_churn}%</b> '
                    f'({int(df["es_churn_plan"].sum()):,} chats de "Cancelar plan", umbral {META_CHURN}%). '
                    f'Es cancelación de suscripción = pérdida de ingresos. Máxima prioridad de retención.</div>',
                    unsafe_allow_html=True)
    if pct_cal < META_PCT_CAL:
        st.markdown(f'<div class="alert-box">⚠️ <b>Cobertura de encuesta {pct_cal}%</b> — el rating se calcula '
                    f'solo sobre {n_cal:,}/{total:,} chats. El insatisfecho suele NO calificar: no leer 4,8 como satisfacción global.</div>',
                    unsafe_allow_html=True)
    if pct_sla2 >= META_SLA2:
        st.markdown(f'<div class="ok-box">✅ <b>Operación de respuesta de primer nivel:</b> '
                    f'{pct_sla2}% responde en ≤2 min (mediana {fmt_min(tpr_med)}).</div>', unsafe_allow_html=True)

    # Banner KPI Opción Yo
    st.markdown('<div class="sec-title">📌 Indicadores Clave</div>', unsafe_allow_html=True)
    st.markdown('<div class="kpi-grid">' +
        kpi_card("Chats atendidos", f"{total:,}", kind="alt") +
        kpi_card("CSAT (muestra)", f"{rating_prom:.2f}", f"cobertura {pct_cal}%",
                 kind="ok" if rating_prom >= META_RATING else "amber") +
        kpi_card("1ra respuesta (mediana)", fmt_min(tpr_med),
                 semaforo(tpr_med, META_TPR_MED, False), kind="ok" if tpr_med <= META_TPR_MED else "warn") +
        kpi_card("% SLA ≤2 min", f"{pct_sla2}%", kind="ok" if pct_sla2 >= META_SLA2 else "warn") +
        kpi_card("Churn de plan", f"{pct_churn}%", f"meta ≤{META_CHURN}%",
                 kind="warn" if pct_churn > META_CHURN else "ok") +
        kpi_card("Vol. recurrente", f"{pct_vol_recur}%", f"{n_recurrentes:,} clientes ≥2", kind="amber") +
        kpi_card("Reprogramaciones", f"{pct_reprog}%", kind="amber") +
        '</div>', unsafe_allow_html=True)

    st.markdown("")
    g1, g2, g3 = st.columns(3)

    def gauge(title, val, ref, rng, steps, suffix="", invert=False):
        v = round(float(val), 2) if not pd.isna(val) else 0
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta", value=v,
            number={"suffix": suffix, "font": {"size": 28, "color": OY_INK}},
            delta={"reference": ref,
                   "increasing": {"color": OY_WARN if invert else OY_OK},
                   "decreasing": {"color": OY_OK if invert else OY_WARN}},
            title={"text": title, "font": {"size": 14, "color": OY_TEAL_DARK}},
            gauge={"axis": {"range": rng}, "bar": {"color": OY_TEAL},
                   "steps": steps,
                   "threshold": {"line": {"color": OY_OK, "width": 3}, "thickness": .85, "value": ref}}))
        return style_fig(fig, 250)

    with g1:
        st.plotly_chart(gauge("⭐ Calificación", rating_prom, META_RATING, [1,5],
            [{"range":[1,4],"color":"#FADBD8"},{"range":[4,META_RATING],"color":"#FDEBD0"},
             {"range":[META_RATING,5],"color":"#D5F5E3"}]), use_container_width=True)
    with g2:
        tprc = min(float(tpr_med) if not pd.isna(tpr_med) else 0, 30)
        st.plotly_chart(gauge("⚡ 1ra respuesta (min)", tprc, META_TPR_MED, [0,30],
            [{"range":[0,META_TPR_MED],"color":"#D5F5E3"},{"range":[META_TPR_MED,10],"color":"#FDEBD0"},
             {"range":[10,30],"color":"#FADBD8"}], " min", True), use_container_width=True)
    with g3:
        st.plotly_chart(gauge("💸 Churn de plan", pct_churn, META_CHURN, [0,30],
            [{"range":[0,META_CHURN],"color":"#D5F5E3"},{"range":[META_CHURN,18],"color":"#FDEBD0"},
             {"range":[18,30],"color":"#FADBD8"}], "%", True), use_container_width=True)

    # Narrativa automática
    st.markdown('<div class="sec-title">📝 Lectura automática</div>', unsafe_allow_html=True)
    top_motivo = motivo_principal(df["labels"])
    peor_reg = (df.groupby("region")["es_churn_plan"].mean()*100).sort_values(ascending=False)
    reg_txt = f"{peor_reg.index[0]} ({peor_reg.iloc[0]:.0f}%)" if len(peor_reg) else "–"
    st.markdown(f"""<div class="info-box">
    • <b>Retención es el frente crítico:</b> {pct_cancel}% de los chats son cancelaciones
      ({pct_churn}% churn de plan + {pct_reprog}% reprogramaciones). Motivo #1 de contacto: <b>{top_motivo}</b>.<br>
    • <b>Atención sobresaliente:</b> mediana de 1ra respuesta {fmt_min(tpr_med)} y {pct_sla2}% en ≤2 min — activo a destacar.<br>
    • <b>Región con mayor churn de plan:</b> {reg_txt}. CSAT de muestra {csat}% · detractores {detractor}%.
    </div>""", unsafe_allow_html=True)

    # ── Clientes que más contactan + motivo ─────────────────────────
    st.markdown('<div class="sec-title">📞 Clientes que más contactan</div>', unsafe_allow_html=True)
    st.markdown('<div class="kpi-grid">' +
        kpi_card("% del volumen recurrente", f"{pct_vol_recur}%",
                 f"{chats_recur:,} de {total:,} chats", kind="alt") +
        kpi_card("Clientes recurrentes (≥2)", f"{n_recurrentes:,}",
                 f"de {n_clientes:,} únicos", kind="amber") +
        kpi_card("Máx. contactos de 1 cliente", f"{max_contactos}", kind="warn") +
        '</div>', unsafe_allow_html=True)
    st.markdown('<div class="alert-box">💡 Alta recurrencia suele indicar un problema sin resolver. '
                'Un cliente con muchos contactos y motivo de cancelación = riesgo de churn — priorizar contacto proactivo.</div>',
                unsafe_allow_html=True)

    topc = build_top_clientes(df, 15)
    cc1, cc2 = st.columns([1.5, 1])
    with cc1:
        st.markdown("**Top 15 clientes por frecuencia de contacto**")
        sty = (topc.style
               .map(lambda v: f"color:{OY_WARN};font-weight:700" if v == "Sí" else "", subset=["¿Churn plan?"])
               .format({"Calif. prom":"{:.2f}"}))
        st.dataframe(sty, use_container_width=True, hide_index=True, height=430)
        st.download_button("⬇️ Descargar clientes recurrentes (.csv)",
                           topc.to_csv(index=False).encode("utf-8"),
                           "clientes_recurrentes.csv", "text/csv")
    with cc2:
        st.markdown("**Motivo por el que llaman** (clientes recurrentes)")
        rec_phones = set(_contactos[_contactos >= 2].index)
        rexp = (df[df["phone"].isin(rec_phones)]["labels"].fillna("Sin etiqueta")
                .str.split(r",\s*").explode().str.strip())
        rmot = rexp.value_counts().head(8).reset_index()
        rmot.columns = ["Motivo", "Chats"]
        fig = px.bar(rmot, x="Chats", y="Motivo", orientation="h", color="Chats",
                     color_continuous_scale="Teal", text="Chats")
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False, yaxis={"categoryorder":"total ascending"})
        st.plotly_chart(style_fig(fig, 430), use_container_width=True)


# ╔══════════════════════════════════════════════════════════════════╗
#  2 · RENDIMIENTO AGENTES  (espejo PDF p5/14 + fix mediana)
# ╚══════════════════════════════════════════════════════════════════╝
with tab_ag:
    st.markdown('<div class="sec-title">📊 Rendimiento de Agentes</div>', unsafe_allow_html=True)
    st.caption(("Mediana" if usar_mediana else "Promedio") +
               " (cambia en el panel lateral). La mediana evita que un chat reabierto de horas distorsione al agente.")

    ag = build_agent_kpis(df, usar_mediana)
    eq_cal = df["rating_num"].mean()
    eq_tpr = fmt_min((np.median if usar_mediana else np.mean)(tpr_v)) if len(tpr_v) else "–"

    st.markdown('<div class="kpi-grid">' +
        kpi_card("Chats atendidos", f"{total:,}", kind="alt") +
        kpi_card("Calificación equipo", f"{eq_cal:.2f}", kind="ok") +
        kpi_card("1ra respuesta", eq_tpr, kind="") +
        kpi_card("% Calificados", f"{pct_cal}%", kind="amber") +
        '</div>', unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])
    with c1:
        cols = ["Agente","Chats Atendidos","Calificación","% Calificados",
                "Primera respuesta","T. interacción","T. resolución","% SLA ≤2min","% Churn plan"]
        def _cal_color(v):
            if not isinstance(v, (int, float)) or pd.isna(v):
                return ""
            return f"color:{OY_OK};font-weight:700" if v >= META_RATING else f"color:{OY_WARN};font-weight:700"
        def _churn_color(v):
            if not isinstance(v, (int, float)) or pd.isna(v):
                return ""
            return f"color:{OY_WARN};font-weight:700" if v > META_CHURN else f"color:{OY_INK}"
        sty = (ag[cols].style
               .map(_cal_color, subset=["Calificación"])
               .map(_churn_color, subset=["% Churn plan"])
               .format({"Calificación":"{:.2f}","% Calificados":"{:.1f}",
                        "% SLA ≤2min":"{:.1f}","% Churn plan":"{:.1f}"}))
        st.dataframe(sty, use_container_width=True, hide_index=True, height=460)
        st.download_button("⬇️ Descargar ranking de agentes (.csv)",
                           ag.to_csv(index=False).encode("utf-8"), "agentes.csv", "text/csv")
    with c2:
        top = ag.nlargest(12, "Chats Atendidos")
        fig = px.bar(top, x="Chats Atendidos", y="Agente", orientation="h",
                     color="Calificación", color_continuous_scale="RdYlGn", range_color=[3.5,5],
                     title="Top agentes por volumen")
        fig.update_layout(yaxis={"categoryorder":"total ascending"})
        st.plotly_chart(style_fig(fig, 460), use_container_width=True)


# ╔══════════════════════════════════════════════════════════════════╗
#  3 · COMPARATIVO SEMANA / DÍA  (NUEVO — solicitado)
# ╚══════════════════════════════════════════════════════════════════╝
with tab_sd:
    st.markdown('<div class="sec-title">📅 Comparativo de Agentes por Semana y Día</div>', unsafe_allow_html=True)

    top_ags = df["agent"].value_counts().head(15).index.tolist()
    dsd = df[df["agent"].isin(top_ags)].copy()
    dsd["dia_es"] = pd.Categorical(dsd["dia_nombre"].map(DIAS_ES),
                                   categories=[DIAS_ES[d] for d in DIAS_ORDER_EN], ordered=True)

    metrica = st.radio("Métrica a comparar", ["Chats", "Calificación", "1ra respuesta (min)"],
                       horizontal=True)

    def build_pivot(group_col):
        rows = []
        for (ag_, key), g in dsd.groupby(["agent", group_col], observed=True):
            if metrica == "Chats":
                val = len(g)
            elif metrica == "Calificación":
                val = g["rating_num"].mean()
            else:
                t = g["tpr_min"].dropna(); val = t.median() if len(t) else np.nan
            rows.append({"Agente": ag_, "k": str(key), "val": val})
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame(rows).pivot(index="Agente", columns="k", values="val")

    cscale = "Teal" if metrica == "Chats" else ("RdYlGn" if metrica == "Calificación" else "RdYlGn_r")

    st.subheader(f"🗓️ {metrica} · Agente × Semana")
    pw = build_pivot("semana")
    if not pw.empty:
        fig = px.imshow(pw, aspect="auto", color_continuous_scale=cscale,
                        labels=dict(x="Semana (inicio)", y="", color=metrica), text_auto=True)
        st.plotly_chart(style_fig(fig, 60 + 26*len(pw)), use_container_width=True)

    st.subheader(f"📆 {metrica} · Agente × Día de semana")
    pd_ = build_pivot("dia_es")
    if not pd_.empty:
        orden = [d for d in [DIAS_ES[x] for x in DIAS_ORDER_EN] if d in pd_.columns]
        pd_ = pd_[orden]
        fig = px.imshow(pd_, aspect="auto", color_continuous_scale=cscale,
                        labels=dict(x="", y="", color=metrica), text_auto=True)
        st.plotly_chart(style_fig(fig, 60 + 26*len(pd_)), use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📈 Volumen por agente y semana")
        evo = (dsd.groupby(["agent","semana"], observed=True).size().reset_index(name="Chats"))
        evo["semana"] = pd.to_datetime(evo["semana"])
        fig = px.line(evo, x="semana", y="Chats", color="agent", markers=True,
                      color_discrete_sequence=COLOR_SEQ, labels={"semana":"","agent":"Agente"})
        st.plotly_chart(style_fig(fig, 360), use_container_width=True)
    with c2:
        st.subheader("🌡️ Carga global · Día × Hora")
        heat = df.groupby(["dia_nombre","hora"]).size().reset_index(name="chats")
        heat["dia_es"] = pd.Categorical(heat["dia_nombre"].map(DIAS_ES),
                                        categories=[DIAS_ES[d] for d in DIAS_ORDER_EN], ordered=True)
        piv = heat.pivot_table(index="dia_es", columns="hora", values="chats", aggfunc="sum", observed=True).fillna(0)
        fig = px.imshow(piv, aspect="auto", color_continuous_scale="Teal",
                        labels=dict(x="Hora", y="", color="Chats"))
        st.plotly_chart(style_fig(fig, 360), use_container_width=True)

    st.subheader("🏆 Ranking semanal (chats atendidos)")
    rk = (dsd.groupby(["semana","agent"], observed=True).size().reset_index(name="Chats")
          .sort_values(["semana","Chats"], ascending=[True, False]))
    rk["semana"] = rk["semana"].astype(str)
    st.dataframe(rk.pivot(index="agent", columns="semana", values="Chats").fillna(0).astype(int),
                 use_container_width=True)


# ╔══════════════════════════════════════════════════════════════════╗
#  4 · PRIMERA RESPUESTA – RANGOS  (espejo PDF p16)
# ╚══════════════════════════════════════════════════════════════════╝
with tab_tpr:
    st.markdown('<div class="sec-title">⚡ Primera Respuesta — Rangos</div>', unsafe_allow_html=True)
    t = tpr_v
    buckets = {
        "Within 2 minutes":   int((t <= 2).sum()),
        "Within 5 minutes":   int(((t > 2) & (t <= 5)).sum()),
        "Within 15 minutes":  int(((t > 5) & (t <= 15)).sum()),
        "Within 30 minutes":  int(((t > 15) & (t <= 30)).sum()),
        "Over 30 minutes":    int((t > 30).sum()),
    }
    bdf = pd.DataFrame({"Rango": buckets.keys(), "Chats": buckets.values()})
    bdf["%"] = (bdf["Chats"]/len(t)*100).round(2) if len(t) else 0

    c1, c2 = st.columns([1, 1.4])
    with c1:
        st.markdown('<div class="kpi-grid">' +
            kpi_card("Mediana", fmt_min(tpr_med), kind="alt") +
            kpi_card("≤2 min", f"{pct_sla2}%", kind="ok") +
            kpi_card(">30 min", f"{pct_over30}%", kind="warn" if pct_over30 > 5 else "amber") +
            '</div>', unsafe_allow_html=True)
        st.dataframe(bdf, use_container_width=True, hide_index=True)
    with c2:
        fig = px.bar(bdf, x="Chats", y="Rango", orientation="h", text="%",
                     color="Rango",
                     color_discrete_map={"Within 2 minutes":OY_OK,"Within 5 minutes":"#7BC96F",
                                         "Within 15 minutes":OY_AMBER,"Within 30 minutes":"#E8842E",
                                         "Over 30 minutes":OY_WARN})
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.update_layout(showlegend=False, yaxis={"categoryorder":"array",
            "categoryarray":list(buckets.keys())[::-1]})
        st.plotly_chart(style_fig(fig, 320), use_container_width=True)

    st.subheader("Primera respuesta por agente")
    ag = build_agent_kpis(df, usar_mediana)
    fig = px.bar(ag.sort_values("TPR val (min)").head(20), x="TPR val (min)", y="Agente",
                 orientation="h", color="TPR val (min)", color_continuous_scale="RdYlGn_r",
                 labels={"TPR val (min)":"min ("+("mediana" if usar_mediana else "prom")+")"})
    fig.update_layout(yaxis={"categoryorder":"total descending"})
    st.plotly_chart(style_fig(fig, 460), use_container_width=True)


# ╔══════════════════════════════════════════════════════════════════╗
#  5 · ETIQUETAS  (espejo PDF p6/8/18)
# ╚══════════════════════════════════════════════════════════════════╝
with tab_lab:
    st.markdown('<div class="sec-title">🏷️ Etiquetas & Motivos de Contacto</div>', unsafe_allow_html=True)
    exp = df.copy()
    exp["label"] = exp["labels"].fillna("Sin etiqueta").str.split(r",\s*")
    exp = exp.explode("label"); exp["label"] = exp["label"].str.strip()
    top = exp["label"].value_counts().head(20).reset_index()
    top.columns = ["label","cantidad"]

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(top, x="cantidad", y="label", orientation="h", color="cantidad",
                     color_continuous_scale="Teal", title="Top 20 motivos")
        fig.update_layout(showlegend=False, yaxis={"categoryorder":"total ascending"})
        st.plotly_chart(style_fig(fig, 520), use_container_width=True)
    with c2:
        fig = px.pie(top.head(12), names="label", values="cantidad",
                     title="Proporción top 12", color_discrete_sequence=COLOR_SEQ, hole=.35)
        st.plotly_chart(style_fig(fig, 520), use_container_width=True)

    rl = []
    for lbl, g in exp[exp["calificado"]].groupby("label"):
        if len(g) >= 5:
            rl.append({"label":lbl, "rating":round(float(g["rating_num"].mean()),2), "n":len(g)})
    if rl:
        rldf = pd.DataFrame(rl).sort_values("rating")
        fig = px.bar(rldf, x="rating", y="label", orientation="h", color="rating",
                     color_continuous_scale="RdYlGn", range_color=[1,5], text="rating",
                     title="Calificación promedio por motivo (mín. 5 cal.)")
        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig.update_layout(showlegend=False, yaxis={"categoryorder":"total ascending"})
        st.plotly_chart(style_fig(fig, 460), use_container_width=True)


# ╔══════════════════════════════════════════════════════════════════╗
#  6 · CANCELACIONES & RETENCIÓN
# ╚══════════════════════════════════════════════════════════════════╝
with tab_canc:
    st.markdown('<div class="sec-title">🚨 Cancelaciones & Retención</div>', unsafe_allow_html=True)
    n_churn = int(df["es_churn_plan"].sum()); n_rep = int(df["es_reprogramacion"].sum())
    st.markdown('<div class="kpi-grid">' +
        kpi_card("Churn de plan", f"{n_churn:,}", f"{pct_churn}% del total", kind="warn") +
        kpi_card("Reprogramaciones", f"{n_rep:,}", f"{pct_reprog}%", kind="amber") +
        kpi_card("Cancelaciones totales", f"{int(df['es_cancelacion'].sum()):,}", f"{pct_cancel}%", kind="alt") +
        '</div>', unsafe_allow_html=True)

    sub_map = {"Cancelar plan (CHURN)":"Cancelar plan", "Cancelación +24hrs":"Cancelaci[oó]n \\+24",
               "Cancelación tardía":"Cancelaci[oó]n tard", "Postergación de fecha":"Postergaci",
               "Esp. cancela sesión":"Esp\\. cancela"}
    rows = [{"Sub-tipo":k, "Chats":int(df["labels"].fillna("").str.contains(v, case=False, regex=True).sum())}
            for k, v in sub_map.items()]
    sub = pd.DataFrame(rows).sort_values("Chats", ascending=False)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(sub, x="Chats", y="Sub-tipo", orientation="h", color="Sub-tipo",
                     color_discrete_map={"Cancelar plan (CHURN)":OY_WARN}, title="Composición de cancelaciones")
        fig.update_layout(showlegend=False, yaxis={"categoryorder":"total ascending"})
        st.plotly_chart(style_fig(fig, 320), use_container_width=True)
    with c2:
        evo = df.groupby(gran_col).agg(
            churn=("es_churn_plan","sum"), rep=("es_reprogramacion","sum"), n=("phone","size")).reset_index()
        evo["% churn"] = (evo["churn"]/evo["n"]*100).round(1)
        evo["% reprog"] = (evo["rep"]/evo["n"]*100).round(1)
        evo[gran_col] = pd.to_datetime(evo[gran_col].astype(str))
        fig = px.line(evo, x=gran_col, y=["% churn","% reprog"], markers=True,
                      color_discrete_map={"% churn":OY_WARN,"% reprog":OY_AMBER}, title="Tendencia (%)")
        fig.add_hline(y=META_CHURN, line_dash="dash", line_color=OY_OK)
        st.plotly_chart(style_fig(fig, 320), use_container_width=True)

    st.subheader("🔁 Clientes con cancelaciones repetidas")
    canc = df[df["es_cancelacion"]]
    cc = []
    for phone, g in canc.groupby("phone"):
        cc.append({"Teléfono":phone, "Cancelaciones":len(g),
                   "Cliente":safe_mode(g["contact"]), "Región":safe_mode(g["region"]),
                   "Sub-tipo frecuente":motivo_principal(g["labels"]),
                   "¿Churn plan?": "Sí" if g["es_churn_plan"].any() else "No"})
    if cc:
        st.dataframe(pd.DataFrame(cc).sort_values("Cancelaciones", ascending=False).head(25),
                     use_container_width=True, hide_index=True)


# ╔══════════════════════════════════════════════════════════════════╗
#  7 · EVOLUCIÓN  (espejo PDF p7/17)
# ╚══════════════════════════════════════════════════════════════════╝
with tab_evo:
    st.markdown('<div class="sec-title">📈 Rendimiento a lo Largo del Tiempo</div>', unsafe_allow_html=True)
    rows = []
    for periodo, g in df.groupby(gran_col):
        t = g["tpr_min"].dropna(); r = g.loc[g["resol_min"]>0,"resol_min"].dropna()
        rows.append({"periodo":str(periodo), "Total":len(g),
                     "Calificación":round(g["rating_num"].mean(),3) if g["calificado"].any() else np.nan,
                     "1ra respuesta (min)":round(t.median(),2) if len(t) else np.nan,
                     "Resolución (min)":round(r.median(),1) if len(r) else np.nan,
                     "% Calificados":safe_pct(g["calificado"].sum(),len(g)),
                     "% Churn":safe_pct(g["es_churn_plan"].sum(),len(g))})
    evo = pd.DataFrame(rows); evo["periodo"] = pd.to_datetime(evo["periodo"])

    fig = make_subplots(specs=[[{"secondary_y":True}]])
    fig.add_trace(go.Bar(x=evo["periodo"], y=evo["Total"], name="Chats", marker_color=OY_TEAL, opacity=.85))
    fig.add_trace(go.Scatter(x=evo["periodo"], y=evo["Calificación"], name="Calificación",
                             line=dict(color=OY_BLUE, width=2.5), mode="lines+markers"), secondary_y=True)
    fig.add_hline(y=META_RATING, line_dash="dash", line_color=OY_OK, secondary_y=True)
    fig.update_yaxes(title_text="Chats", secondary_y=False)
    fig.update_yaxes(title_text="Calificación", range=[4,5.05], secondary_y=True)
    fig.update_layout(title="Volumen y Calificación", hovermode="x unified",
                      legend=dict(orientation="h", y=1.1))
    st.plotly_chart(style_fig(fig, 360), use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.line(evo, x="periodo", y="1ra respuesta (min)", markers=True,
                      color_discrete_sequence=[OY_TEAL], title="1ra respuesta — mediana (min)")
        fig.add_hline(y=META_TPR_MED, line_dash="dash", line_color=OY_WARN)
        st.plotly_chart(style_fig(fig, 300), use_container_width=True)
    with c2:
        fig = px.line(evo, x="periodo", y="% Churn", markers=True,
                      color_discrete_sequence=[OY_WARN], title="% Churn de plan")
        fig.add_hline(y=META_CHURN, line_dash="dash", line_color=OY_OK)
        st.plotly_chart(style_fig(fig, 300), use_container_width=True)

    evo_x = evo.copy(); evo_x["periodo"] = evo_x["periodo"].dt.strftime("%Y-%m-%d")
    st.dataframe(evo_x, use_container_width=True, hide_index=True)
    st.download_button("⬇️ Descargar evolución (.csv)",
                       evo_x.to_csv(index=False).encode("utf-8"), "evolucion.csv", "text/csv")


# ╔══════════════════════════════════════════════════════════════════╗
#  8 · MÉTRICAS CHATS / DETALLE  (espejo PDF p9)
# ╚══════════════════════════════════════════════════════════════════╝
with tab_det:
    st.markdown('<div class="sec-title">📋 Métricas de Chats (Detalle)</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([2, 2])
    search = c1.text_input("🔎 Buscar cliente, teléfono o etiqueta", "")
    s1, s2, s3 = c2.columns(3)
    solo_cal = s1.checkbox("Calificados"); solo_churn = s2.checkbox("Churn plan"); solo_30 = s3.checkbox("TPR>30min")

    d = df.copy()
    d["1ra resp (min)"] = d["tpr_min"].round(2)
    d["Interac (min)"]  = d["dur_min"].round(1)
    d["Resol (min)"]    = d["resol_min"].round(1)
    cols = {"contact":"Cliente","phone":"Teléfono","agent":"Agente","tag":"Equipo",
            "region":"Región","created_at":"Fecha","status":"Estado","rating":"Calif.",
            "1ra resp (min)":"1ra resp (min)","Interac (min)":"Interac (min)","Resol (min)":"Resol (min)",
            "labels":"Etiquetas","finish_type":"Cierre","es_churn_plan":"¿Churn?"}
    d = d[list(cols)].rename(columns=cols)
    if search:
        m = (d["Cliente"].fillna("").str.contains(search, case=False)
             | d["Teléfono"].fillna("").str.contains(search, case=False)
             | d["Etiquetas"].fillna("").str.contains(search, case=False))
        d = d[m]
    if solo_cal:   d = d[d["Calif."] != "-"]
    if solo_churn: d = d[d["¿Churn?"] == True]
    if solo_30:    d = d[d["1ra resp (min)"] > 30]

    st.markdown(f"**{len(d):,} registros**")
    st.dataframe(d, use_container_width=True, height=500, hide_index=True)
    st.download_button("⬇️ Descargar detalle filtrado (.csv)",
                       d.to_csv(index=False).encode("utf-8"), "detalle_chats.csv", "text/csv")


# ════════════════════════════════════════════════════════════════════
#  PESTAÑAS QUE REQUIEREN OTROS EXPORTS DE TREBLE
# ════════════════════════════════════════════════════════════════════
def need_export(nombre, columnas, archivo):
    st.markdown(f'<div class="info-box">📎 Esta sección reproduce <b>{nombre}</b> del tablero de Treble. '
                f'El archivo <code>treble.csv</code> no contiene estos datos; súbelos en el panel lateral '
                f'(<i>{archivo}</i>) para activarla.<br>Columnas esperadas: {", ".join(columnas)}.</div>',
                unsafe_allow_html=True)


with tab_out:
    st.markdown('<div class="sec-title">📤 Outbound / Consumo de Conversaciones</div>', unsafe_allow_html=True)
    if up_out is not None:
        o = load_simple(up_out)
        st.caption(f"{len(o):,} registros cargados.")
        tipo_col = next((c for c in o.columns if c.lower() in ("contact_type","tipo","type")), None)
        if tipo_col:
            vc = o[tipo_col].str.upper().value_counts()
            st.markdown('<div class="kpi-grid">' +
                kpi_card("Total", f"{len(o):,}", kind="alt") +
                kpi_card("Inbound", f"{int(vc.get('INBOUND',0)):,}", kind="") +
                kpi_card("Outbound", f"{int(vc.get('OUTBOUND',0)):,}", kind="ok") +
                '</div>', unsafe_allow_html=True)
            fig = px.pie(values=vc.values, names=vc.index, hole=.4,
                         color_discrete_sequence=[OY_TEAL, OY_BLUE], title="Distribución por tipo")
            st.plotly_chart(style_fig(fig, 320), use_container_width=True)
        name_col = next((c for c in o.columns if c.lower() in ("name","conversación","conversacion","conversation")), None)
        if name_col:
            top = o[name_col].value_counts().head(10).reset_index()
            top.columns = ["Conversación","Total"]
            fig = px.bar(top, x="Total", y="Conversación", orientation="h", color="Total",
                         color_continuous_scale="Teal", title="Top 10 conversaciones más enviadas")
            fig.update_layout(showlegend=False, yaxis={"categoryorder":"total ascending"})
            st.plotly_chart(style_fig(fig, 380), use_container_width=True)
        st.dataframe(o.head(300), use_container_width=True, hide_index=True)
    else:
        need_export("Consumo / Outbound", ["Name","Contact_Type","Created_At","Country_Code","Cellphone"],
                    "Outbound / Consumo")

with tab_fail:
    st.markdown('<div class="sec-title">❌ Fallas de Envío</div>', unsafe_allow_html=True)
    if up_fail is not None:
        f = load_simple(up_fail); st.dataframe(f, use_container_width=True, hide_index=True)
    else:
        need_export("Fallas de Envío", ["Conversación","Fallas","% fallas","Sesión activa","Bloqueado"],
                    "Fallas de envío")

with tab_inv:
    st.markdown('<div class="sec-title">💰 Inversión (USD)</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Precios Treble por conversación: 0–5k <b>$0.20</b> · '
                '5k–10k <b>$0.18</b> · 10k–20k <b>$0.15</b> · &gt;20k <b>$0.12</b>.</div>', unsafe_allow_html=True)
    if up_out is not None:
        o = load_simple(up_out); n = len(o)
        price = 0.20 if n<=5000 else 0.18 if n<=10000 else 0.15 if n<=20000 else 0.12
        st.markdown('<div class="kpi-grid">' +
            kpi_card("Conversaciones", f"{n:,}", kind="alt") +
            kpi_card("Precio/conv.", f"${price:.2f}", kind="") +
            kpi_card("Inversión estimada", f"${n*price:,.2f}", kind="ok") +
            '</div>', unsafe_allow_html=True)
    else:
        need_export("Inversión", ["Conversación","Total","Inversión"], "Outbound / Consumo")

with tab_hsm:
    st.markdown('<div class="sec-title">📨 HSM</div>', unsafe_allow_html=True)
    if up_hsm is not None:
        h = load_simple(up_hsm); st.dataframe(h, use_container_width=True, hide_index=True)
    else:
        need_export("HSM (plantillas)", ["HSM","enviados","entregados","Respuestas","% Respuestas"], "HSM")

with tab_conx:
    st.markdown('<div class="sec-title">🟢 Horarios ON/OFF & Tiempo de Conexión</div>', unsafe_allow_html=True)
    if up_conx is not None:
        c = load_simple(up_conx); st.dataframe(c, use_container_width=True, hide_index=True)
    else:
        need_export("Horarios / Conexión", ["agent_email","conection_time","date","status"], "Horarios / Conexión")


# ── Footer ───────────────────────────────────────────────────────────
st.divider()
st.caption(f"Opción Yo · Dashboard ATC v2 · Fuente: treble.csv · "
           f"Metas: Calif≥{META_RATING} · TPR≤{fmt_min(META_TPR_MED)} · SLA2≥{META_SLA2}% · "
           f"Churn≤{META_CHURN}% · Cobertura≥{META_PCT_CAL}% · Streamlit + Plotly")
