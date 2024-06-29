import subprocess
import logging
import streamlit as st

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_command(command, tool_name):
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        return result.stdout, result.stderr
    except FileNotFoundError:
        message = f"{tool_name.capitalize()} is not installed. Please install it using 'pip install {tool_name}'."
        logger.error(message)
        st.write(message)
    except Exception as e:
        logger.error(f"Error running {tool_name}: {e}")
        st.error(f"Error running {tool_name}. Please try again.")
    return "", ""

def run_analysis_tool(tool_name, file_path):
    command = [tool_name, file_path] if tool_name in ['pylint', 'flake8'] else [tool_name, '-r', file_path]
    return run_command(command, tool_name)

def check_safety():
    return run_command(["safety", "check"], "safety")

def check_mypy(file_path):
    return run_command(["mypy", file_path], "mypy")

def check_black(file_path):
    return run_command(["black", "--check", file_path], "black")

# Example usage in Streamlit
if __name__ == "__main__":
    st.title("Code Analysis Tools")

    uploaded_file = st.file_uploader("Choose a file", type=["py"])
    if uploaded_file is not None:
        file_path = uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.write("## Pylint Analysis")
        stdout, stderr = run_analysis_tool("pylint", file_path)
        st.text(stdout)
        if stderr:
            st.error(stderr)

        st.write("## Mypy Analysis")
        stdout, stderr = check_mypy(file_path)
        st.text(stdout)
        if stderr:
            st.error(stderr)

        st.write("## Black Check")
        stdout, stderr = check_black(file_path)
        st.text(stdout)
        if stderr:
            st.error(stderr)

        st.write("## Safety Check")
        stdout, stderr = check_safety()
        st.text(stdout)
        if stderr:
            st.error(stderr)
