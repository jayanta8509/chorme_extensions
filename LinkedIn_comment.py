import os
import re
from pydantic import BaseModel
from openai import AsyncOpenAI
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add parent directory to path to import shared_client
sys.path.append(str(Path(__file__).parent.parent))
from shared_client import get_async_client

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

    
class linkedin_comment_model(BaseModel):
    linkedin_comment1: str
    linkedin_comment2: str
    linkedin_comment3: str


class linkedin_comment_data(BaseModel):
    linkedin_comment: linkedin_comment_model


async def analyze_linkedin_comment(post_text_data, comment_style, comment_type):   
    # Auto-determine word limits based on comment style
    style_limits = {
        "Professional": "50",
        "Friendly": "50", 
        "Long": "70",
        "Short": "50"
    }
    
    # Get the word limit for the selected style
    word_limit = style_limits.get(comment_style, "50")  # Default to 50 if style not found
    
    prompt_template = """You are a LinkedIn user writing authentic comments. Generate EXACTLY 3 DISTINCT, unique, natural-sounding comments.

CRITICAL: You MUST generate ALL 3 comments. Each comment MUST be different from the others.

REQUIREMENTS:
- Stay within word limit (50 words for most, 70 for Long)
- Sound human and conversational
- Use contractions and natural phrasing
- Make each comment approach the topic from a different angle

STYLES:
Professional: Knowledgeable but conversational. Example: "I've seen this work well in my team. The key is getting buy-in early."

Friendly: Like chatting over coffee. Example: "Love this! I tried something similar last month and it changed how we work."

Long: Brief stories with examples. Example: "This resonates with me. Last year we faced similar challenges. We tried a different approach and learned that simple solutions work best."

Short: Quick and punchy. Example: "Exactly what I needed today. Thanks for sharing!"

TYPES:
Positive: Show enthusiasm and support. Vary the approach (enthusiasm, agreement, personal experience).
Negative: Share different perspectives respectfully. Vary the approach (skepticism, concern, alternative viewpoint, implementation doubt, past experience).

TIPS: 
- Use contractions, vary sentence length, include filler words (really, actually, just), minimal emojis (0-2 max)
- For negative comments: Be constructive, question implementation, share concerns, or offer alternative perspectives
- Each of the 3 comments should take a slightly different angle or focus on different aspects"""

    # Get the async client
    client = await get_async_client()
    
    completion = await client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt_template},
            {"role": "user", "content": f"Post: {post_text_data}\n\nStyle: {comment_style} | Type: {comment_type} | Max: {word_limit} words\n\nGenerate 3 complete, distinct comments. Do not leave any comment empty."}
        ],
        response_format=linkedin_comment_data,
        temperature=0.9,  # Higher temperature for more creative, diverse responses
        max_tokens=800,   # Increased to ensure enough tokens for all 3 comments (especially for negative/complex ones)
    )

    analysis_response = completion.choices[0].message
    total_tokens = completion.usage.total_tokens

    if hasattr(analysis_response, 'refusal') and analysis_response.refusal:
        print(f"Model refused to respond: {analysis_response.refusal}")
        return None, total_tokens
    else:
        parsed_data = linkedin_comment_data(linkedin_comment=analysis_response.parsed.linkedin_comment)
        return parsed_data, total_tokens