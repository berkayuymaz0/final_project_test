import streamlit as st
import tempfile
import os
import logging
from analysis_tools import run_analysis_tool, check_mypy, check_black, check_safety
from ai_interaction import get_ai_suggestions, scan_file_with_virustotal, get_file_report
from utils import display_analysis_results, generate_summary_statistics, plot_indicator_distribution, export_analysis_results_to_csv, export_analysis_results_to_json, export_analysis_results_to_pdf
from database_code import save_analysis, load_analyses, load_analysis_by_id

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_python_code(file):
    """
    Analyze a Python file using various tools and return the combined output and detailed results.
    
    :param file: File-like object representing the Python file to analyze.
    :return: Tuple of combined output string and detailed results dictionary.
    """
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
        
        vt_scan_result = scan_file_with_virustotal(temp_file_path)
        file_id = vt_scan_result.get('data', {}).get('id')
        vt_report = get_file_report(file_id) if file_id else {}

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
            f"### VirusTotal Scan Result:\n```\n{vt_scan_result}\n```\n"
            f"### VirusTotal Report:\n```\n{vt_report}\n```\n\n"
        )

        detailed_results.append({
            "Bandit": bandit_output + bandit_error,
            "Pylint": pylint_output + pylint_error,
            "Flake8": flake8_output + flake8_error,
            "Mypy": mypy_output + mypy_error,
            "Black": black_output + black_error,
            "Safety": safety_output + safety_error,
            "VirusTotal": vt_report
        })

        return combined_output, detailed_results

    finally:
        os.remove(temp_file_path)

def display_python_code_analysis():
    """
    Display the Python Code Analysis interface and handle file upload, analysis, and results display.
    """
    st.subheader("Python Code Analysis")

    file_to_analyze = st.file_uploader("Upload your Python file here and click on 'Analyze'", type='py')
    if st.button("Analyze") and file_to_analyze:
        with st.spinner('Analyzing the Python file...'):
            try:
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
            except Exception as e:
                st.error(f"Error analyzing the Python file: {e}")
                logger.error(f"Error analyzing the Python file: {e}")

    st.write("## Previous Analyses")
    analyses = load_analyses()
    if analyses:
        for analysis_id, filename, result, timestamp in analyses:
            with st.expander(f"Analysis for {filename} (Uploaded on {timestamp})"):
                st.markdown(result, unsafe_allow_html=True)
                if st.button(f"Load Analysis {analysis_id}", key=f"load_{analysis_id}"):
                    loaded_result = load_analysis_by_id(analysis_id)
                    if loaded_result:
                        st.write("## Loaded Analysis Result")
                        st.markdown(loaded_result, unsafe_allow_html=True)
    else:
        st.write("No previous analyses found.")
    
    st.subheader("Export Analysis Results")
    export_format = st.selectbox("Select export format", ["CSV", "JSON", "PDF"])
    if st.button("Export Analysis Results"):
        if export_format == "CSV":
            csv_data = export_analysis_results_to_csv(detailed_results)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name="python_code_analysis.csv",
                mime="text/csv",
            )
        elif export_format == "JSON":
            json_data = export_analysis_results_to_json(detailed_results)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name="python_code_analysis.json",
                mime="application/json",
            )
        elif export_format == "PDF":
            pdf_data = export_analysis_results_to_pdf(detailed_results)
            st.download_button(
                label="Download PDF",
                data=pdf_data,
                file_name="python_code_analysis.pdf",
                mime="application/pdf",
            )
