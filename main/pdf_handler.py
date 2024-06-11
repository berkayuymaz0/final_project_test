import PyPDF2
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
import logging
import warnings

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress specific FutureWarnings
warnings.filterwarnings("ignore", category=FutureWarning, module="huggingface_hub.file_download")

# Load the Sentence Transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

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
        logger.error(f"Error extracting text from PDF: {e}")
        raise RuntimeError(f"Error extracting text from PDF: {e}")

def generate_embeddings(texts):
    try:
        embeddings = model.encode(texts, convert_to_tensor=True)
        return embeddings
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        raise RuntimeError(f"Error generating embeddings: {e}")
