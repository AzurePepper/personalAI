import pdfplumber
from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from langchain.chains import (create_history_aware_retriever,
                              create_retrieval_chain)
from langchain.text_splitter import RecursiveCharacterTextSplitter

## Load .evn for API_KEYs
# load_dotenv()


# Read from pdf
def get_pdf_text(file):
    with pdfplumber.open(file) as pdf:
        text = ""
        
        if len(pdf.pages) > 3:
            raise ValueError("Number of page should be less than 3")

        for page in pdf.pages:
            text += page.extract_text()
        return text


# doc_path = "Tony (DongHee) Lee Resume.pdf"
#
# text = get_pdf_text(doc_path)
# print(text)


def get_fomatted_doc(text: str):
    llm = ChatOpenAI()
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are going to recieve a long string text extracted from PDF file. Since it's format got dropped from extraction, I want you to apply format to make it good better.",
            ),
            ("user", "{input}"),
        ]
    )

    output_parser = StrOutputParser()

    chain = prompt | llm | output_parser
    res = chain.invoke({"input": text})

    return res


def get_translated_doc(text: str):

    llm = ChatOpenAI()
    translation_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are tasked with being an excellent English-Korean translator. Your objective is to translate the provided document extracted from a PDF file.",
            ),
            (
                "system",
                "Present the translation in semantic paragraphs, matching each section of the original text with its corresponding translated segment. Ensure clarity by separating the original text into meaningful units followed by the translation of each respective part",
            ),
            ("user", "{input}"),
        ]
    )
    output_parser = StrOutputParser()

    translation_chain = translation_prompt | llm | output_parser

    res = translation_chain.invoke({"input": text})
    return res


# TODO
# RAG model for remeber conversation history and previous information.

