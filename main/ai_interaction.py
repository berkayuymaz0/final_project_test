import openai
from dotenv import load_dotenv
import os
import logging
import time
from functools import lru_cache

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key
api_key = os.getenv('OPENAI_API_KEY')
if api_key is None:
    raise ValueError("OpenAI API key not found. Please set the 'OPENAI_API_KEY' environment variable.")

openai.api_key = api_key

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiting
RATE_LIMIT = 60  # max 60 requests per minute
rate_limiter = []

# Caching AI responses
@lru_cache(maxsize=100)
def cached_ask_question_to_openai(question, context, model):
    return ask_question_to_openai(question, context, model)

def ask_question_to_openai(question, context, model="gpt-3.5-turbo"):
    # Rate limiting
    current_time = time.time()
    rate_limiter.append(current_time)
    rate_limiter[:] = [timestamp for timestamp in rate_limiter if current_time - timestamp < 60]
    if len(rate_limiter) > RATE_LIMIT:
        time.sleep(60 - (current_time - rate_limiter[0]))

    # Create a unique cache key
    cache_key = f"{model}_{context}_{question}"
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{context}\n\nQ: {question}\nA:"}
            ]
        )
        answer = response['choices'][0]['message']['content'].strip()
        logger.info(f"AI response received for question: {question}")
        return answer
    except openai.error.OpenAIError as e:
        logger.error(f"An error occurred while communicating with the OpenAI API: {e}")
        return f"An error occurred while communicating with the OpenAI API: {e}"

def get_ai_suggestions(combined_output, context="code analysis", model="gpt-3.5-turbo"):
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
            model=model,
            messages=[
                {"role": "system", "content": prompt_context.get(context, "You are a helpful assistant.")},
                {"role": "user", "content": f"Here are the results of the analysis:\n{combined_output}\nPlease provide detailed suggestions and insights."}
            ]
        )
        suggestions = response['choices'][0]['message']['content'].strip()
        logger.info(f"AI suggestions received for context: {context}")
        return suggestions
    except openai.error.OpenAIError as e:
        logger.error(f"An error occurred while communicating with the OpenAI API: {e}")
        return f"An error occurred while communicating with the OpenAI API: {e}"
