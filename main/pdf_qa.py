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

def display_pdf_question_answering():

    st.title("PDF Question Answering Chatbot")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "context_memory" not in st.session_state:
        st.session_state.context_memory = load_context()

    pdf_text = ""
    uploaded_file = st.file_uploader("Upload a PDF file (optional)", type="pdf")
    if uploaded_file is not None:
        with st.spinner('Extracting text from PDF...'):
            try:
                pdf_text = extract_text_from_pdf(uploaded_file)
                st.success("PDF content successfully extracted!")
                st.write(f"Filename: {uploaded_file.name}, Size: {uploaded_file.size / 1024:.2f} KB")
            except Exception as e:
                st.error(f"Error extracting text from PDF: {e}")
                logger.error(f"Error extracting text from PDF: {e}")

    combined_context = get_combined_context()
    user_input = st.text_input("You: ", placeholder="Type your message here")

    model = st.selectbox("Choose AI Model", options=["gpt-3.5-turbo", "gpt-4"])

    if st.button("Send"):
        if user_input:
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
                    st.session_state.context_memory += f"\nQ: {user_input}\nA: {answer}"
                    save_context(st.session_state.context_memory)
                except Exception as e:
                    st.error(f"Error generating response: {e}")
                    logger.error(f"Error generating response: {e}")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Chat History")
    display_chat_history(st.session_state.chat_history)

    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.session_state.context_memory = ""
        clear_context()
        st.experimental_rerun()

    chat_history_text = "\n\n".join([f"You: {chat['question']}\nBot: {chat['answer']}\nTimestamp: {chat['timestamp']}" for chat in st.session_state.chat_history])
    st.download_button(
        label="Download Chat History",
        data=chat_history_text,
        file_name="chat_history.txt",
        mime="text/plain"
    )

def display_chat_history(chat_history):
    for chat in chat_history:
        st.markdown(f"""
        <div style='border: 1px solid #ccc; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>
            <p><strong>You:</strong> {html.escape(chat['question'])}</p>
            <p><strong>Bot:</strong> {html.escape(chat['answer'])}</p>
            <p style='text-align: right; font-size: 0.8em; color: #888;'><i>{chat['timestamp']}</i></p>
        </div>
        """, unsafe_allow_html=True)
