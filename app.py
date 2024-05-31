import streamlit as st
import PyPDF2
import openai
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
from datetime import datetime
import subprocess
import tempfile
import oletools.oleid
import logging

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

logger = logging.getLogger()
logging.basicConfig(level=logging.ERROR)

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    return text

@st.cache_data
def generate_embeddings(text):
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text
    )
    embeddings = np.array([data['embedding'] for data in response['data']])
    return embeddings

def ask_question_to_openai(question, context):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"{context}\n\nQ: {question}\nA:"}
        ]
    )
    answer = response['choices'][0]['message']['content'].strip()
    return answer

def run_analysis_tool(tool_name, file_path):
    try:
        result = subprocess.run(
            [tool_name, file_path] if tool_name in ['pylint', 'flake8'] else [tool_name, '-r', file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        return result.stdout, result.stderr
    except FileNotFoundError:
        st.write(f"{tool_name.capitalize()} is not installed. Please install it using 'pip install {tool_name}'.")
    except Exception as e:
        logger.error(f"Error running {tool_name}: {e}")
        st.error(f"Error running {tool_name}. Please try again.")
    return "", ""

def analyze_ole_files(files):
    for uploaded_file in files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name

        try:
            oid = oletools.oleid.OleID(temp_file_path)
            indicators = oid.check()

            st.write(f"Results for {uploaded_file.name}:")
            for indicator in indicators:
                st.write(f'Indicator id={indicator.id} name="{indicator.name}" type={indicator.type} value={repr(indicator.value)}')
                st.write('Description:', indicator.description)
                st.write('')
        except Exception as e:
            logger.error(f"Error analyzing OLE file: {e}")
            st.error("Error analyzing OLE file. Please try again.")
        finally:
            os.remove(temp_file_path)

def get_ai_suggestions(combined_output):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a code analysis expert."},
            {"role": "user", "content": f"Here are the results of the code analysis:\n{combined_output}\nPlease provide suggestions for improvement."}
        ]
    )
    suggestions = response['choices'][0]['message']['content'].strip()
    return suggestions

def main():
    st.title("PDF Question Answering and Analysis Tool")

    sidebar_option = st.sidebar.selectbox(
        "Choose a section",
        ("PDF Question Answering", "OLE Tool", "Python Code Analysis")
    )

    if sidebar_option == "PDF Question Answering":
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
                            similarities = cosine_similarity([question_embedding], embeddings)[0]
                            most_relevant_chunk = chunks[np.argmax(similarities)]

                            answer = ask_question_to_openai(question, most_relevant_chunk)
                            st.session_state.chat_history.append({
                                "question": question,
                                "answer": answer,
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            })
                            st.session_state.first_question_asked = True
                        st.experimental_rerun()

            if st.session_state.first_question_asked:
                follow_up_question = st.text_area("Ask a follow-up question about the chat history", placeholder="Type your follow-up question here")

                if st.button("Ask Follow-up"):
                    if follow_up_question:
                        with st.spinner('Generating response...'):
                            chat_history_text = "\n".join([f"Q: {chat['question']}\nA: {chat['answer']}" for chat in st.session_state.chat_history])
                            follow_up_answer = ask_question_to_openai(follow_up_question, chat_history_text)
                            st.session_state.chat_history.append({
                                "question": follow_up_question,
                                "answer": follow_up_answer,
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            })

            if st.session_state.chat_history:
                st.write("### Chat History")
                chat_history_html = ""
                for i, chat in enumerate(st.session_state.chat_history):
                    chat_history_html += f"""
                    <div style="padding: 10px; border: 1px solid #ccc; border-radius: 5px; margin-bottom: 10px;">
                        <strong>Q{i+1}:</strong> {chat['question']}<br>
                        <strong>A{i+1}:</strong> {chat['answer']}<br>
                        <small><i>{chat['timestamp']}</i></small>
                    </div>
                    """
                st.markdown(chat_history_html, unsafe_allow_html=True)

            if st.button("Clear Chat History"):
                st.session_state.chat_history = []
                st.session_state.first_question_asked = False
                st.experimental_rerun()

    elif sidebar_option == "OLE Tool":
        st.subheader("OLE Tool")
        ole_files = st.file_uploader("Upload your file here and click on 'Use OLE Tool'", accept_multiple_files=True)
        if st.button("Use OLE Tool") and ole_files:
            analyze_ole_files(ole_files)

    elif sidebar_option == "Python Code Analysis":
        st.subheader("Python Code Analysis")
        file_to_analyze = st.file_uploader("Upload your Python file here and click on 'Analyze'", type='py')
        if st.button("Analyze") and file_to_analyze:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
                temp_file.write(file_to_analyze.read())
                temp_file_path = temp_file.name
            try:
                bandit_output, bandit_error = run_analysis_tool('bandit', temp_file_path)
                pylint_output, pylint_error = run_analysis_tool('pylint', temp_file_path)
                flake8_output, flake8_error = run_analysis_tool('flake8', temp_file_path)

                # Combine the outputs
                combined_output = f"Bandit Output:\n{bandit_output}\nBandit Errors:\n{bandit_error}\n\n"
                combined_output += f"Pylint Output:\n{pylint_output}\nPylint Errors:\n{pylint_error}\n\n"
                combined_output += f"Flake8 Output:\n{flake8_output}\nFlake8 Errors:\n{flake8_error}\n\n"

                # Display the combined output
                st.write("Combined Analysis Results:")
                st.text(combined_output)

                # Use AI to provide suggestions based on combined output
                st.write("AI Suggestions:")
                ai_suggestions = get_ai_suggestions(combined_output)
                st.write(ai_suggestions)
            finally:
                os.remove(temp_file_path)

if __name__ == "__main__":
    main()
