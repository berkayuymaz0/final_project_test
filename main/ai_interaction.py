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
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{context}\n\nQ: {question}\nA:"}
            ]
        )
        answer = response['choices'][0]['message']['content'].strip()
        return answer
    except openai.error.OpenAIError as e:
        return f"An error occurred while communicating with the OpenAI API: {e}"

def get_ai_suggestions(combined_output, context="code analysis"):
    try:
        prompt_context = {
            "code analysis": "You are a code analysis expert.",
            "oletools": (
                "You are an expert in analyzing OLE files and identifying potential security threats. "
                "Based on the following analysis results, identify any security threats, suggest appropriate mitigation strategies, "
                "and provide a detailed explanation for each indicator detected."
            )
        }
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt_context.get(context, "You are a helpful assistant.")},
                {"role": "user", "content": f"Here are the results of the analysis:\n{combined_output}\nPlease provide detailed suggestions and insights."}
            ]
        )
        suggestions = response['choices'][0]['message']['content'].strip()
        return suggestions
    except openai.error.OpenAIError as e:
        return f"An error occurred while communicating with the OpenAI API: {e}"
