import streamlit as st
import tempfile
import os
from analysis_tools import run_analysis_tool, check_mypy, check_black, check_safety
from ai_interaction import get_ai_suggestions
from report_generator import generate_report

def display_python_code_analysis():
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

            combined_output = (
                f"Bandit Output:\n{bandit_output}\nBandit Errors:\n{bandit_error}\n\n"
                f"Pylint Output:\n{pylint_output}\nPylint Errors:\n{pylint_error}\n\n"
                f"Flake8 Output:\n{flake8_output}\nFlake8 Errors:\n{flake8_error}\n\n"
                f"Mypy Output:\n{mypy_output}\nMypy Errors:\n{mypy_error}\n\n"
                f"Black Output:\n{black_output}\nBlack Errors:\n{black_error}\n\n"
                f"Safety Output:\n{safety_output}\nSafety Errors:\n{safety_error}\n\n"
            )

            st.write("Combined Analysis Results:")
            st.text(combined_output)

            st.write("AI Suggestions:")
            ai_suggestions = get_ai_suggestions(combined_output)
            st.write(ai_suggestions)

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
