import streamlit as st
import pandas as pd
import io
import logging
import html
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def display_chat_history():
    chat_history_html = ""
    for i, chat in enumerate(st.session_state.chat_history):
        user_question = html.escape(chat['question'])
        bot_answer = html.escape(chat['answer'])
        chat_history_html += f"""
        <div class="chat-box">
            <div class="user-message">
                <strong>Q{i+1}:</strong> {user_question}<br>
                <small class="timestamp"><i>{chat['timestamp']}</i></small>
            </div>
            <div class="bot-message">
                <strong>A{i+1}:</strong> {bot_answer}<br>
                <small class="timestamp"><i>{chat['timestamp']}</i></small>
            </div>
        </div>
        """
    st.markdown(chat_history_html, unsafe_allow_html=True)

def get_relevant_context(chat_history):
    chat_history_text = "\n".join(f"Q: {chat['question']}\nA: {chat['answer']}" for chat in chat_history)
    return chat_history_text

def display_analysis_results(combined_output, details):
    st.markdown("### Combined Analysis Results")
    st.markdown(combined_output, unsafe_allow_html=True)

    st.markdown("### Detailed Results by Tool")
    for tool, result in details[0].items():
        with st.expander(f"Tool: {tool}"):
            st.markdown(f"```\n{result}\n```")

def generate_summary_statistics(detailed_results):
    summary_data = []
    for file_details in detailed_results:
        for tool, result in file_details.items():
            summary_data.append({
                "Tool": tool,
                "Result": result
            })
    df = pd.DataFrame(summary_data)
    summary_stats = df.groupby(['Tool']).size().reset_index(name='Count')
    return summary_stats

def plot_indicator_distribution(detailed_results):
    summary_data = []
    for file_details in detailed_results:
        for tool, result in file_details.items():
            summary_data.append({
                "Tool": tool,
                "Result": result
            })
    df = pd.DataFrame(summary_data)
    
    # Plot distribution of tool usage
    tool_counts = df['Tool'].value_counts()
    st.write("### Tool Usage Distribution")
    st.bar_chart(tool_counts)

def export_analysis_results_to_csv(detailed_results, file_name="analysis_results.csv"):
    summary_data = []
    for file_details in detailed_results:
        for tool, result in file_details.items():
            summary_data.append({
                "Tool": tool,
                "Result": result
            })
    df = pd.DataFrame(summary_data)
    csv = df.to_csv(index=False)
    return csv

def export_analysis_results_to_json(detailed_results, file_name="analysis_results.json"):
    summary_data = []
    for file_details in detailed_results:
        for tool, result in file_details.items():
            summary_data.append({
                "Tool": tool,
                "Result": result
            })
    df = pd.DataFrame(summary_data)
    json_data = df.to_json(orient="records")
    return json_data

def export_analysis_results_to_pdf(detailed_results, file_name="analysis_results.pdf"):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2.0, height - 50, "Analysis Results")

    y = height - 100
    c.setFont("Helvetica", 10)
    for file_details in detailed_results:
        for tool, result in file_details.items():
            c.drawString(50, y, f"Tool: {tool}")
            y -= 15
            for line in result.split('\n'):
                c.drawString(50, y, line)
                y -= 15
                if y < 50:
                    c.showPage()
                    c.setFont("Helvetica", 10)
                    y = height - 50

    c.save()
    buffer.seek(0)
    return buffer
