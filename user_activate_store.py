from openai import AsyncOpenAI
from mem0 import Memory
import asyncio
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Async OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = AsyncOpenAI(api_key=openai_api_key)

# Qdrant Cloud configuration
config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "mem0_collection",
            "url": os.getenv("QDRANT_URL"),
            "api_key": os.getenv("QDRANT_API_KEY"),
        }
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "model": "text-embedding-3-large",  # Using your preferred model
            "api_key": openai_api_key
        }
    },
    "llm": {
        "provider": "openai",
        "config": {
            "model": os.getenv('LLM_MODEL', 'gpt-4o-mini'),
            "api_key": openai_api_key
        }
    }
}

# Initialize Memory with Qdrant Cloud configuration
memory = Memory.from_config(config)


def store_user_data(user_id: str, user_data: dict):
    """Store user data in Qdrant Cloud via Mem0"""
    try:
        # Create a descriptive text for the user data
        data_text = f"User preferences for {user_id}: " + ", ".join([
            f"{key} is {value}" for key, value in user_data.items()
        ])
        
        # Store in Mem0 (which will use Qdrant Cloud backend)
        result = memory.add(data_text, user_id=user_id, metadata=user_data)
        
        # Extract memory IDs from result
        memory_ids = []
        if result and 'results' in result:
            memory_ids = [item.get('id', 'unknown') for item in result['results']]
        
        return {
            "success": True,
            "message": "User data stored successfully",
            "memory_ids": memory_ids,
            "user_id": user_id,
            "data_stored": user_data
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error storing data: {e}",
            "user_id": user_id,
            "error": str(e)
        }


def get_user_data(user_id: str, query: str = "user preferences"):
    """Retrieve user data from Qdrant Cloud via Mem0"""
    try:
        results = memory.search(query=query, user_id=user_id, limit=5)
        
        return {
            "success": True,
            "user_id": user_id,
            "query": query,
            "results_count": len(results.get('results', [])),
            "results": results.get('results', [])
        }
    except Exception as e:
        return {
            "success": False,
            "user_id": user_id,
            "query": query,
            "error": str(e),
            "results": []
        }