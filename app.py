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
from langchain.llms import HuggingFaceHub
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# Configuration settings
CONFIG = {
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "api_key": os.getenv("OPENAI_API_KEY"),
    "max_retries": 3
}

# Utility function to display messages
def display_message(message, template):
    st.write(template.replace("{{MSG}}", message.content), unsafe_allow_html=True)

# Function to read PDF content
def extract_pdf_text(pdf_files):
    combined_text = ""
    try:
        for pdf_file in pdf_files:
            pdf_reader = PdfReader(pdf_file)
            for page in pdf_reader.pages:
                combined_text += page.extract_text()
    except Exception as e:
        logging.error(f"Error reading PDF: {e}")
        st.error(f"Error reading PDF: {e}")
    return combined_text

# Function to split text into chunks
def split_text_into_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=CONFIG["chunk_size"],
        chunk_overlap=CONFIG["chunk_overlap"],
        length_function=len
    )
    return text_splitter.split_text(text)

# Function to create vector store
def create_vector_store(text_chunks):
    embeddings_model = OpenAIEmbeddings()
    return FAISS.from_texts(texts=text_chunks, embedding=embeddings_model)

# Function to create conversation chain
def create_conversation_chain(vector_store):
    llm_model = ChatOpenAI()
    memory_buffer = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    return ConversationalRetrievalChain.from_llm(llm=llm_model, retriever=vector_store.as_retriever(), memory=memory_buffer)

# Function to handle user input
def handle_user_input(user_query):
    response = st.session_state.conversation({'question': user_query})
    st.session_state.chat_history = response['chat_history']
    for i, message in enumerate(st.session_state.chat_history):
        template = user_template if i % 2 == 0 else bot_template
        display_message(message, template)

# Function to summarize text
def summarize_text(text):
    try:
        summarizer_model = HuggingFaceHub(repo_id="facebook/bart-large-cnn")
        summary = summarizer_model(text)
        return summary
    except Exception as e:
        logging.error(f"Error summarizing text: {e}")
        st.error(f"Error summarizing text: {e}")
        return "Summary not available."

# Function to perform sentiment analysis
def perform_sentiment_analysis(text):
    try:
        sentiment_model = HuggingFaceHub(repo_id="distilbert-base-uncased-finetuned-sst-2-english")
        sentiment = sentiment_model(text)
        return sentiment
    except Exception as e:
        logging.error(f"Error performing sentiment analysis: {e}")
        st.error(f"Error performing sentiment analysis: {e}")
        return "Sentiment analysis not available."

# Function to process PDF files
def process_pdf_files(pdf_files):
    extracted_text = extract_pdf_text(pdf_files)
    if extracted_text:
        text_chunks = split_text_into_chunks(extracted_text)
        vector_store = create_vector_store(text_chunks)
        st.session_state.conversation = create_conversation_chain(vector_store)
        text_summary = summarize_text(extracted_text)
        sentiment_analysis = perform_sentiment_analysis(extracted_text)
        st.write("Summary:", text_summary)
        st.write("Sentiment Analysis:", sentiment_analysis)

# Function to analyze OLE files
def analyze_ole_files(ole_files):
    for ole_file in ole_files:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
                temp_file.write(ole_file.read())
                temp_file_path = temp_file.name
            ole_identifier = oletools.oleid.OleID(temp_file_path)
            indicators = ole_identifier.check()
            st.write(f"Results for {ole_file.name}:")
            for indicator in indicators:
                st.write(f'Indicator id={indicator.id} name="{indicator.name}" type={indicator.type} value={repr(indicator.value)}')
                st.write('Description:', indicator.description)
                st.write('')
            os.remove(temp_file_path)
        except Exception as e:
            logging.error(f"Error analyzing OLE file: {e}")
            st.error(f"Error analyzing OLE file: {e}")

# Function to analyze Python code
def analyze_python_file(python_file):
    def run_bandit_analysis(file_path):
        try:
            result = subprocess.run(['bandit', file_path], capture_output=True, text=True, check=True)
            st.write("Bandit Analysis Results:")
            st.write(result.stdout)
        except subprocess.CalledProcessError as e:
            logging.error(f"Bandit encountered an error: {e.stderr}")
            st.error(f"Bandit encountered an error: {e.stderr}")
        except FileNotFoundError:
            logging.error("Bandit is not installed.")
            st.error("Bandit is not installed. Please install it using 'pip install bandit'.")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
            temp_file.write(python_file.read())
            temp_file_path = temp_file.name
        run_bandit_analysis(temp_file_path)
        os.remove(temp_file_path)
    except Exception as e:
        logging.error(f"Error analyzing Python code: {e}")
        st.error(f"Error analyzing Python code: {e}")

# Main function
def main():
    st.set_page_config(page_title="AppSec", page_icon="random", layout="wide")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    st.header("AppSec Test Application")

    user_query = st.text_input("User input")
    if user_query:
        handle_user_input(user_query)

    with st.sidebar:
        st.subheader("PDF with AI")
        pdf_files = st.file_uploader("Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
        if st.button("Process") and pdf_files:
            with st.spinner("Processing"):
                process_pdf_files(pdf_files)

        st.subheader("OLE Tool")
        ole_files = st.file_uploader("Upload your file here and click on 'Use OLE Tool'", accept_multiple_files=True)
        if st.button("Use") and ole_files:
            analyze_ole_files(ole_files)

        st.subheader("Python Code Analyzer")
        python_file = st.file_uploader("Upload your Python file here and click on 'Analyze'", type='py', accept_multiple_files=False)
        if st.button("Analyze") and python_file:
            analyze_python_file(python_file)

if __name__ == '__main__':
    main()
