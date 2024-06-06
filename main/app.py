import streamlit as st
from pdf_qa import display_pdf_question_answering
from ole_tool import display_ole_tool
from python_code_analysis import display_python_code_analysis
from security_scans import display_security_scans
from dashboard import display_dashboard
from settings import display_settings

def main():
    st.title("Professional Security Analysis Tool")

    sidebar_option = st.sidebar.selectbox(
        "Choose a section",
        ("PDF Question Answering", "OLE Tool", "Python Code Analysis", "Security Scans", "Dashboard", "Settings")
    )

    if sidebar_option == "PDF Question Answering":
        display_pdf_question_answering()
    elif sidebar_option == "OLE Tool":
        display_ole_tool()
    elif sidebar_option == "Python Code Analysis":
        display_python_code_analysis()
    elif sidebar_option == "Security Scans":
        display_security_scans()
    elif sidebar_option == "Dashboard":
        display_dashboard()
    elif sidebar_option == "Settings":
        display_settings()

if __name__ == "__main__":
    main()
