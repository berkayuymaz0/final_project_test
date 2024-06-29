import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def display_dashboard():
    st.subheader("Dashboard")
    st.write("Key Metrics and Trends")

    try:
        # Sample data
        analysis_results = [
            {'date': '2023-05-01', 'vulnerabilities': 10, 'severity': 'High', 'tool': 'Bandit'},
            {'date': '2023-05-02', 'vulnerabilities': 8, 'severity': 'Medium', 'tool': 'Pylint'},
            {'date': '2023-05-03', 'vulnerabilities': 6, 'severity': 'Low', 'tool': 'Flake8'},
            {'date': '2023-05-04', 'vulnerabilities': 5, 'severity': 'High', 'tool': 'Mypy'}
        ]

        df = pd.DataFrame(analysis_results)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

        # Plot: Vulnerabilities over Time
        st.write("### Vulnerabilities over Time")
        plt.figure(figsize=(10, 5))
        plt.plot(df.index, df['vulnerabilities'], marker='o', color='b', linestyle='-')
        plt.xlabel('Date')
        plt.ylabel('Number of Vulnerabilities')
        plt.title('Vulnerabilities Over Time')
        plt.grid(True)
        st.pyplot(plt)
        plt.close()

        # Plot: Severity Levels
        st.write("### Severity Levels")
        severity_counts = df['severity'].value_counts()
        plt.figure(figsize=(10, 5))
        severity_counts.plot(kind='bar', color='skyblue')
        plt.xlabel('Severity Level')
        plt.ylabel('Count')
        plt.title('Severity Levels of Vulnerabilities')
        st.pyplot(plt)
        plt.close()

        # Plot: Tool Usage
        st.write("### Tool Usage")
        tool_usage = df['tool'].value_counts()
        plt.figure(figsize=(10, 5))
        tool_usage.plot(kind='pie', autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
        plt.title('Tool Usage Distribution')
        plt.axis('equal')
        st.pyplot(plt)
        plt.close()

    except Exception as e:
        st.error(f"Error displaying dashboard: {e}")
        logger.error("Error displaying dashboard", exc_info=True)

# Example usage
if __name__ == "__main__":
    display_dashboard()
