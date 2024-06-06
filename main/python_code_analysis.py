import streamlit as st
import tempfile
import os
import logging
from analysis_tools import run_analysis_tool, check_mypy, check_black, check_safety
from ai_interaction import get_ai_suggestions
from utils import display_analysis_results, generate_summary_statistics, plot_indicator_distribution
from database import save_analysis, load_analyses, load_analysis_by_id

logger = logging.getLogger()
logging.basicConfig(level=logging.ERROR)

def analyze_python_code(file):
    results = []
    detailed_results = []
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
        temp_file.write(file.read())
        temp_file_path = temp_file.name

    try:
        bandit_output, bandit_error = run_analysis_tool('bandit', temp_file_path)
        pylint_output, pylint_error = run_analysis_tool('pylint', temp_file_path)
        flake8_output, flake8_error = run_analysis_tool('flake8', temp_file_path)
        mypy_output, mypy_error = check_mypy(temp_file_path)
        black_output, black_error = check_black(temp_file_path)
        safety_output, safety_error = check_safety()

        combined_output = (
            f"### Bandit Output:\n```\n{bandit_output}\n```\n"
            f"### Bandit Errors:\n```\n{bandit_error}\n```\n\n"
            f"### Pylint Output:\n```\n{pylint_output}\n```\n"
            f"### Pylint Errors:\n```\n{pylint_error}\n```\n\n"
            f"### Flake8 Output:\n```\n{flake8_output}\n```\n"
            f"### Flake8 Errors:\n```\n{flake8_error}\n```\n\n"
            f"### Mypy Output:\n```\n{mypy_output}\n```\n"
            f"### Mypy Errors:\n```\n{mypy_error}\n```\n\n"
            f"### Black Output:\n```\n{black_output}\n```\n"
            f"### Black Errors:\n```\n{black_error}\n```\n\n"
            f"### Safety Output:\n```\n{safety_output}\n```\n"
            f"### Safety Errors:\n```\n{safety_error}\n```\n\n"
        )

        detailed_results.append({
            "Bandit": bandit_output + bandit_error,
            "Pylint": pylint_output + pylint_error,
            "Flake8": flake8_output + flake8_error,
            "Mypy": mypy_output + mypy_error,
            "Black": black_output + black_error,
            "Safety": safety_output + safety_error
        })

        return combined_output, detailed_results

    finally:
        os.remove(temp_file_path)

def display_python_code_analysis():
    st.subheader("Python Code Analysis")

    file_to_analyze = st.file_uploader("Upload your Python file here and click on 'Analyze'", type='py')
    if st.button("Analyze") and file_to_analyze:
        with st.spinner('Analyzing the Python file...'):
            combined_output, detailed_results = analyze_python_code(file_to_analyze)
            st.success("Analysis completed!")

            st.write("### Analysis Results")
            display_analysis_results(combined_output, detailed_results)

            st.write("### AI Suggestions")
            ai_suggestions = get_ai_suggestions(combined_output, context="code analysis")
            st.write(ai_suggestions)

            st.download_button(
                label="Download Analysis Results",
                data=combined_output,
                file_name="python_code_analysis.txt",
                mime="text/plain"
            )

            summary_stats = generate_summary_statistics(detailed_results)
            st.write("### Summary Statistics")
            st.table(summary_stats)

            plot_indicator_distribution(detailed_results)

            # Save to database
            save_analysis(file_to_analyze.name, combined_output)

    st.write("## Previous Analyses")
    analyses = load_analyses()
    if analyses:
        for analysis_id, filename, result, timestamp in analyses:
            with st.expander(f"Analysis for {filename} (Uploaded on {timestamp})"):
                st.write(result)
                if st.button(f"Load Analysis {analysis_id}", key=f"load_{analysis_id}"):
                    loaded_result = load_analysis_by_id(analysis_id)
                    if loaded_result:
                        st.write("## Loaded Analysis Result")
                        st.markdown(loaded_result, unsafe_allow_html=True)
    else:
        st.write("No previous analyses found.")
