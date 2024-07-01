import dis
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

def display_landing_page():
    st.markdown("""
        <style>
            .hero {
                text-align: center;
                margin-bottom: 40px;
            }
            .hero h1 {
                font-size: 3em;
                margin: 0;
                padding: 0;
            }
            .hero h2 {
                font-size: 1.5em;
                color: #888;
                margin: 0;
                padding: 10px 0 0 0;
            }
            .feature {
                text-align: center;
                margin: 20px 0;
            }
            .feature img {
                max-width: 100px;
                margin-bottom: 10px;
            }
            .cta {
                text-align: center;
                margin: 40px 0;
            }
            .cta button {
                font-size: 1.2em;
                padding: 10px 20px;
            }
            .feature-icons {
                display: flex;
                justify-content: center;
                gap: 20px;
                margin: 20px 0;
            }
            .feature-icons div {
                flex: 1;
                text-align: center;
            }
        </style>
    """, unsafe_allow_html=True)

    # Hero Section
    st.markdown("""
        <div class="hero">
            <h1>AppSec</h1>
            <h2>Comprehensive tools to keep your code secure and efficient</h2>
        </div>
    """, unsafe_allow_html=True)

    # Feature Highlights
    st.markdown("""
        <div class="feature-icons">
            <div>
                <img src="https://img.icons8.com/ios-filled/100/000000/pdf.png" alt="PDF Analysis"/>
                <h3>Analyze PDF Documents</h3>
                <p>Upload and extract information from PDF files with ease.</p>
            </div>
            <div>
                <img src="https://img.icons8.com/ios-filled/100/000000/lock.png" alt="Security Scans"/>
                <h3>Security Scans</h3>
                <p>Perform thorough security scans on various file types to detect vulnerabilities.</p>
            </div>
            <div>
                <img src="https://img.icons8.com/ios-filled/100/000000/code.png" alt="Code Analysis"/>
                <h3>Code Analysis</h3>
                <p>Use state-of-the-art tools to analyze your code for potential issues and receive AI-driven suggestions for improvements.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="feature">
            <img src="https://d1csarkz8obe9u.cloudfront.net/posterpreviews/wrench-icon-design-template-ae874f6f5a9683885bceba8323ceb0cb_screen.jpg?ts=1625755658" alt="OLE Tool"/>
            <h3>OLE Tool</h3>
            <p>Analyze OLE files to identify potential security threats.</p>
        </div>
    """, unsafe_allow_html=True)


def main():
    st.set_page_config(page_title="AppSec", layout="wide")
    st.sidebar.title("Menu")

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
            display_landing_page()

    if not st.session_state.logged_in:
        if choice == "Login":
            display_landing_page()

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
            ("PDF Question Answering", "OLE Tool", "Code Analysis", "Security Scans", "Dashboard", "Settings")
        )

        if sidebar_option == "PDF Question Answering":
            display_pdf_question_answering()
        elif sidebar_option == "OLE Tool":
            display_ole_tool()
        elif sidebar_option == "Code Analysis":
            display_code_analysis()
        elif sidebar_option == "Security Scans":
            display_security_scans()
        elif sidebar_option == "Dashboard":
            display_dashboard()
        elif sidebar_option == "Settings":
            display_settings()

if __name__ == "__main__":
    main()
