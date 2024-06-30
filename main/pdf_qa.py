import streamlit as st
import numpy as np
from datetime import datetime
from pdf_handler import extract_text_from_pdf, generate_embeddings
from ai_interaction import ask_question_to_openai
from sentence_transformers import util
import logging
import html

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prompts
gen_prompt = '''
    You are a general assistant AI chatbot here to assist the user based on the PDFs they uploaded,
    and the subsequent openAI embeddings. Please assist the user to the best of your knowledge based on 
    uploads, embeddings and the following user input. USER INPUT: 
'''

acc_prompt = '''
    You are an academic assistant AI chatbot here to assist the user based on the academic PDFs they uploaded,
    and the subsequent openAI embeddings. This academic persona allows you to use as much outside academic responses as you can.
    But remember this is an app for academic PDF questions. Please respond in as academic a way as possible, with an academic audience in mind.
    Please assist the user to the best of your knowledge, with this academic persona
    based on uploads, embeddings and the following user input. USER INPUT: 
'''

witty_prompt = '''
    You are a witty assistant AI chatbot here to assist the user based on the PDFs they uploaded,
    and the subsequent openAI embeddings. This witty persona should make you come off as lighthearted,
    be joking responses and original, with the original user question still being answered.
    Please assist the user to the best of your knowledge, with this comedic persona
    based on uploads, embeddings and the following user input. USER INPUT: 
'''

def set_prompt(personality):
    if personality == 'general assistant':
        return gen_prompt
    elif personality == 'academic':
        return acc_prompt
    elif personality == 'witty':
        return witty_prompt

def display_pdf_question_answering():
    st.title("PDF Question Answering Chatbot")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

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

    # Chatbot settings
    st.sidebar.header("Chat Bot Settings")
    model = st.selectbox(label='Model', options=['gpt-3.5-turbo','llama3'])
    personality = st.sidebar.selectbox('Personality', options=['general assistant', 'academic', 'witty'])
    temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.5)
    prompt = set_prompt(personality)

    user_input = st.text_input("You: ", placeholder="Type your message here")

    if st.button("Send"):
        if user_input:
            context = prompt
            if pdf_text:
                chunks = pdf_text.split("\n\n")
                embeddings = generate_embeddings(chunks)
                question_embedding = generate_embeddings([user_input])[0]
                similarities = util.cos_sim(question_embedding, embeddings)[0]
                most_relevant_chunk = chunks[similarities.argmax()]
                context += f"\nContext from PDF: {most_relevant_chunk}"

            with st.spinner('Generating response...'):
                try:
                    answer = ask_question_to_openai(user_input, context, model=model)
                    st.session_state.chat_history.append({
                        "question": user_input,
                        "answer": answer,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                except Exception as e:
                    st.error(f"Error generating response: {e}")
                    logger.error(f"Error generating response: {e}")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Chat History")
    display_chat_history(st.session_state.chat_history)

    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
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

if __name__ == "__main__":
    display_pdf_question_answering()
