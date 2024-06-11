import streamlit as st
import pandas as pd
import io
import logging
import html

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

def export_analysis_results(detailed_results, format="txt"):
    if format == "txt":
        output = io.StringIO()
        for file_details in detailed_results:
            for tool, result in file_details.items():
                output.write(f"Tool: {tool}\nResult:\n{result}\n\n")
        return output.getvalue()

    return ""
