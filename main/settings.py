import streamlit as st
from config_manager import save_config, load_config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def display_settings():
    st.subheader("Settings")
    try:
        config = load_config()
    
        st.write("Configure Analysis Tools")
        pylint_threshold = st.number_input("Pylint Threshold", value=config.get("pylint_threshold", 7.0))
        flake8_threshold = st.number_input("Flake8 Threshold", value=config.get("flake8_threshold", 7.0))
    
        if st.button("Save Settings"):
            config['pylint_threshold'] = pylint_threshold
            config['flake8_threshold'] = flake8_threshold
            save_config(config)
            st.success("Settings saved")
    except Exception as e:
        st.error(f"Error loading settings: {e}")
        logger.error(f"Error loading settings: {e}")
