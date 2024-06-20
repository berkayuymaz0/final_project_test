import streamlit as st
from analysis_tools import check_safety
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def display_security_scans():
    """
    Display the security scans interface and run safety checks on the project.
    """
    st.subheader("Security Scans")
    st.write("Run additional security scans on your project.")

    if st.button("Run Safety Check"):
        try:
            safety_output, safety_error = check_safety()
            st.write("Safety Check Results:")
            st.text(safety_output)
            if safety_error:
                st.error(f"Safety Check Errors:\n{safety_error}")
        except Exception as e:
            st.error(f"Error running safety check: {e}")
            logger.error(f"Error running safety check: {e}", exc_info=True)

# Example usage in Streamlit
if __name__ == "__main__":
    display_security_scans()
