"""Interfaz Streamlit de ClinicFlow AI Agent."""

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
    page_title="ClinicFlow AI Agent",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp { background: #f7fafc; }
    .hero {
        padding: 1.8rem 2rem;
        border-radius: 20px;
        background: linear-gradient(135deg, #0f766e 0%, #0b5d67 100%);
        color: white;
        margin-bottom: 1.25rem;
        box-shadow: 0 10px 30px rgba(15, 118, 110, .16);
    }
    .hero h1 { margin: 0; font-size: 2rem; }
    .hero p { margin: .55rem 0 0; opacity: .92; }
    .notice {
        border-left: 4px solid #0f766e;
        background: #ecfdf5;
        padding: .85rem 1rem;
        border-radius: 8px;
        color: #134e4a;
        margin-bottom: 1rem;
    }
    [data-testid="stChatMessage"] {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
    }
    </style>
    <div class="hero">
      <h1>ClinicFlow AI Agent</h1>
      <p>Asistente informativo de Clínica Horizonte · Atención clara y segura</p>
    </div>
    <div class="notice">
      Este asistente ofrece información administrativa y de preparación.
      No diagnostica, no prescribe medicamentos y no sustituye a un profesional de salud.
    </div>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner="Preparando la base de conocimiento…")
def build_retriever(data_path: str) -> ClinicRetriever:
    documents = load_knowledge_base(data_path)
    return ClinicRetriever(documents)


def render_sources(sources: list[dict]) -> None:
    """Muestra evidencia recuperada sin exponer el prompt interno."""
    with st.expander("Fuentes consultadas", expanded=False):
        if not sources:
            st.caption("No fue necesario consultar una fuente documental.")
            return
        for source in sources:
            st.markdown(
                f"**{source['title']}** · {source['category']}  \n"
                f"{source['content']}  \n"
                f"*Referencia: {source['source']} · "
                f"Relevancia: {source['score']:.0%}*"
            )
            st.divider()


with st.sidebar:
    st.header("Configuración")
    api_key = st.text_input(
        "Gemini API key (opcional si está en .env)",
        type="password",
        help="La clave solo se usa durante esta sesión y no se guarda en el CSV.",
    )
    st.caption("Modelo de embeddings: paraphrase-multilingual-MiniLM-L12-v2")
    st.divider()
    st.subheader("Puede preguntar sobre")
    st.markdown(
        "- Citas, cancelaciones y reprogramaciones\n"
        "- Seguros y cobertura\n"
        "- Privacidad de pacientes\n"
        "- Preparación y cuidados de consulta"
    )
    if st.button("Limpiar conversación", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

try:
    retriever = build_retriever(str(DATA_PATH))
    agent = ClinicAgent(retriever=retriever, api_key=api_key or None)
except Exception as exc:
    st.error(f"No se pudo iniciar la aplicación: {exc}")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            render_sources(message.get("sources", []))

question = st.chat_input("Escriba su pregunta sobre la clínica…")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Consultando información de la clínica…"):
            try:
                result = agent.answer(question)
                answer = result["answer"]
                sources = result["sources"]
            except ValueError as exc:
                answer = f"⚙️ {exc}"
                sources = []
            except Exception as exc:
                error_text = str(exc).lower()
                if "api key" in error_text or "permission_denied" in error_text:
                    detail = (
                        "La clave de Gemini no es válida, fue bloqueada o no tiene "
                        "permisos. Genere una clave nueva en Google AI Studio."
                    )
                elif "not_found" in error_text or "404" in error_text:
                    detail = (
                        "El modelo de Gemini configurado no está disponible. "
                        "Revise GEMINI_MODEL en el archivo .env."
                    )
                elif "resource_exhausted" in error_text or "429" in error_text:
                    detail = (
                        "La cuota de Gemini está agotada temporalmente. "
                        "Espere unos minutos o revise la cuota del proyecto."
                    )
                elif "unavailable" in error_text or "503" in error_text:
                    detail = (
                        "Gemini no está disponible temporalmente. "
                        "Inténtelo nuevamente en unos minutos."
                    )
                else:
                    detail = (
                        "No se pudo conectar con Gemini. Revise la terminal para "
                        "conocer el detalle técnico."
                    )
                print(f"Error al generar respuesta con Gemini: {exc}")
                answer = f"⚠️ {detail}"
                sources = []
        st.markdown(answer)
        render_sources(sources)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "sources": sources}
    )

st.caption(
    "Clínica Horizonte es una entidad ficticia creada para el Alura Agent Challenge."
)
