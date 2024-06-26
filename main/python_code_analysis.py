import streamlit as st
import tempfile
import os
import pandas as pd
import logging
from analysis_tools import run_analysis_tool
from ai_interaction import get_ai_suggestions
from utils import generate_summary_statistics, plot_indicator_distribution
from database_code import save_analysis, load_analyses, load_analysis_by_id

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def format_output(output, error):
    """Format the output and error messages for better readability."""
    return output.replace('\n', '<br>'), error.replace('\n', '<br>')

def analyze_file(file_path, file_type):
    """Analyze a single file based on its type and return results and detailed information."""
    results = []

    if file_type == "python":
        tools = ["bandit", "pylint", "flake8", "mypy", "black", "safety"]
    elif file_type == "c":
        tools = ["cppcheck", "clang-analyzer", "clang-format"]
    elif file_type == "javascript":
        tools = ["eslint"]
    else:
        st.error("Unsupported file type.")
        return results

    for tool in tools:
        output, error = run_analysis_tool(tool, file_path)
        formatted_output, formatted_error = format_output(output, error)
        results.append({
            "Tool": tool.replace('-', ' ').capitalize(),
            "Output": formatted_output,
            "Error": formatted_error
        })

        if tool == "clang-format":
            with open(file_path, 'r') as f:
                formatted_content = f.read()
            results.append({
                "Tool": "Formatted File",
                "Output": formatted_content.replace('\n', '<br>'),
                "Error": ""
            })

    return results

def analyze_files(files):
    """Analyze multiple files and return results and detailed information."""
    all_details = []
    for uploaded_file in files:
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        if file_extension == ".py":
            file_type = "python"
        elif file_extension in [".c", ".h"]:
            file_type = "c"
        elif file_extension in [".js"]:
            file_type = "javascript"
        else:
            st.error(f"Unsupported file type: {file_extension}")
            continue

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name

        try:
            details = analyze_file(temp_file_path, file_type)
            all_details.append((uploaded_file.name, details))
        except Exception as e:
            logger.error(f"Error analyzing file: {e}")
            st.error(f"Error analyzing {uploaded_file.name}. Please try again.")
        finally:
            os.remove(temp_file_path)

    return all_details

def display_code_analysis():
    st.subheader("Code Analysis")

    # Settings section
    st.sidebar.header("Analysis Settings")
    selected_language = st.sidebar.selectbox("Select language", ["Python", "C", "JavaScript"])
    st.sidebar.write(f"Analyzing {selected_language} files.")

    # File uploader for files
    code_files = st.file_uploader("Upload your code files here", accept_multiple_files=True, type=["py", "c", "h", "js"])
    if st.button("Analyze Code Files") and code_files:
        with st.spinner('Analyzing code files...'):
            analysis_results = analyze_files(code_files)

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
                    file_name="code_analysis_results.txt",
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
                for uploaded_file, result in zip(code_files, combined_results):
                    save_analysis(uploaded_file.name, result)

    st.write("## Previous Analyses")
    display_previous_analyses()

def display_previous_analyses():
    st.subheader("Previous Analyses")
    analyses = load_analyses()

    if analyses:
        df = pd.DataFrame(analyses, columns=["ID", "Filename", "Result", "Timestamp"])
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])
        df.sort_values(by="Timestamp", ascending=False, inplace=True)

        for _, row in df.iterrows():
            with st.expander(f"Analysis for {row['Filename']} (Uploaded on {row['Timestamp'].strftime('%Y-%m-%d %H:%M:%S')})"):
                st.markdown(f"**Filename:** {row['Filename']}")
                st.markdown(f"**Timestamp:** {row['Timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                st.markdown("**Result:**")
                st.code(row['Result'])

                if st.button(f"Load Analysis {row['ID']}", key=f"load_{row['ID']}"):
                    loaded_result = load_analysis_by_id(row['ID'])
                    if loaded_result:
                        st.markdown("## Loaded Analysis Result")
                        st.text(loaded_result)
    else:
        st.write("No previous analyses found.")

if __name__ == "__main__":
    display_code_analysis()
