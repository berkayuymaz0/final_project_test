import streamlit as st
import numpy as np
from datetime import datetime
from pdf_handler import extract_text_from_pdf, generate_embeddings
from ai_interaction import ask_question_to_openai
from utils import display_chat_history
from database_ole import load_analyses, save_context, load_context, clear_context
from sentence_transformers import util
import logging
import html

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_combined_context():
    """
    Load all analyses and combine their results into a single context string.
    
    :return: Combined context as a string.
    """
    try:
        analyses = load_analyses()
        combined_context = ""
        if analyses:
            for analysis_id, filename, result, timestamp in analyses:
                combined_context += f"Analysis for {filename} (Uploaded on {timestamp}):\n{result}\n\n"
        return combined_context
    except Exception as e:
        logger.error(f"Error loading analyses: {e}")
        return ""

def update_context_memory(user_input, answer):
    """
    Update the context memory with the latest question and answer.
    
    :param user_input: The user's input question.
    :param answer: The generated answer from the AI.
    """
    st.session_state.context_memory += f"\nQ: {user_input}\nA: {answer}"
    save_context(st.session_state.context_memory)

def handle_file_upload(uploaded_file):
    """
    Handle the uploaded PDF file and extract its text.
    
    :param uploaded_file: The uploaded PDF file.
    :return: Extracted text from the PDF.
    """
    with st.spinner('Extracting text from PDF...'):
        try:
            pdf_text = extract_text_from_pdf(uploaded_file)
            st.success("PDF content successfully extracted!")
            st.write(f"Filename: {uploaded_file.name}, Size: {uploaded_file.size / 1024:.2f} KB")
            return pdf_text
        except Exception as e:
            st.error(f"Error extracting text from PDF: {e}")
            logger.error(f"Error extracting text from PDF: {e}")
            return ""

def handle_user_input(user_input, pdf_text, combined_context, model):
    """
    Handle the user's input, generate a response, and update the chat history.
    
    :param user_input: The user's input question.
    :param pdf_text: The extracted text from the uploaded PDF.
    :param combined_context: The combined context from previous analyses and context memory.
    :param model: The selected AI model.
    """
    context = combined_context + st.session_state.context_memory
    if pdf_text:
        chunks = pdf_text.split("\n\n")
        embeddings = generate_embeddings(chunks)
        question_embedding = generate_embeddings([user_input])[0]
        similarities = util.cos_sim(question_embedding, embeddings)[0]
        most_relevant_chunk = chunks[similarities.argmax()]
        context += f"\nContext from PDF: {most_relevant_chunk}"

    with st.spinner('Generating response...'):
        try:
            answer = ask_question_to_openai(user_input, context, model)
            st.session_state.chat_history.append({
                "question": user_input,
                "answer": answer,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            update_context_memory(user_input, answer)
        except Exception as e:
            st.error(f"Error generating response: {e}")
            logger.error(f"Error generating response: {e}")

def display_pdf_question_answering():
    """
    Display the PDF Question Answering chatbot interface.
    """
    st.title("PDF Question Answering Chatbot")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "context_memory" not in st.session_state:
        st.session_state.context_memory = load_context()

    pdf_text = ""
    uploaded_file = st.file_uploader("Upload a PDF file (optional)", type="pdf")
    if uploaded_file is not None:
        pdf_text = handle_file_upload(uploaded_file)

    combined_context = get_combined_context()
    user_input = st.text_input("You: ", placeholder="Type your message here")

    model = st.selectbox("Choose AI Model", options=["gpt-3.5-turbo", "gpt-4"])

    if st.button("Send"):
        if user_input:
            handle_user_input(user_input, pdf_text, combined_context, model)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Chat History")
    display_chat_history(st.session_state.chat_history)

    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.session_state.context_memory = ""
        clear_context()
        st.rerun()  # Updated

    chat_history_text = "\n\n".join([f"You: {chat['question']}\nBot: {chat['answer']}\nTimestamp: {chat['timestamp']}" for chat in st.session_state.chat_history])
    st.download_button(
        label="Download Chat History",
        data=chat_history_text,
        file_name="chat_history.txt",
        mime="text/plain"
    )

def display_chat_history(chat_history):
    """
    Display the chat history in a formatted manner.
    
    :param chat_history: List of dictionaries containing chat history.
    """
    for chat in chat_history:
        st.markdown(f"""
        <div style='border: 1px solid #ccc; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>
            <p><strong>You:</strong> {html.escape(chat['question'])}</p>
            <p><strong>Bot:</strong> {html.escape(chat['answer'])}</p>
            <p style='text-align: right; font-size: 0.8em; color: #888;'><i>{chat['timestamp']}</i></p>
        </div>
        """, unsafe_allow_html=True)

# Ensure the functions are imported correctly for Streamlit to recognize them
if __name__ == "__main__":
    display_pdf_question_answering()
