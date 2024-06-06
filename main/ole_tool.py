import streamlit as st
import tempfile
import os
import oletools.oleid
import logging
from ai_interaction import get_ai_suggestions
from utils import display_analysis_results, generate_summary_statistics, plot_indicator_distribution

logger = logging.getLogger()
logging.basicConfig(level=logging.ERROR)

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
                file_results += (
                    f'Indicator id={indicator.id} name="{indicator.name}" '
                    f'type={indicator.type} value={repr(indicator.value)}\n'
                    f'Description: {indicator.description}\n\n'
                )
                details.append({
                    "id": indicator.id,
                    "name": indicator.name,
                    "type": indicator.type,
                    "value": repr(indicator.value),
                    "description": indicator.description,
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

            st.write("## AI Suggestions")
            ai_suggestions = get_ai_suggestions(combined_results, context="oletools")
            st.write(ai_suggestions)

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


def display_analysis_results(file_results, details):
    st.markdown("### File Analysis")
    st.text(file_results)

    st.markdown("### Detailed Indicators")
    for detail in details:
        with st.expander(f"Indicator: {detail['name']}"):
            st.write(f"**ID:** {detail['id']}")
            st.write(f"**Type:** {detail['type']}")
            st.write(f"**Value:** {detail['value']}")
            st.write(f"**Description:** {detail['description']}")
