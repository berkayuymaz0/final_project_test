import streamlit as st
import subprocess
import tempfile
import os
import oletools.oleid
import logging

logger = logging.getLogger()
logging.basicConfig(level=logging.ERROR)

def run_analysis_tool(tool_name, file_path):
    try:
        result = subprocess.run(
            [tool_name, file_path] if tool_name in ['pylint', 'flake8'] else [tool_name, '-r', file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        return result.stdout, result.stderr
    except FileNotFoundError:
        st.write(f"{tool_name.capitalize()} is not installed. Please install it using 'pip install {tool_name}'.")
    except Exception as e:
        logger.error(f"Error running {tool_name}: {e}")
        st.error(f"Error running {tool_name}. Please try again.")
    return "", ""

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

def check_safety():
    try:
        result = subprocess.run(
            ["safety", "check"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        return result.stdout, result.stderr
    except FileNotFoundError:
        st.write("Safety is not installed. Please install it using 'pip install safety'.")
    except Exception as e:
        logger.error(f"Error running safety: {e}")
        st.error("Error running safety. Please try again.")
    return "", ""

def check_mypy(file_path):
    try:
        result = subprocess.run(
            ["mypy", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        return result.stdout, result.stderr
    except FileNotFoundError:
        st.write("Mypy is not installed. Please install it using 'pip install mypy'.")
    except Exception as e:
        logger.error(f"Error running mypy: {e}")
        st.error("Error running mypy. Please try again.")
    return "", ""

def check_black(file_path):
    try:
        result = subprocess.run(
            ["black", "--check", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        return result.stdout, result.stderr
    except FileNotFoundError:
        st.write("Black is not installed. Please install it using 'pip install black'.")
    except Exception as e:
        logger.error(f"Error running black: {e}")
        st.error("Error running black. Please try again.")
    return "", ""
