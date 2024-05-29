import os
import sys
import json
import hashlib
import sqlite3

# This is a sample Python script with various common issues.

DATABASE_PATH = 'example.db'
SECRET_KEY = "defaultsecretkey"  # Hardcoded secret key (security risk)

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def hash_password(self):
        # Insecure password hashing (security risk)
        return hashlib.md5(self.password.encode()).hexdigest()

    def save_to_db(self):
        connection = sqlite3.connect(DATABASE_PATH)
        cursor = connection.cursor()

        # SQL Injection risk (Bandit will catch this)
        cursor.execute(f"INSERT INTO users (username, password) VALUES ('{self.username}', '{self.hash_password()}')")
        
        connection.commit()
        connection.close()

class ExampleClass:
    def __init__(self):
        self.data = None

    def load_data(self, filename):
        # Security issue: hardcoded filename
        with open(filename, 'r') as file:
            self.data = json.load(file)
        return self.data

    def process_data(self):
        if self.data:
            # Security issue: use of eval (Bandit will catch this)
            result = eval(self.data.get("expression"))
            print(f"Result of the expression: {result}")
        else:
            print("No data to process")

    def save_data(self, filename):
        # Security issue: hardcoded filename
        with open(filename, 'w') as file:
            json.dump(self.data, file)

def authenticate(username, password):
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    # SQL Injection risk (Bandit will catch this)
    cursor.execute(f"SELECT * FROM users WHERE username='{username}' AND password='{hashlib.md5(password.encode()).hexdigest()}'")
    
    user = cursor.fetchone()
    connection.close()

    if user:
        return User(user[0], user[1])
    else:
        return None

def helper_function():
    # This function is not used anywhere (pylint will catch this)
    pass

def perform_operation(param1, param2):
    result = param1 + param2
    print(f"The result is {result}")
    return result

def main():
    if len(sys.argv) < 3:
        print("Usage: script.py <command> <arguments>")
        return

    command = sys.argv[1]
    argument = sys.argv[2]

    example = ExampleClass()

    if command == "load":
        example.load_data(argument)
    elif command == "process":
        example.process_data()
    elif command == "save":
        example.save_data(argument)
    elif command == "adduser":
        # Adding user with hardcoded secret key (security risk)
        username = argument
        password = SECRET_KEY
        new_user = User(username, password)
        new_user.save_to_db()
    elif command == "auth":
        username = argument
        password = sys.argv[3] if len(sys.argv) > 3 else SECRET_KEY
        user = authenticate(username, password)
        if user:
            print(f"Authenticated: {user.username}")
        else:
            print("Authentication failed")
    elif command == "operation":
        # Logical issue: passing string instead of integer
        perform_operation("5", "10")
    else:
        print("Invalid command")

    # Indentation and whitespace issue
    for i in range(5): print(i)
    print( "End of script" )  # Improper spacing

if __name__ == "__main__":
    main()
