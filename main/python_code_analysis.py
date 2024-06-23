import streamlit as st
import tempfile
import os
import pandas as pd
import logging
from analysis_tools import run_analysis_tool, check_mypy, check_black, check_safety
from ai_interaction import get_ai_suggestions, scan_file_with_virustotal, get_file_report
from utils import generate_summary_statistics, plot_indicator_distribution
from database_code import save_analysis, load_analyses, load_analysis_by_id

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def format_output(output, error):
    """Format the output and error messages for better readability."""
    return output.replace('\n', '<br>'), error.replace('\n', '<br>')

def analyze_python_file(file_path):
    """Analyze a single Python file and return results and detailed information."""
    results = []
    tools = ["bandit", "pylint", "flake8", "mypy", "black", "safety"]
    
    for tool in tools:
        if tool == "mypy":
            output, error = check_mypy(file_path)
        elif tool == "black":
            output, error = check_black(file_path)
        elif tool == "safety":
            output, error = check_safety()
        else:
            output, error = run_analysis_tool(tool, file_path)

        formatted_output, formatted_error = format_output(output, error)
        results.append({
            "Tool": tool.capitalize(),
            "Output": formatted_output,
            "Error": formatted_error
        })
    
    return results

def analyze_python_files(files):
    """Analyze multiple Python files and return results and detailed information."""
    all_details = []
    for uploaded_file in files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name

        try:
            details = analyze_python_file(temp_file_path)
            all_details.append((uploaded_file.name, details))
        except Exception as e:
            logger.error(f"Error analyzing Python file: {e}")
            st.error(f"Error analyzing {uploaded_file.name}. Please try again.")
        finally:
            os.remove(temp_file_path)

    return all_details

def display_python_code_analysis():
    st.subheader("Python Code Analysis")

    # File uploader for Python files
    python_files = st.file_uploader("Upload your Python files here", accept_multiple_files=True, type=["py"])
    if st.button("Analyze Python Files") and python_files:
        with st.spinner('Analyzing Python files...'):
            analysis_results = analyze_python_files(python_files)

            if analysis_results:
                combined_results = []
                all_ai_suggestions = []
                for file_name, details in analysis_results:
                    combined_context = "\n\n".join([f"{d['Tool']}: {d['Output']} {d['Error']}" for d in details])
                    ai_suggestions = get_ai_suggestions(combined_context, context="code analysis")

                    # Display results for each file
                    st.write(f"## Analysis Results for {file_name}")
                    df = pd.DataFrame(details)
                    st.write(df.to_html(escape=False), unsafe_allow_html=True)

                    combined_results.append(df.to_string())
                    all_ai_suggestions.append(f"AI Suggestions for {file_name}:\n{ai_suggestions}")

                st.download_button(
                    label="Download Analysis Results",
                    data="\n\n".join(combined_results),
                    file_name="python_code_analysis_results.txt",
                    mime="text/plain"
                )

                all_details = [d for _, details in analysis_results for d in details]
                summary_stats = generate_summary_statistics(all_details)
                st.write("## Summary Statistics")
                st.table(summary_stats)

                plot_indicator_distribution(all_details)

                # Display AI suggestions
                st.write("## AI Suggestions")
                st.write("\n\n".join(all_ai_suggestions))

                # Save results to database
                for uploaded_file, result in zip(python_files, combined_results):
                    save_analysis(uploaded_file.name, result)

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
                        st.text(loaded_result)
    else:
        st.write("No previous analyses found.")

if __name__ == "__main__":
    display_python_code_analysis()
