import streamlit as st;
from dotenv import load_dotenv;
from langchain_community.document_loaders import WebBaseLoader;
from langchain_community.vectorstores import Chroma;
from langchain_core.messages import AIMessage, HumanMessage;
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder;
from langchain_openai import OpenAIEmbeddings, ChatOpenAI;

from langchain.text_splitter import RecursiveCharacterTextSplitter;
from langchain.chains import create_history_aware_retriever, create_retrieval_chain;
from langchain.chains.combine_documents import create_stuff_documents_chain;

## Load .evn for API_KEYs
load_dotenv()

def get_vectorstore_from_url(url:str):
    loader = WebBaseLoader(url)
    document = loader.load()

    # split teh documents into chunks
    text_splitter = RecursiveCharacterTextSplitter()
    document_chunks = text_splitter.split_documents(document)

    # create a vectorstore from the chunks
    vector_stores = Chroma.from_documents(document_chunks, OpenAIEmbeddings())
    return vector_stores

def get_context_retriever_chain(vector_store):
    llm = ChatOpenAI()
    
    retriever = vector_store.as_retriever()
    
    prompt = ChatPromptTemplate.from_messages([
      MessagesPlaceholder(variable_name="chat_history"),
      ("user", "{input}"),
      ("user", "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation")
    ])
    
    retriever_chain = create_history_aware_retriever(llm, retriever, prompt)
    
    return retriever_chain

def get_conversational_rag_chain(retriever_chain):
    """
    Contect_retriever_chain takes care of semantic search.
    And here it connect semantic search and question in LLM
    """
    
    llm = ChatOpenAI()
    
    prompt = ChatPromptTemplate.from_messages([
      ("system", "Answer the user's questions based on the below context:\n\n{context}"),
      MessagesPlaceholder(variable_name="chat_history"),
      ("user", "{input}"),
    ])
    
    stuff_documents_chain = create_stuff_documents_chain(llm,prompt)
    
    #TODO how the chain connects each other
    return create_retrieval_chain(retriever_chain, stuff_documents_chain)

    
def get_response(user_input):
    retriever_chain = get_context_retriever_chain(st.session_state.vector_store)
    conversation_rag_chain = get_conversational_rag_chain(retriever_chain)
    
    response = conversation_rag_chain.invoke({
        "chat_history": st.session_state.chat_history,
        "input": user_input
    })
    
    return response['answer']


st.set_page_config(page_title="Chat with websites", page_icon="🎃")
st.title("Chat with websites")

# Initialize persisiting chat_history list

##### sidebar
with st.sidebar:
    st.header("settings")
    website_url = st.text_input("webites URL")
    

##### coversation
if website_url is None or website_url == "":
    st.info("Please enter a website URL")

else :
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

