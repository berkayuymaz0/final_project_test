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
from langchain.llms import HuggingFaceHub
import streamlit as st
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
    chunks = text_splitter.split_text(text)
    return chunks


def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()

    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore


def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
 
    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain


def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)


def main():
    load_dotenv()
    st.set_page_config(page_title="AppSec",
                       page_icon="random", layout="wide",)
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    st.header("test_app")
    user_question = st.text_input("user input")
    if user_question:
        handle_userinput(user_question)

    with st.sidebar:
        st.subheader("Pdf with AI")
        pdf_docs = st.file_uploader(
            "Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
        if st.button("Process"):
            with st.spinner("Processing"):
                # get pdf text
                raw_text = get_pdf_text(pdf_docs)

                # get the text chunks
                text_chunks = get_text_chunks(raw_text)

                # create vector store
                vectorstore = get_vectorstore(text_chunks)

                # create conversation chain
                st.session_state.conversation = get_conversation_chain(
                    vectorstore)
       
        st.subheader("Ole Tool")

# File uploader widget for multiple files
        file = st.file_uploader("Upload your file here and click on 'use oletool'", accept_multiple_files=True)

        if st.button("Use"):
            if file is not None:
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

                    # Optionally, delete the temporary file after analysis
                    os.remove(temp_file_path)
            else:
                st.write("Please upload a file to analyze.")
        st.subheader("Python code analyze")
        file_to_analyze = st.file_uploader("Upload your Python file here and click on 'Python code analyze'", type='py', accept_multiple_files=False)
        
        if st.button("Analyze"):
            if file_to_analyze is not None:
                def run_bandit(file_path):
                    try:
                        # Run the Bandit command
                        result = subprocess.run(['bandit', file_path], capture_output=True, text=True, check=True)

                        # Print the output
                        st.write("Bandit Analysis Results:")
                        st.write(result.stdout)

                    except subprocess.CalledProcessError as e:
                        # If there's an error (e.g., Bandit found issues), print the error output
                        st.write("Bandit encountered an error:")
                        st.write(e.stderr)
                    except FileNotFoundError:
                        st.write("Bandit is not installed. Please install it using 'pip install bandit'.")

                # Save the uploaded file to a temporary location
                with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
                    temp_file.write(file_to_analyze.read())
                    temp_file_path = temp_file.name

                # Run the bandit analysis on the saved file
                run_bandit(temp_file_path)

                # Optionally, delete the temporary file after analysis
                os.remove(temp_file_path)
            else:
                st.write("Please upload a Python file to analyze.")


if __name__ == '__main__':
    main()
