import os
from openai import OpenAI
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_ai(messages):
    """Send conversation to OpenAI and return response"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Small, fast, cost-effective
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message.content

def start_prompt():
    """System instructions for AI behavior"""
    return [
        {"role": "system", "content": (
            "You are a career advisor AI. "
            "You will ask questions step by step to understand a person’s skills, passions, and abilities. "
            "Each time, you must present clear multiple-choice options. "
            "Sometimes allow multiple selections, sometimes only one. "
            "When you have enough info, tell the user you are ready, then recommend the most suitable career path "
            "and provide a step-by-step guide to achieve it."
        )}
    ]
