# AppSec

## Overview

**AppSec** is a comprehensive web application security analysis tool designed to provide detailed insights into the security posture of your code and documents. This tool integrates multiple static analysis tools and AI-driven suggestions to enhance your security analysis workflow.

## Features

- **PDF Question Answering**: Upload PDF files and ask questions about their content. The tool uses AI to provide detailed answers.
- **OLE Tool Analysis**: Analyze OLE files for potential security threats and vulnerabilities. Provides detailed insights and AI-driven suggestions.
- **Python Code Analysis**: Upload Python files to be analyzed by multiple static analysis tools. The tool provides detailed results, summarized insights, and AI-driven suggestions.
- **Security Scans**: Run various security scans on your project to identify vulnerabilities.
- **Dashboard**: Visualize key metrics and trends from your security analyses.
- **Settings**: Configure analysis tool thresholds and other settings.

## Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/berkayuymaz0/final_project_test
    cd AppSec
    ```

2. **Set up a virtual environment**:
    ```sh
    python -m venv venv
    source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
    ```

3. **Install the required packages**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:
    - Create a `.env` file in the root directory of the project.
    - Add your OpenAI API key in the `.env` file:
    ```env
    OPENAI_API_KEY=your_openai_api_key
    ```

## Usage

1. **Run the Streamlit app**:
    ```sh
    streamlit run app.py
    ```

2. **Navigate through the application**:
    - **PDF Question Answering**: Upload a PDF and interact with the AI to get answers about the content.
    - **OLE Tool**: Upload OLE files and get detailed analysis and AI suggestions.
    - **Python Code Analysis**: Upload Python files to be analyzed by multiple tools, view detailed results, and get AI suggestions.
    - **Security Scans**: Run additional security scans on your project.
    - **Dashboard**: Visualize the results of your analyses.
    - **Settings**: Configure tool thresholds and settings.

## Components

### PDF Question Answering

- **Upload a PDF**: Optionally upload a PDF file.
- **Ask Questions**: Interact with the AI by asking questions about the uploaded PDF.
- **Chat History**: View and download the chat history.

### OLE Tool Analysis

- **Upload OLE Files**: Upload OLE files for analysis.
- **Detailed Analysis**: View detailed results of the analysis, categorized by severity.
- **AI Suggestions**: Get AI-driven suggestions based on the analysis results.
- **Previous Analyses**: Load and view results of previous analyses.

### Python Code Analysis

- **Upload Python Files**: Upload Python files for comprehensive analysis.
- **Multiple Tools**: Analyze using Bandit, Pylint, Flake8, Mypy, Black, and Safety.
- **Detailed Results**: View detailed results from each tool.
- **AI Suggestions**: Get AI-driven suggestions based on the analysis results.
- **Previous Analyses**: Load and view results of previous analyses.

### Security Scans

- **Run Security Scans**: Run additional security scans on your project to identify vulnerabilities.

### Dashboard

- **Visualize Metrics**: View key metrics and trends from your analyses.
- **Summary Statistics**: Get summarized insights from your analyses.

### Settings

- **Configure Tools**: Set thresholds and configure settings for analysis tools.


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

