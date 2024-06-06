import streamlit as st
from config_manager import save_config, load_config

def display_settings():
    st.subheader("Settings")
    config = load_config()
    
    st.write("Configure Analysis Tools")
    pylint_threshold = st.number_input("Pylint Threshold", value=config.get("pylint_threshold", 7.0))
    flake8_threshold = st.number_input("Flake8 Threshold", value=config.get("flake8_threshold", 7.0))
    
    if st.button("Save Settings"):
        config['pylint_threshold'] = pylint_threshold
        config['flake8_threshold'] = flake8_threshold
        save_config(config)
        st.success("Settings saved")
