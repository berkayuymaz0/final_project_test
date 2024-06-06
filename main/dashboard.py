import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def display_dashboard():
    st.subheader("Dashboard")
    st.write("Key Metrics and Trends")

    analysis_results = [
        {'date': '2023-05-01', 'vulnerabilities': 10, 'severity': 'High', 'tool': 'Bandit'},
        {'date': '2023-05-02', 'vulnerabilities': 8, 'severity': 'Medium', 'tool': 'Pylint'},
        {'date': '2023-05-03', 'vulnerabilities': 6, 'severity': 'Low', 'tool': 'Flake8'},
        {'date': '2023-05-04', 'vulnerabilities': 5, 'severity': 'High', 'tool': 'Mypy'}
    ]

    df = pd.DataFrame(analysis_results)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    st.write("Vulnerabilities over Time")
    plt.figure(figsize=(10, 5))
    plt.plot(df.index, df['vulnerabilities'], marker='o', color='b', linestyle='-')
    plt.xlabel('Date')
    plt.ylabel('Number of Vulnerabilities')
    plt.title('Vulnerabilities Over Time')
    plt.grid(True)
    st.pyplot(plt)

    st.write("Severity Levels")
    severity_counts = df['severity'].value_counts()
    plt.figure(figsize=(10, 5))
    severity_counts.plot(kind='bar', color='skyblue')
    plt.xlabel('Severity Level')
    plt.ylabel('Count')
    plt.title('Severity Levels of Vulnerabilities')
    st.pyplot(plt)

    st.write("Tool Usage")
    tool_usage = df['tool'].value_counts()
    plt.figure(figsize=(10, 5))
    tool_usage.plot(kind='pie', autopct='%1.1f%%', startangle=90)
    plt.title('Tool Usage Distribution')
    plt.axis('equal')
    st.pyplot(plt)
