import streamlit as st
import tempfile
import os
import oletools.oleid
import logging
import pandas as pd
from ai_interaction import get_ai_suggestions
from utils import generate_summary_statistics, plot_indicator_distribution
from database_ole import save_analysis, load_analyses, load_analysis_by_id

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define severity levels for OLE indicators
SEVERITY_LEVELS = {
    "high": ["OleObject", "Macros"],
    "medium": ["SuspiciousKeywords", "Metadata"],
    "low": ["FileProperties", "Other"]
}

def categorize_severity(indicator_name):
    """Categorize the severity of an OLE indicator."""
    for severity, indicators in SEVERITY_LEVELS.items():
        if indicator_name in indicators:
            return severity
    return "low"

def analyze_ole_file(file_path):
    """Analyze a single OLE file and return results and detailed information."""
    oid = oletools.oleid.OleID(file_path)
    indicators = oid.check()
    details = []

    for indicator in indicators:
        severity = categorize_severity(indicator.name)
        context = (
            f"Indicator id={indicator.id} name={indicator.name} type={indicator.type} "
            f"value={repr(indicator.value)} severity={severity}\nDescription: {indicator.description}"
        )
        details.append({
            "id": indicator.id,
            "name": indicator.name,
            "type": indicator.type,
            "value": repr(indicator.value),
            "description": indicator.description,
            "severity": severity,
            "context": context
        })

    return details

def analyze_ole_files(files):
    """Analyze multiple OLE files and return results and detailed information."""
    all_details = []
    for uploaded_file in files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".doc") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name

        try:
            details = analyze_ole_file(temp_file_path)
            all_details.append((uploaded_file.name, details))
        except Exception as e:
            logger.error(f"Error analyzing OLE file: {e}")
            st.error(f"Error analyzing {uploaded_file.name}. Please try again.")
        finally:
            os.remove(temp_file_path)

    return all_details

def display_ole_tool():
    st.subheader("OLE Tool")

    # File uploader for OLE files
    ole_files = st.file_uploader("Upload your OLE files here", accept_multiple_files=True, type=["docx", "xls", "ppt"])
    if st.button("Analyze OLE Files") and ole_files:
        with st.spinner('Analyzing OLE files...'):
            analysis_results = analyze_ole_files(ole_files)

            if analysis_results:
                combined_results = []
                for file_name, details in analysis_results:
                    combined_context = "\n\n".join([d["context"] for d in details])
                    ai_suggestions = get_ai_suggestions(combined_context, context="oletools")

                    # Display results for each file
                    st.write(f"## Analysis Results for {file_name}")
                    df = pd.DataFrame(details)
                    df["AI Insights"] = ai_suggestions
                    st.dataframe(df)

                    combined_results.append(df.to_string())

                st.download_button(
                    label="Download Analysis Results",
                    data="\n\n".join(combined_results),
                    file_name="ole_analysis_results.txt",
                    mime="text/plain"
                )

                all_details = [d for _, details in analysis_results for d in details]
                summary_stats = generate_summary_statistics(all_details)
                st.write("## Summary Statistics")
                st.table(summary_stats)

                plot_indicator_distribution(all_details)

                # Save results to database
                for uploaded_file, result in zip(ole_files, combined_results):
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
    display_ole_tool()
