import streamlit as st

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
