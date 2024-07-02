from langchain_community.chat_models import ChatOllama
from langchain.text_splitter import CharacterTextSplitter
import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from PyPDF2 import PdfReader
import logging
import requests

# Load environment variables from .env file
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
os.environ['OPENAI_API_KEY'] = openai_api_key

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

def get_conversation_chain(vectorstore, temp, model):
    if model == 'llama3':
        llm = ChatOllama(
            model='llama3',
            temperature=temp,
            num_gpu=1,
            top_p=0.9,
            base_url='http://localhost:11434',
            max_tokens=10000,
            max_tokens_history=10000,
        )
    else:
        llm = ChatOpenAI(temperature=temp, model_name=model)
    
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory,
    )
    return conversation_chain

def ask_question_to_openai(question, context, model="gpt-3.5-turbo"):
    try:
        temp = 0.7  # default temperature
        vectorstore = get_vectorstore(context.split("\n\n"))
        conversation_chain = get_conversation_chain(vectorstore, temp, model)
        response = conversation_chain({'question': question})
        
        # Log the entire response to inspect its structure
        logger.info(f"Response from LangChain: {response}")
        
        # Extract the answer based on the actual response structure
        answer = response.get('answer', 'No answer provided')
        logger.info(f"AI response received for question: {question}")
        return answer
    except Exception as e:
        logger.error(f"An error occurred while communicating with the OpenAI API via LangChain: {e}")
        return f"An error occurred while communicating with the OpenAI API: {e}"

def get_ai_suggestions(combined_output, context="code analysis", model="gpt-3.5-turbo"):
    try:
        prompt_context = {
            "code analysis": (
                "You are a Code Analyst AI here to assist the user based on the analysis results from various tools "
                "(e.g., Bandit, Pylint, Flake8, Mypy, Black, Safety). Identify any issues, suggest appropriate fixes, "
                "and provide a detailed explanation for each fix. Here are the analysis results:\n\n"
            ),
            "oletools": (
                "You are a Security Analyst AI specializing in OLE files. Based on the analysis results, identify any security threats, "
                "suggest appropriate mitigation strategies, and provide a detailed explanation for each indicator detected.Here are the analysis results:\n\n"
            )
        }
        temp = 0.7  # default temperature
        vectorstore = get_vectorstore(combined_output.split("\n\n"))
        conversation_chain = get_conversation_chain(vectorstore, temp, model)
        prompt = prompt_context.get(context, "You are a helpful assistant.")
        response = conversation_chain({'question': f"{prompt}{combined_output}\nPlease provide detailed suggestions and specific fixes for the identified issues."})
        
        # Log the entire response to inspect its structure
        logger.info(f"Response from LangChain: {response}")
        
        # Extract the suggestions based on the actual response structure
        suggestions = response.get('answer', 'No suggestions provided')
        logger.info(f"AI suggestions received for context: {context}")
        return suggestions
    except Exception as e:
        logger.error(f"An error occurred while communicating with the OpenAI API via LangChain: {e}")
        return f"An error occurred while communicating with the OpenAI API: {e}"


# VirusTotal Integration
VIRUSTOTAL_API_KEY = os.getenv('VIRUSTOTAL_API_KEY')

def scan_file_with_virustotal(file_path):
    url = "https://www.virustotal.com/api/v3/files"
    headers = {
        "x-apikey": VIRUSTOTAL_API_KEY
    }
    files = {
        "file": (os.path.basename(file_path), open(file_path, "rb"))
    }
    response = requests.post(url, headers=headers, files=files)
    return response.json()

def get_file_report(file_id):
    url = f"https://www.virustotal.com/api/v3/files/{file_id}"
    headers = {
        "x-apikey": VIRUSTOTAL_API_KEY
    }
    response = requests.get(url, headers=headers)
    return response.json()
