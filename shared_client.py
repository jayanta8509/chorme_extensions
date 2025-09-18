"""
Shared AsyncOpenAI Client Configuration

This module provides a properly configured AsyncOpenAI client that supports
true concurrent requests by using custom HTTP client settings.
"""
import os
import httpx
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Create custom HTTP client with higher connection limits for concurrency
custom_http_client = httpx.AsyncClient(
    limits=httpx.Limits(
        max_connections=50,      # Allow up to 50 concurrent connections
        max_keepalive_connections=20,  # Keep 20 connections alive
    ),
    timeout=httpx.Timeout(
        connect=30.0,    # 30 seconds to establish connection
        read=120.0,      # 2 minutes to read response
        write=30.0,      # 30 seconds to send request
        pool=30.0        # 30 seconds to get connection from pool
    )
)

# Create shared async OpenAI client instance
async_openai_client = AsyncOpenAI(
    api_key=openai_api_key,
    http_client=custom_http_client
)

async def get_async_client():
    """
    Get the shared AsyncOpenAI client instance.
    
    Returns:
        AsyncOpenAI: Configured async OpenAI client
    """
    return async_openai_client

async def close_client():
    """
    Close the HTTP client when shutting down.
    """
    await custom_http_client.aclose()
