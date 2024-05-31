import PyPDF2
import openai
import numpy as np
from dotenv import load_dotenv
import os 
load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    num_pages = len(pdf_reader.pages)
    for page_num in range(num_pages):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    return text

def generate_embeddings(text):
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text
    )
    embeddings = np.array([data['embedding'] for data in response['data']])
    return embeddings
