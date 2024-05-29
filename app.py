import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, bot_template, user_template
import subprocess
import os
import tempfile
import oletools.oleid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_pdf_text(pdf_docs):
    text = ""
    try:
        for pdf in pdf_docs:
            pdf_reader = PdfReader(pdf)
            for page in pdf_reader.pages:
                text += page.extract_text()
    except Exception as e:
        logger.error(f"Error reading PDF: {e}")
        st.error("Error reading PDF. Please try again.")
    return text

def get_text_chunks(text):
    try:
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
    except Exception as e:
        logger.error(f"Error splitting text: {e}")
        st.error("Error processing text. Please try again.")
        chunks = []
    return chunks

def get_vectorstore(text_chunks):
    try:
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    except Exception as e:
        logger.error(f"Error creating vectorstore: {e}")
        st.error("Error creating vectorstore. Please try again.")
        vectorstore = None
    return vectorstore

def get_conversation_chain(vectorstore):
    try:
        llm = ChatOpenAI()
        memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
        conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever(),
            memory=memory
        )
    except Exception as e:
        logger.error(f"Error creating conversation chain: {e}")
        st.error("Error creating conversation chain. Please try again.")
        conversation_chain = None
    return conversation_chain

def handle_userinput(user_question):
    try:
        response = st.session_state.conversation({'question': user_question})
        st.session_state.chat_history = response['chat_history']

        for i, message in enumerate(st.session_state.chat_history):
            template = user_template if i % 2 == 0 else bot_template
            st.write(template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
    except Exception as e:
        logger.error(f"Error handling user input: {e}")
        st.error("Error processing user input. Please try again.")

def run_analysis_tool(tool_name, file_path):
    try:
        result = subprocess.run(
            [tool_name, file_path] if tool_name in ['pylint', 'flake8'] else [tool_name, '-r', file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        return result.stdout, result.stderr
    except FileNotFoundError:
        st.write(f"{tool_name.capitalize()} is not installed. Please install it using 'pip install {tool_name}'.")
    except Exception as e:
        logger.error(f"Error running {tool_name}: {e}")
        st.error(f"Error running {tool_name}. Please try again.")
    return "", ""

def analyze_ole_files(files):
    for uploaded_file in files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name

        try:
            oid = oletools.oleid.OleID(temp_file_path)
            indicators = oid.check()

            st.write(f"Results for {uploaded_file.name}:")
            for indicator in indicators:
                st.write(f'Indicator id={indicator.id} name="{indicator.name}" type={indicator.type} value={repr(indicator.value)}')
                st.write('Description:', indicator.description)
                st.write('')
        except Exception as e:
            logger.error(f"Error analyzing OLE file: {e}")
            st.error("Error analyzing OLE file. Please try again.")
        finally:
            os.remove(temp_file_path)

def process_pdfs(pdf_docs):
    with st.spinner("Processing"):
        raw_text = get_pdf_text(pdf_docs)
        text_chunks = get_text_chunks(raw_text)
        vectorstore = get_vectorstore(text_chunks)
        if vectorstore:
            st.session_state.conversation = get_conversation_chain(vectorstore)

def ensure_conversation_chain():
    if "conversation" not in st.session_state or st.session_state.conversation is None:
        # Initialize conversation chain with an empty vectorstore if not already initialized
        st.session_state.conversation = get_conversation_chain(get_vectorstore([]))

def get_ai_suggestions(combined_output):
    try:
        ensure_conversation_chain()  # Ensure conversation chain is initialized

        response = st.session_state.conversation({'question': f"Please provide suggestions based on the following analysis results:\n{combined_output}"})
        suggestions = response['chat_history'][-1].content
        return suggestions
    except Exception as e:
        logger.error(f"Error getting AI suggestions: {e}")
        return "Error getting AI suggestions. Please try again."

def main():
    load_dotenv()
    st.set_page_config(page_title="AppSec", page_icon="random", layout="wide")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    st.header("test_app")
    user_question = st.text_input("user input")
    if user_question:
        if st.session_state.conversation:
            handle_userinput(user_question)
        else:
            st.error("Please process a PDF first to initialize the conversation chain.")

    with st.sidebar:
        st.subheader("Pdf with AI")
        pdf_docs = st.file_uploader("Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
        if st.button("Process") and pdf_docs:
            process_pdfs(pdf_docs)

        st.subheader("Ole Tool")
        ole_files = st.file_uploader("Upload your file here and click on 'use oletool'", accept_multiple_files=True)
        if st.button("Use") and ole_files:
            analyze_ole_files(ole_files)

        st.subheader("Python code analyze")
        file_to_analyze = st.file_uploader("Upload your Python file here and click on 'Analyze'", type='py')
        if st.button("Analyze") and file_to_analyze:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
                temp_file.write(file_to_analyze.read())
                temp_file_path = temp_file.name
            try:
                bandit_output, bandit_error = run_analysis_tool('bandit', temp_file_path)
                pylint_output, pylint_error = run_analysis_tool('pylint', temp_file_path)
                flake8_output, flake8_error = run_analysis_tool('flake8', temp_file_path)

                # Combine the outputs
                combined_output = f"Bandit Output:\n{bandit_output}\nBandit Errors:\n{bandit_error}\n\n"
                combined_output += f"Pylint Output:\n{pylint_output}\nPylint Errors:\n{pylint_error}\n\n"
                combined_output += f"Flake8 Output:\n{flake8_output}\nFlake8 Errors:\n{flake8_error}\n\n"

                # Display the combined output
                st.write("Combined Analysis Results:")
                st.text(combined_output)

                # Use AI to provide suggestions based on combined output
                st.write("AI Suggestions:")
                ai_suggestions = get_ai_suggestions(combined_output)
                st.write(ai_suggestions)
            finally:
                os.remove(temp_file_path)

if __name__ == '__main__':
    main()
