import os
import re
from pydantic import BaseModel
import sys
from pathlib import Path

# Add parent directory to path to import shared_client
sys.path.append(str(Path(__file__).parent.parent))
from shared_client import get_async_client

    
class professional_data(BaseModel):
    tone_one: str
    tone_two: str
    tone_three: str


async def professional_tone(text):
    prompt_template = """
    You are a professional communication expert specializing in business writing and tone optimization.

    Your task is to analyze the user's text and provide three enhanced professional versions that maintain the same core message while improving grammar, clarity, and business appropriateness.

    **REQUIREMENTS:**
    1. **Grammar & Spelling**: Fix all grammatical errors, typos, and punctuation issues
    2. **Professional Tone**: Transform casual language into business-appropriate communication
    3. **Word Count Consistency**: All three versions should have similar word counts (within 10-15% of each other)
    4. **Message Preservation**: Maintain the original meaning and intent
    5. **Tone Variations**: Provide slightly different professional approaches:

    **TONE STYLES:**
    - **Formal Professional**: Traditional business communication, very polished and conservative
    - **Modern Professional**: Contemporary business style, approachable yet professional
    - **Executive Professional**: Strategic and authoritative, suitable for leadership communication

    **OUTPUT FORMAT:**
    Return your response as a JSON object with exactly three tone variations:
    - tone_one: Formal Professional version
    - tone_two: Modern Professional version
    - tone_three: Executive Professional version

    **GUIDELINES:**
    - Use strong action verbs
    - Eliminate filler words and weak phrases
    - Ensure clear, concise language
    - Maintain consistent terminology across all versions
    - Focus on clarity and impact
    - Use proper business etiquette
    """

    # Get the async client
    client = await get_async_client()

    completion = await client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt_template},
            {"role": "user", "content": f"Transform this text into three professional tone variations: {text}"}
        ],
        response_format=professional_data,
    )

    analysis_response = completion.choices[0].message
    total_tokens = completion.usage.total_tokens

    if hasattr(analysis_response, 'refusal') and analysis_response.refusal:
        print(f"Model refused to respond: {analysis_response.refusal}")
        return None, total_tokens
    else:
        parsed_data = analysis_response.parsed
        return parsed_data, total_tokens