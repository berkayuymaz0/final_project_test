# AppSec Test Application

This application is designed to provide various functionalities related to security testing, including PDF text extraction, OLE (Object Linking and Embedding) file analysis, and Python code analysis. It utilizes several libraries and tools to achieve these functionalities.

## Features

- **PDF with AI**: Upload PDF files to extract text and perform summarization and sentiment analysis.
- **OLE Tool**: Analyze OLE files for potential security risks.
- **Python Code Analyzer**: Upload Python files to perform static code analysis using Bandit, pylint, and flake8.

## Installation

To run this application locally, follow these steps:


1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Run the Streamlit application:

```bash
streamlit run app.py
```

## Usage

After running the application, you will be prompted to authenticate with your username and password. Once authenticated, you can access the following functionalities:

### PDF with AI

- Upload PDF files using the provided interface.
- Click on the "Process" button to extract text, summarize content, and perform sentiment analysis.

### OLE Tool

- Upload OLE files using the provided interface.
- Click on the "Use" button to analyze the files for potential security risks.

### Python Code Analyzer

- Upload Python files using the provided interface.
- Click on the "Analyze" button to perform static code analysis using Bandit, pylint, and flake8.

## Authentication

This application requires authentication for access. Please enter your username and password to proceed.

## Dependencies

- streamlit
- dotenv
- PyPDF2
- langchain
- htmlTemplates
- subprocess
- oletools
- tempfile
- HuggingFaceHub
- matplotlib
- streamlit_authenticator

## Configuration

Configuration settings such as chunk size, chunk overlap, and API key are specified in the `CONFIG` dictionary within the code. Additionally, authentication settings can be configured in the `login_config/config.yaml` file.

## Notes

- Ensure that you have the necessary permissions and access rights to analyze sensitive files and data.
- Use caution when analyzing potentially malicious files, and always verify the source of the files before processing.



## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.