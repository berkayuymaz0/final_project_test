import PyPDF2
import openai
import numpy as np
from dotenv import load_dotenv
import os

load_dotenv()

# Set OpenAI API key
api_key = os.getenv('OPENAI_API_KEY')
if api_key is None:
    raise ValueError("OpenAI API key not found. Please set the 'OPENAI_API_KEY' environment variable.")

openai.api_key = api_key

def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        num_pages = len(pdf_reader.pages)
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
        return text
    except Exception as e:
        raise RuntimeError(f"Error extracting text from PDF: {e}")

def generate_embeddings(text):
    try:
        response = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=text
        )
        embeddings = np.array([data['embedding'] for data in response['data']])
        return embeddings
    except openai.error.OpenAIError as e:
        raise RuntimeError(f"Error generating embeddings: {e}")
