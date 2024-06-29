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
    """
    Extract text from a PDF file.
    
    :param file: File-like object representing the PDF file.
    :return: Extracted text as a string.
    """
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        num_pages = len(pdf_reader.pages)
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() or ""
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        raise RuntimeError(f"Error extracting text from PDF: {e}")

def generate_embeddings(texts):
    """
    Generate embeddings for a list of texts using a Sentence Transformer model.
    
    :param texts: List of texts to generate embeddings for.
    :return: Embeddings as a tensor.
    """
    try:
        embeddings = model.encode(texts, convert_to_tensor=True)
        return embeddings
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        raise RuntimeError(f"Error generating embeddings: {e}")

# Example usage
if __name__ == "__main__":
    sample_pdf_path = "sample.pdf"
    try:
        with open(sample_pdf_path, "rb") as f:
            text = extract_text_from_pdf(f)
            logger.info(f"Extracted text: {text[:500]}")  # Log the first 500 characters of extracted text

            texts = text.split("\n")  # Example: split text into sentences or paragraphs
            embeddings = generate_embeddings(texts)
            logger.info(f"Generated embeddings: {embeddings}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
