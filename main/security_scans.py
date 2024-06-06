import streamlit as st
from analysis_tools import check_safety

def display_security_scans():
    st.subheader("Security Scans")
    st.write("Run additional security scans on your project.")
    if st.button("Run Safety Check"):
        safety_output, safety_error = check_safety()
        st.write("Safety Check Results:")
        st.text(safety_output)
        if safety_error:
            st.error(safety_error)
