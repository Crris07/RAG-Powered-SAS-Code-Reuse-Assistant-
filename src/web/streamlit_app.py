"""Streamlit web UI."""

import streamlit as st

from src.core.logger import get_logger
from src.embeddings.vector_store import VectorStore
from src.llm.code_generator import CodeGenerator
from src.rag.retriever import CodeRetriever

logger = get_logger(__name__)


@st.cache_resource(show_spinner=False)
def get_retriever() -> CodeRetriever:
    """Load model-backed retriever once per Streamlit process."""
    vector_store = VectorStore()
    return CodeRetriever(vector_store)


@st.cache_resource(show_spinner=False)
def get_code_generator() -> CodeGenerator:
    """Load code generator once per Streamlit process."""
    return CodeGenerator()


st.set_page_config(
    page_title="SAS RAG Assistant",
    page_icon="SAS",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("SAS RAG Assistant")
st.markdown("**Retrieval-Augmented Generation for SAS Code Reuse**")

if "generated_code" not in st.session_state:
    st.session_state.generated_code = None
if "retrieved_snippets" not in st.session_state:
    st.session_state.retrieved_snippets = []

with st.sidebar:
    st.header("Settings")
    top_k = st.slider("Number of similar snippets", 1, 10, 3)
    temperature = st.slider("LLM temperature", 0.0, 1.0, 0.2, 0.1)
    max_tokens = st.slider("Max tokens", 256, 4000, 1024, 256)

tab_generate, tab_search = st.tabs(["Generate Code", "Search Corpus"])

with tab_generate:
    st.subheader("Generate SAS Code")
    requirement = st.text_area(
        "Enter your code requirement:",
        placeholder="Example: Generate ADSL subject-level analysis dataset with safety flags",
        height=120,
    )

    if st.button("Generate Code", type="primary"):
        if not requirement.strip():
            st.warning("Please enter a requirement.")
        else:
            try:
                with st.spinner("Retrieving and generating..."):
                    retriever = get_retriever()
                    code_gen = get_code_generator()

                    retrieved = retriever.retrieve(requirement, top_k=top_k)
                    st.session_state.retrieved_snippets = retrieved

                    if retrieved:
                        context = retriever.format_context(retrieved)
                        generated_code = code_gen.adapt_code(
                            context,
                            requirement,
                            temperature=temperature,
                            max_tokens=max_tokens,
                        )
                    else:
                        generated_code = code_gen.generate_code(
                            requirement,
                            temperature=temperature,
                            max_tokens=max_tokens,
                        )

                    st.session_state.generated_code = generated_code
                    st.success("Code generated.")
            except Exception as exc:
                logger.exception("Streamlit generation failed")
                st.error(f"Error: {exc}")

    if st.session_state.generated_code:
        col_snippets, col_code = st.columns([1, 1])

        with col_snippets:
            st.subheader("Retrieved Snippets")
            if st.session_state.retrieved_snippets:
                for index, snippet in enumerate(st.session_state.retrieved_snippets, 1):
                    similarity = snippet.get("similarity", 0.0)
                    final_score = snippet.get("final_score", 0.0)
                    rerank_score = snippet.get("rerank_score", 0.0)
                    label = (
                        f"Snippet {index} | Similarity: {similarity:.2%} | "
                        f"Final: {final_score:.4f}"
                    )
                    with st.expander(label):
                        st.caption(f"Rerank score: {rerank_score:.4f}")
                        st.code(snippet["code"], language="sas")
            else:
                st.info("No similar snippets found.")

        with col_code:
            st.subheader("Generated Code")
            st.code(st.session_state.generated_code, language="sas")
            st.download_button(
                label="Download Generated Code",
                data=st.session_state.generated_code,
                file_name="generated_code.sas",
                mime="text/plain",
            )

with tab_search:
    st.subheader("Search Code Corpus")
    with st.form("search_form"):
        search_query = st.text_input("Enter search query:")
        submitted = st.form_submit_button("Search")

    if submitted and search_query.strip():
        try:
            retriever = get_retriever()
            results = retriever.retrieve(search_query, top_k=top_k)

            if results:
                st.success(f"Found {len(results)} results.")
                for index, snippet in enumerate(results, 1):
                    similarity = snippet.get("similarity", 0.0)
                    final_score = snippet.get("final_score", 0.0)
                    rerank_score = snippet.get("rerank_score", 0.0)
                    label = (
                        f"Result {index} | Similarity: {similarity:.2%} | "
                        f"Final: {final_score:.4f}"
                    )
                    with st.expander(label):
                        st.caption(f"Rerank score: {rerank_score:.4f}")
                        st.code(snippet["code"], language="sas")
            else:
                st.info("No results found.")
        except Exception as exc:
            logger.exception("Streamlit search failed")
            st.error(f"Error: {exc}")

st.divider()
st.markdown(
    "<small>SAS RAG Assistant v0.1.0 | Built with FastAPI, ChromaDB, and Streamlit</small>",
    unsafe_allow_html=True,
)
