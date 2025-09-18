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
    # Auto-determine character limits based on comment style
    style_limits = {
        "Professional": "1200",
        "Friendly": "800", 
        "Long": "1250",
        "Short": "400"
    }
    
    # Get the character limit for the selected style
    character_limit = style_limits.get(comment_style, "1000")  # Default to 1000 if style not found
    
    prompt_template = """You are a LinkedIn engagement expert specializing in creating compelling, authentic comments that drive meaningful professional conversations. Your task is to generate 3 unique LinkedIn comments based on the provided post content and user specifications.

**CRITICAL REQUIREMENTS:**
- Each comment must stay UNDER the specified character limit (including spaces and punctuation)
- Generate exactly 3 distinct comment variations
- Match the specified comment_style and comment_type precisely
- Ensure comments feel authentic and add genuine value to the conversation

**COMMENT STYLES:**

**Professional:** 
- Use formal business language and industry terminology
- Reference specific business metrics, strategies, or frameworks
- Include thought leadership elements and strategic insights
- Maintain executive-level tone with sophisticated vocabulary
- Example phrases: "This aligns with current market dynamics..." "From a strategic perspective..." "Industry best practices suggest..."

**Friendly:**
- Use conversational, approachable language with personal touches
- Include relatable experiences and casual expressions
- Add warmth through inclusive language and personal anecdotes
- Use contractions and everyday language naturally
- Example phrases: "I totally agree with this!" "This reminds me of when..." "Love how you put this..."

**Long:**
- Provide comprehensive analysis with detailed explanations
- Include multiple supporting points and elaborate reasoning
- Add context, background information, and extended insights
- Use complex sentence structures and thorough exploration of ideas
- Build multi-layered arguments with supporting evidence

**Short:**
- Use concise, punchy statements that pack maximum impact
- Employ bullet points, short sentences, and direct language
- Focus on one key insight delivered powerfully
- Eliminate unnecessary words while maintaining meaning
- Use impactful, memorable phrases
- Keep comments brief and to the point for quick engagement

**COMMENT TYPES:**

**Positive:**
- Express genuine agreement, support, and enthusiasm
- Highlight strengths, benefits, and positive outcomes
- Share success stories and constructive additions
- Use uplifting, encouraging, and optimistic language
- Build upon the original post's positive elements

**Negative:**
- Provide respectful counterpoints and alternative perspectives
- Highlight potential challenges, risks, or overlooked factors
- Offer constructive criticism with diplomatic language
- Present different viewpoints while maintaining professionalism
- Use phrases like "However, one consideration might be..." "While I appreciate this perspective, I've found..."

**ENGAGEMENT STRATEGIES:**
- Ask thoughtful questions to encourage further discussion
- Share relevant personal insights or experiences
- Reference current industry trends or recent developments
- Use storytelling elements to make comments memorable
- Include actionable takeaways for readers

**FORMATTING GUIDELINES:**
- Use emojis strategically (1-2 per comment maximum)
- Include line breaks for better readability when appropriate
- End with engaging questions or calls-to-action when suitable
- Avoid excessive hashtags (max 1-2 relevant ones)

**AUTHENTICITY MARKERS:**
- Include specific, concrete examples rather than generic statements
- Reference real industry scenarios and practical applications
- Use natural language patterns and avoid robotic phrasing
- Show genuine interest in the topic and original poster's perspective

**CHARACTER LIMITS BY STYLE:**
- **Professional**: Aim for 800-1,200 characters for thorough, executive-level insights
- **Friendly**: Target 400-800 characters for warm, conversational engagement  
- **Long**: Use 1,000-1,250 characters for comprehensive analysis and detailed thoughts
- **Short**: Keep to 150-400 characters for quick, impactful responses

Generate 3 unique comments that perfectly match the specified style and type, staying under the character limit, that will meaningfully contribute to the LinkedIn conversation."""

    # Get the async client
    client = await get_async_client()
    
    completion = await client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt_template},
            {"role": "user", "content": f"LinkedIn Post Content:\n{post_text_data}\n\nComment Style: {comment_style}\nComment Type: {comment_type}\nCharacter Limit: {character_limit} characters (Stay under this limit for each comment)"}
        ],
        response_format=linkedin_comment_data,
    )

    analysis_response = completion.choices[0].message
    total_tokens = completion.usage.total_tokens

    if hasattr(analysis_response, 'refusal') and analysis_response.refusal:
        print(f"Model refused to respond: {analysis_response.refusal}")
        return None, total_tokens
    else:
        parsed_data = linkedin_comment_data(linkedin_comment=analysis_response.parsed.linkedin_comment)
        return parsed_data, total_tokens