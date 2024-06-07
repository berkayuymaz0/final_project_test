import streamlit as st
import tempfile
import os
import oletools.oleid
import logging
from ai_interaction import get_ai_suggestions
from utils import display_analysis_results, generate_summary_statistics, plot_indicator_distribution, export_analysis_results
from database_ole import save_analysis, load_analyses, load_analysis_by_id

logger = logging.getLogger()
logging.basicConfig(level=logging.ERROR)

SEVERITY_LEVELS = {
    "high": ["OleObject", "Macros"],
    "medium": ["SuspiciousKeywords", "Metadata"],
    "low": ["FileProperties", "Other"]
}

def categorize_severity(indicator_name):
    for severity, indicators in SEVERITY_LEVELS.items():
        if indicator_name in indicators:
            return severity
    return "low"

def analyze_ole_files(files):
    results = []
    detailed_results = []
    for uploaded_file in files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name

        try:
            oid = oletools.oleid.OleID(temp_file_path)
            indicators = oid.check()

            file_results = f"Results for {uploaded_file.name}:\n"
            details = []

            for indicator in indicators:
                severity = categorize_severity(indicator.name)
                context = f"Indicator id={indicator.id} name={indicator.name} type={indicator.type} value={repr(indicator.value)} severity={severity}\nDescription: {indicator.description}"
                ai_insights = get_ai_suggestions(context, context="oletools")

                file_results += (
                    f'Indicator id={indicator.id} name="{indicator.name}" '
                    f'type={indicator.type} value={repr(indicator.value)} severity={severity}\n'
                    f'Description: {indicator.description}\n'
                    f'AI Insights: {ai_insights}\n\n'
                )

                details.append({
                    "id": indicator.id,
                    "name": indicator.name,
                    "type": indicator.type,
                    "value": repr(indicator.value),
                    "description": indicator.description,
                    "severity": severity,
                    "ai_insights": ai_insights
                })
            results.append(file_results)
            detailed_results.append(details)
        except Exception as e:
            logger.error(f"Error analyzing OLE file: {e}")
            st.error("Error analyzing OLE file. Please try again.")
        finally:
            os.remove(temp_file_path)
    
    return results, detailed_results

def display_ole_tool():
    st.subheader("OLE Tool")
    
    ole_files = st.file_uploader("Upload your file here and click on 'Use OLE Tool'", accept_multiple_files=True)
    if st.button("Use OLE Tool") and ole_files:
        results, detailed_results = analyze_ole_files(ole_files)
        
        if results:
            combined_results = "\n".join(results)
            st.write("## Analysis Results")
            for file_results, file_details in zip(results, detailed_results):
                display_analysis_results(file_results, file_details)

            st.download_button(
                label="Download Analysis Results",
                data=combined_results,
                file_name="ole_analysis_results.txt",
                mime="text/plain"
            )

            summary_stats = generate_summary_statistics(detailed_results)
            st.write("## Summary Statistics")
            st.table(summary_stats)

            plot_indicator_distribution(detailed_results)

            # Save to database
            for uploaded_file, result in zip(ole_files, results):
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

def display_analysis_results(file_results, details):
    st.markdown("### File Analysis")
    st.text(file_results)

    st.markdown("### Detailed Indicators")
    for detail in details:
        with st.expander(f"Indicator: {detail['name']} (Severity: {detail['severity'].capitalize()})"):
            st.write(f"**ID:** {detail['id']}")
            st.write(f"**Type:** {detail['type']}")
            st.write(f"**Value:** {detail['value']}")
            st.write(f"**Description:** {detail['description']}")
            st.write(f"**AI Insights:** {detail['ai_insights']}")

