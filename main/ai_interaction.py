import openai
from dotenv import load_dotenv
from sympy import im
import os
load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

def ask_question_to_openai(question, context):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"{context}\n\nQ: {question}\nA:"}
        ]
    )
    answer = response['choices'][0]['message']['content'].strip()
    return answer

def get_ai_suggestions(combined_output):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a code analysis expert."},
            {"role": "user", "content": f"Here are the results of the code analysis:\n{combined_output}\nPlease provide suggestions for improvement."}
        ]
    )
    suggestions = response['choices'][0]['message']['content'].strip()
    return suggestions
