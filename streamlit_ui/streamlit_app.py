import sqlite3
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.core.config import DOCUMENTS_DIR  # noqa: E402
from backend.core.document_loader import UnsupportedFileTypeError  # noqa: E402
from backend.core.rag_service import (  # noqa: E402
    ask_question,
    create_collection,
    index_document,
    list_chat_history,
    list_collections,
    list_documents,
    save_chat,
)
from backend.database.db import init_db  # noqa: E402

SUPPORTED_TYPES = ["pdf", "docx", "txt", "md"]

st.set_page_config(page_title="Yerel Belge Soru-Cevap", layout="wide")
init_db()


def save_upload(uploaded_file, collection_id: int) -> Path:
    target_dir = DOCUMENTS_DIR / str(collection_id)
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / uploaded_file.name
    target_path.write_bytes(uploaded_file.getbuffer())
    return target_path


def render_collection_sidebar() -> int | None:
    st.sidebar.header("Koleksiyon")
    collections = list_collections()

    with st.sidebar.form("yeni_koleksiyon"):
        name = st.text_input("Yeni koleksiyon adi")
        description = st.text_input("Aciklama (istege bagli)")
        if st.form_submit_button("Olustur") and name.strip():
            try:
                create_collection(name.strip(), description.strip() or None)
                st.rerun()
            except sqlite3.IntegrityError:
                st.sidebar.error(f"'{name}' adinda bir koleksiyon zaten var.")

    if not collections:
        st.sidebar.info("Once bir koleksiyon olustur.")
        return None

    selected = st.sidebar.selectbox(
        "Aktif koleksiyon",
        options=[collection["id"] for collection in collections],
        format_func=lambda id: next(
            collection["name"] for collection in collections if collection["id"] == id
        ),
    )

    return selected


def render_documents_tab(collection_id: int) -> None:
    uploaded_files = st.file_uploader(
        "Belge yukle", type=SUPPORTED_TYPES, accept_multiple_files=True
    )
    if uploaded_files and st.button("Indeksle", type="primary"):
        for uploaded_file in uploaded_files:
            path = save_upload(uploaded_file, collection_id)
            with st.spinner(f"{uploaded_file.name} indeksleniyor..."):
                try:
                    result = index_document(str(path), collection_id)
                except UnsupportedFileTypeError as error:
                    st.error(str(error))
                    continue
            st.success(
                f"{result['filename']}: {result['chunk_count']} parca, "
                f"{result['char_count']} karakter"
            )

    documents = list_documents(collection_id)
    if not documents:
        st.info("Bu koleksiyonda henuz belge yok.")
        return

    st.dataframe(
        [
            {
                "Belge": document["filename"],
                "Tur": document["file_type"],
                "Parca": document["chunk_count"],
                "Karakter": document["char_count"],
                "Kelime": document["word_count"],
                "Eklenme": document["created_at"],
            }
            for document in documents
        ],
        hide_index=True,
        width="stretch",
    )


def render_question_tab(collection_id: int) -> None:
    question = st.text_input("Sorunuz")

    if not (st.button("Sor", type="primary") and question.strip()):
        return

    with st.spinner("Cevap uretiliyor (model ilk cagrida yukleniyor)..."):
        result = ask_question(question.strip(), collection_id)
    save_chat(question.strip(), result["answer"], collection_id)

    st.markdown("### Cevap")
    st.write(result["answer"])

    st.markdown("### Kaynaklar")
    if not result["sources"]:
        st.caption("Bu koleksiyonda eslesen belge bulunamadi.")
        return
    # ayni belgeden birden fazla parca gelebilir, kaynakcada belge adi bir kez yazilir
    for filename in dict.fromkeys(source["filename"] for source in result["sources"]):
        st.write(f"- {filename}")


def render_history_tab(collection_id: int) -> None:
    history = list_chat_history(collection_id)
    if not history:
        st.info("Bu koleksiyonda henuz soru sorulmamis.")
        return

    for entry in history:
        with st.expander(f"{entry['created_at']} - {entry['question']}"):
            st.write(entry["answer"])


st.title("Yerel Belge Soru-Cevap")
collection_id = render_collection_sidebar()

if collection_id is None:
    st.info("Baslamak icin soldaki panelden bir koleksiyon olustur.")
else:
    documents_tab, question_tab, history_tab = st.tabs(
        ["Belgeler", "Soru sor", "Gecmis"]
    )
    with documents_tab:
        render_documents_tab(collection_id)
    with question_tab:
        render_question_tab(collection_id)
    with history_tab:
        render_history_tab(collection_id)
