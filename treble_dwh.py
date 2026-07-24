"""
╔══════════════════════════════════════════════════════════════════╗
║  treble_dwh.py · Data Warehouse de Treble (ClickHouse) en vivo    ║
║  para el Dashboard ATC — Opción Yo                                ║
║                                                                   ║
║  · Credenciales SOLO desde Streamlit Secrets (nunca en código).   ║
║  · Solo lectura. Datos con retraso máx. 3 h · últimos 3 meses.    ║
║  · Da los indicadores EXACTOS de Treble (misma fuente).           ║
╚══════════════════════════════════════════════════════════════════╝

Secrets (Streamlit → Settings → Secrets):
    [treble_dwh]
    host = "eaoxkoa7g7.us-east-1.aws.clickhouse.cloud"
    port = 8443
    user = "opcionyo_readonly"
    password = "TU_CONTRASEÑA"
    database = "client_analytics"

requirements.txt:  clickhouse-connect
"""

import pandas as pd
import streamlit as st

DB = "client_analytics"
# Colas ATC (Vista Treble). Ajustable si cambia la operación.
ATC_TAGS = ["default", "especialistas", "sdd"]


def dwh_activo() -> bool:
    try:
        return bool(st.secrets.get("treble_dwh"))
    except Exception:
        return False


@st.cache_resource(show_spinner=False)
def _client():
    import clickhouse_connect
    c = st.secrets["treble_dwh"]
    user = c.get("username") or c.get("user") or c.get("usuario")
    pwd  = c.get("password") or c.get("contraseña") or c.get("pass") or c.get("contrasena")
    host = c.get("host") or c.get("servidor")
    return clickhouse_connect.get_client(
        host=host, port=int(c.get("port", 8443)),
        username=user, password=pwd, secure=True,
        connect_timeout=15, send_receive_timeout=90,
        database=c.get("database", DB))


@st.cache_data(ttl=600, show_spinner="⏳ Consultando Data Warehouse de Treble…")
def q(sql: str) -> pd.DataFrame:
    """Ejecuta SQL de solo lectura y devuelve un DataFrame (cache 10 min)."""
    return _client().query_df(sql)


def probar_conexion() -> tuple:
    """(ok: bool, mensaje: str). Para el botón de prueba en el dashboard."""
    try:
        cli = _client()
        v = cli.server_version
        t = cli.query_df(f"SHOW TABLES FROM {DB}")
        return True, f"Conectado ✓ · ClickHouse {v} · {len(t)} tablas"
    except Exception as e:
        return False, f"{type(e).__name__}: {str(e)[:200]}"


# ── TIEMPO MEDIO DE INTERACCIÓN (oficial · fact_agent_daily) ──────
@st.cache_data(ttl=600)
def interaccion_oficial_semanal(dias: int = 120) -> pd.DataFrame:
    """Interacción EXACTA de Treble = avg_response_time_sec de fact_agent_daily
    (métrica ya calculada por Treble), ponderada por chats atendidos y por semana."""
    sql = f"""
    SELECT
        toStartOfWeek(day, 1) AS semana,
        round(medianIf(avg_response_time_sec, avg_response_time_sec > 0), 0) AS interaccion_seg
    FROM {DB}.fact_agent_daily
    WHERE day >= now() - INTERVAL {dias} DAY
      AND chats_handled > 0
    GROUP BY semana
    ORDER BY semana
    """
    return q(sql)


# ── DATOS DE IA / BOT (desde fact_sessions) ──────────────────────
@st.cache_data(ttl=600)
def ia_semanal(dias: int = 120) -> pd.DataFrame:
    """Métricas de IA del Excel de gerencia, usando fact_sessions.status:
       'AI' = cerrado por el bot · 'HumanHandover' = derivado a agente.
       Total IA = AI + HumanHandover (coincide con el Excel: Total = Derivados + Cerrados)."""
    sql = f"""
    SELECT
        toStartOfWeek(created_at, 1)                            AS semana,
        countIf(status IN ('AI', 'HumanHandover'))              AS total_chats_ia,
        countIf(status = 'HumanHandover')                       AS ia_derivados,
        countIf(status = 'AI')                                  AS ia_cerrados,
        round(countIf(status = 'HumanHandover') * 100.0
              / nullIf(countIf(status IN ('AI', 'HumanHandover')), 0), 2) AS pct_derivacion_ia
    FROM {DB}.fact_sessions
    WHERE created_at >= now() - INTERVAL {dias} DAY
      AND lower(inbound_outbound) = 'inbound'
    GROUP BY semana
    ORDER BY semana
    """
    return q(sql)


# ── RESUMEN ATC DIARIO (en vivo · formato del reporte de Yésica) ──
@st.cache_data(ttl=600)
def _col_equipo() -> str:
    cols = columnas("fact_conversations")
    return "team_name" if "team_name" in cols else "tag_name"


@st.cache_data(ttl=600)
def equipos_disponibles() -> list:
    col = _col_equipo()
    try:
        d = q(f"SELECT DISTINCT {col} AS eq FROM {DB}.fact_conversations "
              f"WHERE created_at >= now() - INTERVAL 60 DAY ORDER BY eq")
        return [x for x in d["eq"].tolist() if x and str(x).strip()]
    except Exception:
        return []


@st.cache_data(ttl=300)
def resumen_atc_dia(dia: str, equipos=None) -> pd.DataFrame:
    """Detalle por agente de UN día, calculado desde las conversaciones del
    equipo seleccionado (igual que el filtro 'Equipo' del panel de Treble)."""
    col = _col_equipo()
    filtro = ""
    if equipos:
        lst = "', '".join(str(e).lower().replace("'", "") for e in equipos)
        filtro = f"AND lower(c.{col}) IN ('{lst}')"
    sql = f"""
    SELECT
        c.agent_name                                              AS agente,
        count()                                                   AS chats,
        countIf(c.rating > 0)                                     AS calificados,
        round(avgIf(c.rating, c.rating > 0), 2)                   AS calificacion,
        round(avgIf(c.first_response_sec, c.first_response_sec >= 0), 0) AS primera_resp_seg,
        round(avgIf(dateDiff('second', c.created_at, c.finished_at),
                    c.finished_at IS NOT NULL), 0)                AS resolucion_seg
    FROM {DB}.fact_conversations AS c
    WHERE toDate(c.created_at) = toDate('{dia}')
      AND c.first_agent_message_at IS NOT NULL
      {filtro}
    GROUP BY c.agent_name
    ORDER BY chats DESC
    """
    return q(sql)


@st.cache_data(ttl=300)
def interaccion_dia(dia: str) -> pd.DataFrame:
    """Tiempo medio de interacción por agente (única fuente: fact_agent_daily)."""
    sql = f"""
    SELECT
        agent_name              AS agente,
        avg_response_time_sec   AS interaccion_seg
    FROM {DB}.fact_agent_daily
    WHERE toDate(day) = toDate('{dia}')
      AND chats_handled > 0
    """
    return q(sql)


@st.cache_data(ttl=300)
def ultimo_dia_dwh() -> str:
    d = q(f"SELECT max(toDate(day)) AS d FROM {DB}.fact_agent_daily")
    return str(d.iloc[0]["d"]) if not d.empty else ""


@st.cache_data(ttl=3600)
def columnas(tabla: str) -> list:
    """Columnas reales de una tabla (permite adaptarse al esquema sin adivinar)."""
    try:
        return list(q(f"DESCRIBE TABLE {DB}.{tabla}")["name"])
    except Exception:
        return []


@st.cache_data(ttl=600, show_spinner="⏳ Cargando conversaciones desde el Data Warehouse…")
def cargar_conversaciones(dias: int = 90) -> pd.DataFrame:
    """Trae fact_conversations con el MISMO esquema que el export CSV de Treble,
    para que el dashboard lo consuma sin cambios. Se adapta a las columnas que
    existan realmente (etiquetas, contacto, etc.)."""
    cols = columnas("fact_conversations")
    if not cols:
        return pd.DataFrame()

    def has(c):
        return c in cols

    def pick(*cands, default="''"):
        for c in cands:
            if has(c):
                return f"c.{c}"
        return default

    _labels = pick("labels", "label_names", "label_name", "labels_names", "tags", default="''")
    _contact = pick("contact_name", "contact", "customer_name", default="''")
    _phone = pick("contact_wa_id", "cellphone", "phone", "contact_phone", default="''")
    _lastmsg = pick("last_message_at", "last_message", default="c.finished_at")
    _sender = pick("last_message_sender", "last_sender", default="''")
    _transfer = ("c.last_transfer_from" if has("last_transfer_from")
                 else ("if(c.transfer_count > 0, 'transferido', NULL)" if has("transfer_count") else "NULL"))
    _finish = pick("finish_type", "finished_by", default="''")
    _assigned = pick("assigned_at", "first_assignment_at", default="c.created_at")

    sql = f"""
    SELECT
        toString({_phone})                                              AS phone,
        toString({_contact})                                            AS contact,
        toString(c.tag_name)                                            AS tag,
        toString(c.agent_name)                                          AS agent,
        formatDateTime(c.created_at, '%Y-%m-%d %H:%M:%S')               AS created_at,
        formatDateTime({_assigned}, '%Y-%m-%d %H:%M:%S')                AS assigned_at,
        if(c.finished_at IS NULL, '',
           formatDateTime(c.finished_at, '%Y-%m-%d %H:%M:%S'))          AS finished_at,
        toString({_transfer})                                           AS last_transfer_from,
        if(c.first_agent_message_at IS NULL, '',
           formatDateTime(c.first_agent_message_at, '%Y-%m-%d %H:%M:%S')) AS agent_first_message,
        if({_lastmsg} IS NULL, '',
           formatDateTime({_lastmsg}, '%Y-%m-%d %H:%M:%S'))             AS last_message,
        toString({_sender})                                             AS last_message_sender,
        formatDateTime(toDateTime(greatest(dateDiff('second', c.created_at,
            ifNull(c.finished_at, c.created_at)), 0), 'UTC'), '%H:%M:%S') AS duration,
        if(c.rating > 0, toString(c.rating), '-')                       AS rating,
        toString(c.status)                                              AS status,
        toString({_finish})                                             AS finish_type,
        formatDateTime(toDateTime(greatest(toInt64(ifNull(c.first_response_sec, 0)), 0),
                       'UTC'), '%H:%M:%S')   AS agent_first_message_from_allocation,
        toString({_labels})                                             AS labels
    FROM {DB}.fact_conversations AS c
    WHERE c.created_at >= now() - INTERVAL {dias} DAY
    """
    df = q(sql)
    if not df.empty:
        df["business_scope_id"] = ""
        df["agent_first_message_from_creation"] = df["agent_first_message_from_allocation"]
    return df


def _tags_sql() -> str:
    return "', '".join(ATC_TAGS)


# ── EXPLORACIÓN (temporal, para descubrir esquema de IA y calibrar) ─
@st.cache_data(ttl=600)
def listar_tablas() -> pd.DataFrame:
    return q(f"SHOW TABLES FROM {DB}")


@st.cache_data(ttl=600)
def muestra(tabla: str, n: int = 5) -> pd.DataFrame:
    return q(f"SELECT * FROM {DB}.{tabla} LIMIT {int(n)}")


@st.cache_data(ttl=600)
def distribucion(tabla: str, col: str) -> pd.DataFrame:
    return q(f"SELECT {col}, count() AS filas FROM {DB}.{tabla} "
             f"GROUP BY {col} ORDER BY filas DESC LIMIT 30")


@st.cache_data(ttl=600)
def interaccion_calibracion(dias: int = 30) -> pd.DataFrame:
    """Varias definiciones de 'interacción' para comparar contra Treble y elegir la correcta."""
    sql = f"""
    WITH conv AS (
        SELECT
            conversation_id,
            dateDiff('second', minIf(created_at, sender='AGENT'),
                     maxIf(created_at, sender='AGENT'))            AS span_agente,
            dateDiff('second', minIf(created_at, sender='AGENT'),
                     max(created_at))                              AS hasta_ultimo
        FROM {DB}.fact_agent_messages
        WHERE created_at >= now() - INTERVAL {dias} DAY
        GROUP BY conversation_id
        HAVING countIf(sender='AGENT') > 0
    )
    SELECT
        round(avg(span_agente), 0)       AS prom_span_agente_seg,
        round(median(span_agente), 0)    AS mediana_span_agente_seg,
        round(avg(hasta_ultimo), 0)      AS prom_hasta_ultimo_seg,
        round(median(hasta_ultimo), 0)   AS mediana_hasta_ultimo_seg
    FROM conv
    """
    return q(sql)


# ── MÉTRICAS SEMANALES ATC (exactas · fact_conversations) ─────────
@st.cache_data(ttl=600)
def metricas_semanales(dias: int = 120) -> pd.DataFrame:
    """Réplica del Histórico Semanal Global de Angela, con los números
    EXACTOS de Treble. 'atendido' = el agente respondió (first_agent_message_at)."""
    sql = f"""
    SELECT
        toStartOfWeek(created_at, 1)                                   AS semana,
        count()                                                        AS chats_atendidos,
        round(avgIf(rating, rating > 0), 2)                            AS rating_atc,
        countIf(rating > 0)                                            AS chats_calificados,
        round(countIf(rating > 0) * 100.0 / count(), 2)               AS pct_calificados,
        round(countIf(rating < 4 AND rating > 0) * 100.0 / count(), 2) AS pct_rating_bajo4,
        round(countIf(rating > 4) * 100.0 / count(), 2)               AS pct_rating_sobre4,
        round(medianIf(first_response_sec, first_response_sec > 0), 0)     AS primera_resp_seg,
        round(countIf(first_response_sec <= 300) * 100.0 / count(), 2) AS pct_5min,
        round(countIf(first_response_sec > 300 AND first_response_sec <= 600) * 100.0 / count(), 2) AS pct_10min,
        round(countIf(first_response_sec > 1800) * 100.0 / count(), 2) AS pct_30min,
        round(medianIf(dateDiff('second', created_at, finished_at),
                    finished_at IS NOT NULL), 0)                       AS resolucion_seg
    FROM {DB}.fact_conversations
    WHERE created_at >= now() - INTERVAL {dias} DAY
      AND first_agent_message_at IS NOT NULL
      AND lower(inbound_outbound) = 'inbound'
      AND lower(tag_name) IN ('{_tags_sql()}')
    GROUP BY semana
    ORDER BY semana
    """
    return q(sql)


# ── TIEMPO MEDIO DE INTERACCIÓN (desde mensajes) ──────────────────
@st.cache_data(ttl=600)
def interaccion_semanal(dias: int = 120) -> pd.DataFrame:
    """Interacción por semana calculada a nivel de mensajes (lo que faltaba
    en el CSV). Definición: (último mensaje − primer mensaje del agente) por
    conversación, promediado. ⚠️ Calibrar contra la UI de Treble la 1ª vez."""
    sql = f"""
    WITH conv AS (
        SELECT
            conversation_id,
            toStartOfWeek(min(created_at), 1) AS semana,
            dateDiff('second',
                     minIf(created_at, sender = 'AGENT'),
                     max(created_at))          AS interac_seg
        FROM {DB}.fact_agent_messages
        WHERE created_at >= now() - INTERVAL {dias} DAY
        GROUP BY conversation_id
        HAVING countIf(sender = 'AGENT') > 0
    )
    SELECT semana, round(avg(interac_seg), 0) AS interaccion_seg
    FROM conv
    GROUP BY semana
    ORDER BY semana
    """
    return q(sql)


# ── MÉTRICAS POR AGENTE (para 'Agente Histórico Semanal') ─────────
@st.cache_data(ttl=600)
def metricas_por_agente(dias: int = 120) -> pd.DataFrame:
    sql = f"""
    SELECT
        agent_name,
        toStartOfWeek(created_at, 1)                                   AS semana,
        count()                                                        AS chats_atendidos,
        round(avgIf(rating, rating > 0), 2)                            AS rating_atc,
        round(countIf(rating < 4 AND rating > 0) * 100.0 / count(), 2) AS pct_rating_bajo4,
        round(countIf(rating > 4) * 100.0 / count(), 2)               AS pct_rating_sobre4,
        round(avgIf(first_response_sec, first_response_sec > 0), 0)    AS primera_resp_seg,
        round(countIf(first_response_sec <= 300) * 100.0 / count(), 2) AS pct_5min,
        round(countIf(first_response_sec > 1800) * 100.0 / count(), 2) AS pct_30min,
        round(avgIf(dateDiff('second', created_at, finished_at),
                    finished_at IS NOT NULL), 0)                       AS resolucion_seg
    FROM {DB}.fact_conversations
    WHERE created_at >= now() - INTERVAL {dias} DAY
      AND first_agent_message_at IS NOT NULL
      AND lower(tag_name) IN ('{_tags_sql()}')
    GROUP BY agent_name, semana
    ORDER BY agent_name, semana
    """
    return q(sql)
