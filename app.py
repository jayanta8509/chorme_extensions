"""
Production-Ready FastAPI Application for LinkedIn Content Generation
Endpoints:
- /generate-comment: Generate LinkedIn comments
- /generate-post: Generate LinkedIn posts
"""

import os
import time
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
import asyncio

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
import uvicorn

from LinkedIn_comment import analyze_linkedin_comment
from LinkedIn_post import generate_intelligent_linkedin_post
from user_activate_store import  store_user_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("linkedin_api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Lifespan Events (modern FastAPI approach)
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("LinkedIn Content Generator API starting up...")
    logger.info("API Documentation available at: http://localhost:8000/docs")
    
    yield
    
    # Shutdown
    logger.info("LinkedIn Content Generator API shutting down...")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="LinkedIn Content Generator API",
    description="Production-ready API for generating LinkedIn comments and posts with user memory",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Trusted Host Middleware (configure for production)
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"]  # Configure this properly for production
)

# Request/Response Models
class CommentGenerationRequest(BaseModel):
    """Request model for LinkedIn comment generation"""
    user_id: str = Field(..., min_length=1, max_length=100, description="Unique user identifier")
    comment_style: str = Field(..., description="Comment style: Professional, Friendly, Long, Short")
    comment_type: str = Field(..., description="Comment type: positive, negative")
    post_text: str = Field(..., min_length=3, max_length=5000, description="LinkedIn post text to comment on")
    
    @field_validator('comment_style')
    @classmethod
    def validate_style(cls, v):
        allowed_styles = ["Professional", "Friendly", "Long", "Short"]
        if v not in allowed_styles:
            raise ValueError(f"comment_style must be one of: {allowed_styles}")
        return v
    
    @field_validator('comment_type')
    @classmethod
    def validate_type(cls, v):
        # Convert to lowercase for flexibility
        v_lower = v.lower()
        allowed_types = ["positive", "negative"]
        if v_lower not in allowed_types:
            raise ValueError(f"comment_type must be one of: {allowed_types}")
        return v_lower

class PostGenerationRequest(BaseModel):
    """Request model for LinkedIn post generation"""
    input_context: str = Field(..., min_length=10, max_length=2000, description="Context or topic for the LinkedIn post")
    user_id: str = Field(..., min_length=1, max_length=100, description="Unique user identifier")

class CommentGenerationResponse(BaseModel):
    """Response model for LinkedIn comment generation"""
    success: bool
    comments: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str

class PostGenerationResponse(BaseModel):
    """Response model for LinkedIn post generation"""
    success: bool
    post: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log response
        logger.info(f"Response: {response.status_code} - {process_time:.4f}s")
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Request failed: {str(e)} - {process_time:.4f}s")
        raise

# Health Check Endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0"
    )

# LinkedIn Comment Generation Endpoint
@app.post("/generate-comment", response_model=CommentGenerationResponse, tags=["Content Generation"])
async def generate_linkedin_comment(request: CommentGenerationRequest):
    """
    Generate LinkedIn comments based on a post
    
    This endpoint generates 3 unique LinkedIn comments based on the provided post text,
    user preferences, and specified style/type parameters.
    """
    try:
        logger.info(f"Generating comment for user: {request.user_id}")
        
        # Use the provided comment style and type from request
        comment_style = request.comment_style
        comment_type = request.comment_type
        
        # Generate comments using the existing function
        result, tokens = await analyze_linkedin_comment(
            post_text_data=request.post_text,
            comment_style=comment_style,
            comment_type=comment_type
        )
        
        if result is None:
            raise HTTPException(status_code=500, detail="Failed to generate comments")
        
        # Store user activity
        activity_data = {
            "action": "linkedin_comment_generated",
            "post_text_preview": request.post_text[:100] + "..." if len(request.post_text) > 100 else request.post_text,
            "comment_style": comment_style,
            "comment_type": comment_type,
            "tokens_used": tokens
        }
        
        store_result = store_user_data(request.user_id, activity_data)
        
        # Format response
        comments = {
            "comment1": result.linkedin_comment.linkedin_comment1,
            "comment2": result.linkedin_comment.linkedin_comment2,
            "comment3": result.linkedin_comment.linkedin_comment3
        }
        
        metadata = {
            "tokens_used": tokens,
            "comment_style": comment_style,
            "comment_type": comment_type,
            "activity_stored": store_result.get("success", False),
            "comment_lengths": {
                "comment1": len(comments["comment1"]),
                "comment2": len(comments["comment2"]),
                "comment3": len(comments["comment3"])
            }
        }
        
        logger.info(f"Successfully generated comments for user: {request.user_id}")
        
        return CommentGenerationResponse(
            success=True,
            comments=comments,
            metadata=metadata,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating comment for user {request.user_id}: {str(e)}")
        return CommentGenerationResponse(
            success=False,
            error=f"Internal server error: {str(e)}",
            timestamp=datetime.utcnow().isoformat()
        )

# LinkedIn Post Generation Endpoint
@app.post("/generate-post", response_model=PostGenerationResponse, tags=["Content Generation"])
async def generate_linkedin_post(request: PostGenerationRequest):
    """
    Generate intelligent LinkedIn posts with user memory
    
    This endpoint generates personalized LinkedIn posts based on user context,
    previous activity, and stored preferences.
    """
    try:
        logger.info(f"Generating post for user: {request.user_id}")
        
        # Generate post using the intelligent system (it will automatically use stored preferences)
        result = await generate_intelligent_linkedin_post(
            input_data=request.input_context,
            user_id=request.user_id
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to generate post: {result.get('error', 'Unknown error')}"
            )
        
        metadata = {
            "character_count": result.get("character_count", 0),
            "word_count": result.get("word_count", 0),
            "within_limits": result.get("within_limits", False),
            "hashtags": result.get("hashtags", []),
            "tokens_used": result.get("tokens_used", 0),
            "user_preferences_used": result.get("user_preferences_used", False),
            "activity_stored": result.get("activity_stored", False)
        }
        
        logger.info(f"Successfully generated post for user: {request.user_id}")
        
        return PostGenerationResponse(
            success=True,
            post=result.get("post"),
            metadata=metadata,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating post for user {request.user_id}: {str(e)}")
        return PostGenerationResponse(
            success=False,
            error=f"Internal server error: {str(e)}",
            timestamp=datetime.utcnow().isoformat()
        )

# User Data Endpoints removed as per user request

# Error Handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    logger.error(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Lifespan events are now handled above in the app initialization

if __name__ == "__main__":
    # Production configuration
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Set to False for production
        workers=1,     # Adjust based on your needs
        log_level="info"
    )
