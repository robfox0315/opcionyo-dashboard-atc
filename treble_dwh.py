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
