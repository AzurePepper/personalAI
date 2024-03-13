import os

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from pyperclip import copy

from backend.backend import (get_parsed_translated_text, get_response,
                             get_vectorstore_from_url)

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
        "spinner": "Loading.....",
        "sidebar_radio": "Choose AI function",
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
        "spinner": "⏳ 처리중...",
        "sidebar_radio": "원하시는 기능을 선택해주세요",
        "copy_to_clipboard": "클립보드에 복사",
        "success_copy": "텍스트가 클립보드에 복사되었습니다!",
    },
}

label = lang_pair["korean"]



## -> FrontEnd Start:


# Authentication
password_container = st.empty()
user_password = password_container.text_input(
    "Enter the password | 비밀번호를 입력하세요:", type="password"
)

if user_password == kor_password :
    password_container.empty()
    label = lang_pair["korean"]
    authenticated = True
elif user_password == en_password:
    password_container.empty()
    label = lang_pair["english"]
    authenticated = True
else:
    authenticated = False

# --------------------------------------------------

    ## -> Main Rendering
if authenticated:
    # Main Header
    st.title(label["greeting"])

    # Sidebar
    with st.sidebar:
        mode = st.radio(label["sidebar_radio"], ("Translation", "Chatbot"))

    if mode == "Translation":
        if "uploaded_file" not in st.session_state:
            st.session_state.uploaded_file = None

        uploaded_file = st.file_uploader(label["upload_file"], type="pdf")

        # Only when new file uploaded
        if uploaded_file:
            st.session_state.uploaded_file = uploaded_file
            file_id = uploaded_file.file_id
            if file_id not in st.session_state:
                st.session_state[file_id] = {
                    "name": uploaded_file.name,
                    "parsed": False,
                }

        if st.session_state.uploaded_file:
            session_obj = st.session_state[st.session_state.uploaded_file.file_id]
            try:

                if not session_obj["parsed"]:
                    with st.spinner(label["spinner"]):
                        parsed, translated = get_parsed_translated_text(
                            st.session_state.uploaded_file
                        )
                        session_obj["parsed_text"] = parsed
                        session_obj["translated_text"] = translated
                        session_obj["parsed"] = True

                # Render parsed_text from pdf file
                with st.expander(
                    label["original_file"] + f": {st.session_state.uploaded_file.name}"
                ):
                    st.markdown(session_obj["parsed_text"])
                st.divider()

                # Render the translation outcome
                with st.expander(label["translation"]):
                    st.markdown(session_obj["translated_text"])

            except ValueError:
                uploaded_file = None
                st.warning(label["page_limit_warning"])

    elif mode == "Chatbot":

        website_url = st.text_input("webites URL")
        if website_url is None or website_url == "":
            st.info("Please enter a website URL")

        else:
            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []
                st.session_state.chat_history.append(
                    AIMessage(content="Hello, I'm a bot, How can I help you")
                )

            if "vector_stores" not in st.session_state:
                st.session_state.vector_store = get_vectorstore_from_url(website_url)

            ##### user input
            user_query = st.chat_input("Type your message here... ")
            ## When st.chat_input is used in the main body of an app, it will be pinned to the bottom of the page.

            if user_query is not None and user_query != "":
                respose = get_response(user_query)
                st.session_state.chat_history.append(HumanMessage(content=user_query))
                st.session_state.chat_history.append(AIMessage(content=respose))

            ##### conversation
            for message in st.session_state.chat_history:
                if isinstance(message, AIMessage):
                    with st.chat_message("AI"):
                        st.write(message.content)

                elif isinstance(message, HumanMessage):
                    with st.chat_message("Human"):
                        st.write(message.content)
