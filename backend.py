import os
from openai import OpenAI
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def ask_ai(messages):
    """Send conversation to OpenAI and return response"""
    response = client.chat.completions.create(
        model="gpt-5mini",
        messages=messages,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def start_prompt():
    """System instructions for AI behavior"""
    return [
        {
            "role": "system",
            "content": (
                "You are an enthusiastic and supportive career advisor AI. "
                "Guide users step by step to discover their passions, skills, and career goals. "
                "For each question, provide clear multiple-choice options formatted as bullet points using '-'.\n\n"
                "Important rules:\n"
                "- If only one answer should be chosen, end with 'Select one:'.\n"
                "- If multiple answers are allowed, end with 'Select all that apply:'.\n"
                "- Ask 4-6 thoughtful questions to understand their profile.\n"
                "- When you have sufficient information, say 'I am ready to give you a career recommendation.'\n"
                "- Then provide a detailed career recommendation including:\n"
                "  * The recommended career path and why it's perfect for them\n"
                "  * Key skills they should develop\n"
                "  * Step-by-step action plan (short-term and long-term)\n"
                "  * Resources and next steps\n"
                "- Be encouraging, specific, and actionable in your recommendations."
            ),
        }
    ]


def generate_roadmap_image(recommendation_text, user_profile):
    """Generate a simple, clean roadmap image using DALL-E based on the career recommendation"""

    # Extract career from recommendation
    career_path = "Professional"

    career_keywords = {
        "data scientist": "Data Scientist",
        "data analyst": "Data Analyst",
        "software engineer": "Software Engineer",
        "developer": "Software Developer",
        "product manager": "Product Manager",
        "ux designer": "UX Designer",
        "ui designer": "UI Designer",
        "designer": "Designer",
        "business analyst": "Business Analyst",
        "marketing": "Marketing Specialist",
        "project manager": "Project Manager",
        "consultant": "Consultant",
        "engineer": "Engineer"
    }

    recommendation_lower = recommendation_text.lower()
    for keyword, title in career_keywords.items():
        if keyword in recommendation_lower:
            career_path = title
            break

    # Simple 4-step roadmap
    prompt = f"""Create a simple, clean career roadmap diagram for: {career_path}

LAYOUT:
- 4 boxes only, arranged horizontally left to right
- Simple arrows connecting the boxes
- White background
- Each box same size

BOX LABELS (exact text):
Box 1: "Learn & Study"
Box 2: "Practice & Build"
Box 3: "Get Experience"
Box 4: "Career Success"

STYLE:
- Minimalist and clean
- Blue gradient boxes
- White text inside boxes
- Simple straight arrows between boxes
- NO icons, NO decorations, NO extra elements
- Professional and simple
- Like a basic flowchart
- Very easy to understand

Keep it extremely simple - just 4 boxes with text and arrows."""

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1792x1024",
            quality="standard",
            n=1,
        )
        return response.data[0].url
    except Exception as e:
        print(f"Error generating image: {e}")
        raise e