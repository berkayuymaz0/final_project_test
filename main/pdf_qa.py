import streamlit as st
import numpy as np
from datetime import datetime
from pdf_handler import extract_text_from_pdf, generate_embeddings
from ai_interaction import ask_question_to_openai
from utils import display_chat_history, get_relevant_context

def display_pdf_question_answering():
    st.subheader("PDF Question Answering")
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "first_question_asked" not in st.session_state:
        st.session_state.first_question_asked = False

    if uploaded_file is not None:
        with st.spinner('Extracting text from PDF...'):
            document_text = extract_text_from_pdf(uploaded_file)
        st.success("PDF content successfully extracted!")
        st.write(f"Filename: {uploaded_file.name}, Size: {uploaded_file.size / 1024:.2f} KB")

        chunks = document_text.split("\n\n")
        embeddings = generate_embeddings(chunks)

        if not st.session_state.first_question_asked:
            question = st.text_input("Ask a question about the PDF content", placeholder="Type your question here")

            if st.button("Ask"):
                if question:
                    with st.spinner('Generating response...'):
                        question_embedding = generate_embeddings([question])[0]
                        question_embedding = np.array(question_embedding).reshape(1, -1)
                        embeddings_array = np.array(embeddings)
                        similarities = np.matmul(question_embedding, embeddings_array.T).flatten()
                        most_relevant_chunk = chunks[np.argmax(similarities)]

                        answer = ask_question_to_openai(question, most_relevant_chunk)
                        st.session_state.chat_history.append({
                            "question": question,
                            "answer": answer,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        st.session_state.first_question_asked = True
                    st.rerun()

        if st.session_state.first_question_asked:
            follow_up_question = st.text_area("Ask a follow-up question about the chat history", placeholder="Type your follow-up question here")

            if st.button("Ask Follow-up"):
                if follow_up_question:
                    with st.spinner('Generating response...'):
                        relevant_context = get_relevant_context(st.session_state.chat_history)
                        follow_up_answer = ask_question_to_openai(follow_up_question, relevant_context)
                        st.session_state.chat_history.append({
                            "question": follow_up_question,
                            "answer": follow_up_answer,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })

        if st.session_state.chat_history:
            st.write("### Chat History")
            display_chat_history()

        if st.button("Clear Chat History"):
            st.session_state.chat_history = []
            st.session_state.first_question_asked = False
            st.rerun()
