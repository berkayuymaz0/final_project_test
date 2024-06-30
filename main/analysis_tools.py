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
    try:
        if tool_name == 'cppcheck':
            result = subprocess.run(
                [tool_name, '--enable=all', '--output-file=cppcheck_output.txt', file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            with open('cppcheck_output.txt', 'r') as f:
                output = f.read()
            error = result.stderr

        elif tool_name == 'clang-analyzer':
            result = subprocess.run(
                ['clang', '--analyze', file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            output, error = result.stdout, result.stderr

        elif tool_name == 'clang-format':
            result = subprocess.run(
                ['clang-format', '-i', file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            output, error = "File formatted successfully.", result.stderr

        else:
            result = subprocess.run(
                [tool_name, file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            output, error = result.stdout, result.stderr

        return output, error

    except FileNotFoundError:
        st.write(f"{tool_name.capitalize()} is not installed. Please install it using the appropriate package manager.")
    except Exception as e:
        logger.error(f"Error running {tool_name}: {e}")
        st.error(f"Error running {tool_name}. Please try again.")
    return "", ""

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
