"""
╔══════════════════════════════════════════════════════════════╗
║  DASHBOARD GERENCIAL ATC · OPCIÓN YO  ·  v3                 ║
║  8 pestañas · 6 KPIs invisibles · Marca Opción Yo           ║
║  Stack: Streamlit ≥1.40 · Pandas ≥2.1 · Plotly ≥5.20       ║
║  Ejecutar: python -m streamlit run dashboard_atc_v3.py       ║
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import os
import base64
import requests
from datetime import datetime

# ══════════════════════════════════════════════════════════════
#  CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="ATC · Opción Yo",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Paleta corporativa ────────────────────────────────────────
OY_TEAL      = "#16B6C2"
OY_TEAL_DARK = "#0E7C86"
OY_BLUE      = "#3B6FE0"
OY_OK        = "#0F9D6B"
OY_WARN      = "#DC2626"
OY_AMBER     = "#D98A0B"
OY_INK       = "#0F172A"
COLOR_SEQ    = [OY_TEAL, OY_BLUE, OY_AMBER, "#7E57C2", "#EC4899",
                "#26A69A", "#FF7043", "#42A5F5", "#9CCC65", "#5C6BC0"]

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');
:root{
  --oy-teal:#16B6C2; --oy-td:#0E7C86; --oy-blue:#3B6FE0;
  --oy-ok:#0F9D6B; --oy-warn:#DC2626; --oy-amb:#D98A0B; --oy-purple:#6D4AFF;
  --ink:#0F172A; --ink-2:#475569; --ink-3:#64748B;
  --surface:#F6F7F9; --card:#FFFFFF; --line:#E6E9EF;
}
html,body,[class*="css"],.stApp,[data-testid="stAppViewContainer"],
[data-testid="stSidebar"]{font-family:'Inter',-apple-system,'Segoe UI',sans-serif;}
.stApp{background:var(--surface);}
.block-container{padding-top:1.3rem;max-width:1440px;}
h1,h2,h3,h4,h5{font-family:'Space Grotesk','Inter',sans-serif;color:var(--ink);
  font-weight:700;letter-spacing:-.018em;}
/* Look de producto: ocultar menú, footer y barra superior de Streamlit */
#MainMenu,footer,[data-testid="stToolbar"],[data-testid="stDecoration"]{visibility:hidden;height:0;}
.sec{font-family:'Space Grotesk','Inter',sans-serif;}

[data-testid="stMetric"]{background:var(--card);border:1px solid var(--line);
  border-radius:12px;padding:14px 16px;}
[data-testid="stMetricValue"]{font-size:1.55rem!important;font-weight:800;color:var(--ink);
  font-variant-numeric:tabular-nums;letter-spacing:-.02em;}
[data-testid="stMetricLabel"]{font-size:.72rem!important;color:var(--ink-3);font-weight:600;
  text-transform:uppercase;letter-spacing:.04em;}

/* Header — sobrio y premium */
.oy-header{display:flex;align-items:center;gap:18px;
  background:linear-gradient(120deg,#0B5560 0%,var(--oy-td) 55%,#12A2AE 100%);
  padding:20px 26px;border-radius:14px;margin:0 0 16px;
  box-shadow:0 1px 0 rgba(255,255,255,.14) inset,0 10px 26px rgba(11,85,96,.20);}
.oy-logo{font-weight:800;font-size:1.7rem;color:#fff;line-height:1.1;letter-spacing:-.015em;
  white-space:nowrap;padding-right:18px;border-right:1px solid rgba(255,255,255,.28);
  display:flex;align-items:center;}
.oy-logo span{color:#CFF6FA;margin-left:5px;font-weight:600;}
.oy-htxt{display:flex;flex-direction:column;justify-content:center;}
.oy-htitle{color:#fff;font-weight:700;font-size:1.05rem;margin:0;letter-spacing:-.01em;}
.oy-hsub{color:#BFEAEF;font-size:.8rem;margin:2px 0 0;font-weight:500;}

/* Section — eyebrow con acento lateral, no píldora de color */
.sec{background:transparent;color:var(--ink);padding:0 0 0 12px;
  border-left:4px solid var(--oy-teal);font-weight:700;font-size:1.06rem;
  margin:10px 0 12px;display:block;letter-spacing:-.01em;line-height:1.25;}
.sec.red{border-color:var(--oy-warn);}
.sec.amb{border-color:var(--oy-amb);}
.sec.ok{border-color:var(--oy-ok);}
.sec.blue{border-color:var(--oy-blue);}

/* KPI — tarjetas blancas con acento (look corporativo) */
.kpi-grid{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:12px;}
.kpi{flex:1;min-width:148px;background:var(--card);border:1px solid var(--line);
  border-radius:12px;padding:14px 16px;position:relative;overflow:hidden;
  box-shadow:0 1px 2px rgba(15,23,42,.04);}
.kpi::before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--oy-teal);}
.kpi.alt::before{background:var(--oy-blue);}
.kpi.ok::before{background:var(--oy-ok);}
.kpi.warn::before{background:var(--oy-warn);}
.kpi.amber::before{background:var(--oy-amb);}
.kpi.dark::before{background:var(--oy-td);}
.kpi .l{font-size:.7rem;color:var(--ink-3);font-weight:600;text-transform:uppercase;letter-spacing:.05em;}
.kpi .v{font-size:1.6rem;font-weight:800;margin-top:3px;color:var(--ink);
  font-variant-numeric:tabular-nums;letter-spacing:-.02em;line-height:1.12;}
.kpi.ok .v{color:#0B7A53;} .kpi.warn .v{color:#B91C1C;} .kpi.amber .v{color:#B26D06;}
.kpi .d{font-size:.72rem;color:var(--ink-3);margin-top:3px;font-weight:500;}

/* Avisos — sobrios */
.crit{background:#FEF2F2;border-left:4px solid var(--oy-warn);padding:.65rem .9rem;
  border-radius:8px;margin-bottom:.7rem;color:#991B1B;font-size:.9rem;}
.alrt{background:#FFFBEB;border-left:4px solid var(--oy-amb);padding:.65rem .9rem;
  border-radius:8px;margin-bottom:.7rem;color:#92660A;font-size:.9rem;}
.good{background:#F0FDF4;border-left:4px solid var(--oy-ok);padding:.65rem .9rem;
  border-radius:8px;margin-bottom:.7rem;color:#166534;font-size:.9rem;}
.info{background:#F0FAFB;border-left:4px solid var(--oy-teal);padding:.7rem .9rem;
  border-radius:8px;margin-bottom:.7rem;color:#0E5A63;font-size:.9rem;}
.invis{background:#F5F3FF;border-left:4px solid var(--oy-purple);padding:.7rem .9rem;
  border-radius:8px;margin-bottom:.7rem;color:#4C36B3;font-weight:500;font-size:.9rem;}

/* Tabs — subrayado limpio, no píldora rellena */
.stTabs [data-baseweb="tab-list"]{gap:2px;flex-wrap:wrap;border-bottom:1px solid var(--line);}
.stTabs [data-baseweb="tab"]{background:transparent;border-radius:8px 8px 0 0;
  padding:8px 13px;font-weight:600;color:var(--ink-3);font-size:.85rem;}
.stTabs [aria-selected="true"]{color:var(--oy-td)!important;background:transparent!important;
  border-bottom:2px solid var(--oy-teal)!important;}

[data-testid="stSidebar"]{background:#FFFFFF;border-right:1px solid var(--line);}
[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:10px;}
.stButton>button{border-radius:9px;font-weight:600;border:1px solid var(--line);}
</style>

""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  AUTENTICACIÓN OPCIONAL
# ══════════════════════════════════════════════════════════════
def _secret(k):
    try: return st.secrets.get(k)
    except: return None

def require_auth():
    pw = _secret("app_password")
    if not pw or st.session_state.get("auth_ok"): return
    st.markdown('<div class="oy-header"><div class="oy-logo">opción<span> yo</span></div>'
                '<div><p class="oy-htitle">Dashboard ATC · Acceso restringido</p>'
                '<p class="oy-hsub">Introduce la contraseña para continuar</p></div></div>',
                unsafe_allow_html=True)
    with st.form("login"):
        inp = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Entrar"):
            if inp == pw: st.session_state["auth_ok"] = True; st.rerun()
            else: st.error("Contraseña incorrecta.")
    st.stop()

require_auth()


# ══════════════════════════════════════════════════════════════
#  METAS GERENCIALES
# ══════════════════════════════════════════════════════════════
META_RATING  = 4.85
META_TPR     = 6.0      # min (promedio)
META_SLA2    = 80.0     # %
META_CAL     = 50.0     # % cobertura encuesta
META_CHURN   = 8.0      # %
META_GHOST   = 2.0      # % chats sin respuesta final
META_TRANSF  = 8.0      # % transferencias

DIAS_ES  = {"Monday":"Lunes","Tuesday":"Martes","Wednesday":"Miércoles",
            "Thursday":"Jueves","Friday":"Viernes","Saturday":"Sábado","Sunday":"Domingo"}
DIAS_ORD = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

REGION = {"1":"EE.UU./Canadá","52":"México","57":"Colombia","58":"Venezuela",
          "34":"España","54":"Argentina","56":"Chile","51":"Perú","593":"Ecuador",
          "591":"Bolivia","507":"Panamá","44":"UK","49":"Alemania","55":"Brasil"}

REQ_COLS = {"phone","agent","created_at","labels","rating",
            "agent_first_message_from_allocation","status"}


# ══════════════════════════════════════════════════════════════
#  FUNCIONES AUXILIARES
# ══════════════════════════════════════════════════════════════
def hms_to_min(serie: pd.Series) -> pd.Series:
    def _p(v):
        try:
            p = str(v).strip().split(":")
            return int(p[0])*60 + int(p[1]) + float(p[2])/60
        except: return np.nan
    return serie.apply(_p)

def fmt_min(m) -> str:
    if m is None or (isinstance(m, float) and np.isnan(m)) or m < 0: return "–"
    m = float(m)
    return f"{int(m//60):02d}:{int(m%60):02d}:{int((m*60)%60):02d}"

def safe_pct(n, d) -> float:
    return round(float(n)/float(d)*100, 1) if d else 0.0

def safe_mode(s, default="–"):
    s = s.dropna()
    return s.mode().iloc[0] if len(s) and len(s.mode()) else default

def motivo_ppal(lbl_serie: pd.Series) -> str:
    flat = lbl_serie.dropna().str.split(r",\s*").explode().str.strip()
    return flat.mode().iloc[0] if len(flat) and len(flat.mode()) else "–"

def kpi(label, value, delta="", kind=""):
    d = f'<div class="d">{delta}</div>' if delta else ""
    return f'<div class="kpi {kind}"><div class="l">{label}</div><div class="v">{value}</div>{d}</div>'

def sfig(fig, h=320):
    fig.update_layout(height=h, margin=dict(t=46, b=10, l=10, r=10),
                      font=dict(color=OY_INK, family="Inter,Segoe UI,sans-serif"),
                      plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    if fig.layout.title.text:
        fig.update_layout(title_font=dict(color=OY_TEAL_DARK, size=14))
    else:
        fig.update_layout(title_text="", margin=dict(t=12, b=10, l=10, r=10))
    return fig

def gauge(title, val, ref, rng, steps, suffix="", invert=False):
    v = round(float(val), 2) if not (isinstance(val,float) and np.isnan(val)) else 0
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta", value=v,
        number={"suffix":suffix,"font":{"size":26,"color":OY_INK}},
        delta={"reference":ref,
               "increasing":{"color":OY_WARN if invert else OY_OK},
               "decreasing":{"color":OY_OK if invert else OY_WARN}},
        title={"text":title,"font":{"size":13,"color":OY_TEAL_DARK}},
        gauge={"axis":{"range":rng},"bar":{"color":OY_TEAL},
               "steps":steps,
               "threshold":{"line":{"color":OY_OK,"width":3},"thickness":.85,"value":ref}}))
    return sfig(fig, 240)


# ══════════════════════════════════════════════════════════════
#  CARGA Y LIMPIEZA
# ══════════════════════════════════════════════════════════════
@st.cache_data(show_spinner="⏳ Procesando datos…")
def load_data(file) -> pd.DataFrame:
    try: df = pd.read_csv(file, dtype=str)
    except Exception as e: st.error(f"No se pudo leer: {e}"); st.stop()
    faltan = REQ_COLS - set(df.columns)
    if faltan: st.error(f"Faltan columnas: {sorted(faltan)}"); st.stop()
    df = df.drop(columns=[c for c in ["username"] if c in df.columns])

    # Fechas
    for c in ["created_at","assigned_at","finished_at","agent_first_message","last_message"]:
        if c in df.columns: df[c] = pd.to_datetime(df[c], errors="coerce")

    # Tiempos operacionales
    df["tpr_min"]     = hms_to_min(df["agent_first_message_from_allocation"])
    df["dur_min"]     = hms_to_min(df.get("duration", pd.Series(dtype=str)))
    df["resol_min"]   = ((df["finished_at"] - df["created_at"]).dt.total_seconds()/60).clip(lower=0)

    # Handle time ACTIVO (primer mensaje agente → último mensaje)
    if "agent_first_message" in df.columns and "last_message" in df.columns:
        df["handle_min"] = ((df["last_message"] - df["agent_first_message"])
                            .dt.total_seconds()/60).clip(lower=0)
    else:
        df["handle_min"] = np.nan

    # Lag asignación (creación → asignación)
    if "assigned_at" in df.columns:
        df["lag_asig_min"] = ((df["assigned_at"] - df["created_at"])
                              .dt.total_seconds()/60).clip(lower=0)
    else:
        df["lag_asig_min"] = np.nan

    # Rating
    df["rating_num"] = pd.to_numeric(df["rating"].replace("-", np.nan), errors="coerce")
    df["calificado"] = df["rating_num"].notna()

    # Tiempo
    df["fecha"]   = df["created_at"].dt.date
    df["hora"]    = df["created_at"].dt.hour
    df["dia_nombre"] = df["created_at"].dt.day_name()
    df["semana"]  = df["created_at"].dt.to_period("W").apply(
        lambda p: p.start_time.date() if pd.notna(p) else None)
    df["mes"]     = df["created_at"].dt.to_period("M").apply(
        lambda p: p.start_time.date() if pd.notna(p) else None)

    # SLA
    df["sla_2min"]  = df["tpr_min"] <= 2
    df["sla_5min"]  = df["tpr_min"] <= 5
    df["sla_15min"] = df["tpr_min"] <= 15
    df["sla_30min"] = df["tpr_min"] <= 30
    df["dur_outlier"] = df["dur_min"] > 300

    # Cancelaciones — 3 BLOQUES SEPARADOS Y BIEN DEFINIDOS
    lbl = df["labels"].fillna("")

    # CHURN = pérdida real de ingresos (cancelan la suscripción)
    df["es_churn"]    = lbl.str.contains(r"Cancelar plan|Reembolso", case=False, regex=True)

    # CANCELACIÓN DE SESIÓN = cancelan una sesión puntual (NO cancelan el plan)
    df["es_cancel_sesion"] = lbl.str.contains(
        r"Cancelaci[oó]n \+24|Cancelaci[oó]n tard|Esp\. cancela",
        case=False, regex=True)

    # POSTERGACIÓN DE PAGO = tema financiero/administrativo (va en bloque propio)
    df["es_postergacion"] = lbl.str.contains(r"Postergaci", case=False, regex=True)

    # REPROG = cancelación de sesión + postergación (juntos para tendencia consolidada)
    df["es_reprog"]   = df["es_cancel_sesion"] | df["es_postergacion"]
    df["es_cancel"]   = df["es_churn"] | df["es_reprog"]

    # Chats fantasma (último mensaje del cliente)
    if "last_message_sender" in df.columns:
        df["ghost"] = df["last_message_sender"].str.upper().str.contains(
            "USER|CONTACT|CLIENT", na=False)
    else:
        df["ghost"] = False

    # Transferidos
    df["transferido"] = df["last_transfer_from"].notna() if "last_transfer_from" in df.columns else False

    # Sin etiqueta
    df["sin_label"] = lbl.str.strip().eq("")

    # ID único de chat (phone + created_at) — usado para ajustes de rating
    df["chat_id"] = df["phone"].astype(str) + "|" + df["created_at"].astype(str)

    # Región
    cc = df["phone"].str.extract(r"^\+?(\d{1,3})")[0]
    df["region"] = cc.map(REGION).fillna("Otros")

    # Etiqueta principal
    df["label_ppal"] = lbl.replace("", "Sin etiqueta").str.split(r",\s*").str[0].str.strip()

    # Reintentos mismo día
    df["date"] = df["created_at"].dt.date
    reint = df.groupby(["phone","date"]).transform("size")
    df["reintento"] = reint > 1

    # ── NORMALIZACIÓN DE COLAS (colas creadas con nombre de persona → equipo real) ──
    # Config errónea en Treble: existen colas con nombre de agente. Se reagrupan
    # a su equipo real para un análisis por cola/equipo consistente. (Mapeo: Iva)
    COLA_NORM = {
        "lau m": "gestor consultoria", "laura m": "gestor consultoria",
        "lau p": "retención", "laura p": "retención",
        "lau o": "mantenimiento", "carolina": "mantenimiento",
        "giselle": "mantenimiento", "carlos": "mantenimiento",
        "alonso": "retención", "diana": "retención",
        "glina": "retención", "claudia": "retención",   # Fidelización (confirmado en HubSpot)
    }
    if "tag" in df.columns:
        df["tag"] = df["tag"].apply(
            lambda t: COLA_NORM.get(str(t).strip().lower(), t) if pd.notna(t) else t)

    # ── DEFINICIÓN "CHATS ATENDIDOS" (igual que Treble) ──────────────
    # Treble cuenta como "atendido" el chat que un AGENTE RESPONDIÓ
    # (envió el primer mensaje), no los que entraron a la cola sin
    # respuesta. Esto alinea los números del dashboard con Treble.
    df["atendido"] = df["agent_first_message"].notna()
    df = df[df["atendido"]].copy()

    return df


def build_agent_kpis(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for ag, g in data.groupby("agent"):
        n   = len(g)
        cal = g["rating_num"].dropna(); nc = len(cal)
        tpr = g["tpr_min"].dropna();   nt = len(tpr)
        hnd = g.loc[g["handle_min"] < 500, "handle_min"].dropna()
        rows.append({
            "Agente":          ag,
            "Chats":           n,
            "% Total":         safe_pct(n, len(data)),
            "TPR prom (min)":  round(float(tpr.mean()), 2) if nt else np.nan,
            "TPR val (min)":   round(float(tpr.mean()), 2) if nt else np.nan,
            "Handle (min)":    round(float(hnd.median()), 1) if len(hnd) else np.nan,
            "Rating":          round(float(cal.mean()), 2) if nc else np.nan,
            "% Calificados":   safe_pct(nc, n),
            "% Churn":         safe_pct(g["es_churn"].sum(), n),
            "Cola":            safe_mode(g["tag"]) if "tag" in g.columns else "–",
            "Nivel":           "",
        })
    df_ag = pd.DataFrame(rows).sort_values("Chats", ascending=False)
    def nivel(r):
        tpr_v_ = r["TPR val (min)"]
        rat_   = r["Rating"]
        if (not (isinstance(rat_,  float) and np.isnan(rat_))  and rat_  >= META_RATING and
            not (isinstance(tpr_v_,float) and np.isnan(tpr_v_)) and tpr_v_ <= 2):
            return "⭐ Top"
        if ((not (isinstance(rat_,  float) and np.isnan(rat_))  and rat_  < 4.5) or
            (not (isinstance(tpr_v_,float) and np.isnan(tpr_v_)) and tpr_v_ > 10) or
            r["% Churn"] > 40):
            return "⚠️ Atención"
        return "✅ Bueno"
    df_ag["Nivel"] = df_ag.apply(nivel, axis=1)
    return df_ag


def top_clientes(data: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    rows = []
    for ph, g in data.groupby("phone"):
        rows.append({
            "Teléfono":         ph,
            "Cliente":          safe_mode(g["contact"]) if "contact" in g.columns else "–",
            "Contactos":        len(g),
            "Motivo principal": motivo_ppal(g["labels"]),
            "Cola":             safe_mode(g["tag"]) if "tag" in g.columns else "–",
            "Región":           safe_mode(g["region"]),
            "Agente frecuente": safe_mode(g["agent"]),
            "Rating prom":      round(float(g["rating_num"].mean()), 2)
                                if g["rating_num"].notna().any() else np.nan,
            "¿Churn?":          "Sí" if g["es_churn"].any() else "No",
            "Última inter.":    str(g["created_at"].max().date())
                                if g["created_at"].notna().any() else "–",
        })
    return pd.DataFrame(rows).sort_values("Contactos", ascending=False).head(n)


# ══════════════════════════════════════════════════════════════
#  ALMACENAMIENTO PERSISTENTE COMPARTIDO (GitHub)
#  Hace que el histórico de treble se guarde y lo vea TODO el mundo,
#  no solo la sesión actual. Si no hay token configurado, el dashboard
#  funciona igual que antes (modo sesión), sin romperse.
#
#  Configuración en Streamlit → Settings → Secrets:
#     [github]
#     token  = "github_pat_xxx"        # PAT con Contents: Read/Write
#     repo   = "robfox0315/opcionyo-data"
#     path   = "treble_historico.csv"  # opcional
#     branch = "main"                  # opcional
# ══════════════════════════════════════════════════════════════
_GH = dict(st.secrets.get("github", {})) if hasattr(st, "secrets") else {}
PERSIST = bool(_GH.get("token") and _GH.get("repo"))
_GH_PATH   = _GH.get("path", "treble_historico.csv")
_GH_BRANCH = _GH.get("branch", "main")

# Archivo de datos PRECARGADO en el repo (para que el equipo vea la data sin subir nada).
# Roberto lo actualiza reemplazando este CSV en GitHub.
DATA_FILE = "treble_historico.csv"

def _gh_url():
    return f"https://api.github.com/repos/{_GH['repo']}/contents/{_GH_PATH}"

def _gh_headers():
    return {"Authorization": f"token {_GH['token']}",
            "Accept": "application/vnd.github+json"}

@st.cache_data(ttl=60, show_spinner=False)
def gh_load_df():
    """Lee el histórico compartido desde GitHub (vacío si no existe)."""
    if not PERSIST:
        return pd.DataFrame()
    try:
        r = requests.get(_gh_url(), headers=_gh_headers(),
                         params={"ref": _GH_BRANCH}, timeout=20)
        if r.status_code == 404:
            return pd.DataFrame()
        r.raise_for_status()
        content = base64.b64decode(r.json()["content"])
        return pd.read_csv(io.BytesIO(content), dtype=str)
    except Exception:
        return pd.DataFrame()

def _gh_sha():
    try:
        r = requests.get(_gh_url(), headers=_gh_headers(),
                         params={"ref": _GH_BRANCH}, timeout=20)
        return r.json().get("sha") if r.status_code == 200 else None
    except Exception:
        return None

def gh_save_df(df: pd.DataFrame) -> bool:
    """Guarda (sobrescribe) el histórico compartido en GitHub."""
    if not PERSIST:
        return False
    try:
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        payload = {
            "message": f"Histórico treble · {len(df):,} filas · {datetime.now():%Y-%m-%d %H:%M}",
            "content": base64.b64encode(csv_bytes).decode("ascii"),
            "branch": _GH_BRANCH,
        }
        sha = _gh_sha()
        if sha:
            payload["sha"] = sha
        r = requests.put(_gh_url(), headers=_gh_headers(), json=payload, timeout=30)
        r.raise_for_status()
        gh_load_df.clear()
        return True
    except Exception as e:
        st.error(f"No se pudo guardar en el almacén compartido: {e}")
        return False


# ══════════════════════════════════════════════════════════════
#  GESTIÓN DEL HISTÓRICO ACUMULADO
#  Guarda en session_state un DataFrame maestro que crece
#  cada vez que se sube un CSV nuevo. Nunca reemplaza — siempre
#  agrega filas nuevas (deduplicando por phone+created_at).
# ══════════════════════════════════════════════════════════════
if "df_historico" not in st.session_state:
    st.session_state["df_historico"] = pd.DataFrame()
if "archivos_cargados" not in st.session_state:
    st.session_state["archivos_cargados"] = []
if "ajustes_rating" not in st.session_state:
    # dict: {chat_id → {"excluir": True, "motivo": "...", "confirmado_por": "..."}}
    # chat_id = phone + "|" + created_at
    st.session_state["ajustes_rating"] = {}

# Cargar el histórico COMPARTIDO (GitHub) una vez por sesión
if PERSIST and not st.session_state.get("_persist_loaded"):
    _base = gh_load_df()
    if not _base.empty:
        st.session_state["df_historico"] = _base
        st.session_state["archivos_cargados"] = ["📡 histórico compartido"]
    st.session_state["_persist_loaded"] = True


def _leer_csv_robusto(archivo) -> pd.DataFrame:
    """Lee un CSV tolerando BOM, encoding y separadores raros (; \\t |)."""
    def _try(enc, sep):
        if hasattr(archivo, "seek"):
            archivo.seek(0)
        return pd.read_csv(archivo, dtype=str, encoding=enc, sep=sep,
                           engine="python" if sep is None else "c")
    d = None
    for enc in ("utf-8-sig", "latin-1"):
        try:
            d = _try(enc, ",")
            break
        except Exception:
            continue
    if d is None:
        d = _try("utf-8-sig", None)          # autodetección
    # Limpiar BOM/espacios en nombres de columna
    d.columns = [str(c).replace("\ufeff", "").strip() for c in d.columns]
    # Si quedó en 1 sola columna, el separador no era coma → reintentar
    if d.shape[1] == 1:
        for sep in (";", "\t", "|"):
            try:
                d2 = _try("utf-8-sig", sep)
                if d2.shape[1] > 1:
                    d2.columns = [str(c).replace("\ufeff", "").strip() for c in d2.columns]
                    return d2
            except Exception:
                pass
    return d


@st.cache_data(show_spinner="⏳ Cargando histórico…")
def _fusionar_historico(firma):
    """Fusiona base + updates y deduplica (versión más fresca gana).
    'firma' = tupla (ruta, mtime); la caché se invalida solo si cambia un archivo."""
    frames = []
    for i, (f, _) in enumerate(firma):
        try:
            dfx = _leer_csv_robusto(f)
            if "phone" in dfx.columns and "created_at" in dfx.columns:
                dfx["_ord"] = i
                frames.append(dfx)
        except Exception:
            pass
    if not frames:
        return pd.DataFrame()
    merged = pd.concat(frames, ignore_index=True)
    merged["_k"] = merged["phone"].astype(str) + "|" + merged["created_at"].astype(str)
    merged = (merged.sort_values("_ord")
                    .drop_duplicates("_k", keep="last")
                    .drop(columns=["_ord", "_k"]))
    return merged


def acumular_csv(archivo) -> pd.DataFrame:
    """Carga un CSV y lo acumula al histórico sin duplicar filas."""
    try:
        nuevo = _leer_csv_robusto(archivo)
    except Exception as e:
        st.error(f"No se pudo leer el archivo: {e}")
        return st.session_state["df_historico"]

    # Validar que sea un export de Treble
    if "phone" not in nuevo.columns or "created_at" not in nuevo.columns:
        st.error("⚠️ Este CSV no parece un export de Treble: no encuentro las columnas "
                 "'phone' y/o 'created_at'. Verifica que subiste el archivo correcto "
                 "(el reporte de chats de Treble), sin abrirlo/guardarlo en Excel.")
        return st.session_state["df_historico"]

    if st.session_state["df_historico"].empty:
        st.session_state["df_historico"] = nuevo
    else:
        hist = st.session_state["df_historico"]
        # Deduplicar: key = phone + created_at (identifica cada chat único)
        if "phone" in nuevo.columns and "created_at" in nuevo.columns:
            key_hist = hist["phone"].astype(str) + "|" + hist["created_at"].astype(str)
            key_new  = nuevo["phone"].astype(str) + "|" + nuevo["created_at"].astype(str)
            filas_nuevas = nuevo[~key_new.isin(set(key_hist))]
            if len(filas_nuevas) > 0:
                st.session_state["df_historico"] = pd.concat(
                    [hist, filas_nuevas], ignore_index=True)
        else:
            st.session_state["df_historico"] = pd.concat(
                [hist, nuevo], ignore_index=True)

    return st.session_state["df_historico"]


# ══════════════════════════════════════════════════════════════
#  HEADER DE MARCA
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div class="oy-header">
  <div class="oy-logo">opción<span>yo</span></div>
  <div class="oy-htxt">
    <p class="oy-htitle">Atención al Cliente</p>
    <p class="oy-hsub">Panel de gestión</p>
  </div>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════
# ── Carga de datos (silenciosa · sin panel lateral) ─────────
import glob
if st.session_state["df_historico"].empty:
    _fuentes = []
    for _ruta in [DATA_FILE, os.path.join("data", DATA_FILE)]:
        if os.path.exists(_ruta):
            _fuentes.append(_ruta)
            break
    _fuentes += sorted(glob.glob("updates/*.csv")) + sorted(glob.glob("data/updates/*.csv"))
    if not _fuentes and os.path.exists("treble.csv"):
        _fuentes = ["treble.csv"]
    _firma = tuple((f, os.path.getmtime(f)) for f in _fuentes if os.path.exists(f))
    if _firma:
        _merged = _fusionar_historico(_firma)
        if not _merged.empty:
            st.session_state["df_historico"] = _merged

if st.session_state["df_historico"].empty:
    st.warning("No encuentro datos. Sube treble_historico.csv al repositorio.")
    st.stop()

# ── FUENTE HÍBRIDA: histórico CSV + últimos 90 días EN VIVO del Data Warehouse ──
_dwh_estado = None
try:
    import treble_dwh as _tw
    if _tw.dwh_activo():
        _live = _tw.cargar_conversaciones(90)
        if not _live.empty:
            _base = st.session_state["df_historico"].copy()
            _base["_o"], _live["_o"] = 0, 1          # el DWH gana
            _mix = pd.concat([_base, _live], ignore_index=True)
            _mix["_k"] = _mix["phone"].astype(str) + "|" + _mix["created_at"].astype(str)
            _mix = (_mix.sort_values("_o").drop_duplicates("_k", keep="last")
                        .drop(columns=["_o", "_k"]))
            st.session_state["df_historico"] = _mix
            _dwh_estado = ("ok", len(_live))
        else:
            _dwh_estado = ("vacio", 0)
    else:
        _dwh_estado = ("inactivo", 0)
except Exception as _e:
    _dwh_estado = ("error", f"{type(_e).__name__}: {str(_e)[:400]}")

try:
    df_raw = load_data(io.StringIO(st.session_state["df_historico"].to_csv(index=False)))
except Exception as e:
    st.error(f"Error procesando datos: {e}")
    st.stop()

# Aviso SOLO si la actualización en vivo falló (para no dejar datos viejos en silencio)
if _dwh_estado and _dwh_estado[0] == "error":
    st.warning(f"⚠️ No se pudo actualizar en vivo desde el Data Warehouse. "
               f"Mostrando histórico hasta {df_raw['created_at'].max():%d/%m/%Y}. "
               f"Detalle: {_dwh_estado[1]}")
elif _dwh_estado and _dwh_estado[0] == "vacio":
    st.warning(f"⚠️ El Data Warehouse no devolvió conversaciones (consulta vacía). "
               f"Mostrando histórico hasta {df_raw['created_at'].max():%d/%m/%Y}.")

# Sin filtros globales: cada pestaña define su propio rango de fechas.
ags = colas = regs = labs = ests = []
gc = "semana"
dur_excl_out = True
_FMIN = df_raw["created_at"].min().date()
_FMAX = df_raw["created_at"].max().date()
_AGENTES_OPTS = sorted(df_raw["agent"].dropna().unique())
_COLAS_OPTS = sorted(df_raw["tag"].dropna().unique())


def filtro_fecha(key, label="📅 Rango de fechas", con_agente=True):
    """Filtro propio de cada pestaña: fecha + (opcional) agente y cola/especialista."""
    if con_agente:
        c1, c2, c3 = st.columns([2, 2, 2])
        with c1:
            r = st.date_input(label, (_FMIN, _FMAX), min_value=_FMIN, max_value=_FMAX,
                              key=f"fecha_{key}")
        with c2:
            ags = st.multiselect("👤 Agente", _AGENTES_OPTS, placeholder="Todos", key=f"ag_{key}")
        with c3:
            colas = st.multiselect("📂 Cola / Especialista", _COLAS_OPTS, placeholder="Todas",
                                   key=f"co_{key}")
    else:
        r = st.date_input(label, (_FMIN, _FMAX), min_value=_FMIN, max_value=_FMAX, key=f"fecha_{key}")
        ags, colas = [], []
    fi = r[0] if isinstance(r, (list, tuple)) and len(r) == 2 else _FMIN
    ff = r[1] if isinstance(r, (list, tuple)) and len(r) == 2 else _FMAX
    return fi, ff, ags, colas


def _ctx(f_ini, f_fin, ags=None, colas=None):
    """Filtra df_raw por fecha (+ agente/cola opcionales) y calcula TODAS las métricas.
    Cada pestaña vuelca el resultado a globals() para tener su propio contexto."""
    df = df_raw[(df_raw["created_at"].dt.date >= f_ini) &
                (df_raw["created_at"].dt.date <= f_fin)].copy()
    if ags:
        df = df[df["agent"].isin(ags)]
    if colas:
        df = df[df["tag"].isin(colas)]
    df["rating_original"] = df["rating_num"].copy()
    df["rating_ajustado"] = False
    _aj = st.session_state.get("ajustes_rating", {})
    if _aj and "chat_id" in df.columns:
        for _cid, _info in _aj.items():
            if _info.get("excluir"):
                _m = df["chat_id"] == _cid
                df.loc[_m, "rating_num"] = np.nan
                df.loc[_m, "rating_ajustado"] = True

    N          = len(df)
    n_cal      = int(df["calificado"].sum())
    pct_cal    = safe_pct(n_cal, N)
    rating     = df["rating_num"].mean()
    tpr_v      = df["tpr_min"].dropna()
    tpr_prom   = tpr_v.mean() if len(tpr_v) else np.nan
    tpr_p90    = tpr_v.quantile(.9) if len(tpr_v) else np.nan
    tpr_med    = tpr_v.median() if len(tpr_v) else np.nan
    pct_sla2   = safe_pct(df["sla_2min"].sum(), len(tpr_v)) if len(tpr_v) else 0
    pct_sla5   = safe_pct(df["sla_5min"].sum(), len(tpr_v)) if len(tpr_v) else 0
    pct_over30 = safe_pct((tpr_v > 30).sum(), len(tpr_v)) if len(tpr_v) else 0
    pct_churn  = safe_pct(df["es_churn"].sum(), N)
    pct_reprog = safe_pct(df["es_reprog"].sum(), N)
    pct_ghost  = safe_pct(df["ghost"].sum(), N)
    pct_transf = safe_pct(df["transferido"].sum(), N)
    pct_sin_lbl= safe_pct(df["sin_label"].sum(), N)
    csat       = safe_pct((df["rating_num"] >= 4).sum(), n_cal) if n_cal else 0
    det        = safe_pct((df["rating_num"] <= 3).sum(), n_cal) if n_cal else 0
    prom5      = safe_pct((df["rating_num"] == 5).sum(), n_cal) if n_cal else 0
    contactos  = df.groupby("phone").size()
    n_recur    = int((contactos >= 2).sum())
    pct_vol_recur = safe_pct(contactos[contactos >= 2].sum(), N)
    hnd_v      = df.loc[df["handle_min"] < 500, "handle_min"].dropna()
    hnd_med    = hnd_v.median() if len(hnd_v) else np.nan
    lag_v      = df["lag_asig_min"].dropna()
    lag_prom   = lag_v.mean() if len(lag_v) else np.nan
    n_ghost    = int(df["ghost"].sum())
    n_reint    = int(df["reintento"].sum())
    hora_pico  = int(safe_mode(df["hora"], 0))
    dia_pico   = DIAS_ES.get(safe_mode(df["dia_nombre"]), "–")
    top_motivo = motivo_ppal(df["labels"])
    ag_churn   = build_agent_kpis(df)
    n_rating  = {i: int((df["rating_num"] == i).sum()) for i in [1, 2, 3, 4, 5]}
    n_bajas   = n_rating[1] + n_rating[2] + n_rating[3]
    n_altas   = n_rating[4] + n_rating[5]
    pct_1     = safe_pct(n_rating[1], n_cal)
    pct_2     = safe_pct(n_rating[2], n_cal)
    pct_3     = safe_pct(n_rating[3], n_cal)
    pct_4     = safe_pct(n_rating[4], n_cal)
    pct_5     = safe_pct(n_rating[5], n_cal)
    pct_bajas = safe_pct(n_bajas, n_cal)
    pct_altas = safe_pct(n_altas, n_cal)
    prom_bajas = df.loc[df["rating_num"] <= 3, "rating_num"].mean()
    prom_altas = df.loc[df["rating_num"] >= 4, "rating_num"].mean()
    return {k: v for k, v in locals().items() if not k.startswith("_")}

# ══════════════════════════════════════════════════════════════
#  TABS
# ══════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════
#  RESPALDO EXCEL — cálculo del histórico semanal/mensual por agente
#  Replica las filas de la hoja "AgenteHistorico semanal" del Excel.
#  Definiciones tomadas de las fórmulas del propio Excel (Base tratada):
#   · Agrupación por FECHA DE ASIGNACIÓN (assigned_at), semana ISO
#     fechada al DOMINGO que la cierra.
#   · Buckets de tiempo idénticos: ≤5min · rango 5-10min · >30min.
#   · % rating <4 / >4 sobre el TOTAL de chats (igual que tu Histórico global).
# ══════════════════════════════════════════════════════════════
RESP_AGENTES = {                       # etiqueta del Excel → nombre real en el CSV
    "Ivonne Gonzalez":  "Ivonne González",
    "Estefany Suarez":  "Estefany Suárez",
    "Samira Pirique":   "Samira Pirique",
    "Yesith Solano":    "Yesith Solano",
    "Lizbeth Calcina":  "Lizbeth Calcina",
    "Mary Cardenas":    "Mary Cárdenas",
    "Camila Rodriguez": "Camila Rodriguez",
    "Sofia Castro":     "Sofia Castro",
    "Eduardo Liendo":   "Eduardo Liendo",     # nuevo
    "Erika Quiñonez":   "Erika Quinonez",     # retirada (se conserva su histórico)
}
RESP_RETIRADOS = {"Erika Quinonez"}            # se muestran solo si tienen datos
RESP_NUEVOS    = {"Eduardo Liendo"}
RESP_FILAS = [
    "Chats atendidos",
    "Rating ATC",
    "# Chats calificados",
    "% Chats calificados",
    "Porcentaje de chats Rating <4",
    "Porcentaje rating >4",
    "Promedio primera respuesta",
    "Porcentaje de chats atendidos antes de los 5 minutos",
    "Porcentaje de chats atendidos antes de los 10 minutos",
    "Porcentaje de chats atendidos después de los 30 minutos",
    "Tiempo medio interacción",
    "Duración promedio",
]
RESP_MESES = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",
              7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",
              11:"Noviembre",12:"Diciembre"}


def _resp_min_to_hms(m) -> str:
    if pd.isna(m): return ""
    s = int(round(float(m) * 60))
    return f"{s//3600}:{(s%3600)//60:02d}:{s%60:02d}"


def resp_preparar(dfr: pd.DataFrame) -> pd.DataFrame:
    """Usa las columnas ya calculadas por load_data (rating_num, tpr_min, dur_min).
    Agrupa por created_at (mismo criterio que el resto del dashboard y Treble)."""
    d = dfr.copy()
    d["_fecha"] = d["created_at"]                     # ← criterio único (Opción A)
    d = d[d["_fecha"].notna()].copy()
    d["_rating"] = d["rating_num"]
    d["_tpr"]    = d["tpr_min"]
    d["_dur"]    = d["dur_min"]
    wd = d["_fecha"].dt.weekday                       # lun=0 … dom=6
    d["_domingo"] = (d["_fecha"] + pd.to_timedelta(6 - wd, unit="D")).dt.normalize()
    d["_mes"]     = d["_fecha"].dt.to_period("M")
    return d


def resp_bloque(g: pd.DataFrame) -> dict:
    n = len(g)
    if n == 0:
        return {f: "" for f in RESP_FILAS}
    r, tpr = g["_rating"], g["_tpr"]
    n_cal = int(r.notna().sum())
    return {
        "Chats atendidos": n,
        "Rating ATC": round(r.mean(), 2) if r.notna().any() else "",
        "# Chats calificados": n_cal,
        "% Chats calificados": round(n_cal / n * 100, 2),
        "Porcentaje de chats Rating <4": round((r < 4).sum() / n * 100, 2),
        "Porcentaje rating >4":          round((r > 4).sum() / n * 100, 2),
        "Promedio primera respuesta":    _resp_min_to_hms(tpr.mean()),
        "Porcentaje de chats atendidos antes de los 5 minutos":
            round((tpr <= 5).sum() / n * 100, 2),
        "Porcentaje de chats atendidos antes de los 10 minutos":
            round(((tpr > 5) & (tpr <= 10)).sum() / n * 100, 2),
        "Porcentaje de chats atendidos después de los 30 minutos":
            round((tpr > 30).sum() / n * 100, 2),
        "Tiempo medio interacción": "",              # ← viene de Treble (no en CSV)
        "Duración promedio": _resp_min_to_hms(g["_dur"].mean()),
    }


_RESP_DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

def resp_picos(sub: pd.DataFrame) -> dict:
    """Día/hora con más chats (promedio) + récord día-hora. Sirve para semana y mes.
    'Promedio' = promedio de chats por día-de-semana / por hora entre los días del periodo."""
    if sub is None or sub.empty:
        return {"Día con más chats (promedio)": "—",
                "Horas con más chats (promedio)": "—",
                "Día y hora con más chats (récord)": "—"}
    f = sub["_fecha"]
    # promedio por día de semana (cuenta diaria → promedio por dow)
    por_dia = sub.groupby([f.dt.dayofweek, f.dt.date]).size().groupby(level=0).mean()
    dmax = int(por_dia.idxmax())
    # promedio por hora
    por_hora = sub.groupby([f.dt.hour, f.dt.date]).size().groupby(level=0).mean()
    hmax = int(por_hora.idxmax())
    # récord: celda (fecha, hora) con más chats
    rec = sub.groupby([f.dt.date, f.dt.hour]).size()
    (rfecha, rhora), rval = rec.idxmax(), int(rec.max())
    return {
        "Día con más chats (promedio)":  f"{_RESP_DIAS[dmax]} ({por_dia.max():.0f})",
        "Horas con más chats (promedio)": f"{hmax:02d}:00 hrs ({por_hora.max():.0f})",
        "Día y hora con más chats (récord)":
            f"{_RESP_DIAS[pd.Timestamp(rfecha).dayofweek]} {rhora:02d}:00 · "
            f"{pd.Timestamp(rfecha):%d/%m/%Y} ({rval} chats)",
    }


def resp_tabla(d: pd.DataFrame, agente_real=None, cierres=True) -> pd.DataFrame:
    reales = list(RESP_AGENTES.values())
    allag = d[d["agent"].isin(reales)]
    base = allag if agente_real is None else d[d["agent"] == agente_real]
    dom_tot = allag.groupby("_domingo").size()      # denominador = todo el equipo
    mes_tot = allag.groupby("_mes").size()
    cols = {}
    for dom, g in sorted(base.groupby("_domingo"), key=lambda x: x[0]):
        b = resp_bloque(g)
        if agente_real is not None:
            tot = dom_tot.get(dom, 0)
            b["% del total (equipo)"] = round(len(g) / tot * 100, 1) if tot else 0
        cols[pd.Timestamp(dom).strftime("%d/%m/%Y")] = b
    if cierres:
        for per, g in sorted(base.groupby("_mes"), key=lambda x: x[0]):
            b = resp_bloque(g)
            if agente_real is not None:
                tot = mes_tot.get(per, 0)
                b["% del total (equipo)"] = round(len(g) / tot * 100, 1) if tot else 0
            cols[f"Cierre {RESP_MESES[per.month]} {per.year}"] = b
    filas = RESP_FILAS + (["% del total (equipo)"] if agente_real is not None else [])
    return pd.DataFrame(cols).reindex(filas)


def resp_dia_hora_pico(wk: pd.DataFrame):
    """Matriz día×hora de una semana + indicadores (día/hora con más y menos chats)."""
    dias_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    w = wk.copy()
    w["_wd"] = w["_fecha"].dt.weekday
    w["_h"]  = w["_fecha"].dt.hour
    piv = (w.pivot_table(index="_wd", columns="_h", values="_fecha",
                         aggfunc="count", fill_value=0)
             .reindex(index=range(7), columns=range(24), fill_value=0))
    z = piv.values
    por_dia  = piv.sum(axis=1)
    por_hora = piv.sum(axis=0)
    ij = np.unravel_index(int(np.argmax(z)), z.shape) if z.size and z.max() > 0 else (0, 0)
    info = {
        "dias": dias_es, "z": z,
        "dia_max":  (dias_es[int(por_dia.idxmax())],  int(por_dia.max())),
        "dia_min":  (dias_es[int(por_dia.idxmin())],  int(por_dia.min())),
        "hora_max": (int(por_hora.idxmax()), int(por_hora.max())),
        "record":   (dias_es[ij[0]], ij[1], int(z[ij]) if z.size else 0),
    }
    return info


def resp_exportar_excel(d: pd.DataFrame, cierres=True):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as xw:
        resp_tabla(d, None, cierres).to_excel(xw, sheet_name="Totales 9 agentes")
        bloques = []
        for etq, real in RESP_AGENTES.items():
            t = resp_tabla(d, real, cierres)
            bloques.append(pd.DataFrame([[""]*t.shape[1]], columns=t.columns, index=[etq]))
            bloques.append(t)
            bloques.append(pd.DataFrame([[""]*t.shape[1]], columns=t.columns, index=[""]))
        pd.concat(bloques).to_excel(xw, sheet_name="Por agente")
    return buf.getvalue()


(t1, t_atc, t2, t3, t4, t5, t6, t7, t8, t9, t_aj, t_esp) = st.tabs([
    "🏠 Resumen Ejecutivo",
    "📋 Resumen ATC (día)",
    "⭐ Calificación",
    "🚨 Cancelaciones & Churn",
    "⚡ Tiempo de Respuesta",
    "📊 Rendimiento Agentes",
    "🏷️ Etiquetas & Motivos",
    "📞 Clientes que más llaman",
    "📋 Explorador de Chats",
    "💡 Insights & Recomendaciones",
    "⚙️ Ajuste de Calificaciones",
    "🎓 Especialistas: Calif. bajas",
])


# ╔═══════════════════════════════════════╗
#  TAB 1 — RESUMEN EJECUTIVO
# ╚═══════════════════════════════════════╝
with t1:
    _fi, _ff, _ags, _colas = filtro_fecha("resumen", con_agente=False)
    _dfr = df_raw[(df_raw["created_at"].dt.date >= _fi) &
                  (df_raw["created_at"].dt.date <= _ff)]

    rdA = resp_preparar(_dfr)
    rgA = rdA[rdA["tag"].fillna("").str.lower().isin(["default", "especialistas", "sdd"])]
    _sem = sorted(rgA["_domingo"].dropna().unique())

    if not _sem:
        st.info("Sin datos ATC en el rango seleccionado.")
    else:
        _serie = []
        for dom in _sem:
            g = rgA[rgA["_domingo"] == dom]; n = len(g)
            _serie.append({
                "Semana": pd.Timestamp(dom), "Chats": n,
                "Rating": round(g["_rating"].mean(), 2) if g["_rating"].notna().any() else np.nan,
                "%Calif": round(g["_rating"].notna().mean() * 100, 1),
                "1aResp": g["_tpr"].mean(),
                "Rating>4": round((g["_rating"] > 4).sum() / n * 100, 1) if n else 0,
                "Duración": g["_dur"].mean(),
            })
        sdf = pd.DataFrame(_serie)
        _lbls = [s.strftime("%d/%m/%Y") for s in sdf["Semana"]]

        st.markdown('<div class="sec">📈 Cierre semanal</div>', unsafe_allow_html=True)
        cS1, cS2 = st.columns([1, 3])
        wk_sel = cS1.selectbox("Semana (cierre domingo)", _lbls, index=len(_lbls) - 1, key="rz_wk")
        _i = _lbls.index(wk_sel); row = sdf.iloc[_i]
        prev = sdf.iloc[_i - 1] if _i > 0 else None

        def _dl(cur, prv, unit=""):
            if prv is None or pd.isna(prv) or pd.isna(cur):
                return ""
            d = cur - prv
            return f"{'▲' if d >= 0 else '▼'} {abs(d):.2f}{unit} vs sem. ant."

        st.markdown('<div class="kpi-grid">' +
            kpi("Chats atendidos", f"{int(row['Chats']):,}",
                _dl(row['Chats'], prev['Chats'] if prev is not None else None), kind="alt") +
            kpi("Rating ATC", f"{row['Rating']:.2f}" if pd.notna(row['Rating']) else "—",
                _dl(row['Rating'], prev['Rating'] if prev is not None else None),
                kind="ok" if pd.notna(row['Rating']) and row['Rating'] >= META_RATING else "amber") +
            kpi("% Calificados", f"{row['%Calif']:.1f}%",
                _dl(row['%Calif'], prev['%Calif'] if prev is not None else None, "pp")) +
            kpi("Primera respuesta", fmt_min(row['1aResp']),
                _dl(row['1aResp'], prev['1aResp'] if prev is not None else None, "min"), kind="dark") +
            kpi("Rating > 4", f"{row['Rating>4']:.1f}%",
                _dl(row['Rating>4'], prev['Rating>4'] if prev is not None else None, "pp"), kind="ok") +
            kpi("Duración prom", fmt_min(row['Duración']), "", kind="amber") +
            '</div>', unsafe_allow_html=True)

        _colbar = [OY_TEAL_DARK if i == _i else OY_TEAL for i in range(len(sdf))]
        g1, g2 = st.columns(2)
        with g1:
            st.markdown("**Chats atendidos por semana**")
            fig = go.Figure(go.Bar(x=_lbls, y=sdf["Chats"], marker_color=_colbar,
                                   text=sdf["Chats"], textposition="outside"))
            st.plotly_chart(sfig(fig, 260), use_container_width=True)
        with g2:
            st.markdown("**Rating ATC por semana**")
            fig = go.Figure(go.Scatter(x=_lbls, y=sdf["Rating"], mode="lines+markers",
                                       line=dict(color=OY_TEAL_DARK, width=3)))
            fig.add_hline(y=META_RATING, line_dash="dash", line_color=OY_OK,
                          annotation_text=f"Meta {META_RATING}")
            st.plotly_chart(sfig(fig, 260), use_container_width=True)
        g3, g4 = st.columns(2)
        with g3:
            st.markdown("**Primera respuesta (min) por semana**")
            fig = go.Figure(go.Scatter(x=_lbls, y=sdf["1aResp"], mode="lines+markers",
                                       line=dict(color=OY_BLUE, width=3), fill="tozeroy",
                                       fillcolor="rgba(59,111,224,.10)"))
            st.plotly_chart(sfig(fig, 240), use_container_width=True)
        with g4:
            st.markdown("**% Calificados por semana**")
            fig = go.Figure(go.Scatter(x=_lbls, y=sdf["%Calif"], mode="lines+markers",
                                       line=dict(color=OY_AMBER, width=3)))
            st.plotly_chart(sfig(fig, 240), use_container_width=True)

        st.divider()

        st.markdown('<div class="sec">📊 Histórico Semanal · Global</div>', unsafe_allow_html=True)
        _PICO = ["Día con más chats (promedio)", "Horas con más chats (promedio)",
                 "Día y hora con más chats (récord)"]

        def _tabla_hist(base, cierres=True):
            cols = {}
            for dom, g in sorted(base.groupby("_domingo"), key=lambda x: x[0]):
                b = resp_bloque(g); b.update(resp_picos(g))
                cols[pd.Timestamp(dom).strftime("%d/%m/%Y")] = b
            if cierres:
                for per, g in sorted(base.groupby("_mes"), key=lambda x: x[0]):
                    b = resp_bloque(g); b.update(resp_picos(g))
                    cols[f"Cierre {RESP_MESES[per.month]} {per.year}"] = b
            return pd.DataFrame(cols).reindex(RESP_FILAS + _PICO)

        _cg = st.toggle("Incluir cierres mensuales", value=True, key="rg_cierres")
        tab_glob = _tabla_hist(rgA, _cg)

        # ── Completar con el DWH: Tiempo interacción + filas de IA (guardado) ──
        try:
            import treble_dwh as _hd
            if _hd.dwh_activo():
                def _sund(monday):   # DWH usa lunes; la tabla usa domingo
                    return (pd.Timestamp(monday) + pd.Timedelta(days=6)).strftime("%d/%m/%Y")

                def _hms(seg):
                    if pd.isna(seg):
                        return ""
                    s = int(seg)
                    return f"{s//3600}:{(s%3600)//60:02d}:{s%60:02d}"

                # Interacción semanal = MEDIANA de agentes ATC (método Treble)
                _iw = _hd.interaccion_oficial_semanal(120)
                _imap = {_sund(r["semana"]): _hms(r["interaccion_seg"]) for _, r in _iw.iterrows()}
                for col in tab_glob.columns:
                    val = _imap.get(col, "")
                    tab_glob.loc["Tiempo medio interacción", col] = val if val else "N/D"
        except Exception:
            pass  # sin DWH, la tabla queda con interacción en blanco (como el CSV)

        st.dataframe(tab_glob, use_container_width=True, height=620)
        st.download_button("⬇️ Descargar Histórico Semanal Global (.csv)",
                           tab_glob.to_csv().encode("utf-8"),
                           "historico_semanal_global.csv", "text/csv", key="rg_csv")

        st.markdown('<div class="sec blue">👥 Agente · Histórico Semanal</div>', unsafe_allow_html=True)
        _pres = set(rgA["agent"].unique())
        for etq, real in RESP_AGENTES.items():
            if real not in _pres:
                continue
            with st.expander(f"👤 {etq}"):
                st.dataframe(resp_tabla(rdA, real, _cg), use_container_width=True)

# ╔═══════════════════════════════════════╗
#  TAB · RESUMEN ATC (día) — EN VIVO desde el Data Warehouse
# ╚═══════════════════════════════════════╝
with t_atc:
    # Metas del reporte diario (editables aquí)
    META_1RESP_S = 60      # 00:01:00
    META_INTER_S = 300     # 00:05:00
    META_RESOL_S = 7200    # 02:00:00

    def _hms(s):
        if s is None or (isinstance(s, float) and pd.isna(s)):
            return "—"
        s = int(round(float(s)))
        return f"{s//3600:02d}:{(s%3600)//60:02d}:{s%60:02d}"

    st.markdown('<div class="sec">📋 Resumen ATC · reporte diario</div>', unsafe_allow_html=True)

    _dwh_ok = False
    try:
        import treble_dwh as _rd
        _dwh_ok = _rd.dwh_activo()
    except Exception:
        _dwh_ok = False

    if not _dwh_ok:
        st.info("Conecta el Data Warehouse en Secrets para ver el reporte diario.")
    else:
        try:
            _u = _rd.ultimo_dia_dwh()
            _hoy = pd.Timestamp(_u).date() if _u else pd.Timestamp.today().date()
        except Exception:
            _hoy = pd.Timestamp.today().date()
        try:
            _eqs = _rd.equipos_disponibles()
        except Exception:
            _eqs = []
        _def = ([e for e in _eqs if str(e).lower() == "default"] or
                [e for e in _eqs if str(e).lower() in ("sdd", "especialistas", "default")] or _eqs)

        cA, cC = st.columns([1, 2])
        _dia = cA.date_input("📅 Día", value=_hoy, key="atc_dia")
        _eq_sel = None
        try:
            _base = _rd.resumen_atc_dia(str(_dia))
        except Exception as _e:
            _base = pd.DataFrame()
            st.markdown(f'<div class="alrt">No se pudo consultar el DWH: {_e}</div>',
                        unsafe_allow_html=True)
        _ags_op = sorted(_base["agente"].dropna().unique()) if not _base.empty else []
        _ag_sel = cC.multiselect("👤 Agente (opcional)", _ags_op, placeholder="Los 8 de ATC",
                                 key="atc_ag")

        if _base.empty:
            st.info("Sin datos de ATC para ese día en el Data Warehouse.")
        else:
            try:
                _iv = _rd.interaccion_dia(str(_dia), _eq_sel)
            except Exception:
                _iv = pd.DataFrame(columns=["agente", "interaccion_seg"])
            m = _base.merge(_iv, on="agente", how="left") if not _iv.empty \
                else _base.assign(interaccion_seg=np.nan)
            if _ag_sel:
                m = m[m["agente"].isin(_ag_sel)]

            w = pd.to_numeric(m["chats"], errors="coerce").fillna(0)
            tot = int(w.sum())

            def _pond(col, peso=None):
                v = pd.to_numeric(m[col], errors="coerce")
                p = w if peso is None else pd.to_numeric(m[peso], errors="coerce").fillna(0)
                ok = v.notna() & (p > 0)
                return float((v[ok] * p[ok]).sum() / p[ok].sum()) if ok.any() else np.nan

            _cal = _pond("calificacion", "calificados")
            _fr, _re = _pond("primera_resp_seg"), _pond("resolucion_seg")
            # Interacción: MEDIANA de los agentes (método de Treble, robusto a outliers)
            _iv_vals = pd.to_numeric(m["interaccion_seg"], errors="coerce").dropna()
            _in = float(_iv_vals.median()) if len(_iv_vals) else np.nan

            # ── Panel de indicadores (estilo Treble, más limpio) ──
            k1, k2, k3 = st.columns([1.15, 1, 1.15])
            with k1:
                st.markdown('<div class="kpi-grid" style="flex-direction:column">' +
                    kpi("Chats atendidos", f"{tot:,}", _dia.strftime("%d/%m/%Y"), kind="alt") +
                    kpi("Primera respuesta", _hms(_fr), f"meta ≤ {_hms(META_1RESP_S)}",
                        kind="ok" if (not pd.isna(_fr) and _fr <= META_1RESP_S) else "warn") +
                    '</div>', unsafe_allow_html=True)
            with k2:
                st.plotly_chart(gauge("Calificación", 0 if pd.isna(_cal) else _cal, META_RATING, [0, 5],
                    [{"range": [0, 4.5], "color": "#FADBD8"},
                     {"range": [4.5, META_RATING], "color": "#FDEBD0"},
                     {"range": [META_RATING, 5], "color": "#D5F5E3"}]), use_container_width=True)
            with k3:
                st.markdown('<div class="kpi-grid" style="flex-direction:column">' +
                    kpi("Tiempo medio interacción", _hms(_in), f"meta ≤ {_hms(META_INTER_S)}",
                        kind="ok" if (not pd.isna(_in) and _in <= META_INTER_S) else "warn") +
                    kpi("Tiempo resolución", _hms(_re), f"meta ≤ {_hms(META_RESOL_S)}",
                        kind="ok" if (not pd.isna(_re) and _re <= META_RESOL_S) else "warn") +
                    '</div>', unsafe_allow_html=True)

            _ok_n = sum([(not pd.isna(_cal) and _cal >= META_RATING),
                         (not pd.isna(_fr) and _fr <= META_1RESP_S),
                         (not pd.isna(_in) and _in <= META_INTER_S),
                         (not pd.isna(_re) and _re <= META_RESOL_S)])
            _cls = "good" if _ok_n == 4 else ("info" if _ok_n >= 3 else "alrt")
            st.markdown(f'<div class="{_cls}">Cumplimiento del día: <b>{_ok_n} de 4 indicadores</b> · '
                        f'{len(m)} agentes · equipos: {", ".join(_eq_sel) if _eq_sel else "todos"}</div>',
                        unsafe_allow_html=True)

            # ── Detalle por agente ──
            st.markdown("##### Detalle por agente")
            tabla = pd.DataFrame({
                "Agente": m["agente"],
                "Chats Atendidos": pd.to_numeric(m["chats"], errors="coerce").astype("Int64"),
                "Calificación": pd.to_numeric(m["calificacion"], errors="coerce").round(2),
                "Primera respuesta": m["primera_resp_seg"].apply(_hms),
                "Tiempo medio interacción": m["interaccion_seg"].apply(_hms),
                "Tiempo resolución": m["resolucion_seg"].apply(_hms),
            }).sort_values("Chats Atendidos", ascending=False)
            st.dataframe(tabla, use_container_width=True, hide_index=True,
                         height=min(520, 60 + 36 * len(tabla)))
            st.download_button("⬇️ Descargar reporte del día (.csv)",
                               tabla.to_csv(index=False).encode("utf-8"),
                               f"resumen_atc_{_dia}.csv", "text/csv", key="atc_csv")

            # ── MENSAJE PARA SLACK (completo, listo para copiar) ──
            _MESES = {1:"enero",2:"febrero",3:"marzo",4:"abril",5:"mayo",6:"junio",7:"julio",
                      8:"agosto",9:"septiembre",10:"octubre",11:"noviembre",12:"diciembre"}

            def _corto(s):
                """MM:SS si es menos de una hora; si no, H:MM:SS."""
                if s is None or (isinstance(s, float) and pd.isna(s)):
                    return "—"
                s = int(round(float(s)))
                return f"{s//60:02d}:{s%60:02d}" if s < 3600 else f"{s//3600}:{(s%3600)//60:02d}:{s%60:02d}"

            def _num(x, dec=2):
                return "—" if pd.isna(x) else f"{x:.{dec}f}".replace(".", ",")

            _ok_cal = (not pd.isna(_cal)) and _cal >= META_RATING
            _ok_fr  = (not pd.isna(_fr))  and _fr <= META_1RESP_S
            _ok_in  = (not pd.isna(_in))  and _in <= META_INTER_S
            _ok_re  = (not pd.isna(_re))  and _re <= META_RESOL_S
            _c = lambda ok: "✅" if ok else "❌"

            _fallidos = [n for n, ok in [("la calificación", _ok_cal),
                                         ("la primera respuesta", _ok_fr),
                                         ("el tiempo de interacción", _ok_in),
                                         ("el tiempo de resolución", _ok_re)] if not ok]
            _acciones = {
                "la calificación": "brindar una experiencia excepcional en cada conversación: "
                                   "validar al cliente, leer el contexto completo y acompañarlo "
                                   "hasta el cierre de su solicitud",
                "la primera respuesta": "tomar los chats apenas se asignan para responder dentro "
                                        "del primer minuto",
                "el tiempo de interacción": "agilizar las respuestas dentro del chat sin afectar "
                                            "la calidad de la atención",
                "el tiempo de resolución": "cerrar los casos el mismo día y hacer seguimiento a "
                                           "los que quedan abiertos",
            }
            if not _fallidos:
                _narr = ("¡Cumplimos los 4 indicadores! Mantengamos este nivel: constancia en la "
                         "calidad y en los tiempos de atención.")
            elif len(_fallidos) == 1:
                _f = _fallidos[0]
                _narr = (f"El único indicador fuera de meta fue *{_f.replace('la ', '').replace('el ', '')}*, "
                         f"por lo que hoy nuestro principal foco debe ser {_acciones[_f]}.")
            else:
                _narr = ("Los indicadores fuera de meta fueron " +
                         ", ".join(_fallidos[:-1]) + f" y {_fallidos[-1]}. "
                         f"Hoy nuestro foco será {_acciones[_fallidos[0]]}.")

            _txt = (
                f"📊 *Resultados ATC | {_dia.day} de {_MESES[_dia.month]}*\n"
                f"Buen día, equipo. 💙\n\n"
                f"Ayer atendimos *{tot:,} conversaciones* y estos fueron los resultados:\n"
                f"⭐ Calificación: {_num(_cal)} {_c(_ok_cal)}\n"
                f"💬 Chats atendidos: {tot:,}\n"
                f"🕐 Primera respuesta: {_corto(_fr)} {_c(_ok_fr)}\n"
                f"💭 Tiempo medio de interacción: {_corto(_in)} {_c(_ok_in)}\n"
                f"⌛ Tiempo de resolución: {_hms(_re)} {_c(_ok_re)}\n\n"
                f"Cumplimos *{_ok_n} de los 4 indicadores*. {_narr}"
            )

            # Focos individuales
            _focos = []
            for _, r in m.sort_values("chats", ascending=False).iterrows():
                _rr = pd.to_numeric(r.get("calificacion"), errors="coerce")
                _rf = pd.to_numeric(r.get("primera_resp_seg"), errors="coerce")
                _ri = pd.to_numeric(r.get("interaccion_seg"), errors="coerce")
                _rs = pd.to_numeric(r.get("resolucion_seg"), errors="coerce")
                _mal = []
                if pd.isna(_rr) or _rr < META_RATING:
                    _mal.append(f"el rating ({_num(_rr)})" if not pd.isna(_rr) else "registrar calificaciones")
                if not pd.isna(_rf) and _rf > META_1RESP_S:
                    _mal.append(f"la primera respuesta ({_corto(_rf)})")
                if not pd.isna(_ri) and _ri > META_INTER_S:
                    _mal.append(f"la interacción ({_corto(_ri)})")
                if not pd.isna(_rs) and _rs > META_RESOL_S:
                    _mal.append(f"la resolución ({_hms(_rs)})")
                if not _mal:
                    _extra = " y mantuviste un rating de 5" if (not pd.isna(_rr) and _rr >= 5) else ""
                    _focos.append(f"• *{r['agente']}*: ¡Excelente trabajo! Cumpliste todos "
                                  f"los indicadores{_extra}.")
                else:
                    _bien = []
                    if not pd.isna(_rr) and _rr >= META_RATING:
                        _bien.append(f"excelente calidad ({_num(_rr)})")
                    if not pd.isna(_rs) and _rs <= META_RESOL_S:
                        _bien.append("buena resolución")
                    _pre = (", ".join(_bien).capitalize() + ". ") if _bien else ""
                    _focos.append(f"• *{r['agente']}*: {_pre}El foco está en mejorar "
                                  + ", ".join(_mal) + ".")
            _txt_focos = "*Focos individuales*\n" + "\n".join(_focos)
            _obj = ("🎯 *Objetivo para hoy:* mantener los indicadores en meta y sostener la "
                    "calidad de la atención." if not _fallidos else
                    f"🎯 *Objetivo para hoy:* recuperar {_fallidos[0]} y sostener los indicadores "
                    f"que ya estamos cumpliendo.")

            st.markdown('<div class="sec ok">📨 Mensaje para Slack</div>', unsafe_allow_html=True)
            cS1, cS2 = st.columns([1, 1])
            _inc_focos = cS1.toggle("Incluir focos individuales", value=True, key="atc_focos")
            _inc_obj = cS2.toggle("Incluir objetivo del día", value=True, key="atc_obj")
            _final = _txt + (("\n\n" + _txt_focos) if _inc_focos else "") + \
                     (("\n\n" + _obj) if _inc_obj else "")
            st.code(_final, language=None)
            st.download_button("⬇️ Descargar mensaje (.txt)", _final.encode("utf-8"),
                               f"reporte_atc_{_dia}.txt", "text/plain", key="atc_txt")


# ╔═══════════════════════════════════════╗
#  TAB 2 — CALIFICACIÓN
# ╚═══════════════════════════════════════╝
with t2:
    _fi, _ff, _ags, _colas = filtro_fecha("cal")
    globals().update(_ctx(_fi, _ff, _ags, _colas))
    st.markdown('<div class="sec">⭐ Calificación & Satisfacción</div>', unsafe_allow_html=True)
    if pct_cal < META_CAL:
        st.markdown(f'<div class="alrt">⚠️ Solo <b>{pct_cal}%</b> de chats calificaron '
                    f'({n_cal:,}/{N:,}). El insatisfecho abandona sin calificar: '
                    f'el 4.8 sobreestima la satisfacción real.</div>', unsafe_allow_html=True)

    st.markdown('<div class="kpi-grid">' +
        kpi("Rating promedio", f"{rating:.2f}", f"meta ≥{META_RATING}",
            kind="ok" if rating >= META_RATING else "warn") +
        kpi("CSAT (≥4 ★)", f"{csat}%", kind="ok") +
        kpi("Detractores (≤3★)", f"{det}%", f"{int((df['rating_num']<=3).sum()):,} chats",
            kind="warn" if det > 5 else "amber") +
        kpi("Promotores (5★)", f"{prom5}%", kind="ok") +
        kpi("Cobertura encuesta", f"{pct_cal}%", f"meta ≥{META_CAL}%",
            kind="ok" if pct_cal >= META_CAL else "amber") +
        '</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        # Distribución 1–5
        dist = {i: int((df["rating_num"]==i).sum()) for i in [1,2,3,4,5]}
        ddf = pd.DataFrame({"Estrella":[f"{i}★" for i in [1,2,3,4,5]],
                             "Chats":list(dist.values())})
        ddf["%"] = (ddf["Chats"]/n_cal*100).round(1) if n_cal else 0
        colors = [OY_WARN,"#FF7043",OY_AMBER,OY_TEAL,OY_OK]
        fig = go.Figure()
        for i,row in ddf.iterrows():
            fig.add_trace(go.Bar(x=[row["Chats"]], y=[row["Estrella"]],
                                  orientation="h", marker_color=colors[i],
                                  text=f'{row["Chats"]:,} ({row["%"]:.1f}%)',
                                  textposition="outside", name=row["Estrella"]))
        fig.update_layout(showlegend=False, title="Distribución de calificaciones",
                          barmode="stack", yaxis={"categoryorder":"array",
                          "categoryarray":["1★","2★","3★","4★","5★"]})
        st.plotly_chart(sfig(fig, 320), use_container_width=True)
    with c2:
        # Rating por agente
        ag_r = ag_churn[ag_churn["Rating"].notna()].sort_values("Rating")
        cols_bar = [OY_OK if r >= META_RATING else OY_AMBER if r >= 4.5 else OY_WARN
                    for r in ag_r["Rating"]]
        fig = px.bar(ag_r, x="Rating", y="Agente", orientation="h",
                     color="Rating", color_continuous_scale="RdYlGn",
                     range_color=[3.5,5], text="Rating",
                     title="Rating promedio por agente")
        fig.add_vline(x=META_RATING, line_dash="dash", line_color=OY_TEAL)
        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig.update_layout(showlegend=False, yaxis={"categoryorder":"total ascending"})
        st.plotly_chart(sfig(fig, 380), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        # Evolución rating
        evo = df.groupby(gc)["rating_num"].mean().reset_index()
        evo.columns = ["periodo","rating"]
        evo["periodo"] = pd.to_datetime(evo["periodo"].astype(str))
        fig = px.line(evo, x="periodo", y="rating", markers=True,
                      color_discrete_sequence=[OY_TEAL], title="Evolución del rating")
        fig.add_hline(y=META_RATING, line_dash="dash", line_color=OY_OK,
                      annotation_text=f"Meta {META_RATING}")
        fig.update_yaxes(range=[4.3, 5.1])
        st.plotly_chart(sfig(fig, 300), use_container_width=True)
    with c4:
        # Rating por hora
        hr = df.groupby("hora")["rating_num"].agg(["mean","count"]).reset_index()
        hr.columns = ["hora","rating","n"]
        hr = hr[hr["n"] >= 20]
        fig = px.bar(hr, x="hora", y="rating", color="rating",
                     color_continuous_scale="RdYlGn", range_color=[4.4,5.0],
                     title="Rating promedio por hora del día")
        fig.add_hline(y=META_RATING, line_dash="dash", line_color=OY_TEAL)
        fig.update_xaxes(tickmode="linear", tick0=0, dtick=1)
        st.plotly_chart(sfig(fig, 300), use_container_width=True)

    # Rating por motivo
    exp = df.copy()
    exp["label"] = exp["labels"].fillna("Sin etiqueta").str.split(r",\s*")
    exp = exp.explode("label"); exp["label"] = exp["label"].str.strip()
    rlbl = exp[exp["calificado"]].groupby("label")["rating_num"].agg(["mean","count"])
    rlbl = rlbl[rlbl["count"] >= 5].sort_values("mean").reset_index()
    rlbl.columns = ["Motivo","Rating","n"]
    fig = px.bar(rlbl, x="Rating", y="Motivo", orientation="h", color="Rating",
                 color_continuous_scale="RdYlGn", range_color=[1,5],
                 text="Rating", title="Rating promedio por motivo de contacto (min. 5 cal.)")
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig.update_layout(showlegend=False, yaxis={"categoryorder":"total ascending"})
    st.plotly_chart(sfig(fig, max(400, len(rlbl)*22)), use_container_width=True)

    # Rating por cola
    if "tag" in df.columns:
        rt = df[df["calificado"]].groupby("tag")["rating_num"].agg(["mean","count"]).reset_index()
        rt = rt[rt["count"] >= 5].sort_values("mean")
        fig = px.bar(rt, x="mean", y="tag", orientation="h", color="mean",
                     color_continuous_scale="RdYlGn", range_color=[4,5],
                     text="mean", title="Rating por cola/equipo")
        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        st.plotly_chart(sfig(fig, 280), use_container_width=True)


# ╔═══════════════════════════════════════╗
#  TAB 3 — CANCELACIONES & CHURN
# ╚═══════════════════════════════════════╝
with t3:
    _fi, _ff, _ags, _colas = filtro_fecha("canc")
    globals().update(_ctx(_fi, _ff, _ags, _colas))
    n_churn        = int(df["es_churn"].sum())
    n_cancel_sesion= int(df["es_cancel_sesion"].sum())
    n_postergacion = int(df["es_postergacion"].sum())
    n_reprog       = int(df["es_reprog"].sum())
    n_canc         = int(df["es_cancel"].sum())
    pct_cancel_ses = safe_pct(n_cancel_sesion, N)
    pct_posterg    = safe_pct(n_postergacion, N)

    # ── BLOQUE A: CHURN DE PLAN ──────────────────────────────
    st.markdown('<div class="sec red">🔴 BLOQUE A — Churn de Plan (pérdida de suscripción)</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="crit">Etiquetas contadas: <b>"Cancelar plan"</b> + <b>"Reembolso"</b><br>'
        'El cliente cancela su <b>suscripción completa</b>. '
        'Es pérdida directa de ingresos recurrentes. '
        '<b>No confundir con cancelación de sesión</b> — eso está en el Bloque B.</div>',
        unsafe_allow_html=True)
    st.markdown('<div class="kpi-grid">' +
        kpi("Churn de plan", f"{n_churn:,}",
            f"{pct_churn}% del total de chats", kind="warn") +
        kpi("  Cancelar plan",
            f'{int(df["labels"].fillna("").str.contains("Cancelar plan",case=False).sum()):,}',
            "cancelan suscripción", kind="warn") +
        kpi("  Reembolsos",
            f'{int(df["labels"].fillna("").str.contains("Reembolso",case=False).sum()):,}',
            "solicitud de devolución", kind="warn") +
        kpi("Meta churn", f"≤{META_CHURN}%",
            "🔴 SUPERADA" if pct_churn > META_CHURN else "✅ OK",
            kind="warn" if pct_churn > META_CHURN else "ok") +
        '</div>', unsafe_allow_html=True)
    st.plotly_chart(gauge("💸 Churn de Plan", pct_churn, META_CHURN, [0,30],
        [{"range":[0,META_CHURN],"color":"#D5F5E3"},{"range":[META_CHURN,18],"color":"#FDEBD0"},
         {"range":[18,30],"color":"#FADBD8"}],"%",True), use_container_width=False)

    # ── BLOQUE B: CANCELACIÓN DE SESIÓN ──────────────────────
    st.markdown('<div class="sec amb">🟠 BLOQUE B — Cancelación de Sesión (no cancela el plan)</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="alrt">Etiquetas contadas: <b>"Cancelación +24hrs"</b> · '
        '<b>"Cancelación tardía"</b> · <b>"Esp. cancela sesión"</b><br>'
        'El cliente cancela una <b>sesión puntual</b> pero <b>mantiene su suscripción</b>. '
        'Es un problema operativo (reagenda, inasistencia), no de retención de ingresos.</div>',
        unsafe_allow_html=True)
    sub_cancel = {
        "Cancelación +24hrs":   r"Cancelaci[oó]n \+24",
        "Cancelación tardía":   r"Cancelaci[oó]n tard",
        "Esp. cancela sesión":  r"Esp\. cancela",
    }
    sub_rows_b = [{"Sub-motivo": k,
                   "Chats": int(df["labels"].fillna("").str.contains(v, case=False, regex=True).sum())}
                  for k, v in sub_cancel.items()]
    sub_df_b = pd.DataFrame(sub_rows_b).sort_values("Chats", ascending=False)
    sub_df_b["%"] = (sub_df_b["Chats"]/N*100).round(1)

    st.markdown('<div class="kpi-grid">' +
        kpi("Cancelaciones de sesión", f"{n_cancel_sesion:,}",
            f"{pct_cancel_ses}% del total", kind="amber") +
        kpi("Sub-motivo #1", sub_df_b.iloc[0]["Sub-motivo"] if len(sub_df_b) else "–",
            f'{sub_df_b.iloc[0]["Chats"]:,} chats' if len(sub_df_b) else "", kind="amber") +
        '</div>', unsafe_allow_html=True)

    cb1, cb2 = st.columns(2)
    with cb1:
        fig = px.bar(sub_df_b, x="Chats", y="Sub-motivo", orientation="h",
                     color="Chats",
                     color_continuous_scale=[[0,"#FFF0E0"],[1,OY_AMBER]],
                     text="Chats", title="Composición: cancelaciones de sesión")
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False, yaxis={"categoryorder":"total ascending"})
        st.plotly_chart(sfig(fig, 240), use_container_width=True)
    with cb2:
        st.dataframe(sub_df_b, use_container_width=True, hide_index=True)

    # ── BLOQUE C: POSTERGACIÓN DE FECHA (pago/plan) ──────────
    st.markdown('<div class="sec dark">🔵 BLOQUE C — Postergación de Fecha (pago o plan)</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="info">Etiqueta contada: <b>"Postergación de fecha"</b><br>'
        'El cliente solicita postergar la <b>fecha de cobro o vencimiento de su plan</b>. '
        'Es un tema administrativo/financiero — diferente a cancelar sesión y diferente a cancelar el plan.</div>',
        unsafe_allow_html=True)
    st.markdown('<div class="kpi-grid">' +
        kpi("Postergaciones de fecha", f"{n_postergacion:,}",
            f"{pct_posterg}% del total de chats", kind="dark") +
        '</div>', unsafe_allow_html=True)

    # ── BLOQUE D: VISIÓN CONSOLIDADA ─────────────────────────
    st.markdown('<div class="sec blue">📊 BLOQUE D — Visión Consolidada</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="kpi-grid">' +
        kpi("Total (todos los tipos)", f"{n_canc:,}", f"{safe_pct(n_canc,N)}% del total", kind="alt") +
        kpi("Churn de plan", f"{pct_churn}%", "pérdida de suscripción", kind="warn") +
        kpi("Cancelación de sesión", f"{pct_cancel_ses}%", "mantiene el plan", kind="amber") +
        kpi("Postergación de fecha", f"{pct_posterg}%", "tema administrativo", kind="dark") +
        '</div>', unsafe_allow_html=True)

    # Tendencia mensual — solo churn vs cancelación de sesión (postergación va aparte)
    evo = df.groupby(gc).agg(
        churn=("es_churn","sum"),
        cancel_ses=("es_cancel_sesion","sum"),
        posterg=("es_postergacion","sum"),
        n=("phone","size")).reset_index()
    evo["% Churn plan"]     = (evo["churn"]/evo["n"]*100).round(1)
    evo["% Cancel. sesión"] = (evo["cancel_ses"]/evo["n"]*100).round(1)
    evo["% Postergación"]   = (evo["posterg"]/evo["n"]*100).round(1)
    evo[gc] = pd.to_datetime(evo[gc].astype(str))
    fig = px.line(evo, x=gc,
                  y=["% Churn plan","% Cancel. sesión","% Postergación"],
                  markers=True,
                  color_discrete_map={"% Churn plan":OY_WARN,
                                      "% Cancel. sesión":OY_AMBER,
                                      "% Postergación":OY_BLUE},
                  title="Tendencia: Churn vs Cancelación de Sesión vs Postergación")
    fig.add_hline(y=META_CHURN, line_dash="dash", line_color=OY_OK,
                  annotation_text=f"Meta churn {META_CHURN}%")
    st.plotly_chart(sfig(fig, 320), use_container_width=True)

    cd1, cd2 = st.columns(2)
    with cd1:
        # Obs 8: Agentes de retención — cambiar texto, no es problema de routing
        st.subheader("👥 Agentes del equipo de retención")
        ag_c = ag_churn[["Agente","Chats","% Churn"]].sort_values("% Churn",ascending=False).head(10)
        ag_c["Rol"] = ag_c["% Churn"].apply(
            lambda x: "🎯 Equipo Retención" if x > 40 else "📞 Soporte General")
        st.dataframe(ag_c, use_container_width=True, hide_index=True)
        st.markdown(
            '<div class="info">💡 Los agentes con alto % de churn en cartera son el '
            '<b>equipo de retención</b> — reciben chats de "Cancelar plan" de forma deliberada. '
            'No es un error de routing; es una asignación intencional. '
            'Sugerencia: documentar formalmente el rol y medir con KPIs de retención '
            '(% de clientes retenidos, no % de churn).</div>', unsafe_allow_html=True)
    with cd2:
        # Obs 4: Tabla solo con churn real (sin +24hrs)
        st.subheader("🔁 Clientes con churn de plan repetido")
        canc_cli = []
        # Obs 4: filtrar solo es_churn (no es_cancel que incluye +24hrs)
        for ph, g in df[df["es_churn"]].groupby("phone"):
            canc_cli.append({
                "Teléfono":    ph,
                "Cancelaciones": len(g),
                "Cliente":     safe_mode(g["contact"]) if "contact" in g.columns else "–",
                "Motivo":      motivo_ppal(g["labels"]),
            })
        if canc_cli:
            cc_df = pd.DataFrame(canc_cli).sort_values("Cancelaciones",ascending=False).head(15)
            # Obs 5: link a explorador de chats
            st.dataframe(cc_df, use_container_width=True, hide_index=True, height=300)
            st.download_button("⬇️ CSV churn de plan",
                               cc_df.to_csv(index=False).encode(),
                               "churn_plan.csv","text/csv")


# ╔═══════════════════════════════════════╗
#  TAB 4 — TIEMPO DE RESPUESTA
# ╚═══════════════════════════════════════╝
with t4:
    _fi, _ff, _ags, _colas = filtro_fecha("tpr")
    globals().update(_ctx(_fi, _ff, _ags, _colas))
    st.markdown('<div class="sec">⚡ Tiempo de Respuesta & SLA</div>', unsafe_allow_html=True)
    st.markdown('<div class="kpi-grid">' +
        kpi("TPR promedio", fmt_min(tpr_prom), f"como Treble", kind="alt") +
        kpi("TPR mediana", fmt_min(tpr_med), "robusto a outliers", kind="") +
        kpi("TPR p90", fmt_min(tpr_p90), "9 de 10 ≤ este valor") +
        kpi("% SLA ≤2 min", f"{pct_sla2}%", kind="ok" if pct_sla2 >= META_SLA2 else "warn") +
        kpi("% SLA ≤5 min", f"{pct_sla5}%", kind="ok" if pct_sla5 >= 90 else "amber") +
        kpi(">30 min", f"{pct_over30}%", kind="warn" if pct_over30 > 5 else "amber") +
        '</div>', unsafe_allow_html=True)

    # Rangos SLA tipo Treble
    buckets = [("≤2 min",df["sla_2min"].sum()),
               ("≤5 min",(df["tpr_min"].between(2,5)).sum()),
               ("≤15 min",(df["tpr_min"].between(5,15)).sum()),
               ("≤30 min",(df["tpr_min"].between(15,30)).sum()),
               (">30 min",(df["tpr_min"]>30).sum())]
    bdf = pd.DataFrame(buckets, columns=["Rango","Chats"])
    bdf["%"] = (bdf["Chats"]/len(tpr_v)*100).round(1) if len(tpr_v) else 0
    c1, c2 = st.columns([1,1.5])
    with c1:
        st.dataframe(bdf, use_container_width=True, hide_index=True)
    with c2:
        cols_sla = [OY_OK,"#7BC96F",OY_AMBER,"#E8842E",OY_WARN]
        fig = go.Figure()
        for i,(r,n,p) in enumerate(zip(bdf["Rango"],bdf["Chats"],bdf["%"])):
            fig.add_trace(go.Bar(x=[n],y=[r],orientation="h",
                                  marker_color=cols_sla[i],
                                  text=f"{n:,} ({p:.1f}%)",textposition="outside",name=r))
        fig.update_layout(showlegend=False,title="Distribución SLA de Primera Respuesta",
                          yaxis={"categoryorder":"array","categoryarray":[b[0] for b in buckets[::-1]]})
        st.plotly_chart(sfig(fig,280), use_container_width=True)

    # KPI INVISIBLE #1 — Lag de asignación
    st.markdown('<div class="invis">🔮 <b>KPI INVISIBLE #1 — Lag de Asignación</b><br>'
                f'El 7.9% de los chats esperó >30 min <b>antes de ser asignado</b> a un agente. '
                f'El TPR del agente empieza a correr desde la asignación — '
                f'pero el cliente ya lleva media hora esperando sin que nadie lo vea. '
                f'Promedio lag: {fmt_min(lag_prom)} · 90.1% se asigna en &lt;1 min.</div>',
                unsafe_allow_html=True)

    lag_buckets = [("< 1 min",   int((lag_v<1).sum())),
                   ("1–5 min",   int(lag_v.between(1,5).sum())),
                   ("5–30 min",  int(lag_v.between(5,30).sum())),
                   ("> 30 min",  int((lag_v>30).sum()))]
    ldf = pd.DataFrame(lag_buckets, columns=["Rango","Chats"])
    ldf["%"] = (ldf["Chats"]/len(lag_v)*100).round(1) if len(lag_v) else 0
    # Colores fijos: verde = rápido (bueno), rojo = lento (malo)
    lag_colors = [OY_OK, "#7BC96F", OY_AMBER, OY_WARN]
    fig = go.Figure()
    for i, (r, n, p) in enumerate(zip(ldf["Rango"], ldf["Chats"], ldf["%"])):
        fig.add_trace(go.Bar(
            x=[n], y=[r], orientation="h",
            marker_color=lag_colors[i],
            text=f"{n:,} ({p:.1f}%)", textposition="outside",
            name=r, showlegend=False))
    fig.update_layout(
        title="Lag de Asignación (creación → asignación a agente) — Verde = rápido ✅",
        yaxis={"categoryorder":"array",
               "categoryarray":["< 1 min","1–5 min","5–30 min","> 30 min"]})
    st.plotly_chart(sfig(fig, 240), use_container_width=True)

    # KPI INVISIBLE #2 — Chats fantasma
    st.markdown(f'<div class="invis">🔮 <b>KPI INVISIBLE #2 — Chats Fantasma</b><br>'
                f'{n_ghost:,} chats ({pct_ghost}%) fueron cerrados con el <b>último mensaje '
                f'del CLIENTE</b>. El cliente preguntó o escribió algo y el agente no respondió '
                f'antes del cierre. Daño de imagen silencioso. Meta &lt;{META_GHOST}%.</div>',
                unsafe_allow_html=True)

    c3, c4 = st.columns(2)
    with c3:
        # TPR por agente — columna correcta: "TPR val (min)"
        ag_tpr = ag_churn[ag_churn["TPR val (min)"].notna()].sort_values("TPR val (min)")
        fig = px.bar(ag_tpr, x="TPR val (min)", y="Agente", orientation="h",
                     color="TPR val (min)",
                     color_continuous_scale="RdYlGn_r",
                     title="TPR promedio por agente (min)",
                     labels={"TPR val (min)":"min"})
        fig.add_vline(x=META_TPR, line_dash="dash", line_color=OY_TEAL)
        fig.update_layout(showlegend=False, yaxis={"categoryorder":"total descending"})
        st.plotly_chart(sfig(fig,420), use_container_width=True)
    with c4:
        # Correlación TPR vs Rating
        if len(tpr_v) > 100:
            st.subheader("TPR vs Rating — ¿Hay correlación?")
            df_cal2 = df[df["calificado"] & df["tpr_min"].notna()].copy()
            df_cal2["tpr_bucket"] = pd.cut(df_cal2["tpr_min"],
                bins=[0,1,2,5,10,30,9999],labels=["0–1min","1–2min","2–5min","5–10min","10–30min",">30min"])
            cr = df_cal2.groupby("tpr_bucket",observed=True)["rating_num"].agg(["mean","count"]).reset_index()
            cr.columns = ["Bucket TPR","Rating prom","n"]
            fig = px.bar(cr, x="Bucket TPR", y="Rating prom",
                         color="Rating prom", color_continuous_scale="RdYlGn",
                         range_color=[4.5,5.0], text="Rating prom",
                         title="Rating promedio por tiempo de respuesta")
            fig.update_traces(texttemplate="%{text:.3f}", textposition="outside")
            fig.add_hline(y=META_RATING, line_dash="dash", line_color=OY_TEAL)
            st.plotly_chart(sfig(fig,380), use_container_width=True)

# ╔═══════════════════════════════════════╗
#  TAB 5 — RENDIMIENTO AGENTES
# ╚═══════════════════════════════════════╝
with t5:
    _fi, _ff, _ags, _colas = filtro_fecha("rend")
    globals().update(_ctx(_fi, _ff, _ags, _colas))
    st.markdown('<div class="sec">📊 Rendimiento de Agentes</div>', unsafe_allow_html=True)
    st.markdown('<div class="kpi-grid">' +
        kpi("Chats atendidos", f"{N:,}", kind="alt") +
        kpi("Rating equipo", f"{rating:.2f}", kind="ok" if rating >= META_RATING else "amber") +
        kpi("TPR promedio", fmt_min(tpr_prom)) +
        kpi("% Calificados", f"{pct_cal}%", kind="amber") +
        kpi("Handle time real", fmt_min(hnd_med), "mediana activo", kind="dark") +
        '</div>', unsafe_allow_html=True)

    ag = build_agent_kpis(df)
    cols_show = ["Agente","Chats","% Total","TPR prom (min)","Handle (min)",
                 "Rating","% Calificados","% Churn","Cola","Nivel"]

    def color_nivel(v):
        if v == "⭐ Top": return f"color:{OY_OK};font-weight:700"
        if v == "⚠️ Atención": return f"color:{OY_WARN};font-weight:700"
        return ""

    sty = (ag[cols_show].style
           .map(color_nivel, subset=["Nivel"])
           .map(lambda v: f"color:{OY_WARN};font-weight:700"
                if isinstance(v,(int,float)) and not np.isnan(v) and v > META_CHURN*0.8 else "",
                subset=["% Churn"])
           .format({"Rating":"{:.2f}","% Total":"{:.1f}","% Calificados":"{:.1f}",
                    "% Churn":"{:.1f}","TPR prom (min)":"{:.2f}","Handle (min)":"{:.1f}"}))
    st.dataframe(sty, use_container_width=True, hide_index=True, height=480)

    st.markdown("""
    **Leyenda de Nivel:**
    ⭐ **Top** = Rating ≥4.85 Y TPR ≤2 min  ·  
    ✅ **Bueno** = Indicadores en rango aceptable  ·  
    ⚠️ **Atención** = Rating <4.5 O TPR >10 min O %Churn >40%
    """)

    st.markdown(
        '<div class="invis">🔮 <b>KPI INVISIBLE #3 — Equipo de Retención</b><br>'
        'Algunos agentes tienen >70% de sus chats con etiqueta "Cancelar plan". '
        'Esto <b>no es un error de routing</b> — es una asignación deliberada. '
        'Esos agentes forman el <b>equipo de retención</b> de Opción Yo. '
        'Sugerencia: medir su éxito con KPIs de retención '
        '(% de clientes que NO cancelaron tras el chat), no con métricas de soporte general.</div>',
        unsafe_allow_html=True)

    st.download_button("⬇️ CSV ranking agentes", ag.to_csv(index=False).encode(),
                       "agentes.csv","text/csv")

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(ag.sort_values("Chats",ascending=False).head(15),
                     x="Chats", y="Agente", orientation="h",
                     color="Rating", color_continuous_scale="RdYlGn",
                     range_color=[3.5,5], title="Top agentes por volumen (color=rating)")
        fig.update_layout(yaxis={"categoryorder":"total ascending"})
        st.plotly_chart(sfig(fig,420), use_container_width=True)
    with c2:
        # Heatmap agente × semana
        top15 = df["agent"].value_counts().head(15).index
        dsd = df[df["agent"].isin(top15)].copy()
        pw = (dsd.groupby(["agent","semana"],observed=True).size()
              .reset_index(name="Chats")
              .pivot(index="agent",columns="semana",values="Chats").fillna(0))
        pw.columns = [str(c) for c in pw.columns]
        fig = px.imshow(pw, aspect="auto", color_continuous_scale="Teal",
                        labels=dict(x="Semana",y="",color="Chats"),
                        title="Chats por agente × semana")
        st.plotly_chart(sfig(fig,420), use_container_width=True)


# ╔═══════════════════════════════════════╗
#  TAB 6 — ETIQUETAS & MOTIVOS
# ╚═══════════════════════════════════════╝
with t6:
    _fi, _ff, _ags, _colas = filtro_fecha("etiq")
    globals().update(_ctx(_fi, _ff, _ags, _colas))
    st.markdown('<div class="sec">🏷️ Etiquetas & Motivos de Contacto</div>', unsafe_allow_html=True)

    if pct_sin_lbl > 10:
        st.markdown(f'<div class="alrt">⚠️ <b>{int(df["sin_label"].sum()):,} chats sin etiqueta '
                    f'({pct_sin_lbl}%)</b> — punto ciego operativo. '
                    f'Sin label no se puede analizar la causa raíz correctamente.</div>',
                    unsafe_allow_html=True)

    exp = df.copy()
    exp["label"] = exp["labels"].fillna("Sin etiqueta").str.split(r",\s*")
    exp = exp.explode("label"); exp["label"] = exp["label"].str.strip()
    top20 = exp["label"].value_counts().head(20).reset_index()
    top20.columns = ["Motivo","Chats"]
    top20["%"] = (top20["Chats"]/N*100).round(1)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(top20, x="Chats", y="Motivo", orientation="h", color="Chats",
                     color_continuous_scale="Teal", title="Top 20 motivos de contacto")
        fig.update_layout(showlegend=False, yaxis={"categoryorder":"total ascending"})
        st.plotly_chart(sfig(fig,520), use_container_width=True)
    with c2:
        fig = px.pie(top20.head(12), names="Motivo", values="Chats",
                     color_discrete_sequence=COLOR_SEQ, hole=.35,
                     title="Proporción top 12 motivos")
        st.plotly_chart(sfig(fig,520), use_container_width=True)

    # KPI INVISIBLE #4 — Transferencias
    st.markdown(f'<div class="invis">🔮 <b>KPI INVISIBLE #4 — Costo de las Transferencias</b><br>'
                f'{int(df["transferido"].sum()):,} chats fueron transferidos ({pct_transf}%). '
                f'El rating CON transferencia es <b>4.54</b> vs <b>4.79</b> sin transferencia. '
                f'Cada transferencia cuesta <b>0.25 puntos de satisfacción</b>. '
                f'El cliente tiene que explicar su problema dos veces.</div>',
                unsafe_allow_html=True)

    # KPI INVISIBLE #5 — Reintentos (sin jerga)
    st.markdown(
        f'<div class="invis">🔮 <b>KPI INVISIBLE #5 — Clientes que vuelven a escribir el mismo día</b><br>'
        f'<b>{n_reint:,} casos</b> donde el mismo cliente contactó más de una vez en el mismo día. '
        f'Esto sugiere que su problema <b>no quedó resuelto</b> en el primer chat — tuvo que volver a escribir. '
        f'El <b>{safe_pct(len(contactos)-n_reint, len(contactos))}%</b> de los clientes '
        f'resolvió en un solo contacto diario. '
        f'<i>(En la industria esto se mide como FCR — First Contact Resolution, '
        f'o "Resolución en el Primer Contacto")</i></div>',
        unsafe_allow_html=True)

    # Rating por etiqueta
    rlbl2 = exp[exp["calificado"]].groupby("label")["rating_num"].agg(["mean","count"]).reset_index()
    rlbl2 = rlbl2[rlbl2["count"] >= 5].sort_values("mean")
    fig = px.bar(rlbl2, x="mean", y="label", orientation="h", color="mean",
                 color_continuous_scale="RdYlGn", range_color=[1,5],
                 text="mean", title="Rating promedio por etiqueta")
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig.update_layout(showlegend=False, yaxis={"categoryorder":"total ascending"})
    st.plotly_chart(sfig(fig, max(380, len(rlbl2)*18)), use_container_width=True)

    # Tabla completa
    tab_lbl = exp.groupby("label").agg(
        Chats=("phone","size"),
        Rating=("rating_num","mean"),
        n_cal=("calificado","sum")
    ).reset_index()
    tab_lbl["% del total"] = (tab_lbl["Chats"]/N*100).round(1)
    tab_lbl["Rating"] = tab_lbl["Rating"].round(2)
    tab_lbl["¿Cancelación?"] = tab_lbl["label"].str.contains(
        r"Cancelar|Reembolso|Reprog|Postergac|Esp\. cancel",case=False,regex=True).map({True:"Sí",False:"No"})
    tab_lbl = tab_lbl.sort_values("Chats",ascending=False).rename(columns={"label":"Etiqueta"})
    st.dataframe(tab_lbl[["Etiqueta","Chats","% del total","Rating","¿Cancelación?"]],
                 use_container_width=True, hide_index=True, height=320)
    st.download_button("⬇️ CSV etiquetas completo", tab_lbl.to_csv(index=False).encode(),
                       "etiquetas.csv","text/csv")


# ╔════════════════════════════════════════════╗
#  TAB 7 — CLIENTES QUE MÁS LLAMAN
# ╚════════════════════════════════════════════╝
with t7:
    _fi, _ff, _ags, _colas = filtro_fecha("cli")
    globals().update(_ctx(_fi, _ff, _ags, _colas))
    st.markdown('<div class="sec">📞 Clientes que más contactan & sus motivos</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="info">'
        '<b>¿Cómo se construye esto?</b> Se agrupa el CSV por la columna <code>phone</code> '
        '(número de teléfono del cliente). Se cuentan todas sus conversaciones en el período filtrado. '
        'El "Motivo principal" es la etiqueta más frecuente de sus chats (columna <code>labels</code>). '
        '"¿Churn?" = tuvo al menos 1 chat con etiqueta "Cancelar plan" o "Reembolso". '
        '"Handle time" = mediana del tiempo real activo entre mensajes (no la duración del CSV).'
        '</div>', unsafe_allow_html=True)

    st.markdown('<div class="kpi-grid">' +
        kpi("Volumen recurrente", f"{pct_vol_recur}%",
            f"{int(contactos[contactos>=2].sum()):,} de {N:,} chats — clientes con ≥2 contactos",
            kind="alt") +
        kpi("Clientes únicos", f"{len(contactos):,}",
            f"promedio {N/len(contactos):.2f} chats por cliente") +
        kpi("Clientes recurrentes (≥2)", f"{n_recur:,}",
            f"{safe_pct(n_recur, len(contactos))}% de los clientes volvió a contactar", kind="amber") +
        kpi("Clientes con ≥5 contactos", f"{int((contactos>=5).sum()):,}",
            "alta recurrencia = problema posiblemente no resuelto", kind="warn") +
        kpi("Clientes con ≥10 contactos", f"{int((contactos>=10).sum()):,}",
            "requieren revisión individual", kind="warn") +
        kpi("Máx contactos 1 cliente", f"{int(contactos.max())}",
            "cliente más recurrente del período", kind="dark") +
        '</div>', unsafe_allow_html=True)

    st.markdown('<div class="invis">🔮 <b>Dato clave:</b> el 90.4% del volumen de chats proviene de '
                'clientes recurrentes. Cuando el motivo principal de esa recurrencia es cancelación, '
                'indica un problema de retención estructural, no puntual.</div>',
                unsafe_allow_html=True)

    st.markdown("---")
    tf1, tf2, tf3, tf4 = st.columns(4)
    c_search  = tf1.text_input("🔎 Buscar nombre / teléfono / motivo", "")
    c_min     = tf2.number_input("Mínimo de contactos", min_value=1, value=2, step=1)
    c_churn   = tf3.checkbox("Solo clientes con churn")
    c_sinres  = tf4.checkbox("Solo reintentos mismo día")
    n_mostrar = st.slider("Cuántos clientes mostrar (top N)", 5, 50, 25, step=5)

    rows_c = []
    for ph, g in df.groupby("phone"):
        hnd_c = g.loc[g["handle_min"] < 500, "handle_min"].dropna()
        motivos_sorted = (g["labels"].fillna("").str.split(r",\s*").explode()
                          .str.strip().value_counts())
        m1 = motivos_sorted.index[0] if len(motivos_sorted) > 0 else "–"
        m2 = motivos_sorted.index[1] if len(motivos_sorted) > 1 else "–"
        rows_c.append({
            "Teléfono":          ph,
            "Cliente":           safe_mode(g["contact"]) if "contact" in g.columns else "–",
            "Región":            safe_mode(g["region"]),
            "Contactos":         len(g),
            "Motivo principal":  m1,
            "2° Motivo":         m2,
            "Cola frecuente":    safe_mode(g["tag"]) if "tag" in g.columns else "–",
            "Agente frecuente":  safe_mode(g["agent"]),
            "Rating prom":       round(float(g["rating_num"].mean()), 2)
                                 if g["rating_num"].notna().any() else np.nan,
            "% Calificó":        safe_pct(g["calificado"].sum(), len(g)),
            "Handle med (min)":  round(float(hnd_c.median()), 1) if len(hnd_c) else np.nan,
            "¿Churn?":           "Sí" if g["es_churn"].any() else "No",
            "¿Reprog?":          "Sí" if g["es_reprog"].any() else "No",
            "Reintento mismo día": "Sí" if g["reintento"].any() else "No",
            "Último contacto":   str(g["created_at"].max().date())
                                 if g["created_at"].notna().any() else "–",
        })

    tc_full = pd.DataFrame(rows_c).sort_values("Contactos", ascending=False)
    if c_search:
        tc_full = tc_full[tc_full.apply(
            lambda r: c_search.lower() in str(r["Cliente"]).lower()
                   or c_search.lower() in str(r["Teléfono"]).lower()
                   or c_search.lower() in str(r["Motivo principal"]).lower(), axis=1)]
    tc_full = tc_full[tc_full["Contactos"] >= c_min]
    if c_churn:  tc_full = tc_full[tc_full["¿Churn?"] == "Sí"]
    if c_sinres: tc_full = tc_full[tc_full["Reintento mismo día"] == "Sí"]
    tc_show = tc_full.head(n_mostrar)

    st.markdown(f"**{len(tc_full):,} clientes** cumplen los filtros — mostrando top {min(n_mostrar, len(tc_full))}")
    sty_tc = (tc_show.style
              .map(lambda v: f"color:{OY_WARN};font-weight:700;background:#FFF0F0"
                   if v == "Sí" else "", subset=["¿Churn?"])
              .map(lambda v: f"color:{OY_AMBER};font-weight:600"
                   if v == "Sí" else "", subset=["¿Reprog?","Reintento mismo día"])
              .format({"Rating prom":"{:.2f}","Handle med (min)":"{:.1f}",
                       "% Calificó":"{:.1f}"}))
    st.dataframe(sty_tc, use_container_width=True, hide_index=True, height=500)

    d1c, d2c = st.columns(2)
    d1c.download_button("⬇️ CSV clientes filtrados",
                        tc_show.to_csv(index=False).encode(), "clientes.csv","text/csv")
    d2c.download_button("⬇️ CSV todos los clientes",
                        tc_full.to_csv(index=False).encode(), "clientes_todos.csv","text/csv")

    st.markdown("---")
    ca1, ca2 = st.columns(2)
    with ca1:
        st.subheader("Por qué llaman los clientes recurrentes")
        rec_ph2 = set(contactos[contactos >= 2].index)
        rexp_c  = (df[df["phone"].isin(rec_ph2)]["labels"]
                   .fillna("Sin etiqueta").str.split(r",\s*").explode().str.strip())
        rmot_c  = rexp_c.value_counts().head(12).reset_index()
        rmot_c.columns = ["Motivo","Chats"]
        fig_rc = px.bar(rmot_c, x="Chats", y="Motivo", orientation="h",
                        color="Chats", color_continuous_scale="Teal", text="Chats")
        fig_rc.update_traces(textposition="outside")
        fig_rc.update_layout(showlegend=False, yaxis={"categoryorder":"total ascending"})
        st.plotly_chart(sfig(fig_rc, 420), use_container_width=True)
    with ca2:
        st.subheader("¿Cuántas veces contactan?")
        freq_bins = pd.cut(contactos, bins=[0,1,2,5,10,20,999],
                           labels=["1 contacto","2","3–5","6–10","11–20",">20"])
        freq_df = freq_bins.value_counts().sort_index().reset_index()
        freq_df.columns = ["Frecuencia","Clientes"]
        freq_df["%"] = (freq_df["Clientes"]/len(contactos)*100).round(1)
        fig_freq = px.bar(freq_df, x="Frecuencia", y="Clientes",
                          color="Clientes", color_continuous_scale="Teal",
                          text=freq_df["Clientes"].astype(str) + " (" + freq_df["%"].astype(str) + "%)")
        fig_freq.update_traces(textposition="outside")
        fig_freq.update_layout(showlegend=False)
        st.plotly_chart(sfig(fig_freq, 420), use_container_width=True)

    st.subheader("¿Los clientes que más llaman califican diferente?")
    df_freq = df.copy()
    df_freq["freq_cliente"] = df_freq["phone"].map(contactos)
    df_freq["bucket_freq"] = pd.cut(df_freq["freq_cliente"],
                                     bins=[0,1,2,5,10,20,999],
                                     labels=["1 contacto","2","3–5","6–10","11–20",">20"])
    rat_freq = df_freq[df_freq["calificado"]].groupby("bucket_freq", observed=True)["rating_num"].agg(
        ["mean","count"]).reset_index()
    rat_freq.columns = ["Frecuencia","Rating prom","n calificados"]
    rat_freq["Rating prom"] = rat_freq["Rating prom"].round(3)
    fig_rf = px.bar(rat_freq, x="Frecuencia", y="Rating prom",
                    color="Rating prom", color_continuous_scale="RdYlGn",
                    range_color=[4.4, 5.0], text="Rating prom")
    fig_rf.update_traces(texttemplate="%{text:.3f}", textposition="outside")
    fig_rf.add_hline(y=META_RATING, line_dash="dash", line_color=OY_TEAL)
    st.plotly_chart(sfig(fig_rf, 300), use_container_width=True)


# ╔════════════════════════════════════════════╗
#  TAB 8 — EXPLORADOR DE CHATS
# ╚════════════════════════════════════════════╝
with t8:
    _fi, _ff, _ags, _colas = filtro_fecha("expl")
    globals().update(_ctx(_fi, _ff, _ags, _colas))
    st.markdown('<div class="sec">📋 Explorador de Chats (detalle individual)</div>',
                unsafe_allow_html=True)

    st.markdown(
        f'<div class="invis">🔮 <b>KPI INVISIBLE #6 — Handle Time Activo Real</b><br>'
        f'La columna <code>duration</code> mide tiempo hasta el cierre (a veces días después). '
        f'El handle time real (primer→último mensaje) es mediana <b>{fmt_min(hnd_med)}</b> '
        f'vs duración promedio ~327 min. El trabajo real del agente es 6× menor de lo que sugiere la duración.</div>',
        unsafe_allow_html=True)

    st.markdown('<div class="kpi-grid">' +
        kpi("Handle time real (mediana)", fmt_min(hnd_med), "primer→último mensaje activo", kind="alt") +
        kpi("Duración promedio (CSV)",
            fmt_min((df.loc[~df["dur_outlier"].fillna(False), "dur_min"] if dur_excl_out
                     else df["dur_min"]).mean()),
            "sin outliers >5h" if dur_excl_out else "incluye outliers >5h", kind="dark") +
        kpi("Chats fantasma", f"{n_ghost:,}", f"{pct_ghost}% sin respuesta final del agente",
            kind="warn" if pct_ghost > META_GHOST else "amber") +
        '</div>', unsafe_allow_html=True)

    ef1, ef2, ef3 = st.columns(3)
    srch_ex  = ef1.text_input("🔎 Buscar cliente / teléfono / etiqueta","", key="srch_ex")
    f_gho_ex = ef2.checkbox("Solo chats fantasma 👻")
    f_t30_ex = ef3.checkbox("Solo TPR >30 min")
    ef4, ef5 = st.columns(2)
    f_chu_ex = ef4.checkbox("Solo chats con churn")
    f_rep_ex = ef5.checkbox("Solo reprogramaciones")

    det = df.copy()
    det["TPR (min)"]    = det["tpr_min"].round(2)
    det["Handle (min)"] = det["handle_min"].round(1)
    det = det.rename(columns={
        "contact":"Cliente","phone":"Teléfono","agent":"Agente","tag":"Cola",
        "created_at":"Fecha","rating":"Calif.","labels":"Etiquetas","status":"Estado",
        "ghost":"Fantasma","es_churn":"Churn","es_reprog":"Reprog","region":"Región"})
    disp = [c for c in ["Cliente","Teléfono","Agente","Cola","Región","Fecha","Calif.",
                         "TPR (min)","Handle (min)","Etiquetas","Estado","Fantasma","Churn","Reprog"]
             if c in det.columns]
    d = det.copy()
    if srch_ex:
        m = (d.get("Cliente",pd.Series("",index=d.index)).fillna("").str.contains(srch_ex,case=False) |
             d.get("Teléfono",pd.Series("",index=d.index)).fillna("").str.contains(srch_ex,case=False) |
             d.get("Etiquetas",pd.Series("",index=d.index)).fillna("").str.contains(srch_ex,case=False))
        d = d[m]
    if f_gho_ex: d = d[d.get("Fantasma",pd.Series(False,index=d.index)) == True]
    if f_t30_ex: d = d[d["TPR (min)"] > 30]
    if f_chu_ex: d = d[d.get("Churn",pd.Series(False,index=d.index)) == True]
    if f_rep_ex: d = d[d.get("Reprog",pd.Series(False,index=d.index)) == True]

    st.caption(f"**{len(d):,}** registros de {N:,} totales")
    st.dataframe(d[[c for c in disp if c in d.columns]].head(500),
                 use_container_width=True, hide_index=True, height=460)
    st.download_button("⬇️ CSV detalle filtrado",
                       d[[c for c in disp if c in d.columns]].to_csv(index=False).encode(),
                       "detalle_chats.csv","text/csv")


# ╔═══════════════════════════════════════╗
#  TAB 9 — INSIGHTS & RECOMENDACIONES
# ╚═══════════════════════════════════════╝
with t9:
    _fi, _ff, _ags, _colas = filtro_fecha("insi")
    globals().update(_ctx(_fi, _ff, _ags, _colas))
    st.markdown('<div class="sec">💡 Insights & Recomendaciones Estratégicas</div>',
                unsafe_allow_html=True)
    st.caption(f"{N:,} chats · {f_ini} → {f_fin}")

    # KPI rápido banner
    st.markdown('<div class="kpi-grid">' +
        kpi("Contactos únicos", f"{len(contactos):,}", f"{N/len(contactos):.2f} chats/cliente prom", kind="alt") +
        kpi("SLA <2 min", f"{pct_sla2}%", "diferenciador competitivo", kind="ok") +
        kpi("Sin etiqueta", f"{pct_sin_lbl}%", f"{int(df['sin_label'].sum()):,} chats", kind="warn" if pct_sin_lbl>10 else "amber") +
        kpi("Transferidos", f"{pct_transf}%", f"rating cae 0.25 pts", kind="amber") +
        '</div>', unsafe_allow_html=True)

    # ── SECCIÓN 1: ALERTAS CRÍTICAS ──────────────────────────
    st.markdown('<div class="sec red">🔴 ALERTAS CRÍTICAS — Acción inmediata</div>',
                unsafe_allow_html=True)

    alertas = [
        ("Crisis de retención activa", f"{pct_churn}% son cancelaciones de plan ({int(df['es_churn'].sum()):,} chats)",
         "Pérdida directa de clientes activos. Meta 8% superada.",
         "Crear playbook de retención. Asignar 2–3 agentes especializados a 'Cancelar plan'.",
         "Dir. Operaciones", "Semana 1"),
        ("Chats fantasma no resueltos", f"{n_ghost:,} chats ({pct_ghost}%) cerrados con último mensaje del cliente",
         "Cliente ignorado al cierre. Daño silencioso de satisfacción.",
         "Alerta automática a las 2h sin respuesta del agente. Revisión diaria de chats fantasma.",
         "Supervisores", "Semana 1"),
        ("Chats fantasma no resueltos", f"{n_ghost:,} chats ({pct_ghost}%) cerrados con último mensaje del cliente",
         "Cliente ignorado al cierre. Daño silencioso de satisfacción.",
         "Alerta automática a las 2h sin respuesta del agente. Revisión diaria de chats fantasma.",
         "Supervisores", "Semana 1"),
        ("Equipo de retención sin KPIs propios",
         "Carlos Jiménez, Laura Pereira, Alonso Palacios reciben chats de 'Cancelar plan' de forma deliberada",
         "Sin KPIs de retención, no se puede medir si el equipo está logrando salvar clientes.",
         "Definir KPI: % de clientes que NO cancelaron después del chat. "
         "Separar métricas del equipo de retención de las métricas de soporte general.",
         "Coordinadores", "Semana 1"),
        ("15% de chats sin etiqueta", f"{int(df['sin_label'].sum()):,} chats sin label ({pct_sin_lbl}%)",
         "Punto ciego en reportería. Cifras reales de cancelación pueden ser mayores.",
         "Hacer el campo 'Etiqueta' obligatorio al cerrar chat en Treble.",
         "Líder de Calidad", "Semana 2"),
        ("Lag asignación >30 min", f"7.9% de chats esperó más de 30 min antes de ser asignado",
         "El cliente espera sin que ningún agente lo vea. El TPR reportado no captura esto.",
         "Revisar reglas de enrutamiento. Alerta si chat sin asignar >10 min.",
         "Tecnología / Ops", "Semana 2"),
    ]
    for problema, dato, impacto, accion, resp, plazo in alertas:
        st.markdown(f'''<div class="crit">
        <b>🔴 {problema}</b><br>
        📊 <i>Dato:</i> {dato}<br>
        ⚠️ <i>Impacto:</i> {impacto}<br>
        ✅ <i>Acción:</i> {accion}<br>
        👤 {resp} · 📅 {plazo}
        </div>''', unsafe_allow_html=True)

    # ── SECCIÓN 2: ALERTAS DE ATENCIÓN ───────────────────────
    st.markdown('<div class="sec amb">🟡 ALERTAS — Atención en el corto plazo</div>',
                unsafe_allow_html=True)

    atencion = [
        ("Cobertura de encuesta baja", f"{pct_cal}% (meta {META_CAL}%)",
         "Solo calificaron {n_cal:,} de {N:,} chats. El rating de 4.8 sobreestima la satisfacción real.",
         "Encuesta automática post-chat con 1 pregunta (NPS o estrella). Meta: >70% cobertura."),
        ("Transferencias degradan satisfacción", f"{pct_transf}% transferidos → rating baja de 4.79 a 4.54 (-0.25 pts)",
         "El cliente explica su problema dos veces.",
         "Revisar reglas de enrutamiento inicial. Mejorar asignación automática por etiqueta."),
        ("Clientes que vuelven a escribir el mismo día",
         f"{n_reint:,} casos con >1 contacto el mismo día",
         "El problema no se resolvió en el primer chat — el cliente tuvo que volver a escribir.",
         "Identificar los motivos con más reintentos y crear guías de resolución para esos casos."),
        ("Rating bajo en horario nocturno", "4am–6am: rating 4.54 (vs 4.79 global)",
         "La cobertura nocturna tiene menor calidad percibida.",
         "Revisar protocolos nocturnos. Considerar turno dedicado con capacitación específica."),
    ]
    for prob, dato, imp, rec in atencion:
        st.markdown(f'<div class="alrt"><b>🟡 {prob}</b> — {dato}<br>'
                    f'<i>Impacto:</i> {imp}<br><i>Acción:</i> {rec}</div>', unsafe_allow_html=True)

    # ── SECCIÓN 3: FORTALEZAS ────────────────────────────────
    st.markdown('<div class="sec ok">✅ FORTALEZAS — Comunicar, no dar por sentado</div>',
                unsafe_allow_html=True)

    fortalezas = [
        ("SLA de respuesta excepcional", f"{pct_sla2}% responde en ≤2 min · {pct_sla5}% en ≤5 min · mediana {fmt_min(tpr_med)}",
         "Diferenciador competitivo real. Los clientes perciben atención inmediata.",
         "Publicar como benchmark público. Usar en materiales de ventas y retención."),
        ("Rating general alto sobre muestra calificada", f"{rating:.2f}/5 sobre {n_cal:,} calificados",
         "El equipo que califica tiene alta satisfacción. Base de calidad sólida.",
         "Subir cobertura de encuesta para validar si aplica a toda la operación."),
        ("Equipo especialistas: calidad excepcional",
         f"Cola 'especialistas': {len(df[df['tag'].str.lower().eq('especialistas')] if 'tag' in df.columns else pd.DataFrame()):,} chats con rating superior",
         "El modelo de atención especializada es el mejor de la operación.",
         "Documentar el protocolo y replicarlo en el canal general."),
        ("Handle time activo real eficiente", f"Mediana {fmt_min(hnd_med)} de trabajo activo real",
         "La carga real del agente es 6x menor de lo que sugiere la 'duración'.",
         "Usar este dato para dimensionar correctamente la capacidad del equipo."),
    ]
    for fort, dato, xq, como in fortalezas:
        st.markdown(f'<div class="good"><b>✅ {fort}</b><br>'
                    f'{dato}<br><i>Por qué importa:</i> {xq}<br>'
                    f'<i>Cómo potenciarlo:</i> {como}</div>', unsafe_allow_html=True)

    # ── SECCIÓN 4: OPORTUNIDADES ─────────────────────────────
    st.markdown('<div class="sec blue">🚀 OPORTUNIDADES — Dónde invertir</div>',
                unsafe_allow_html=True)

    oportunidades = [
        ("Retención proactiva antes de la cancelación",
         f"2.389 'Cancelar plan' + 133 'Reembolso' = {int(df['es_churn'].sum()):,} pérdidas",
         "Reducir 30–40% del churn con contacto preventivo",
         "Flujo automático 48h antes del vencimiento para clientes en riesgo. Mayor ROI disponible.","Alta"),
        ("Subir cobertura de encuesta de 36% → 70%",
         f"Hoy: {pct_cal}% · Potencial: {int(N*0.7):,} ratings/período",
         "Triplica la data de calidad para gestión de personas",
         "Encuesta post-chat automática con 1 sola pregunta. Configuración en Treble.","Alta"),
        ("Etiquetado obligatorio al cerrar",
         f"15% sin label = {int(df['sin_label'].sum()):,} chats ciegos",
         "Elimina punto ciego. Las cifras de cancelación pueden ser mayores.",
         "Campo 'Etiqueta' requerido en Treble al cerrar chat. Taxonomía máx. 20 opciones.","Alta"),
        ("Alerta automática para chats fantasma",
         f"{n_ghost:,} chats cerrados sin respuesta final del agente",
         "Elimina daño de imagen silencioso",
         "Alerta a supervisor si el último mensaje tiene >2h y es del cliente.","Media"),
        ("Self-service 'Cambiar tarjeta'",
         "440+ chats solo para cambiar método de pago",
         "Libera capacidad del equipo para casos de mayor valor",
         "Implementar flujo self-service en app. Un solo agente (Andrea Hurtado) maneja el 90%.","Media"),
        ("Especializar 2–3 agentes en retención",
         f"Agentes con >70% churn en cartera ya lo están haciendo informalmente",
         "Formaliza el rol, da herramientas y mide correctamente",
         "Crear equipo de retención con playbook, scripts y métricas propias.","Alta"),
    ]
    for op, dato, pot, init, prior in oportunidades:
        prior_color = "crit" if prior=="Alta" else "alrt"
        st.markdown(f'<div class="{prior_color}"><b>🚀 {op}</b> — Prioridad {prior}<br>'
                    f'📊 {dato}<br>🎯 <i>Potencial:</i> {pot}<br>'
                    f'💡 <i>Iniciativa:</i> {init}</div>', unsafe_allow_html=True)

    # ── SECCIÓN 5: HOJA DE RUTA ──────────────────────────────
    st.markdown('<div class="sec">🗓️ Hoja de Ruta — Plan 90 días</div>', unsafe_allow_html=True)
    roadmap = [
        ("Fase 1\nSem 1–2","Etiquetado obligatorio","% chats con label ≥95%","Líder Calidad","Sem 1","🔴"),
        ("Fase 1\nSem 1–2","Alerta chats fantasma >2h","% chats fantasma <2%","Supervisores","Sem 1","🔴"),
        ("Fase 1\nSem 1–2","Definir KPIs del equipo de retención","% clientes retenidos por agente","Coordinadores","Sem 2","🔴"),
        ("Fase 2\nMes 1","Encuesta post-chat automática","Cobertura encuesta >50%","Tecnología","Mes 1","🟡"),
        ("Fase 2\nMes 1","Revisar reglas de transferencia","% transferencias <5%","Ops/Tech","Mes 1","🟡"),
        ("Fase 2\nMes 1","Playbook de retención (Cancelar plan)","Churn <8%","Dir. Ops","Mes 1","🔴"),
        ("Fase 3\nMes 2–3","Self-service cambiar tarjeta","Reducir 400+ chats/mes","Desarrollo","Mes 2","🟡"),
        ("Fase 3\nMes 2–3","Equipo dedicado de retención","Churn <6%","RRHH / Ops","Mes 3","🟢"),
        ("Fase 3\nMes 2–3","Flujo retención proactivo 48h","Reducir churn 30%","CRM / Tech","Mes 3","🟢"),
    ]
    rm_df = pd.DataFrame(roadmap, columns=["Fase","Iniciativa","KPI de éxito","Responsable","Plazo","Prioridad"])
    st.dataframe(rm_df, use_container_width=True, hide_index=True)
    st.download_button("⬇️ Descargar hoja de ruta (.csv)",
                       rm_df.to_csv(index=False).encode(), "hoja_de_ruta.csv","text/csv")

# ╔════════════════════════════════════════════════════════════╗
#  TAB 10 — AJUSTE DE CALIFICACIONES
# ╚════════════════════════════════════════════════════════════╝
with t_aj:
    _fi, _ff, _ags, _colas = filtro_fecha("ajus")
    globals().update(_ctx(_fi, _ff, _ags, _colas))
    st.markdown('<div class="sec">⚙️ Ajuste de Calificaciones</div>',
                unsafe_allow_html=True)

    n_ajustes = sum(1 for v in st.session_state["ajustes_rating"].values() if v.get("excluir"))
    n_ajust_mes = int(df["rating_ajustado"].sum()) if "rating_ajustado" in df.columns else 0

    st.markdown('<div class="kpi-grid">' +
        kpi("Ajustes activos (sesión)", f"{n_ajustes}",
            "calificaciones excluidas del promedio", kind="amber") +
        kpi("Afectan al período actual", f"{n_ajust_mes}",
            "chats excluidos en el rango de fechas filtrado", kind="amber") +
        kpi("Rating sin ajustes", f"{df['rating_original'].mean():.3f}",
            "promedio bruto del CSV", kind="dark") +
        kpi("Rating con ajustes", f"{df['rating_num'].mean():.3f}",
            "promedio tras excluir calificaciones erróneas",
            kind="ok" if df["rating_num"].mean() >= META_RATING else "amber") +
        '</div>', unsafe_allow_html=True)

    st.divider()

    # ── Buscador de chats para excluir ──────────────────────
    st.subheader("🔍 Buscar chat para ajustar su calificación")
    st.caption("Filtra los chats calificados. Cuando encuentres el que quieres excluir, "
               "marca el checkbox y escribe el motivo.")

    aj1, aj2, aj3 = st.columns(3)
    busq_tel   = aj1.text_input("Teléfono del cliente", "", key="aj_tel")
    busq_agent = aj2.text_input("Agente", "", key="aj_agent")
    busq_rating= aj3.selectbox("Calificación", ["Todas","1","2","3","4","5"], key="aj_rating")

    # Construir tabla de chats calificados
    df_cal_aj = df[df["rating_original"].notna()].copy()
    df_cal_aj["rating_original"] = df_cal_aj["rating_original"].astype(int)
    if busq_tel:
        df_cal_aj = df_cal_aj[df_cal_aj["phone"].fillna("").str.contains(busq_tel)]
    if busq_agent:
        df_cal_aj = df_cal_aj[df_cal_aj["agent"].fillna("").str.contains(busq_agent, case=False)]
    if busq_rating != "Todas":
        df_cal_aj = df_cal_aj[df_cal_aj["rating_original"] == int(busq_rating)]

    df_cal_aj = df_cal_aj.sort_values("created_at", ascending=False).head(100)

    if df_cal_aj.empty:
        cal_rango = int(df["rating_original"].notna().sum()) if "rating_original" in df.columns else 0
        cal_total = int(pd.to_numeric(df_raw.get("rating", pd.Series(dtype=str)).replace("-", np.nan),
                                      errors="coerce").notna().sum())
        if busq_tel or busq_agent or busq_rating != "Todas":
            st.info("No hay chats calificados que coincidan con esos filtros de búsqueda. "
                    "Prueba borrando el teléfono/agente o poniendo Calificación = Todas.")
        elif cal_rango == 0 and cal_total > 0:
            st.warning(f"No hay chats calificados en el **rango de fechas** seleccionado, "
                       f"pero el histórico completo sí tiene {cal_total:,} calificados. "
                       f"Amplía el filtro de 📅 Fechas en el panel izquierdo.")
        elif cal_total == 0:
            st.error("El histórico cargado no tiene calificaciones reconocibles. "
                     "Vuelve a subir el treble completo de chats (sin abrirlo en Excel).")
        else:
            st.info("No hay chats calificados que coincidan con los filtros.")
    else:
        st.caption(f"Mostrando {len(df_cal_aj)} chats calificados (máx. 100). "
                   f"Marca los que quieres excluir del promedio.")

        # Mostrar cada chat con un checkbox
        for _, row in df_cal_aj.iterrows():
            chat_id = row["chat_id"]
            ya_excluido = st.session_state["ajustes_rating"].get(chat_id, {}).get("excluir", False)
            motivo_prev = st.session_state["ajustes_rating"].get(chat_id, {}).get("motivo", "")
            conf_prev   = st.session_state["ajustes_rating"].get(chat_id, {}).get("confirmado_por", "")

            with st.expander(
                f"{'🚫' if ya_excluido else '⭐'} "
                f"{int(row['rating_original'])}★ · "
                f"{str(row.get('contact','–'))[:25]} · "
                f"{row.get('agent','–').split('@')[0]} · "
                f"{str(row.get('created_at',''))[:10]} · "
                f"{str(row.get('labels','Sin etiqueta'))[:40]}",
                expanded=ya_excluido):

                c_left, c_right = st.columns([2, 1])
                with c_left:
                    st.caption(f"📞 {row.get('phone','–')} · "
                               f"🏷️ {row.get('labels','Sin etiqueta')} · "
                               f"🕐 {str(row.get('created_at',''))[:16]}")
                    motivo = st.text_input(
                        "Motivo de exclusión",
                        value=motivo_prev,
                        placeholder="Ej: Cliente respondió '1' sin querer al bot",
                        key=f"motivo_{chat_id}")
                    conf = st.text_input(
                        "Confirmado por",
                        value=conf_prev,
                        placeholder="Nombre de quien autoriza (ej: Jessica)",
                        key=f"conf_{chat_id}")
                with c_right:
                    excluir = st.checkbox(
                        "Excluir del promedio",
                        value=ya_excluido,
                        key=f"excl_{chat_id}",
                        help="Al marcar esto, la calificación no entra en el rating del agente ni del equipo")
                    if excluir and not motivo:
                        st.warning("Escribe el motivo antes de guardar.")
                    if st.button("💾 Guardar", key=f"save_{chat_id}"):
                        if excluir and not motivo:
                            st.error("El motivo es obligatorio para excluir una calificación.")
                        else:
                            st.session_state["ajustes_rating"][chat_id] = {
                                "excluir":        excluir,
                                "motivo":         motivo,
                                "confirmado_por": conf,
                                "phone":          row.get("phone",""),
                                "agente":         row.get("agent",""),
                                "cliente":        str(row.get("contact","")),
                                "fecha":          str(row.get("created_at",""))[:10],
                                "rating_original":int(row["rating_original"]),
                                "labels":         row.get("labels",""),
                            }
                            st.rerun()

    st.divider()

    # ── Tabla de todos los ajustes activos ───────────────────
    st.subheader("📋 Registro de ajustes activos")
    if st.session_state["ajustes_rating"]:
        aj_rows = []
        for cid, info in st.session_state["ajustes_rating"].items():
            if info.get("excluir"):
                aj_rows.append({
                    "Fecha":           info.get("fecha","–"),
                    "Cliente":         info.get("cliente","–"),
                    "Teléfono":        info.get("phone","–"),
                    "Agente":          info.get("agente","–").split("@")[0] if info.get("agente") else "–",
                    "Rating original": info.get("rating_original","–"),
                    "Etiqueta":        info.get("labels","–")[:40],
                    "Motivo exclusión":info.get("motivo","–"),
                    "Confirmado por":  info.get("confirmado_por","–"),
                })
        if aj_rows:
            aj_df = pd.DataFrame(aj_rows)
            st.dataframe(aj_df, use_container_width=True, hide_index=True)
            st.download_button(
                "⬇️ Descargar registro de ajustes (.csv)",
                aj_df.to_csv(index=False).encode("utf-8"),
                "ajustes_calificaciones.csv", "text/csv")

            if st.button("🗑️ Eliminar TODOS los ajustes", type="secondary"):
                st.session_state["ajustes_rating"] = {}
                st.rerun()
        else:
            st.info("No hay ajustes activos en esta sesión.")
    else:
        st.info("Aún no has hecho ningún ajuste en esta sesión. "
                "Busca un chat arriba y márcalo para excluirlo.")

    st.markdown(
        '<div class="alrt">⚠️ <b>Importante:</b> Los ajustes se mantienen mientras '
        'la sesión esté activa. Si recargas la página se pierden. '
        'Descarga el CSV antes de cerrar para llevar un registro histórico.</div>',
        unsafe_allow_html=True)
with t_esp:
    _fi, _ff, _ags, _colas = filtro_fecha("esp")
    globals().update(_ctx(_fi, _ff, _ags, _colas))
    st.markdown('<div class="sec amb">🎓 Especialistas · seguimiento de calificaciones bajas</div>',
                unsafe_allow_html=True)

    # ── Controles ──────────────────────────────────────────────
    colas_disp = sorted(df_raw["tag"].dropna().unique()) if "tag" in df_raw.columns else []
    idx_esp = colas_disp.index("especialistas") if "especialistas" in colas_disp else 0
    ce1, ce2, ce3 = st.columns([1.3, 1, 1])
    cola_sel = ce1.selectbox("Cola / equipo", colas_disp, index=idx_esp,
                             key="esp_cola") if colas_disp else None
    umbral_lbl = ce2.radio("Considerar “bajo” como",
                           ["≤ 2 (muy baja)", "≤ 3 (baja)", "≤ 4 (incluye regular)"],
                           index=1, key="esp_umbral")
    umbral = {"≤ 2 (muy baja)": 2, "≤ 3 (baja)": 3, "≤ 4 (incluye regular)": 4}[umbral_lbl]
    dias = ce3.slider("Ventana reciente (días · 0 = todo)", 0, 120, 0, step=15, key="esp_dias")

    # ── Base: cola seleccionada (sin filtros de panel) ─────────
    e = df_raw.copy()
    if cola_sel is not None:
        e = e[e["tag"].fillna("").str.lower() == cola_sel.lower()]
    if dias > 0:
        tope = df_raw["created_at"].max()
        e = e[e["created_at"] >= tope - pd.Timedelta(days=dias)]

    if e.empty:
        st.warning("No hay chats en esta cola para el rango seleccionado.")
    else:
        bajas = e[e["rating_num"] <= umbral].copy()
        n_baja = len(bajas)
        esp_baja = bajas["phone"].nunique()
        peor_rep = (bajas.groupby("phone").size().sort_values(ascending=False))
        top_nombre, top_n = "—", 0
        if len(peor_rep):
            ph_top = peor_rep.index[0]
            top_n = int(peor_rep.iloc[0])
            gtop = e[e["phone"] == ph_top]
            top_nombre = safe_mode(gtop["contact"]) if "contact" in gtop.columns else ph_top

        # ── KPIs ───────────────────────────────────────────────
        st.markdown('<div class="kpi-grid">' +
            kpi("Calificaciones bajas", f"{n_baja:,}",
                f"en cola '{cola_sel}' (rating ≤ {umbral})", kind="warn") +
            kpi("Especialistas distintos", f"{esp_baja:,}",
                "personas que calificaron bajo", kind="amber") +
            kpi("Más bajas (1 especialista)", f"{top_n}",
                f"{top_nombre}", kind="dark") +
            kpi("Rating cola", f"{e['rating_num'].mean():.2f}" if e['rating_num'].notna().any() else "—",
                f"{safe_pct(e['rating_num'].notna().sum(), len(e))}% calificó") +
            '</div>', unsafe_allow_html=True)

        if n_baja == 0:
            st.markdown('<div class="good">✅ No hay calificaciones bajas en este rango. '
                        'Prueba ampliar la ventana o subir el umbral.</div>',
                        unsafe_allow_html=True)
        else:
            # ── TABLA 1: cada calificación baja (la que pidió Iva) ──
            st.markdown("##### 📋 Calificaciones bajas — detalle (más recientes primero)")
            t1d = bajas.sort_values("created_at", ascending=False).copy()
            t1d["Fecha"] = t1d["created_at"].dt.strftime("%Y-%m-%d %H:%M")
            tab1 = t1d.assign(
                Especialista=t1d["contact"] if "contact" in t1d.columns else "—",
                Teléfono=t1d["phone"],
                Calificación=t1d["rating_num"].astype("Int64"),
                Etiqueta=t1d["label_ppal"] if "label_ppal" in t1d.columns else "—",
                Agente=t1d["agent"],
                Región=t1d["region"] if "region" in t1d.columns else "—",
            )[["Fecha", "Especialista", "Teléfono", "Calificación",
               "Etiqueta", "Agente", "Región"]]
            st.dataframe(tab1, use_container_width=True, hide_index=True, height=340)
            st.download_button("⬇️ Descargar detalle (.csv)",
                               tab1.to_csv(index=False).encode("utf-8"),
                               "especialistas_calif_bajas.csv", "text/csv", key="esp_csv1")

            # ── TABLA 2: resumen por especialista (quién repite + riesgo) ──
            st.divider()
            st.markdown("##### 🚩 Resumen por especialista — prioridad de seguimiento")
            st.caption("Ordenado por nº de bajas. **Riesgo** = su última calificación fue baja, "
                       "o calificó bajo y después dejó de calificar.")
            phones_baja = bajas["phone"].unique()
            res = []
            for ph in phones_baja:
                g = e[e["phone"] == ph].sort_values("created_at")
                rated = g[g["rating_num"].notna()]
                ult_calif = rated["rating_num"].iloc[-1] if len(rated) else np.nan
                ult_fecha = rated["created_at"].iloc[-1] if len(rated) else g["created_at"].max()
                ult_baja_fecha = g[g["rating_num"] <= umbral]["created_at"].max()
                post = g[g["created_at"] > ult_baja_fecha]
                dejo = (len(post) > 0) and (post["rating_num"].isna().all())
                ult_es_baja = (not pd.isna(ult_calif)) and (ult_calif <= umbral)
                riesgo = ult_es_baja or dejo
                res.append({
                    "Especialista":   safe_mode(g["contact"]) if "contact" in g.columns else ph,
                    "Teléfono":       ph,
                    "# bajas":        int((g["rating_num"] <= umbral).sum()),
                    "Peor nota":      int(g["rating_num"].min()),
                    "Última nota":    "—" if pd.isna(ult_calif) else int(ult_calif),
                    "Fecha últ. calif.": ult_fecha.strftime("%Y-%m-%d") if pd.notna(ult_fecha) else "—",
                    "Contactos":      len(g),
                    "Agente frecuente": safe_mode(g["agent"]),
                    "⚠️ Riesgo":      "🔴 Sí" if riesgo else "—",
                    "Dejó de calificar": "Sí" if dejo else "No",
                })
            res_df = (pd.DataFrame(res)
                      .sort_values(["# bajas", "Fecha últ. calif."], ascending=[False, False]))
            st.dataframe(res_df, use_container_width=True, hide_index=True, height=320)
            st.download_button("⬇️ Descargar resumen (.csv)",
                               res_df.to_csv(index=False).encode("utf-8"),
                               "especialistas_resumen_bajas.csv", "text/csv", key="esp_csv2")

            n_riesgo = (res_df["⚠️ Riesgo"] == "🔴 Sí").sum()
            st.markdown(
                f'<div class="invis">🔮 <b>Acción sugerida:</b> {n_riesgo} especialista(s) '
                f'en riesgo (última nota baja o dejaron de calificar tras una baja). '
                f'Son los primeros candidatos para una encuesta corta de satisfacción '
                f'y una llamada de seguimiento del equipo de retención.</div>',
                unsafe_allow_html=True)


# ── Footer ──────────────────────────────────────────────────────────
st.divider()
st.caption(f"Opción Yo · Atención al Cliente · actualizado {df_raw['created_at'].max():%d/%m/%Y %H:%M}")
