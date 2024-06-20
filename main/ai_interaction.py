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

# Set VirusTotal API key
virustotal_api_key = os.getenv('VIRUSTOTAL_API_KEY')
if virustotal_api_key is None:
    raise ValueError("VirusTotal API key not found. Please set the 'VIRUSTOTAL_API_KEY' environment variable.")

client = OpenAI(api_key=api_key)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ask_question_to_openai(question, context, model="gpt-3.5-turbo"):
    return _query_openai(
        system_message="You are a helpful assistant.",
        user_message=f"{context}\n\nQ: {question}\nA:",
        model=model
    )

def get_ai_suggestions(combined_output, context="code analysis", model="gpt-3.5-turbo"):
    prompt_context = {
        "code analysis": "You are a code analysis expert.",
        "oletools": (
            "You are an expert in analyzing OLE files and identifying potential security threats. "
            "Based on the following analysis results, identify any security threats, suggest appropriate mitigation strategies, "
            "and provide a detailed explanation for each indicator detected."
        )
    }
    return _query_openai(
        system_message=prompt_context.get(context, "You are a helpful assistant."),
        user_message=f"Here are the results of the analysis:\n{combined_output}\nPlease provide detailed suggestions and insights.",
        model=model
    )

def _query_openai(system_message, user_message, model):
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            model=model,
            max_tokens=150,
            temperature=0.7,
            top_p=0.9
        )
        answer = response.choices[0].message.content.strip()
        logger.info(f"AI response received for query.")
        return answer
    except Exception as e:
        logger.error(f"An error occurred while communicating with the OpenAI API: {e}")
        return f"An error occurred while communicating with the OpenAI API: {e}"

def scan_file_with_virustotal(file_path):
    url = "https://www.virustotal.com/api/v3/files"
    headers = {"x-apikey": virustotal_api_key}
    try:
        with open(file_path, "rb") as file:
            files = {"file": (os.path.basename(file_path), file)}
            response = requests.post(url, headers=headers, files=files)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"An error occurred while scanning the file with VirusTotal: {e}")
        return f"An error occurred while scanning the file with VirusTotal: {e}"

def get_file_report(file_id):
    url = f"https://www.virustotal.com/api/v3/files/{file_id}"
    headers = {"x-apikey": virustotal_api_key}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"An error occurred while retrieving the file report from VirusTotal: {e}")
        return f"An error occurred while retrieving the file report from VirusTotal: {e}"
