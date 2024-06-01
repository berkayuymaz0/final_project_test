import streamlit as st
import os
from datetime import datetime
from pdf_handler import extract_text_from_pdf, generate_embeddings
from ai_interaction import ask_question_to_openai, get_ai_suggestions
from analysis_tools import analyze_ole_files, run_analysis_tool, check_safety, check_mypy, check_black
from report_generator import generate_report
from config_manager import save_config, load_config
import tempfile
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import pandas as pd

def display_chat_history():
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

def get_relevant_context(chat_history, limit=1000):
    chat_history_text = "\n".join([f"Q: {chat['question']}\nA: {chat['answer']}"] for chat in chat_history)
    if len(chat_history_text) > limit:
        chat_history_text = chat_history_text[-limit:]
    return chat_history_text

def display_dashboard(analysis_results):
    st.subheader("Dashboard")
    st.write("Key Metrics and Trends")

    # Example chart for vulnerabilities over time
    st.write("Vulnerabilities over Time")
    df = pd.DataFrame(analysis_results)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    plt.figure(figsize=(10, 5))
    plt.plot(df.index, df['vulnerabilities'], marker='o', color='b', linestyle='-')
    plt.xlabel('Date')
    plt.ylabel('Number of Vulnerabilities')
    plt.title('Vulnerabilities Over Time')
    plt.grid(True)
    st.pyplot(plt)

    # Example bar chart for severity levels
    st.write("Severity Levels")
    severity_counts = df['severity'].value_counts()
    plt.figure(figsize=(10, 5))
    severity_counts.plot(kind='bar', color='skyblue')
    plt.xlabel('Severity Level')
    plt.ylabel('Count')
    plt.title('Severity Levels of Vulnerabilities')
    st.pyplot(plt)

    # Example pie chart for tool usage
    st.write("Tool Usage")
    tool_usage = df['tool'].value_counts()
    plt.figure(figsize=(10, 5))
    tool_usage.plot(kind='pie', autopct='%1.1f%%', startangle=90)
    plt.title('Tool Usage Distribution')
    plt.axis('equal')
    st.pyplot(plt)

def main():
    st.title("Professional Security Analysis Tool")

    sidebar_option = st.sidebar.selectbox(
        "Choose a section",
        ("PDF Question Answering", "OLE Tool", "Python Code Analysis", "Security Scans", "Dashboard", "Settings")
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
                            question_embedding = np.array(question_embedding).reshape(1, -1)
                            embeddings_array = np.array(embeddings)
                            similarities = cosine_similarity(question_embedding, embeddings_array)[0]
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
                mypy_output, mypy_error = check_mypy(temp_file_path)
                black_output, black_error = check_black(temp_file_path)
                safety_output, safety_error = check_safety()

                # Combine the outputs
                combined_output = f"Bandit Output:\n{bandit_output}\nBandit Errors:\n{bandit_error}\n\n"
                combined_output += f"Pylint Output:\n{pylint_output}\nPylint Errors:\n{pylint_error}\n\n"
                combined_output += f"Flake8 Output:\n{flake8_output}\nFlake8 Errors:\n{flake8_error}\n\n"
                combined_output += f"Mypy Output:\n{mypy_output}\nMypy Errors:\n{mypy_error}\n\n"
                combined_output += f"Black Output:\n{black_output}\nBlack Errors:\n{black_error}\n\n"
                combined_output += f"Safety Output:\n{safety_output}\nSafety Errors:\n{safety_error}\n\n"

                # Display the combined output
                st.write("Combined Analysis Results:")
                st.text(combined_output)

                # Use AI to provide suggestions based on combined output
                st.write("AI Suggestions:")
                ai_suggestions = get_ai_suggestions(combined_output)
                st.write(ai_suggestions)

                # Generate detailed report
                if st.button("Generate Report"):
                    report_path = generate_report(combined_output, ai_suggestions)
                    with open(report_path, "rb") as file:
                        st.download_button(
                            label="Download Report",
                            data=file,
                            file_name="security_analysis_report.pdf",
                            mime="application/pdf"
                        )

            finally:
                os.remove(temp_file_path)

    elif sidebar_option == "Security Scans":
        st.subheader("Security Scans")
        st.write("Run additional security scans on your project.")
        if st.button("Run Safety Check"):
            safety_output, safety_error = check_safety()
            st.write("Safety Check Results:")
            st.text(safety_output)
            if safety_error:
                st.error(safety_error)

    elif sidebar_option == "Dashboard":
        # Mock data for example purposes
        analysis_results = [
            {'date': '2023-05-01', 'vulnerabilities': 10, 'severity': 'High', 'tool': 'Bandit'},
            {'date': '2023-05-02', 'vulnerabilities': 8, 'severity': 'Medium', 'tool': 'Pylint'},
            {'date': '2023-05-03', 'vulnerabilities': 6, 'severity': 'Low', 'tool': 'Flake8'},
            {'date': '2023-05-04', 'vulnerabilities': 5, 'severity': 'High', 'tool': 'Mypy'}
        ]
        display_dashboard(analysis_results)

    elif sidebar_option == "Settings":
        st.subheader("Settings")
        config = load_config()
        
        st.write("Configure Analysis Tools")
        pylint_threshold = st.number_input("Pylint Threshold", value=config.get("pylint_threshold", 7.0))
        flake8_threshold = st.number_input("Flake8 Threshold", value=config.get("flake8_threshold", 7.0))
        
        if st.button("Save Settings"):
            config['pylint_threshold'] = pylint_threshold
            config['flake8_threshold'] = flake8_threshold
            save_config(config)
            st.success("Settings saved")

if __name__ == "__main__":
    main()
