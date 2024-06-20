import streamlit as st
import sqlite3
import bcrypt
from pdf_qa import display_pdf_question_answering
from ole_tool import display_ole_tool
from python_code_analysis import display_python_code_analysis
from security_scans import display_security_scans
from dashboard import display_dashboard
from settings import display_settings

# Database management functions
def create_usertable():
    execute_query('CREATE TABLE IF NOT EXISTS userstable(username TEXT, email TEXT, password TEXT)')

def add_userdata(username, email, password):
    execute_query('INSERT INTO userstable(username, email, password) VALUES (?, ?, ?)', (username, email, password))

def get_user_by_email(email):
    query = 'SELECT * FROM userstable WHERE email =?'
    return fetch_one(query, (email,))

def execute_query(query, params=()):
    with sqlite3.connect('data.db') as conn:
        c = conn.cursor()
        c.execute(query, params)
        conn.commit()

def fetch_one(query, params=()):
    with sqlite3.connect('data.db') as conn:
        c = conn.cursor()
        c.execute(query, params)
        return c.fetchone()

# Password hashing and verification
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

# Main application function
def main():
    st.set_page_config(page_title="Professional Security Analysis Tool", layout="wide")
    st.title("Professional Security Analysis Tool")

    menu = ["Home", "Login", "SignUp"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.subheader("Home")
        # Display your main content here

    elif choice == "Login":
        st.subheader("Login Section")

        email = st.sidebar.text_input("Email", key="login_email")
        password = st.sidebar.text_input("Password", type='password', key="login_password")
        if st.sidebar.button("Login"):
            create_usertable()
            user_data = get_user_by_email(email)
            if user_data:
                stored_username, stored_email, stored_password = user_data
                if verify_password(password, stored_password):
                    st.success(f"Logged In as {stored_username}")

                    sidebar_option = st.sidebar.selectbox(
                        "Choose a section",
                        ("PDF Question Answering", "OLE Tool", "Python Code Analysis", "Security Scans", "Dashboard", "Settings")
                    )

                    if sidebar_option == "PDF Question Answering":
                        display_pdf_question_answering()
                    elif sidebar_option == "OLE Tool":
                        display_ole_tool()
                    elif sidebar_option == "Python Code Analysis":
                        display_python_code_analysis()
                    elif sidebar_option == "Security Scans":
                        display_security_scans()
                    elif sidebar_option == "Dashboard":
                        display_dashboard()
                    elif sidebar_option == "Settings":
                        display_settings()
                else:
                    st.warning("Incorrect Email/Password")
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

if __name__ == "__main__":
    main()
