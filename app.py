import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, bot_template, user_template
import subprocess
import os
import tempfile
import oletools.oleid


def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    return text_splitter.split_text(text)


def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    return FAISS.from_texts(texts=text_chunks, embedding=embeddings)


def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    return ConversationalRetrievalChain.from_llm(llm=llm, retriever=vectorstore.as_retriever(), memory=memory)


def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        template = user_template if i % 2 == 0 else bot_template
        st.write(template.replace("{{MSG}}", message.content), unsafe_allow_html=True)


def process_pdf(pdf_docs):
    raw_text = get_pdf_text(pdf_docs)
    text_chunks = get_text_chunks(raw_text)
    vectorstore = get_vectorstore(text_chunks)
    st.session_state.conversation = get_conversation_chain(vectorstore)


def analyze_ole(file):
    for uploaded_file in file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name

        oid = oletools.oleid.OleID(temp_file_path)
        indicators = oid.check()

        st.write(f"Results for {uploaded_file.name}:")
        for i in indicators:
            st.write(f'Indicator id={i.id} name="{i.name}" type={i.type} value={repr(i.value)}')
            st.write('Description:', i.description)
            st.write('')
        os.remove(temp_file_path)


def analyze_python_code(file_to_analyze):
    def run_bandit(file_path):
        try:
            result = subprocess.run(['bandit', file_path], capture_output=True, text=True, check=True)
            st.write("Bandit Analysis Results:")
            st.write(result.stdout)
        except subprocess.CalledProcessError as e:
            st.write("Bandit encountered an error:")
            st.write(e.stderr)
        except FileNotFoundError:
            st.write("Bandit is not installed. Please install it using 'pip install bandit'.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
        temp_file.write(file_to_analyze.read())
        temp_file_path = temp_file.name

    run_bandit(temp_file_path)
    os.remove(temp_file_path)


def main():
    load_dotenv()
    st.set_page_config(page_title="AppSec", page_icon="random", layout="wide")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    st.header("test_app")

    user_question = st.text_input("User input")
    if user_question:
        handle_userinput(user_question)

    with st.sidebar:
        st.subheader("Pdf with AI")
        pdf_docs = st.file_uploader("Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
        if st.button("Process") and pdf_docs:
            with st.spinner("Processing"):
                process_pdf(pdf_docs)

        st.subheader("Ole Tool")
        file = st.file_uploader("Upload your file here and click on 'use oletool'", accept_multiple_files=True)
        if st.button("Use") and file:
            analyze_ole(file)

        st.subheader("Python Code Analyzer")
        file_to_analyze = st.file_uploader("Upload your Python file here and click on 'Analyze'", type='py', accept_multiple_files=False)
        if st.button("Analyze") and file_to_analyze:
            analyze_python_code(file_to_analyze)


if __name__ == '__main__':
    main()
