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
        max_connections=100,     # Allow up to 100 concurrent connections
        max_keepalive_connections=30,  # Keep 30 connections alive for reuse
    ),
    timeout=httpx.Timeout(
        connect=10.0,    # 10 seconds to establish connection
        read=30.0,       # 30 seconds to read response (enough for quick generation)
        write=10.0,      # 10 seconds to send request
        pool=10.0        # 10 seconds to get connection from pool
    ),
    http2=True  # Enable HTTP/2 for better performance
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
