import os

import streamlit as st
from pyperclip import copy

from backend.backend import get_fomatted_doc, get_pdf_text, get_translated_doc

## Handle secret contents
os.environ["OPENAI_API_KEY"] = st.secrets["openai"]["OPENAI_API_KEY"]
kor_password = st.secrets["passwords"]["KOR_PASSWORD"]
en_password = st.secrets["passwords"]["EN_PASSWORD"]

# Language handle
lang_pair = {
    "english": {
        "greeting": "🤖 Good Day ☀️  How Can I Help?",
        "select_language": "Select Language",
        "upload_file": "Upload an article",
        "original_file": "Original File",
        "translation": "Translation",
        "page_limit_warning": "At the moment of dev, page is limited to less than 3 pages, Try Again!",
        "copy_to_clipboard": "Copy to Clipboard",
        "success_copy": "Text copied to clipboard!",
    },
    "korean": {
        "greeting": "🇰🇷 무엇을 도와드릴까요? ",
        "select_language": "언어 선택",
        "upload_file": "원하시는 파일을 선택해주세요",
        "original_file": "업로드 파일",
        "translation": "🇺🇸 -> 🇰🇷",
        "page_limit_warning": "개발단계 최대 업로드 페이지는 최대 3 페이지 입니다. 다른 파일을 선택해주세요",
        "copy_to_clipboard": "클립보드에 복사",
        "success_copy": "텍스트가 클립보드에 복사되었습니다!",
    },
}


def render_traslator(uploaded_file):
    try:
        # Extract text and render parsed text
        text = get_pdf_text(uploaded_file)
        with st.expander(label["original_file"]):
            with st.spinner():
                text = get_fomatted_doc(text)
            st.markdown(text)

        st.divider()

        # Translated and render the translation outcome
        with st.expander(label["translation"]):
            with st.spinner():
                translated_text = get_translated_doc(text)
            st.markdown(translated_text)

            # Copy to clipboard
            copy(translated_text)
            st.success("Text copied to clipboard!")

    except ValueError:
        uploaded_file = None
        st.warning(label["page_limit_warning"])

def get_parsed_translated_text(uploaded_file):
    try:
        # Extract text and render parsed text
        text = get_pdf_text(uploaded_file)
        parsed_text = get_fomatted_doc(text)
        translated_text = get_translated_doc(parsed_text)

        return parsed_text, translated_text

    except ValueError:
        uploaded_file = None
        st.warning(label["page_limit_warning"])




## -> FrontEnd Start:


# Authentication
password_container = st.empty()
user_password = password_container.text_input(
    "Enter the password | 비밀번호를 입력하세요:", type="password"
)

if user_password == kor_password or user_password == en_password:
    password_container.empty()
    # Set Language
    label = lang_pair[user_password]
    # --------------------------------------------------

    ## -> Main Rendering

    # Main Header
    st.title(label["greeting"])

    choice = st.radio("select one", ["Translator", "ChatBot"])

    if choice == "Translator":
        if "uploaded_file" not in st.session_state:
            st.session_state.uploaded_file = None

        uploaded_file = st.file_uploader(label["upload_file"], type="pdf")
        st.session_state.uploaded_file = uploaded_file
        
        if st.session_state.uploaded_file:
            if uploaded_file.name not in st.session_state:
                st.session_state[uploaded_file.name] = {} # Initialize 
                parsed, translated = get_parsed_translated_text(uploaded_file)
                st.session_state[uploaded_file.name]["parsed_text"] = parsed
                st.session_state[uploaded_file.name]["translated_text"] = translated
            
            # Render parsed_text from pdf file
            with st.expander(label["original_file"]):
                st.markdown(st.session_state[uploaded_file.name]["parsed_text"])
            st.divider()

            # Render the translation outcome
            with st.expander(label["translation"]):
                st.markdown(st.session_state[uploaded_file.name]["translated_text"])


    else:
        st.write("In the Progress")
