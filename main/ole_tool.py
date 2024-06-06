import streamlit as st
import tempfile
import os
import oletools.oleid
import logging

logger = logging.getLogger()
logging.basicConfig(level=logging.ERROR)

def analyze_ole_files(files):
    for uploaded_file in files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name

        try:
            oid = oletools.oleid.OleID(temp_file_path)
            indicators = oid.check()

            st.write(f"Results for {uploaded_file.name}:")
            for indicator in indicators:
                st.write(f'Indicator id={indicator.id} name="{indicator.name}" type={indicator.type} value={repr(indicator.value)}')
                st.write('Description:', indicator.description)
                st.write('')
        except Exception as e:
            logger.error(f"Error analyzing OLE file: {e}")
            st.error("Error analyzing OLE file. Please try again.")
        finally:
            os.remove(temp_file_path)

def display_ole_tool():
    st.subheader("OLE Tool")
    ole_files = st.file_uploader("Upload your file here and click on 'Use OLE Tool'", accept_multiple_files=True)
    if st.button("Use OLE Tool") and ole_files:
        analyze_ole_files(ole_files)
