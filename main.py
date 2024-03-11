import os
import streamlit as st
from pyperclip import copy 
from backend.backend import get_pdf_text, get_fomatted_doc, get_translated_doc


# for deployment
os.environ["OPENAI_API_KEY"] = st.secrets['openai']["OPENAI_API_KEY"]

# Language handle
lang_pair = {
    "english": {
        "greeting" : "🤖 Good Day ☀️! How Can I Help?",
        "select_language": "Select Language",
        "upload_file": "Upload an article",
        "original_file": "Original File",
        "translation" : "Translation",
        "copy_to_clipboard": "Copy to Clipboard",
        "success_copy": "Text copied to clipboard!",
    },
    "korean": {
        "greeting" : "🇰🇷 무엇을 도와드릴까요? ",
        "select_language": "언어 선택",
        "upload_file": "원하시는 파일을 선택해 주세요",
        "original_file": "업로드 파일",
        "translation" : "🇺🇸 -> 🇰🇷",
        "copy_to_clipboard": "클립보드에 복사",
        "success_copy": "텍스트가 클립보드에 복사되었습니다!",
    },
}

# ************************************************************

# FrontEnd:
# streamlit and give feature to copy to clipboard

# ************************************************************

st.set_page_config(page_title="퍼스널 AI" + "|" + "Personal Assistant", page_icon="🎃")


# Authentication 
kor_password = "korean"
en_password = "english"

password_container = st.empty()
# Get user input for the password
user_password = password_container.text_input("Enter the password | 비밀번호를 입력하세요:", type="password")


if user_password == kor_password or user_password == en_password:

    password_container.empty()

    label = lang_pair[user_password]


    st.title(label["greeting"])


    # File Upload
    uploaded_file = st.file_uploader(label["upload_file"], type="pdf")

    if uploaded_file:
        try:
            text = get_pdf_text(uploaded_file)
            with st.expander(label['original_file']):
                with st.spinner():
                    text = get_fomatted_doc(text)
                st.markdown(text)

            st.divider()

            with st.expander(label["Translation"]):
                with st.spinner():
                    translated_text = get_translated_doc(text)
                st.markdown(translated_text)

            copy_to_clipboard = st.button("Copy to Clipboard")


            if copy_to_clipboard:
                copy(translated_text)
                st.success("Text copied to clipboard!")

        except ValueError:
            uploaded_file = None
            st.warning("Try again")

