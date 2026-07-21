"""Interfaz web de ClinicFlow AI Agent."""

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from src.agent import ClinicAgent
from src.document_loader import load_knowledge_base
from src.retriever import ClinicRetriever

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "clinic_knowledge_base.csv"

load_dotenv()

st.set_page_config(
    page_title="ClinicFlow | Asistente de Clínica Horizonte",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    :root {
        --brand: #087f75;
        --brand-dark: #075f5a;
        --ink: var(--text-color);
        --muted: var(--text-color);
        --line: rgba(128, 145, 148, .28);
        --surface: var(--secondary-background-color);
        --soft: rgba(8, 127, 117, .11);
    }
    .stApp {
        background:
          radial-gradient(circle at 8% 0%, rgba(13,148,136,.08), transparent 28rem),
          var(--background-color);
        color: var(--ink);
    }
    .block-container { max-width: 900px; padding-top: 5rem; padding-bottom: 2rem; }
    .clinic-nav {
        display: flex; align-items: center; justify-content: space-between;
        gap: 1rem; margin-bottom: 1.4rem;
    }
    .brand { display: flex; align-items: center; gap: .75rem; }
    .brand-mark {
        width: 42px; height: 42px; border-radius: 13px; display: grid;
        place-items: center; color: white; background: var(--brand);
        font-size: 1.25rem; box-shadow: 0 8px 20px rgba(8,127,117,.22);
    }
    .brand-name { font-weight: 750; font-size: 1.08rem; letter-spacing: -.01em; }
    .brand-sub { color: var(--muted); opacity: .68; font-size: .78rem; }
    .online-pill {
        display: inline-flex; align-items: center; gap: .45rem; white-space: nowrap;
        padding: .45rem .75rem; border: 1px solid #c8e9df; border-radius: 999px;
        color: #176c5c; background: #f0fdf9; font-size: .78rem; font-weight: 650;
    }
    .online-dot { width: 7px; height: 7px; border-radius: 50%; background: #20a678; }
    .hero {
        padding: 2rem 2.1rem; border: 1px solid rgba(255,255,255,.12);
        border-radius: 24px; color: white;
        background: linear-gradient(125deg, #075f5a 0%, #087f75 62%, #13998b 100%);
        box-shadow: 0 18px 45px rgba(7,95,90,.18); margin-bottom: 1.2rem;
        position: relative; overflow: hidden;
    }
    .hero:after {
        content: ""; position: absolute; width: 240px; height: 240px;
        border-radius: 50%; right: -90px; top: -115px;
        border: 38px solid rgba(255,255,255,.07);
    }
    .eyebrow { font-size: .76rem; font-weight: 750; letter-spacing: .09em; text-transform: uppercase; opacity: .8; }
    .hero h1 { margin: .55rem 0 .5rem; max-width: 620px; font-size: 2.15rem; line-height: 1.12; letter-spacing: -.035em; }
    .hero p { margin: 0; max-width: 620px; line-height: 1.6; opacity: .88; }
    .trust-row { display: flex; flex-wrap: wrap; gap: .6rem; margin-top: 1.15rem; }
    .trust-chip { padding: .38rem .65rem; border-radius: 8px; background: rgba(255,255,255,.11); font-size: .77rem; }
    .safety-note {
        display: flex; gap: .8rem; align-items: flex-start; margin: 1rem 0 1.15rem;
        padding: .9rem 1rem; border: 1px solid #d4ebe5; border-radius: 14px;
        color: var(--ink); background: var(--soft); font-size: .88rem; line-height: 1.5;
    }
    .section-label { color: var(--muted); opacity: .72; font-size: .78rem; font-weight: 750; text-transform: uppercase; letter-spacing: .075em; margin: .5rem 0 .65rem; }
    .welcome-card {
        padding: 1.15rem 1.2rem; color: var(--ink); background: var(--surface); border: 1px solid var(--line);
        border-radius: 16px; margin: .8rem 0 1rem; box-shadow: 0 5px 18px rgba(25,64,69,.04);
    }
    .welcome-card strong { color: var(--ink); }
    [data-testid="stChatMessage"] {
        color: var(--ink); background: var(--surface); border: 1px solid var(--line); border-radius: 18px;
        padding: .35rem .4rem; box-shadow: 0 5px 18px rgba(25,64,69,.035);
    }
    [data-testid="stChatMessageContent"],
    [data-testid="stChatMessageContent"] p,
    [data-testid="stChatMessageContent"] li { color: var(--ink) !important; line-height: 1.62; }
    [data-testid="stExpander"] { border-color: var(--line); border-radius: 12px; color: var(--ink); background: var(--surface); }
    .source-meta { color: var(--muted); opacity: .68; font-size: .8rem; }
    .stButton > button {
        border-color: #cfe0e2; border-radius: 11px; color: var(--ink); background: var(--surface);
        min-height: 2.75rem; text-align: left; transition: all .15s ease;
    }
    .stButton > button:hover { border-color: var(--brand); color: var(--brand-dark); background: #f2fbf9; transform: translateY(-1px); }
    [data-testid="stChatInput"] { border-color: #bfd7d8; box-shadow: 0 8px 28px rgba(25,64,69,.08); }
    .footer {
        margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid var(--line);
        color: var(--muted); opacity: .68; font-size: .76rem; text-align: center; line-height: 1.5;
    }
    @media (max-width: 640px) {
        .block-container { padding: 4.6rem .85rem 1.5rem; }
        .hero { padding: 1.55rem 1.3rem; border-radius: 19px; }
        .hero h1 { font-size: 1.72rem; }
        .brand-sub { display: none; }
        .online-pill { font-size: .7rem; }
    }
    </style>
    <div class="clinic-nav">
      <div class="brand">
        <div class="brand-mark">✚</div>
        <div><div class="brand-name">ClinicFlow</div><div class="brand-sub">Clínica Horizonte</div></div>
      </div>
      <div class="online-pill"><span class="online-dot"></span> Asistente disponible</div>
    </div>
    <div class="hero">
      <div class="eyebrow">Orientación administrativa 24/7</div>
      <h1>Resuelva sus dudas antes de visitar la clínica</h1>
      <p>Información clara sobre citas, seguros, privacidad y preparación para su consulta.</p>
      <div class="trust-row">
        <span class="trust-chip">✓ Información verificada</span>
        <span class="trust-chip">✓ Fuentes visibles</span>
        <span class="trust-chip">✓ Respuestas en español</span>
      </div>
    </div>
    <div class="safety-note"><span>ⓘ</span><span><strong>Orientación segura:</strong> este asistente no diagnostica, no prescribe medicamentos y no sustituye la atención de un profesional. En una emergencia, contacte inmediatamente los servicios locales de urgencias.</span></div>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner="Preparando información de la clínica…")
def build_retriever(data_path: str) -> ClinicRetriever:
    return ClinicRetriever(load_knowledge_base(data_path))


def render_sources(sources: list[dict]) -> None:
    """Muestra la evidencia recuperada en un formato legible."""
    label = f"Fuentes consultadas ({len(sources)})" if sources else "Fuentes consultadas"
    with st.expander(label, expanded=False):
        if not sources:
            st.caption("Esta respuesta no necesitó una fuente documental.")
            return
        for position, source in enumerate(sources, start=1):
            st.markdown(f"**{position}. {source['title']}**")
            st.markdown(source["content"])
            st.markdown(
                f"<div class='source-meta'>{source['category']} · {source['source']} · "
                f"Coincidencia semántica {source['score']:.0%}</div>",
                unsafe_allow_html=True,
            )
            if position < len(sources):
                st.divider()


def friendly_error(exc: Exception) -> str:
    """Convierte errores del proveedor en mensajes seguros y accionables."""
    error_text = str(exc).lower()
    if "api key" in error_text or "permission_denied" in error_text or "403" in error_text:
        return "La conexión segura con Gemini necesita una clave válida. Revise la configuración del servicio."
    if "not_found" in error_text or "404" in error_text:
        return "El modelo configurado no está disponible. Revise GEMINI_MODEL en el entorno."
    if "resource_exhausted" in error_text or "429" in error_text:
        return "El servicio alcanzó su límite temporal de consultas. Inténtelo nuevamente en unos minutos."
    if "unavailable" in error_text or "503" in error_text:
        return "El asistente está temporalmente ocupado. Inténtelo nuevamente en unos minutos."
    return "No pudimos completar la consulta. Inténtelo nuevamente o contacte a recepción."


with st.sidebar:
    st.markdown("## ClinicFlow")
    st.caption("Panel de la demostración")
    configured_key = os.getenv("GEMINI_API_KEY")
    if configured_key:
        st.success("Gemini configurado", icon="✅")
        api_key = None
    else:
        st.warning("Falta configurar Gemini")
        api_key = st.text_input(
            "Clave de Gemini",
            type="password",
            help="Se utiliza solo durante esta sesión y nunca se guarda.",
        )
    st.divider()
    st.markdown("**Cobertura del asistente**")
    st.markdown(
        "- Citas y reprogramaciones\n"
        "- Seguros y cobertura\n"
        "- Privacidad de pacientes\n"
        "- Preparación de consultas"
    )
    st.divider()
    st.caption("Base ficticia · Sin datos de pacientes reales")
    if st.button("Limpiar conversación", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

try:
    retriever = build_retriever(str(DATA_PATH))
    agent = ClinicAgent(retriever=retriever, api_key=api_key or None)
except Exception as exc:
    st.error(f"No se pudo preparar el asistente: {exc}")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

suggested_question = None
if not st.session_state.messages:
    st.markdown(
        """
        <div class="welcome-card">
          <strong>Hola, soy el asistente virtual de Clínica Horizonte.</strong><br>
          Puede escribir su pregunta o comenzar con una de estas consultas frecuentes.
        </div>
        <div class="section-label">Consultas frecuentes</div>
        """,
        unsafe_allow_html=True,
    )
    suggestion_columns = st.columns(2)
    suggestions = (
        "¿Cómo solicito una cita?",
        "¿Qué documentos debo llevar?",
        "¿Cómo reprogramo mi consulta?",
        "¿Mi seguro cubre la atención?",
    )
    for index, suggestion in enumerate(suggestions):
        with suggestion_columns[index % 2]:
            if st.button(suggestion, key=f"suggestion_{index}", use_container_width=True):
                suggested_question = suggestion

for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            render_sources(message.get("sources", []))

chat_question = st.chat_input("Pregunte sobre citas, seguros o su consulta…")
question = suggested_question or chat_question
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar="👤"):
        st.markdown(question)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Buscando información verificada…"):
            try:
                result = agent.answer(question)
                answer = result["answer"]
                sources = result["sources"]
            except ValueError as exc:
                answer = str(exc)
                sources = []
            except Exception as exc:
                print(f"Error al generar respuesta con Gemini: {exc}")
                answer = friendly_error(exc)
                sources = []
        st.markdown(answer)
        render_sources(sources)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "sources": sources}
    )
    st.rerun()

st.markdown(
    """
    <div class="footer">
      ClinicFlow AI · Demostración educativa con datos exclusivamente ficticios<br>
      Para atención clínica o emergencias, utilice siempre los canales oficiales de salud.
    </div>
    """,
    unsafe_allow_html=True,
)