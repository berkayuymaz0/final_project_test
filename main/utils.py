import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import csv
import io

def display_chat_history():
    chat_history_html = ""
    for i, chat in enumerate(st.session_state.chat_history):
        chat_history_html += f"""
        <div style="padding: 10px; border: 1px solid #ccc; border-radius: 5px; margin-bottom: 10px;">
            <strong>Q{i+1}:</strong> {chat['question']}<br>
            <strong>A{i+1}:</strong> {chat['answer']}<br>
            <small><i>{chat['timestamp']}</i></small>
        </div>
        """
    st.markdown(chat_history_html, unsafe_allow_html=True)

def get_relevant_context(chat_history):
    chat_history_text = "\n".join(f"Q: {chat['question']}\nA: {chat['answer']}" for chat in chat_history)
    return chat_history_text

def display_analysis_results(file_results, details):
    st.markdown("### File Analysis")
    st.text(file_results)

    st.markdown("### Detailed Indicators")
    for detail in details:
        with st.expander(f"Indicator: {detail['name']} (Severity: {detail['severity'].capitalize()})"):
            st.write(f"**ID:** {detail['id']}")
            st.write(f"**Type:** {detail['type']}")
            st.write(f"**Value:** {detail['value']}")
            st.write(f"**Description:** {detail['description']}")
            st.write(f"**AI Insights:** {detail['ai_insights']}")

def generate_summary_statistics(detailed_results):
    summary_data = []
    for file_details in detailed_results:
        for detail in file_details:
            summary_data.append({
                "Name": str(detail['name']),
                "Type": str(detail['type']),
                "Value": str(detail['value'])
            })
    df = pd.DataFrame(summary_data)
    summary_stats = df.groupby(['Type', 'Name']).size().reset_index(name='Count')
    return summary_stats

def plot_indicator_distribution(detailed_results):
    summary_data = []
    for file_details in detailed_results:
        for detail in file_details:
            summary_data.append({
                "Name": str(detail['name']),
                "Type": str(detail['type']),
                "Value": str(detail['value'])
            })
    df = pd.DataFrame(summary_data)
    
    # Plot distribution of indicator types
    type_counts = df['Type'].value_counts()
    st.write("### Indicator Type Distribution")
    st.bar_chart(type_counts)
    
    # Plot distribution of indicator names
    name_counts = df['Name'].value_counts()
    st.write("### Indicator Name Distribution")
    st.bar_chart(name_counts)

def export_analysis_results(detailed_results, format="txt"):
    if format == "txt":
        output = io.StringIO()
        for file_details in detailed_results:
            for detail in file_details:
                output.write(f"ID: {detail['id']}\n")
                output.write(f"Name: {detail['name']}\n")
                output.write(f"Type: {detail['type']}\n")
                output.write(f"Value: {detail['value']}\n")
                output.write(f"Description: {detail['description']}\n")
                output.write(f"Severity: {detail['severity']}\n")
                output.write(f"AI Insights: {detail['ai_insights']}\n\n")
        return output.getvalue()

    return ""
