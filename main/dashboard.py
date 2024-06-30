import streamlit as st
import pandas as pd
import plotly.express as px
import logging
from database_code import load_analyses

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def display_dashboard():
    st.title("Security Analysis Dashboard")

    try:
        # Load data from the database
        analyses = load_analyses()
        df = pd.DataFrame(analyses, columns=["ID", "Filename", "Result", "Timestamp"])
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])
        df['Date'] = df['Timestamp'].dt.date

        # Extract severity counts (example, modify based on actual result format)
        df['High Severity'] = df['Result'].str.count('High')
        df['Medium Severity'] = df['Result'].str.count('Medium')
        df['Low Severity'] = df['Result'].str.count('Low')

        # Summary Metrics
        st.markdown("### Summary Metrics")
        total_analyses = df.shape[0]
        total_high_severity = df['High Severity'].sum()
        total_medium_severity = df['Medium Severity'].sum()
        total_low_severity = df['Low Severity'].sum()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Analyses", total_analyses)
        col2.metric("High Severity", total_high_severity)
        col3.metric("Medium Severity", total_medium_severity)
        col4.metric("Low Severity", total_low_severity)

        # Analyses Over Time
        st.markdown("### Analyses Over Time")
        analyses_over_time = df.groupby('Date').size().reset_index(name='Counts')
        fig_line = px.line(analyses_over_time, x='Date', y='Counts', title='Analyses Over Time', markers=True)
        st.plotly_chart(fig_line, use_container_width=True)

        # Severity Distribution
        st.markdown("### Severity Distribution")
        severity_counts = pd.DataFrame({
            'Severity': ['High', 'Medium', 'Low'],
            'Count': [total_high_severity, total_medium_severity, total_low_severity]
        })
        fig_pie = px.pie(severity_counts, values='Count', names='Severity', title='Severity Distribution')
        st.plotly_chart(fig_pie, use_container_width=True)

        # Vulnerabilities by File Type (example)
        st.markdown("### Vulnerabilities by File Type")
        df['File Type'] = df['Filename'].apply(lambda x: x.split('.')[-1])
        file_type_vulnerabilities = df.groupby('File Type')[['High Severity', 'Medium Severity', 'Low Severity']].sum().reset_index()
        fig_bar = px.bar(file_type_vulnerabilities, x='File Type', y=['High Severity', 'Medium Severity', 'Low Severity'], 
                         title='Vulnerabilities by File Type', barmode='group')
        st.plotly_chart(fig_bar, use_container_width=True)

        # Detailed Analysis Table
        st.markdown("### Detailed Analyses")
        st.dataframe(df[['Filename', 'High Severity', 'Medium Severity', 'Low Severity', 'Timestamp']].sort_values(by="Timestamp", ascending=False))

        # Downloadable CSV
        st.markdown("### Download Data")
        csv_data = df.to_csv(index=False)
        st.download_button(label="Download CSV", data=csv_data, file_name='analysis_data.csv', mime='text/csv')

    except Exception as e:
        st.error(f"Error displaying dashboard: {e}")
        logger.error("Error displaying dashboard", exc_info=True)

if __name__ == "__main__":
    display_dashboard()
