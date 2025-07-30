import streamlit as st
import os
import sys
import pickle
import time
import base64

# Fix import path for local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.query_handler import answer_query
from kg_builder.build_kg import build_knowledge_graph_from_files
from kg_builder.docx_pdf_parser import (
    extract_text_from_pdf,
    extract_text_from_docx,
    extract_text_from_excel
)

# ---- Constants ----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data", "clean_text")


def show_banner(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()

    st.markdown(
        f"""
        <style>
        .fixed-banner {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            z-index: 9999;
            background-color: white;
            border-bottom: 2px solid #e0e0e0;
        }}
        .chat-wrapper {{
            margin-top: 320px;
            display: flex;
            flex-direction: column;
            height: calc(100vh - 320px);
            overflow: hidden;
        }}
        .chat-history {{
            flex: 1;
            overflow-y: auto;
            padding: 1rem 1rem 0 1rem;
        }}
        .chat-message {{
            margin-bottom: 1rem;
        }}
        </style>

        <div class="fixed-banner">
            <img src="data:image/png;base64,{encoded}" style="width:100%; max-height:300px; object-fit:cover;" />
        </div>
        """,
        unsafe_allow_html=True,
    )


def main():
    # ---- Page Config ----
    st.set_page_config(page_title="ISRO HelpBot", layout="wide")

    # ---- Sticky Banner ----
    show_banner("ui/static/moon_bg.png")

    # ---- Session State ----
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # ---- Sidebar ----
    st.sidebar.title("🛰️ ISRO HelpBot")
    st.sidebar.write("Ask questions related to ISRO, satellites, missions, MOSDAC, etc.")

    uploaded_files = st.sidebar.file_uploader(
        "Upload files to update Knowledge Graph",
        type=["txt", "pdf", "docx", "xlsx"],
        accept_multiple_files=True
    )

    if uploaded_files:
        st.sidebar.info("Uploading files and rebuilding KG...")
        os.makedirs(DATA_DIR, exist_ok=True)
        for file in uploaded_files:
            file_path = os.path.join(DATA_DIR, file.name)
            with open(file_path, "wb") as f:
                f.write(file.read())
        with st.spinner("Building Knowledge Graph..."):
            build_knowledge_graph_from_files()
            time.sleep(2)
        st.sidebar.success("Knowledge Graph Updated!")

    if st.sidebar.button("🧹 Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

    # ---- Main Chat Interface ----
    st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)

    # Chat History Display
    st.markdown('<div class="chat-history">', unsafe_allow_html=True)
    for user_msg, bot_reply in st.session_state.chat_history:
        st.markdown(f'<div class="chat-message"><b>you:</b> {user_msg}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-message"><b>bot:</b> {bot_reply}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Chat Input
    st.markdown('<div class="chat-input">', unsafe_allow_html=True)
    user_input = st.chat_input("Ask your question...")
    st.markdown('</div>', unsafe_allow_html=True)

    if user_input:
        with st.spinner("Thinking..."):
            response = answer_query(user_input, st.session_state.chat_history)
            bot_reply = response["llm_response"]
            st.session_state.chat_history.append((user_input, bot_reply))
            st.rerun()

    # Close wrapper
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
