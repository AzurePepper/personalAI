import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pyperclip import copy
import pdfplumber

## Load .env for API_KEYs
load_dotenv()

def get_pdf_text(file):
    with pdfplumber.open(file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
        return text

def get_formatted_doc(text: str, language: str):
    llm = ChatOpenAI()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", translations[language]["format_system"]),
            ("user", "{input}"),
        ]
    )

    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser
    res = chain.invoke({"input": text, "language": language})
    return res

def get_translated_doc(text: str, language: str):
    llm = ChatOpenAI()
    translation_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", translations[language]["translation_system"]),
            ("system", translations[language]["translation_system_extra"]),
            ("user", "{input}"),
        ]
    )
    output_parser = StrOutputParser()
    translation_chain = translation_prompt | llm | output_parser
    res = translation_chain.invoke({"input": text, "language": language})
    return res

# Dictionary for translations
translations = {
    "English": {
        "format_system": "You are going to receive a long string text extracted from a PDF file. Since its format got dropped from extraction, I want you to apply format to make it good better.",
        "translation_system": "You are tasked with being an excellent English-Korean translator. Your objective is to translate the provided document extracted from a PDF file.",
        "translation_system_extra": "Present the translation in semantic paragraphs, matching each section of the original text with its corresponding translated segment. Ensure clarity by separating the original text into meaningful units followed by the translation of each respective part",
        "select_language": "Select Language",
        "upload_article": "Upload an article",
        "original_file": "Original File",
        "translation": "Translation",
        "copy_to_clipboard": "Copy to Clipboard",
        "success_copy": "Text copied to clipboard!",
    },
    "Korean": {
        "format_system": "PDF 파일에서 추출된 긴 문자열 텍스트를 받게 됩니다. 추출 과정에서 형식이 누락되었으므로 형식을 적용하여 더 좋게 만들어 주세요.",
        "translation_system": "당신은 훌륭한 영한 번역기로 임무를 부여받았습니다. 목표는 PDF 파일에서 추출한 제공된 문서를 번역하는 것입니다.",
        "translation_system_extra": "번역된 각 부분에 해당하는 원본 텍스트를 의미 있는 단위로 나누어 각 부분에 대한 번역을 따르도록 원본 텍스트를 의미 있는 단위로 나누어 번역 결과를 제시하십시오. 각 부분에 대한 번역을 따르도록 원본 텍스트를 의미 있는 단위로 나누어 번역 결과를 제시하십시오.",
        "select_language": "언어 선택",
        "upload_article": "기사 업로드",
        "original_file": "원본 파일",
        "translation": "번역",
        "copy_to_clipboard": "클립보드에 복사",
        "success_copy": "텍스트가 클립보드에 복사되었습니다!",
    },
}

# Streamlit App
st.set_page_config(page_title="Personal Assistant", page_icon="🎃")
st.title(translations["English"]["select_language"])

# Language toggle in the sidebar
language = st.sidebar.selectbox(translations["English"]["select_language"], ["English", "Korean"])

# File Upload
uploaded_file = st.file_uploader(translations[language]["upload_article"], type="pdf")

if uploaded_file:
    text = get_pdf_text(uploaded_file)
    with st.expander(translations[language]["original_file"]):
        st.write(text)
        st.divider()
        formatted_text = get_formatted_doc(text, language)
        st.markdown(formatted_text)

    st.divider()

    with st.expander(translations[language]["translation"]):
        with st.spinner():
            translated_text = get_translated_doc(text, language)
        st.markdown(translated_text)

    copy_to_clipboard = st.button(translations[language]["copy_to_clipboard"])

    if copy_to_clipboard:
        copy(translated_text)
        st.success(translations[language]["success_copy"])

