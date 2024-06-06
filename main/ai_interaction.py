import openai
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key
api_key = os.getenv('OPENAI_API_KEY')
if api_key is None:
    raise ValueError("OpenAI API key not found. Please set the 'OPENAI_API_KEY' environment variable.")

openai.api_key = api_key

def ask_question_to_openai(question, context):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{context}\n\nQ: {question}\nA:"}
            ]
        )
        answer = response['choices'][0]['message']['content'].strip()
        return answer
    except openai.error.OpenAIError as e:
        return f"An error occurred while communicating with the OpenAI API: {e}"

def get_ai_suggestions(combined_output):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a code analysis expert."},
                {"role": "user", "content": f"Here are the results of the code analysis:\n{combined_output}\nPlease provide suggestions for improvement."}
            ]
        )
        suggestions = response['choices'][0]['message']['content'].strip()
        return suggestions
    except openai.error.OpenAIError as e:
        return f"An error occurred while communicating with the OpenAI API: {e}"
