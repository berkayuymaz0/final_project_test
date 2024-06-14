import os
import logging
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key
api_key = os.getenv('OPENAI_API_KEY')
if api_key is None:
    raise ValueError("OpenAI API key not found. Please set the 'OPENAI_API_KEY' environment variable.")

client = OpenAI(api_key=api_key)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ask_question_to_openai(question, context, model="gpt-3.5-turbo"):
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{context}\n\nQ: {question}\nA:"}
            ],
            model=model,
            max_tokens=150,
            temperature=0.7,
            top_p=0.9
        )
        answer = response.choices[0].message.content.strip()
        logger.info(f"AI response received for question: {question}")
        return answer
    except Exception as e:
        logger.error(f"An error occurred while communicating with the OpenAI API: {e}")
        return f"An error occurred while communicating with the OpenAI API: {e}"

def get_ai_suggestions(combined_output, context="code analysis", model="gpt-3.5-turbo"):
    try:
        prompt_context = {
            "code analysis": "You are a code analysis expert.",
            "oletools": (
                "You are an expert in analyzing OLE files and identifying potential security threats. "
                "Based on the following analysis results, identify any security threats, suggest appropriate mitigation strategies, "
                "and provide a detailed explanation for each indicator detected."
            )
        }
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt_context.get(context, "You are a helpful assistant.")},
                {"role": "user", "content": f"Here are the results of the analysis:\n{combined_output}\nPlease provide detailed suggestions and insights."}
            ],
            model=model,
            max_tokens=150,
            temperature=0.7,
            top_p=0.9
        )
        suggestions = response.choices[0].message.content.strip()
        logger.info(f"AI suggestions received for context: {context}")
        return suggestions
    except Exception as e:
        logger.error(f"An error occurred while communicating with the OpenAI API: {e}")
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
