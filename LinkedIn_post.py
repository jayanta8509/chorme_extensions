import os
import re
import asyncio
from pydantic import BaseModel
from openai import AsyncOpenAI
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add parent directory to path to import shared_client
sys.path.append(str(Path(__file__).parent.parent))
from shared_client import get_async_client
from user_activate_store import get_user_data, store_user_data

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

    
class linkedin_post_model(BaseModel):
    linkedin_post: str


class linkedin_post_data(BaseModel):
    linkedin_post: linkedin_post_model


async def generate_intelligent_linkedin_post(input_data, user_id):   
    """
    Generate LinkedIn post using user activity data and LLM memory
    
    Args:
        input_data: Current context/topic for the post
        user_id: User identifier for retrieving preferences and storing activity
    
    Returns:
        dict: Generated post data with metadata
    """
    
    try:
        # Step 1: Retrieve user's stored preferences and activity history
        user_preferences = get_user_data(user_id, "linkedin post preferences")
        user_activity = get_user_data(user_id, "previous posts and activity")
        
        # Step 2: Build comprehensive prompt with user memory
        prompt_template = """You are an expert LinkedIn content creator specializing in generating engaging, professional posts that drive meaningful engagement and reflect the user's authentic voice and expertise.

**CRITICAL REQUIREMENTS:**
- Generate exactly ONE compelling LinkedIn post
- Post must be 500-600 words maximum (under 3,000 characters total)
- Include 2-3 relevant hashtags maximum
- Match the user's established voice and style
- Build upon their previous activity and interests
- Create authentic, value-driven content

**USER CONTEXT AND MEMORY:**
{user_context}

**CONTENT STRATEGIES:**

**Professional Tone Indicators:**
- Share insights and lessons learned
- Reference industry trends and developments  
- Include actionable takeaways for readers
- Use storytelling to illustrate points
- Ask engaging questions to drive comments

**Engagement Optimization:**
- Start with a hook that stops the scroll
- Use line breaks for better readability
- Include a clear call-to-action
- Share personal experiences or observations
- End with a thought-provoking question

**Content Types:**
- Industry insights and trends
- Personal learning experiences
- Behind-the-scenes moments
- Career advice and tips
- Company culture and values
- Project successes and challenges
- Thought leadership pieces

**Authenticity Markers:**
- Use first-person perspective naturally
- Include specific, concrete examples
- Show vulnerability and learning moments
- Reference real experiences and outcomes
- Maintain consistent voice and values

Generate a LinkedIn post that feels authentic to this user's voice, builds on their previous content themes, and creates value for their professional network."""

        # Step 3: Prepare user context from stored data
        user_context = f"""
**USER PREFERENCES:**
{format_user_preferences(user_preferences)}

**PREVIOUS ACTIVITY PATTERNS:**
{format_user_activity(user_activity)}

**CURRENT POST CONTEXT:**
{input_data}
"""

        # Step 4: Generate the post
        client = await get_async_client()
        
        completion = await client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt_template.format(user_context=user_context)},
                {"role": "user", "content": f"Create a LinkedIn post based on: {input_data}"}
            ],
            response_format=linkedin_post_data,
        )

        analysis_response = completion.choices[0].message
        total_tokens = completion.usage.total_tokens

        if hasattr(analysis_response, 'refusal') and analysis_response.refusal:
            return {
                "success": False,
                "error": f"Model refused to respond: {analysis_response.refusal}",
                "tokens": total_tokens
            }
        
        # Step 5: Extract generated post
        generated_post = analysis_response.parsed.linkedin_post.linkedin_post
        
        # Validate character count (ensure under 3,000 characters)
        if len(generated_post) > 3000:
            generated_post = generated_post[:2950] + "..."  # Truncate if too long
        
        # Step 6: Store user activity data for future reference
        activity_data = {
            "action": "linkedin_post_generated",
            "input_context": input_data,
            "generated_post": generated_post,
            "post_length": len(generated_post),
            "hashtags_used": extract_hashtags(generated_post),
            "engagement_elements": analyze_engagement_elements(generated_post),
            "timestamp": str(asyncio.get_event_loop().time())
        }
        
        # Store the activity
        store_result = store_user_data(user_id, activity_data)
        
        # Step 7: Return comprehensive result
        word_count = len(generated_post.split())
        char_count = len(generated_post)
        
        return {
            "success": True,
            "post": generated_post,
            "character_count": char_count,
            "word_count": word_count,
            "within_limits": char_count <= 3000 and word_count <= 600,
            "hashtags": extract_hashtags(generated_post),
            "tokens_used": total_tokens,
            "user_preferences_used": user_preferences.get("success", False),
            "activity_stored": store_result.get("success", False),
            "user_id": user_id,
            "input_context": input_data
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "user_id": user_id,
            "input_context": input_data
        }


def format_user_preferences(user_preferences):
    """Format user preferences for prompt context"""
    if not user_preferences.get("success") or not user_preferences.get("results"):
        return "No previous preferences found - this is a new user."
    
    prefs = []
    for result in user_preferences["results"]:
        memory = result.get("memory", "")
        score = result.get("score", 0)
        if score > 0.3:  # Only include relevant preferences
            prefs.append(f"- {memory}")
    
    return "\n".join(prefs) if prefs else "No specific preferences identified."


def format_user_activity(user_activity):
    """Format user activity history for prompt context"""
    if not user_activity.get("success") or not user_activity.get("results"):
        return "No previous activity found - this is a new user."
    
    activities = []
    for result in user_activity["results"]:
        memory = result.get("memory", "")
        timestamp = result.get("created_at", "")
        if "linkedin_post_generated" in memory or "post" in memory.lower():
            activities.append(f"- {memory} (Created: {timestamp[:10]})")
    
    return "\n".join(activities[:5]) if activities else "No previous post activity found."


def extract_hashtags(post_text):
    """Extract hashtags from the generated post"""
    hashtag_pattern = r'#\w+'
    hashtags = re.findall(hashtag_pattern, post_text)
    return hashtags


def analyze_engagement_elements(post_text):
    """Analyze engagement elements in the post"""
    word_count = len(post_text.split())
    char_count = len(post_text)
    
    elements = {
        "has_question": "?" in post_text,
        "has_call_to_action": any(word in post_text.lower() for word in ["share", "comment", "thoughts", "agree", "disagree", "experience"]),
        "has_personal_story": any(word in post_text.lower() for word in ["i", "my", "recently", "yesterday", "last week"]),
        "has_line_breaks": "\n" in post_text,
        "word_count": word_count,
        "character_count": char_count,
        "within_linkedin_limits": char_count <= 3000 and word_count <= 600,
        "optimal_length": 200 <= word_count <= 500  # Optimal engagement range
    }
    return elements


async def store_user_posting_preferences(user_id: str, preferences: dict):
    """Store user's LinkedIn posting preferences"""
    pref_data = {
        "application": "linkedin_posts",
        "posting_style": preferences.get("style", "professional"),
        "preferred_topics": preferences.get("topics", []),
        "post_frequency": preferences.get("frequency", "weekly"),
        "target_audience": preferences.get("audience", "professional_network"),
        "engagement_goals": preferences.get("goals", "thought_leadership")
    }
    
    return store_user_data(user_id, pref_data)


async def get_user_posting_insights(user_id: str):
    """Get insights about user's posting patterns"""
    # Get all posting activity
    all_activity = get_user_data(user_id, "linkedin post activity")
    
    if not all_activity.get("success") or not all_activity.get("results"):
        return {
            "total_posts": 0,
            "avg_post_length": 0,
            "common_hashtags": [],
            "posting_patterns": "No previous posts found"
        }
    
    results = all_activity["results"]
    post_lengths = []
    all_hashtags = []
    
    for result in results:
        memory = result.get("memory", "")
        if "post_length" in memory:
            try:
                length = int(re.search(r'post_length is (\d+)', memory).group(1))
                post_lengths.append(length)
            except:
                pass
        if "hashtags_used" in memory:
            hashtags = re.findall(r'#\w+', memory)
            all_hashtags.extend(hashtags)
    
    # Calculate insights
    from collections import Counter
    hashtag_counts = Counter(all_hashtags)
    
    return {
        "total_posts": len([r for r in results if "linkedin_post_generated" in r.get("memory", "")]),
        "avg_post_length": sum(post_lengths) // len(post_lengths) if post_lengths else 0,
        "common_hashtags": [tag for tag, count in hashtag_counts.most_common(5)],
        "posting_patterns": f"Average post length: {sum(post_lengths) // len(post_lengths) if post_lengths else 0} characters"
    }