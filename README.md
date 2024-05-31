# AppSec Test Application


## Overview

This application is designed to provide various functionalities related to security testing, including PDF text extraction, OLE (Object Linking and Embedding) file analysis, and Python code analysis. It utilizes several libraries and tools to achieve these functionalities.


## Features

- **PDF Question Answering**: Upload a PDF file, extract its content, and interactively ask questions about the content. The app uses AI to provide accurate and relevant answers.
- **OLE Tool**: Analyze OLE files and display detailed indicators and descriptions.
- **Python Code Analysis**: Upload Python files and run multiple analysis tools (`bandit`, `pylint`, `flake8`) to get a combined report along with AI-driven improvement suggestions.
- **Chat History**: Keep track of the questions and answers for the uploaded PDF file, with the ability to ask follow-up questions.
- **User-Friendly Interface**: A clean and intuitive interface with a sidebar for easy navigation between different tools.

## Installation

### Prerequisites

- Python 3.6 or higher
- `pip` (Python package installer)
- OpenAI API Key (sign up at [OpenAI](https://beta.openai.com/signup/) to get your API key)

### Steps
    ```

1. Create a virtual environment:
    ```sh
    python -m venv venv
    ```

2. Activate the virtual environment:

    - On Windows:
      ```sh
      venv\Scripts\activate
      ```
    - On macOS and Linux:
      ```sh
      source venv/bin/activate
      ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the project directory and add your OpenAI API key:
    ```env
    OPENAI_API_KEY=your_openai_api_key
    ```

5. Run the application:
    ```sh
    streamlit run app.py
    ```

## Usage

### PDF Question Answering

1. Navigate to the "PDF Question Answering" section.
2. Upload a PDF file.
3. Once the text extraction is complete, type your question in the input box.
4. Click the "Ask" button to get an AI-generated answer.
5. You can ask follow-up questions based on the chat history.

### OLE Tool

1. Navigate to the "OLE Tool" section.
2. Upload one or more OLE files.
3. Click the "Use OLE Tool" button to analyze the files.
4. Review the indicators and descriptions displayed.

### Python Code Analysis

1. Navigate to the "Python Code Analysis" section.
2. Upload a Python (.py) file.
3. Click the "Analyze" button to run the code analysis tools.
4. Review the combined analysis results and AI suggestions for improvements.

## Code Structure

- `app.py`: Main application script containing the Streamlit UI and logic.
- `pdf_handler.py`: Module for handling PDF text extraction and embedding generation.
- `ai_interaction.py`: Module for interacting with the OpenAI API and generating AI suggestions.
- `analysis_tools.py`: Module for running code analysis tools and analyzing OLE files.
- `requirements.txt`: List of required Python packages.
- `.env`: Environment file to store the OpenAI API key.

## Dependencies

- `streamlit`: Framework for building web applications.
- `PyPDF2`: Library for extracting text from PDF files.
- `openai`: OpenAI API client.
- `scikit-learn`: Machine learning library (used for cosine similarity).
- `python-dotenv`: For loading environment variables from `.env` file.
- `oletools`: Tools for analyzing OLE files.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- OpenAI for providing the powerful language model.
- Streamlit for the easy-to-use web application framework.
- The maintainers of `PyPDF2`, `oletools`, and other dependencies for their valuable tools.

---
