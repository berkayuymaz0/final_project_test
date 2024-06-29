import streamlit as st
import sqlite3
import bcrypt
from pdf_qa import display_pdf_question_answering
from ole_tool import display_ole_tool
from python_code_analysis import display_code_analysis
from security_scans import display_security_scans
from dashboard import display_dashboard
from settings import display_settings

def create_usertable():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT, email TEXT, password TEXT)')
    conn.commit()
    conn.close()

def add_userdata(username, email, password):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('INSERT INTO userstable(username, email, password) VALUES (?, ?, ?)', (username, email, password))
    conn.commit()
    conn.close()

def get_user_by_email(email):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('SELECT * FROM userstable WHERE email =?', (email,))
    data = c.fetchone()
    conn.close()
    return data

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def login_user(email, password):
    user_data = get_user_by_email(email)
    if user_data:
        stored_username, stored_email, stored_password = user_data
        if verify_password(password, stored_password):
            st.session_state.logged_in = True
            st.session_state.username = stored_username
            st.session_state.email = stored_email
            st.success(f"Logged In as {stored_username}")
            return True
    return False

def logout_user():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.email = ""
    st.experimental_rerun()

def main():
    st.set_page_config(page_title="Professional Security Analysis Tool", layout="wide")
    st.title("Professional Security Analysis Tool")

    # Initialize session state variables
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'email' not in st.session_state:
        st.session_state.email = ""

    if st.session_state.logged_in:
        menu = ["Home", "Logout"]
    else:
        menu = ["Home", "Login", "SignUp"]

    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        if st.session_state.logged_in:
            st.subheader(f"Welcome {st.session_state.username}")
        else:
            st.subheader("Home")

    if not st.session_state.logged_in:
        if choice == "Login":
            st.subheader("Login Section")

            email = st.sidebar.text_input("Email", key="login_email")
            password = st.sidebar.text_input("Password", type='password', key="login_password")
            if st.sidebar.button("Login"):
                if login_user(email, password):
                    st.experimental_rerun()
                else:
                    st.warning("Incorrect Email/Password")

        elif choice == "SignUp":
            st.subheader("Create New Account")
            new_user = st.text_input("Username", key="signup_username")
            new_email = st.text_input("Email", key="signup_email")
            new_password = st.text_input("Password", type='password', key="signup_password")

            if st.button("Signup"):
                create_usertable()
                if not new_user or not new_email or not new_password:
                    st.warning("All fields are required")
                elif "@" not in new_email:
                    st.warning("Please enter a valid email address")
                elif len(new_password) < 6:
                    st.warning("Password must be at least 6 characters long")
                elif get_user_by_email(new_email):
                    st.warning("This email is already registered")
                else:
                    hashed_new_password = hash_password(new_password)
                    add_userdata(new_user, new_email, hashed_new_password)
                    st.success("You have successfully created an account")
                    st.info("Go to Login Menu to login")
                    st.experimental_rerun()

    if st.session_state.logged_in:
        if choice == "Logout":
            logout_user()

        sidebar_option = st.sidebar.selectbox(
            "Choose a section",
            ("PDF Question Answering", "OLE Tool", "Python Code Analysis", "Security Scans", "Dashboard", "Settings")
        )

        if sidebar_option == "PDF Question Answering":
            display_pdf_question_answering()
        elif sidebar_option == "OLE Tool":
            display_ole_tool()
        elif sidebar_option == "Python Code Analysis":
            display_code_analysis()
        elif sidebar_option == "Security Scans":
            display_security_scans()
        elif sidebar_option == "Dashboard":
            display_dashboard()
        elif sidebar_option == "Settings":
            display_settings()

if __name__ == "__main__":
    main()
