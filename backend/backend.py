import pdfplumber
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader, TextLoader, WebBaseLoader
from langchain_community.vectorstores import Chroma, FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from langchain.chains import (create_history_aware_retriever,
                              create_retrieval_chain)
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain;


# Read from pdf
def get_pdf_text(file):
    with pdfplumber.open(file) as pdf:
        text = ""

        if len(pdf.pages) > 4:
            raise ValueError("Number of page should be less than 3")

        for page in pdf.pages:
            text += page.extract_text()
        return text


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

def get_parsed_translated_text(uploaded_file):
    # Extract text and render parsed text
    text = get_pdf_text(uploaded_file)
    parsed_text = get_fomatted_doc(text)
    translated_text = get_translated_doc(parsed_text)

    return parsed_text, translated_text



# function for RAG
def get_vectorstore_from_url(url: str):
    loader = WebBaseLoader(url)
    document = loader.load()

    # split the documents into chunks
    text_splitter = RecursiveCharacterTextSplitter()
    document_chunks = text_splitter.split_documents(document)

    # create a vectorstore from the chunks
    vector_stores = Chroma.from_documents(document_chunks, OpenAIEmbeddings())
    return vector_stores

# def get_text_chunks(text):
#     text_splitter = CharacterTextSplitter(
#         separator="\n",
#         chunk_size=1000,
#         chunk_overlap=200,
#         length_function=len
#     )
#     chunks = text_splitter.split_text(text)
#     return chunks

def get_vectorstore_from_pdf(pdf_text: str):
    # loader = PyPDFLoader(pdf_text)
    # documents = loader.load() 

    # split the documents into chunks
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    text_chunks = text_splitter.split_text(pdf_text)

    # create a vectorstore from the chunks

    vector_stores = FAISS.from_texts(texts=text_chunks, embedding=OpenAIEmbeddings())
    return vector_stores

def get_context_retriever_chain(vector_store):
    llm = ChatOpenAI()

    retriever = vector_store.as_retriever()

    prompt = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            (
                "user",
                "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation",
            ),
        ]
    )

    retriever_chain = create_history_aware_retriever(llm, retriever, prompt)

    return retriever_chain


def get_conversational_rag_chain(retriever_chain):
    """
    Contect_retriever_chain takes care of semantic search.
    And here it connect semantic search and question in LLM
    """

    llm = ChatOpenAI()

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Answer the user's questions based on the below context:\n\n{context}",
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ]
    )

    stuff_documents_chain = create_stuff_documents_chain(llm, prompt)

    # TODO how the chain connects each other
    return create_retrieval_chain(retriever_chain, stuff_documents_chain)


def get_response(user_input):
    retriever_chain = get_context_retriever_chain(st.session_state.vector_store)
    conversation_rag_chain = get_conversational_rag_chain(retriever_chain)

    response = conversation_rag_chain.invoke(
        {"chat_history": st.session_state.chat_history, "input": user_input}
    )

    return response["answer"]
