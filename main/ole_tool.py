import streamlit as st
import tempfile
import os
import oletools.oleid
import logging
from ai_interaction import get_ai_suggestions

logger = logging.getLogger()
logging.basicConfig(level=logging.ERROR)

def analyze_ole_files(files):
    results = []
    for uploaded_file in files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name

        try:
            oid = oletools.oleid.OleID(temp_file_path)
            indicators = oid.check()

            file_results = f"Results for {uploaded_file.name}:\n"
            for indicator in indicators:
                file_results += (f'Indicator id={indicator.id} name="{indicator.name}" '
                                 f'type={indicator.type} value={repr(indicator.value)}\n'
                                 f'Description: {indicator.description}\n\n')
            results.append(file_results)
            st.write(file_results)

        except Exception as e:
            logger.error(f"Error analyzing OLE file: {e}")
            st.error("Error analyzing OLE file. Please try again.")
        finally:
            os.remove(temp_file_path)
    
    return results

def display_ole_tool():
    st.subheader("OLE Tool")
    ole_files = st.file_uploader("Upload your file here and click on 'Use OLE Tool'", accept_multiple_files=True)
    if st.button("Use OLE Tool") and ole_files:
        results = analyze_ole_files(ole_files)
        
        if results:
            combined_results = "\n".join(results)
            st.write("AI Suggestions:")
            ai_suggestions = get_ai_suggestions(combined_results, context="oletools")
            st.write(ai_suggestions)
