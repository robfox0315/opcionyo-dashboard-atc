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

# ══════════════════════════════════════════════════════════════
#  CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="ATC · Opción Yo",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Paleta corporativa ────────────────────────────────────────
OY_TEAL      = "#16B6C2"
OY_TEAL_DARK = "#0E8E99"
OY_BLUE      = "#2F80ED"
OY_OK        = "#27AE60"
OY_WARN      = "#E5484D"
OY_AMBER     = "#F2A33C"
OY_INK       = "#16323A"
COLOR_SEQ    = [OY_TEAL, OY_BLUE, OY_AMBER, "#7E57C2", "#EC4899",
                "#26A69A", "#FF7043", "#42A5F5", "#9CCC65", "#5C6BC0"]

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
:root{--oy-teal:#16B6C2;--oy-td:#0E8E99;--oy-blue:#2F80ED;
      --oy-ok:#27AE60;--oy-warn:#E5484D;--oy-amb:#F2A33C;--oy-ink:#16323A;}
.stApp{background:#fff;}
.block-container{padding-top:1.5rem;}
h1,h2,h3{color:var(--oy-td);}
[data-testid="stMetricValue"]{font-size:1.7rem!important;font-weight:800;color:var(--oy-ink);}
[data-testid="stMetricLabel"]{font-size:.78rem!important;color:#5a6b72;font-weight:600;}

.oy-header{display:flex;align-items:center;gap:18px;
  background:linear-gradient(100deg,var(--oy-td) 0%,var(--oy-teal) 48%,#27D0DC 100%);
  padding:20px 28px;border-radius:16px;margin:2px 0 12px;
  box-shadow:0 8px 22px rgba(22,182,194,.28);overflow:visible;}
.oy-logo{font-weight:800;font-size:2rem;color:#fff;line-height:1.2;
  letter-spacing:.4px;white-space:nowrap;padding:2px 18px 2px 0;
  border-right:2px solid rgba(255,255,255,.4);display:flex;align-items:center;}
.oy-logo span{color:#0A4750;margin-left:6px;}
.oy-htxt{display:flex;flex-direction:column;justify-content:center;}
.oy-htitle{color:#fff;font-weight:800;font-size:1.14rem;margin:0;line-height:1.3;}
.oy-hsub{color:#EAFCFE;font-size:.82rem;margin:3px 0 0;line-height:1.2;}

.sec{background:var(--oy-teal);color:#fff;padding:.4rem 1rem;
  border-radius:8px;font-weight:700;margin:.2rem 0 .7rem;
  font-size:.95rem;display:inline-block;}
.sec.red{background:var(--oy-warn);}
.sec.amb{background:var(--oy-amb);}
.sec.ok{background:var(--oy-ok);}
.sec.blue{background:var(--oy-blue);}

.kpi-grid{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:8px;}
.kpi{flex:1;min-width:130px;background:var(--oy-teal);border-radius:12px;
  padding:11px 13px;color:#fff;box-shadow:0 4px 12px rgba(22,182,194,.20);}
.kpi.alt{background:var(--oy-blue);}
.kpi.ok{background:var(--oy-ok);}
.kpi.warn{background:var(--oy-warn);}
.kpi.amber{background:var(--oy-amb);}
.kpi.dark{background:var(--oy-td);}
.kpi .l{font-size:.7rem;opacity:.9;font-weight:600;text-transform:uppercase;letter-spacing:.4px;}
.kpi .v{font-size:1.5rem;font-weight:800;margin-top:2px;}
.kpi .d{font-size:.69rem;opacity:.93;margin-top:2px;}

.crit{background:#FDECEA;border-left:5px solid var(--oy-warn);
  padding:.6rem 1rem;border-radius:6px;margin-bottom:.7rem;color:#7a1f1c;}
.alrt{background:#FFF6E6;border-left:5px solid var(--oy-amb);
  padding:.6rem 1rem;border-radius:6px;margin-bottom:.7rem;color:#7a531a;}
.good{background:#EAF7EF;border-left:5px solid var(--oy-ok);
  padding:.6rem 1rem;border-radius:6px;margin-bottom:.7rem;color:#1d6b3a;}
.info{background:#E9F6F8;border-left:5px solid var(--oy-teal);
  padding:.7rem 1rem;border-radius:6px;margin-bottom:.7rem;color:#0E6873;}
.invis{background:#F0EAFB;border-left:5px solid #7E57C2;
  padding:.7rem 1rem;border-radius:6px;margin-bottom:.7rem;color:#4527a0;font-weight:600;}

.stTabs [data-baseweb="tab-list"]{gap:3px;flex-wrap:wrap;}
.stTabs [data-baseweb="tab"]{background:#F1FAFB;border-radius:8px 8px 0 0;
  padding:5px 10px;font-weight:600;color:var(--oy-td);}
.stTabs [aria-selected="true"]{background:var(--oy-teal)!important;color:#fff!important;}
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
    fig.update_layout(height=h, margin=dict(t=46,b=10,l=10,r=10),
                      font=dict(color=OY_INK, family="Segoe UI,sans-serif"),
                      plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                      title_font=dict(color=OY_TEAL_DARK, size=14))
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


def acumular_csv(archivo) -> pd.DataFrame:
    """Carga un CSV y lo acumula al histórico sin duplicar filas."""
    try:
        nuevo = pd.read_csv(archivo, dtype=str)
    except Exception as e:
        st.error(f"No se pudo leer el archivo: {e}")
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
    <p class="oy-htitle">Dashboard de Gestión · Atención al Cliente</p>
    <p class="oy-hsub">Vista Gerencial · powered by Treble · v3</p>
  </div>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🟢 Opción Yo · ATC v3")

    # ── CARGA ACUMULATIVA ────────────────────────────────────
    st.markdown("#### 📂 Fuente de datos")
    st.caption("Sube un CSV nuevo cada semana — se **agrega** al histórico sin borrar lo anterior.")

    ups = st.file_uploader(
        "Subir CSV de Treble (semanal o completo)",
        type=["csv"],
        key="uploader_csv",
        help="Puedes subir la semana completa o solo la semana nueva. El dashboard acumula automáticamente.")

    if ups is not None:
        nombre = ups.name
        if nombre not in st.session_state["archivos_cargados"]:
            with st.spinner(f"Acumulando {nombre}…"):
                acumular_csv(ups)
                st.session_state["archivos_cargados"].append(nombre)
            st.success(f"✅ {nombre} acumulado")

    # Mostrar estado del histórico
    if not st.session_state["df_historico"].empty:
        hist = st.session_state["df_historico"]
        st.markdown(f"📊 **Histórico acumulado:** {len(hist):,} filas · "
                    f"{len(st.session_state['archivos_cargados'])} archivo(s)")
        if st.session_state["archivos_cargados"]:
            with st.expander("Ver archivos cargados"):
                for i, f in enumerate(st.session_state["archivos_cargados"], 1):
                    st.caption(f"{i}. {f}")
        if st.button("🗑️ Limpiar histórico y empezar de cero", type="secondary"):
            st.session_state["df_historico"] = pd.DataFrame()
            st.session_state["archivos_cargados"] = []
            st.rerun()
    else:
        # Fallback: intentar cargar treble.csv local
        try:
            acumular_csv("treble.csv")
            st.session_state["archivos_cargados"] = ["treble.csv (local)"]
        except Exception:
            st.warning("Sube al menos un CSV de Treble para comenzar.")
            st.stop()

    # Procesar el histórico acumulado
    if st.session_state["df_historico"].empty:
        st.warning("Sube al menos un CSV de Treble para comenzar.")
        st.stop()

    try:
        df_raw = load_data(io.StringIO(
            st.session_state["df_historico"].to_csv(index=False)))
    except Exception as e:
        st.error(f"Error procesando datos: {e}")
        st.stop()

    st.divider()
    st.markdown("#### 🔍 Filtros")
    fmin = df_raw["created_at"].min().date()
    fmax = df_raw["created_at"].max().date()
    rango = st.date_input("📅 Fechas", value=(fmin, fmax), min_value=fmin, max_value=fmax)
    f_ini = rango[0] if len(rango)==2 else fmin
    f_fin = rango[1] if len(rango)==2 else fmax

    ags   = st.multiselect("👤 Agentes", sorted(df_raw["agent"].dropna().unique()), placeholder="Todos")
    colas = st.multiselect("📂 Cola/Equipo", sorted(df_raw["tag"].dropna().unique()), placeholder="Todas") if "tag" in df_raw.columns else []
    regs  = st.multiselect("🌎 Región", sorted(df_raw["region"].dropna().unique()), placeholder="Todas")
    all_lbl = sorted({l.strip() for lst in df_raw["labels"].dropna() for l in lst.split(",") if l.strip()})
    labs  = st.multiselect("🏷️ Etiquetas", all_lbl, placeholder="Todas")
    ests  = st.multiselect("🔖 Estado", sorted(df_raw["status"].dropna().unique()), placeholder="Todos")

    st.divider()
    gran = st.radio("Evolución por", ["Día","Semana","Mes"], index=1, horizontal=True)
    gc   = {"Día":"fecha","Semana":"semana","Mes":"mes"}[gran]
    outliers_on = st.toggle("Incluir outliers duración >5h", value=False)
    st.caption(f"Metas: Calif≥{META_RATING} · TPR≤{META_TPR}min · SLA2≥{META_SLA2}% · Churn≤{META_CHURN}%")

# ── Aplicar filtros ──────────────────────────────────────────
df = df_raw.copy()
df = df[(df["created_at"].dt.date >= f_ini) & (df["created_at"].dt.date <= f_fin)]
if ags:   df = df[df["agent"].isin(ags)]
if colas: df = df[df["tag"].isin(colas)]
if regs:  df = df[df["region"].isin(regs)]
if ests:  df = df[df["status"].isin(ests)]
if labs:
    pat = "|".join(l.replace("+","\\+").replace(".","\\+") for l in labs)
    df = df[df["labels"].fillna("").str.contains(pat, case=False)]
if not outliers_on:
    df = df[~df["dur_outlier"].fillna(False)]

# ── Aplicar ajustes de calificación ─────────────────────────
# Los chats marcados como "excluir" en la pestaña de ajustes
# tienen su rating_num puesto a NaN para que no entren en promedios.
# La columna "rating_ajustado" indica si fue modificado.
df = df.copy()
df["rating_original"] = df["rating_num"].copy()
df["rating_ajustado"] = False
ajustes = st.session_state.get("ajustes_rating", {})
if ajustes:
    for chat_id, info in ajustes.items():
        if info.get("excluir"):
            mask = df["chat_id"] == chat_id
            df.loc[mask, "rating_num"] = np.nan
            df.loc[mask, "rating_ajustado"] = True
if df.empty:
    st.warning("No hay datos para los filtros seleccionados.")
    st.stop()

# ── KPIs globales ────────────────────────────────────────────
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
pct_vol_recur = safe_pct(contactos[contactos>=2].sum(), N)
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

# ── KPIs de calificación detallados (fuente: rating_num 1–5) ─────────
# Solo sobre los {n_cal} chats que SÍ calificaron (36% del total).
# Los que no calificaron quedan fuera — eso se advierte en pantalla.
n_rating  = {i: int((df["rating_num"] == i).sum()) for i in [1,2,3,4,5]}
n_bajas   = n_rating[1] + n_rating[2] + n_rating[3]   # 1★ 2★ 3★
n_altas   = n_rating[4] + n_rating[5]                  # 4★ 5★
pct_1     = safe_pct(n_rating[1], n_cal)
pct_2     = safe_pct(n_rating[2], n_cal)
pct_3     = safe_pct(n_rating[3], n_cal)
pct_4     = safe_pct(n_rating[4], n_cal)
pct_5     = safe_pct(n_rating[5], n_cal)
pct_bajas = safe_pct(n_bajas, n_cal)
pct_altas = safe_pct(n_altas, n_cal)
prom_bajas = df.loc[df["rating_num"] <= 3, "rating_num"].mean()
prom_altas = df.loc[df["rating_num"] >= 4, "rating_num"].mean()

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
    "Erika Quiñonez":   "Erika Quinonez",
}
RESP_FILAS = [
    "Chats atendidos",
    "Rating ATC",
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
    """Usa las columnas ya calculadas por load_data (rating_num, tpr_min, dur_min)."""
    d = dfr.copy()
    asg = d["assigned_at"] if "assigned_at" in d.columns else d["created_at"]
    d["_fecha"] = asg.fillna(d["created_at"])
    d = d[d["_fecha"].notna()].copy()
    d["_rating"] = d["rating_num"]
    d["_tpr"]    = d["tpr_min"]
    d["_dur"]    = d["dur_min"]
    wd = d["_fecha"].dt.weekday                      # lun=0 … dom=6
    d["_domingo"] = (d["_fecha"] + pd.to_timedelta(6 - wd, unit="D")).dt.normalize()
    d["_mes"]     = d["_fecha"].dt.to_period("M")
    return d


def resp_bloque(g: pd.DataFrame) -> dict:
    n = len(g)
    if n == 0:
        return {f: "" for f in RESP_FILAS}
    r, tpr = g["_rating"], g["_tpr"]
    return {
        "Chats atendidos": n,
        "Rating ATC": round(r.mean(), 2) if r.notna().any() else "",
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


def resp_tabla(d: pd.DataFrame, agente_real=None, cierres=True) -> pd.DataFrame:
    reales = list(RESP_AGENTES.values())
    base = d[d["agent"].isin(reales)] if agente_real is None \
        else d[d["agent"] == agente_real]
    cols = {}
    for dom, g in sorted(base.groupby("_domingo"), key=lambda x: x[0]):
        cols[pd.Timestamp(dom).strftime("%d/%m/%Y")] = resp_bloque(g)
    if cierres:
        for per, g in sorted(base.groupby("_mes"), key=lambda x: x[0]):
            cols[f"Cierre {RESP_MESES[per.month]} {per.year}"] = resp_bloque(g)
    return pd.DataFrame(cols).reindex(RESP_FILAS)


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


(t1, t2, t3, t4, t5, t6, t7, t8, t9, t_aj, t_resp, t_esp) = st.tabs([
    "🏠 Resumen Ejecutivo",
    "⭐ Calificación",
    "🚨 Cancelaciones & Churn",
    "⚡ Tiempo de Respuesta",
    "📊 Rendimiento Agentes",
    "🏷️ Etiquetas & Motivos",
    "📞 Clientes que más llaman",
    "📋 Explorador de Chats",
    "💡 Insights & Recomendaciones",
    "⚙️ Ajuste de Calificaciones",
    "📑 Respaldo Excel",
    "🎓 Especialistas: Calif. bajas",
])


# ╔═══════════════════════════════════════╗
#  TAB 1 — RESUMEN EJECUTIVO
# ╚═══════════════════════════════════════╝
with t1:
    st.caption(
        f"📅 **{f_ini} → {f_fin}** · {N:,} chats · {df['agent'].nunique()} agentes · "
        f"Pico: {dia_pico} {hora_pico:02d}h · Fuente: treble.csv"
    )

    # ── Alertas automáticas ──────────────────────────────────
    if pct_churn > META_CHURN:
        st.markdown(
            f'<div class="crit">🚨 <b>CHURN DE PLAN {pct_churn}%</b> — '
            f'{int(df["es_churn"].sum()):,} chats "Cancelar plan / Reembolso" '
            f'(meta ≤{META_CHURN}%). Pérdida directa de ingresos.</div>',
            unsafe_allow_html=True)
    if pct_ghost > META_GHOST:
        st.markdown(
            f'<div class="crit">👻 <b>CHATS FANTASMA {pct_ghost}%</b> — '
            f'{n_ghost:,} chats cerrados con el último mensaje del cliente. '
            f'Nadie respondió antes del cierre.</div>',
            unsafe_allow_html=True)
    if pct_cal < META_CAL:
        st.markdown(
            f'<div class="alrt">⚠️ <b>Cobertura encuesta {pct_cal}%</b> — '
            f'rating calculado sobre {n_cal:,} de {N:,} chats. '
            f'El insatisfecho abandona sin calificar: el promedio sobreestima la satisfacción real.</div>',
            unsafe_allow_html=True)
    if pct_sla2 >= META_SLA2:
        st.markdown(
            f'<div class="good">✅ <b>SLA ≤2 min: {pct_sla2}%</b> — '
            f'promedio {fmt_min(tpr_prom)}. Operación de respuesta de primer nivel.</div>',
            unsafe_allow_html=True)

    # ╌╌╌ BLOQUE 1: TOTALES OPERACIONALES ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
    st.markdown('<div class="sec">📊 Totales Operacionales</div>', unsafe_allow_html=True)
    st.caption("Fuente: todos los campos del CSV de Treble (treble.csv). "
               "Los chats excluidos por filtro no se cuentan.")
    st.markdown('<div class="kpi-grid">' +
        kpi("Chats totales", f"{N:,}", f"{df['agent'].nunique()} agentes", kind="alt") +
        kpi("Clientes únicos", f"{len(contactos):,}",
            f"{N/len(contactos):.2f} chats/cliente prom") +
        kpi("TPR promedio", fmt_min(tpr_prom),
            f"= {tpr_prom:.1f} min · como lo calcula Treble",
            kind="ok" if not np.isnan(tpr_prom) and tpr_prom <= META_TPR else "warn") +
        kpi("% SLA ≤2 min", f"{pct_sla2}%",
            f"{int(df['sla_2min'].sum()):,} de {len(tpr_v):,} chats",
            kind="ok" if pct_sla2 >= META_SLA2 else "warn") +
        kpi("% SLA ≤5 min", f"{pct_sla5}%", kind="ok" if pct_sla5 >= 90 else "amber") +
        kpi("Churn de plan", f"{pct_churn}%",
            f"{int(df['es_churn'].sum()):,} chats · meta ≤{META_CHURN}%",
            kind="warn" if pct_churn > META_CHURN else "ok") +
        '</div>', unsafe_allow_html=True)

    # ╌╌╌ BLOQUE 2: CALIFICACIÓN TOTAL DETALLADA ╌╌╌╌╌╌╌╌╌╌╌╌╌╌
    st.markdown('<div class="sec">⭐ Calificación Total (detalle por estrella)</div>',
                unsafe_allow_html=True)
    st.caption(
        f"Fuente: columna **rating** del CSV. Solo {n_cal:,} de {N:,} chats "
        f"({pct_cal}%) recibieron calificación. Los {N-n_cal:,} sin calificar no entran en los promedios. "
        f"Se muestra el desglose para que gerencia vea la distribución real, no solo el promedio.")

    # Fila 1: KPIs globales de calificación
    st.markdown('<div class="kpi-grid">' +
        kpi("Promedio global (muestra)", f"{rating:.2f} ★",
            f"sobre {n_cal:,} calificados ({pct_cal}%)",
            kind="ok" if rating >= META_RATING else "amber") +
        kpi("Calificaciones 4★ y 5★", f"{n_altas:,}",
            f"{pct_altas}% de los que calificaron — promedio {prom_altas:.2f}★", kind="ok") +
        kpi("Calificaciones 1★, 2★ y 3★", f"{n_bajas:,}",
            f"{pct_bajas}% — promedio {prom_bajas:.2f}★ · detractores reales",
            kind="warn" if pct_bajas > 5 else "amber") +
        kpi("Sin calificar", f"{N - n_cal:,}",
            f"{100 - pct_cal}% del total — pueden ser insatisfechos", kind="dark") +
        '</div>', unsafe_allow_html=True)

    # Fila 2: Desglose estrella por estrella
    st.markdown("**Desglose estrella por estrella** — sobre los chats que sí calificaron:")
    st.markdown('<div class="kpi-grid">' +
        kpi("1 ★ (muy malo)", f"{n_rating[1]:,}", f"{pct_1}%", kind="warn") +
        kpi("2 ★ (malo)", f"{n_rating[2]:,}", f"{pct_2}%",
            kind="warn" if pct_2 > 2 else "amber") +
        kpi("3 ★ (regular)", f"{n_rating[3]:,}", f"{pct_3}%",
            kind="amber" if pct_3 > 3 else "") +
        kpi("4 ★ (bueno)", f"{n_rating[4]:,}", f"{pct_4}%", kind="ok") +
        kpi("5 ★ (excelente)", f"{n_rating[5]:,}", f"{pct_5}%", kind="ok") +
        '</div>', unsafe_allow_html=True)

    # Gráfico distribución de estrellas + gauges
    col_g1, col_g2, col_g3, col_g4 = st.columns([1.4, 1, 1, 1])
    with col_g1:
        dist_df = pd.DataFrame({
            "Estrella": ["1★","2★","3★","4★","5★"],
            "Chats":    [n_rating[i] for i in [1,2,3,4,5]],
            "%":        [pct_1, pct_2, pct_3, pct_4, pct_5],
        })
        colores = [OY_WARN, "#FF7043", OY_AMBER, OY_TEAL, OY_OK]
        fig_dist = go.Figure()
        for i, row in dist_df.iterrows():
            fig_dist.add_trace(go.Bar(
                x=[row["Chats"]], y=[row["Estrella"]],
                orientation="h", marker_color=colores[i],
                text=f'{row["Chats"]:,}  ({row["%"]:.1f}%)',
                textposition="outside", name=row["Estrella"],
                showlegend=False))
        fig_dist.update_layout(
            title="Distribución de calificaciones",
            yaxis={"categoryorder":"array","categoryarray":["1★","2★","3★","4★","5★"]},
            barmode="stack")
        st.plotly_chart(sfig(fig_dist, 260), use_container_width=True)
    with col_g2:
        st.plotly_chart(gauge("⭐ Promedio", rating, META_RATING, [1,5],
            [{"range":[1,4],"color":"#FADBD8"},{"range":[4,META_RATING],"color":"#FDEBD0"},
             {"range":[META_RATING,5],"color":"#D5F5E3"}]), use_container_width=True)
    with col_g3:
        st.plotly_chart(gauge("⚡ TPR prom (min)", min(tpr_prom or 30, 30), META_TPR, [0,30],
            [{"range":[0,META_TPR],"color":"#D5F5E3"},{"range":[META_TPR,15],"color":"#FDEBD0"},
             {"range":[15,30],"color":"#FADBD8"}]," min", True), use_container_width=True)
    with col_g4:
        st.plotly_chart(gauge("💸 Churn", pct_churn, META_CHURN, [0,30],
            [{"range":[0,META_CHURN],"color":"#D5F5E3"},{"range":[META_CHURN,18],"color":"#FDEBD0"},
             {"range":[18,30],"color":"#FADBD8"}],"%", True), use_container_width=True)

    # ╌╌╌ NARRATIVA AUTOMÁTICA ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
    peor_reg = (df.groupby("region")["es_churn"].mean()*100).sort_values(ascending=False)
    reg_txt  = f"{peor_reg.index[0]} ({peor_reg.iloc[0]:.0f}%)" if len(peor_reg) else "–"
    st.markdown(
        f'<div class="info">'
        f'• <b>Retención es el frente crítico:</b> {pct_churn}% churn + {pct_reprog}% reprogramaciones. '
        f'Motivo #1 de contacto: <b>{top_motivo}</b>. Región con mayor churn: {reg_txt}.<br>'
        f'• <b>Calificación con matices:</b> promedio {rating:.2f}★ sobre el {pct_cal}% que calificó. '
        f'De ellos, {pct_altas}% dieron 4★–5★ y {pct_bajas}% dieron 1★–3★ '
        f'({n_bajas:,} detractores reales).<br>'
        f'• <b>Velocidad de respuesta excepcional:</b> {pct_sla2}% responde en ≤2 min '
        f'(promedio {fmt_min(tpr_prom)} · mediana {fmt_min(tpr_med)}). Activo diferenciador.</div>',
        unsafe_allow_html=True)

    # ╌╌╌ BLOQUE 3: CLIENTES QUE MÁS CONTACTAN (resumen) ╌╌╌╌╌
    st.markdown('<div class="sec">📞 Clientes que más contactan</div>', unsafe_allow_html=True)
    st.caption(
        "Fuente: columna **phone** del CSV — se agrupa por número de teléfono. "
        "Se cuentan todas las conversaciones por cliente en el período filtrado. "
        "Ver pestaña **📋 Clientes & Detalle** para la tabla completa y explorador.")
    st.markdown('<div class="kpi-grid">' +
        kpi("Vol. recurrente", f"{pct_vol_recur}%",
            f"{int(contactos[contactos>=2].sum()):,} de {N:,} chats vienen de clientes con ≥2 contactos",
            kind="alt") +
        kpi("Clientes recurrentes (≥2)", f"{n_recur:,}",
            f"de {len(contactos):,} únicos · {safe_pct(n_recur, len(contactos))}% volvió a contactar",
            kind="amber") +
        kpi("Máx contactos 1 cliente", f"{int(contactos.max())}",
            "cliente con mayor recurrencia del período", kind="warn") +
        kpi("Reintentos mismo día", f"{n_reint:,}",
            "mismo cliente >1 vez en un día → problema no resuelto", kind="dark") +
        '</div>', unsafe_allow_html=True)

    # Mini-tabla top 5 + gráfico motivos — el detalle completo está en tab 7
    tc_mini = top_clientes(df, 5)
    cm1, cm2 = st.columns([1, 1.2])
    with cm1:
        st.markdown("**Top 5 clientes** — ver pestaña 📋 para los 25 completos")
        sty_mini = (tc_mini.style
                    .map(lambda v: f"color:{OY_WARN};font-weight:700" if v=="Sí" else "",
                         subset=["¿Churn?"])
                    .format({"Rating prom":"{:.2f}"}))
        st.dataframe(sty_mini, use_container_width=True, hide_index=True, height=230)
        st.markdown("👉 **[Ver tabla completa en pestaña 📋 Clientes & Detalle]**")
    with cm2:
        st.markdown("**Por qué llaman** los clientes recurrentes (≥2 contactos en el período)")
        st.caption("Fuente: columna labels · Se toma la primera etiqueta de cada chat")
        rec_ph = set(contactos[contactos >= 2].index)
        rexp_m = (df[df["phone"].isin(rec_ph)]["labels"]
                  .fillna("Sin etiqueta").str.split(r",\s*").explode().str.strip())
        rmot_m = rexp_m.value_counts().head(8).reset_index()
        rmot_m.columns = ["Motivo","Chats"]
        fig_m = px.bar(rmot_m, x="Chats", y="Motivo", orientation="h",
                       color="Chats", color_continuous_scale="Teal", text="Chats")
        fig_m.update_traces(textposition="outside")
        fig_m.update_layout(showlegend=False, yaxis={"categoryorder":"total ascending"})
        st.plotly_chart(sfig(fig_m, 280), use_container_width=True)


# ╔═══════════════════════════════════════╗
#  TAB 2 — CALIFICACIÓN
# ╚═══════════════════════════════════════╝
with t2:
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
        st.caption("Solo clientes con etiqueta 'Cancelar plan' o 'Reembolso' — "
                   "no incluye cancelaciones de sesión")
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
            st.caption("💡 Para ver los chats individuales de un cliente, "
                       "copia su teléfono y pégalo en el buscador de la pestaña 📋 Explorador de Chats")
            st.download_button("⬇️ CSV churn de plan",
                               cc_df.to_csv(index=False).encode(),
                               "churn_plan.csv","text/csv")


# ╔═══════════════════════════════════════╗
#  TAB 4 — TIEMPO DE RESPUESTA
# ╚═══════════════════════════════════════╝
with t4:
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
    st.caption("🟢 Verde = rápido (bueno) · 🔴 Rojo = lento (problema). "
               "La barra de <1 min es verde porque el 96.7% de los chats se asigna en menos de 1 minuto — eso es excelente.")

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
            st.caption("Correlación TPR vs Rating: casi nula (r≈-0.02). El cliente no penaliza mucho el tiempo — "
                       "pero >30min sí baja el rating de 4.78 → 4.62.")


# ╔═══════════════════════════════════════╗
#  TAB 5 — RENDIMIENTO AGENTES
# ╚═══════════════════════════════════════╝
with t5:
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
        st.caption("Fuente: columna labels · clientes con ≥2 contactos en el período")
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
        st.caption("Fuente: columna phone · distribución de frecuencia por cliente")
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
    st.caption("Fuente: columna rating · comparativa de satisfacción según frecuencia de contacto")
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
    st.markdown('<div class="sec">📋 Explorador de Chats (detalle individual)</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="info"><b>¿Qué ves aquí?</b> Cada fila es una conversación del CSV. '
        'Filtra por cliente, teléfono o etiqueta. '
        '<code>TPR (min)</code> = tiempo desde asignación hasta primer mensaje del agente · '
        '<code>Handle (min)</code> = tiempo real activo (primer → último mensaje) · '
        '<code>Fantasma</code> = último mensaje fue del cliente, no del agente. '
        'Descarga el resultado para análisis externo.</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="invis">🔮 <b>KPI INVISIBLE #6 — Handle Time Activo Real</b><br>'
        f'La columna <code>duration</code> mide tiempo hasta el cierre (a veces días después). '
        f'El handle time real (primer→último mensaje) es mediana <b>{fmt_min(hnd_med)}</b> '
        f'vs duración promedio ~327 min. El trabajo real del agente es 6× menor de lo que sugiere la duración.</div>',
        unsafe_allow_html=True)

    st.markdown('<div class="kpi-grid">' +
        kpi("Handle time real (mediana)", fmt_min(hnd_med), "primer→último mensaje activo", kind="alt") +
        kpi("Duración promedio (CSV)", fmt_min(df["dur_min"].mean()),
            "incluye tiempo post-cierre manual", kind="dark") +
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
    st.markdown('<div class="sec">💡 Insights & Recomendaciones Estratégicas</div>',
                unsafe_allow_html=True)
    st.caption(f"Basado en análisis de {N:,} chats · {f_ini} → {f_fin} · Para uso estratégico del equipo directivo")

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
    st.markdown('<div class="sec">⚙️ Ajuste de Calificaciones</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="info">'
        '<b>¿Para qué sirve esta pestaña?</b><br>'
        'A veces un cliente califica bajo no por el trabajo del agente, sino porque: '
        'respondió "1" sin querer a una pregunta del bot, tuvo un problema con la plataforma, '
        'o su insatisfacción es con el servicio en general y no con la atención. '
        '<br><br>'
        'Aquí puedes <b>excluir esas calificaciones del promedio</b> registrando el motivo. '
        'Los chats excluidos <b>no se borran</b> — solo se sacan del cálculo del rating. '
        'El cambio persiste mientras no recargues la página. '
        'Puedes descargarlo en CSV para llevar un registro histórico.'
        '</div>', unsafe_allow_html=True)

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


# ╔════════════════════════════════════════════════════════════╗
#  TAB 11 — RESPALDO EXCEL (histórico semanal / mensual por agente)
# ╚════════════════════════════════════════════════════════════╝
with t_resp:
    st.markdown('<div class="sec">📑 Respaldo Excel · Histórico semanal y mensual por agente</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="info"><b>¿Para qué sirve?</b><br>'
        'Reproduce exactamente las filas que llenas a mano en la hoja '
        '<b>“AgenteHistorico semanal”</b> del Excel, calculadas desde el treble. '
        'Sube tu CSV en el panel lateral, elige la semana y copia la columna al Excel.<br>'
        'Muestra siempre los <b>9 agentes</b> indicados, ignorando los filtros de fecha '
        'del panel (para que tengas todo el histórico disponible).</div>',
        unsafe_allow_html=True)

    rd = resp_preparar(df_raw)
    reales = list(RESP_AGENTES.values())
    presentes = [a for a in reales if a in set(rd["agent"].unique())]
    faltan = [etq for etq, real in RESP_AGENTES.items() if real not in presentes]
    if faltan:
        st.markdown('<div class="alrt">Sin datos en este CSV para: '
                    + ", ".join(faltan) + '</div>', unsafe_allow_html=True)

    cierres_on = st.toggle("Incluir columnas de cierre mensual", value=True, key="resp_cierres")

    domingos = sorted(rd[rd["agent"].isin(reales)]["_domingo"].unique())
    if not domingos:
        st.warning("No hay chats de estos 9 agentes en el histórico cargado.")
    else:
        labels_sem = [pd.Timestamp(x).strftime("%d/%m/%Y") for x in domingos]

        # ── 1) Vista por semana (para copiar) ──────────────────────
        st.markdown("##### 1️⃣ Por semana — vista para copiar")
        sem = st.selectbox("Semana (domingo que cierra la semana)",
                           labels_sem, index=len(labels_sem)-1, key="resp_sem")
        objetivo = pd.Timestamp(pd.to_datetime(sem, format="%d/%m/%Y")).normalize()
        sub = rd[rd["_domingo"] == objetivo]
        cols_sem = {"TOTAL (9 agentes)": resp_bloque(sub[sub["agent"].isin(reales)])}
        for etq, real in RESP_AGENTES.items():
            cols_sem[etq] = resp_bloque(sub[sub["agent"] == real])
        tab_sem = pd.DataFrame(cols_sem).reindex(RESP_FILAS)
        st.dataframe(tab_sem, use_container_width=True, height=420)
        st.markdown(
            '<div class="alrt">⚠️ <b>“Tiempo medio interacción” queda en blanco a propósito.</b> '
            'Treble lo calcula a nivel de mensajes y no viene en este CSV — es la única '
            'celda que debes copiar del panel de Treble. Las otras 9 son automáticas.</div>',
            unsafe_allow_html=True)

        # ── 2) Histórico completo por agente ───────────────────────
        st.divider()
        st.markdown("##### 2️⃣ Histórico completo (todas las semanas y meses)")
        with st.expander("🟢 TOTALES — los 9 agentes juntos", expanded=True):
            st.dataframe(resp_tabla(rd, None, cierres_on), use_container_width=True)
        for etq, real in RESP_AGENTES.items():
            if real not in presentes:
                continue
            with st.expander(f"👤 {etq}"):
                st.dataframe(resp_tabla(rd, real, cierres_on), use_container_width=True)

        # ── 3) Descargas ───────────────────────────────────────────
        st.divider()
        st.markdown("##### 3️⃣ Descargar")
        c_dl1, c_dl2 = st.columns(2)
        with c_dl1:
            csv_tot = resp_tabla(rd, None, cierres_on).to_csv().encode("utf-8")
            st.download_button("⬇️ Totales (.csv)", csv_tot,
                               "respaldo_totales.csv", "text/csv", key="resp_csv")
        with c_dl2:
            try:
                xls = resp_exportar_excel(rd, cierres_on)
                st.download_button(
                    "⬇️ Respaldo completo (.xlsx)", xls,
                    "respaldo_historico_semanal.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="resp_xlsx")
            except Exception:
                st.caption("Para habilitar el Excel (.xlsx), añade `openpyxl` "
                           "a requirements.txt. Mientras tanto usa el CSV.")


# ╔════════════════════════════════════════════════════════════╗
#  TAB 12 — ESPECIALISTAS: CALIFICACIONES BAJAS (solicitud de Iva)
# ╚════════════════════════════════════════════════════════════╝
with t_esp:
    st.markdown('<div class="sec amb">🎓 Especialistas · seguimiento de calificaciones bajas</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="info"><b>¿Para qué sirve?</b><br>'
        'Detecta qué <b>especialistas calificaron bajo</b> y quiénes lo hacen de forma '
        'repetida, para contactarlos, hacer una encuesta y entender en qué mejorar. '
        'Incluye una señal clave: especialistas que calificaron bajo y luego '
        '<b>dejaron de calificar</b> (descontento silencioso = riesgo de fuga).<br>'
        'Muestra la cola completa ignorando los filtros de fecha del panel.</div>',
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
st.caption(f"Opción Yo · Dashboard ATC v3 · {N:,} chats analizados · "
           f"Metas: Calif≥{META_RATING} · TPR≤{fmt_min(META_TPR)} · "
           f"SLA2≥{META_SLA2}% · Churn≤{META_CHURN}% · "
           f"Streamlit + Plotly · Datos: treble.csv")
