# LinkedIn Content Generator API

A production-ready FastAPI application that leverages AI to generate intelligent LinkedIn posts and comments with user memory and personalization capabilities.

## 🚀 Features

### 🎯 Core Functionality
- **Intelligent LinkedIn Post Generation** - Creates personalized, engaging LinkedIn posts based on user context and preferences
- **Smart Comment Generation** - Generates 3 unique LinkedIn comments with customizable styles and tones
- **AI Image Generation** - Optional DALL-E 3 integration for creating relevant images for posts
- **User Memory System** - Stores and retrieves user preferences and activity history for personalized content

### 🧠 AI-Powered Capabilities
- **User Memory & Personalization** - Learns from user's previous content and preferences
- **Multiple Comment Styles** - Professional, Friendly, Long, and Short comment variations
- **Sentiment Control** - Positive and negative comment types
- **Content Intelligence** - Context-aware generation using GPT-4o-mini
- **Character Limit Management** - Automatic optimization for LinkedIn's content limits

### 🔧 Technical Features
- **Production-Ready Architecture** - Built with FastAPI for high performance
- **Async Operations** - Non-blocking API operations for scalability
- **Vector Memory Storage** - Qdrant Cloud integration for persistent user memory
- **Comprehensive Logging** - Detailed logging for monitoring and debugging
- **API Documentation** - Auto-generated Swagger/OpenAPI documentation
- **CORS Support** - Cross-origin resource sharing enabled
- **Error Handling** - Robust error handling and response validation

## 📋 API Endpoints

### 🏥 Health Check
```
GET /health
```
Returns API health status and version information.

### 📝 Generate LinkedIn Post
```
POST /generate-post
```
Generates intelligent LinkedIn posts with optional image generation.

**Request Body:**
```json
{
  "input_context": "Your topic or context for the LinkedIn post",
  "user_id": "unique_user_identifier",
  "image": true
}
```

**Response:**
```json
{
  "success": true,
  "status_code": 200,
  "post": "Generated LinkedIn post content...",
  "hashtags": ["#AI", "#MachineLearning"],
  "tokens_used": 985,
  "user_preferences_used": true,
  "activity_stored": true,
  "image_requested": true,
  "image_generated": true,
  "image_url": "https://oaidalleapi...png",
  "image_price": "0.04",
  "timestamp": "2025-09-19T08:22:38.019856"
}
```

### 💬 Generate LinkedIn Comments
```
POST /generate-comment
```
Generates 3 unique LinkedIn comments based on a post.

**Request Body:**
```json
{
  "user_id": "unique_user_identifier",
  "comment_style": "Professional",
  "comment_type": "positive",
  "post_text": "LinkedIn post content to comment on"
}
```

**Comment Styles:**
- `Professional` - Formal business language and industry terminology
- `Friendly` - Conversational, approachable language with personal touches
- `Long` - Comprehensive analysis with detailed explanations
- `Short` - Concise, punchy statements with maximum impact

**Comment Types:**
- `positive` - Supportive, encouraging, and optimistic responses
- `negative` - Respectful counterpoints and alternative perspectives

**Response:**
```json
{
  "success": true,
  "status_code": 200,
  "comments": {
    "comment1": "First generated comment...",
    "comment2": "Second generated comment...",
    "comment3": "Third generated comment..."
  },
  "tokens_used": 1288,
  "activity_stored": true,
  "timestamp": "2025-09-19T08:41:14.439834"
}
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- OpenAI API key
- Qdrant Cloud account (for user memory)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd linkedin-content-generator
```

### 2. Create Virtual Environment
```bash
python -m venv env
# On Windows
env\Scripts\activate
# On macOS/Linux
source env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the root directory:
```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
LLM_MODEL=gpt-4o-mini

# Qdrant Cloud Configuration
QDRANT_URL=your_qdrant_cloud_url
QDRANT_API_KEY=your_qdrant_api_key
```

### 5. Run the Application
```bash
python app.py
```

The API will be available at:
- **Main API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Configuration

### Production Settings
The application is configured for production with:
- **Workers**: 3 concurrent workers
- **Reload**: Disabled for production stability
- **Host**: 0.0.0.0 (accessible from all interfaces)
- **Port**: 8000

### Logging
Comprehensive logging is configured with:
- File logging to `linkedin_api.log`
- Console output for real-time monitoring
- Request/response logging middleware
- Error tracking and debugging information

## 📁 Project Structure

```
linkedin-content-generator/
├── app.py                  # Main FastAPI application
├── LinkedIn_comment.py     # Comment generation logic
├── LinkedIn_post.py        # Post generation logic
├── image_generation.py     # DALL-E image generation
├── user_activate_store.py  # User memory and data storage
├── shared_client.py        # Shared OpenAI client configuration
├── requirements.txt        # Python dependencies
├── linkedin_api.log       # Application logs
└── README.md              # Project documentation
```

## 🔐 Security Features

- **Input Validation** - Pydantic models for request validation
- **Character Limits** - Automatic enforcement of LinkedIn content limits
- **Error Handling** - Secure error responses without sensitive data exposure
- **CORS Configuration** - Configurable cross-origin policies
- **Trusted Host Middleware** - Host validation for production security

## 🎯 Key Components

### Memory System
- **Vector Storage**: Qdrant Cloud for efficient similarity search
- **User Personalization**: Learns from user's content patterns
- **Activity Tracking**: Stores generated content for future reference
- **Preference Learning**: Adapts to user's writing style and topics

### AI Models
- **Text Generation**: GPT-4o-mini for cost-effective, high-quality content
- **Image Generation**: DALL-E 3 for relevant visual content
- **Embeddings**: text-embedding-3-large for semantic understanding

### Content Intelligence
- **Style Adaptation**: Matches user's established voice and tone
- **Context Awareness**: Builds upon previous activity and interests
- **Engagement Optimization**: Crafted for maximum LinkedIn engagement
- **Authenticity**: Maintains genuine, professional communication

## 🚀 Performance

- **Async Operations**: Non-blocking I/O for high throughput
- **Token Tracking**: Monitors API usage and costs
- **Response Optimization**: Efficient data structures and minimal payloads
- **Scalable Architecture**: Designed for horizontal scaling

## 📊 Monitoring

- **Health Checks**: Built-in endpoint for service monitoring
- **Comprehensive Logging**: Request/response tracking and error monitoring
- **Token Usage Tracking**: Monitor AI API consumption
- **Performance Metrics**: Response times and success rates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request



## 🆘 Support

For issues, questions, or contributions:
- Check the API documentation at `/docs`
- Review logs in `linkedin_api.log`
- Ensure all environment variables are properly configured
- Verify OpenAI and Qdrant Cloud connectivity

## 🔄 Version History

- **v1.0.0** - Initial production release with core functionality
  - LinkedIn post and comment generation
  - User memory system integration
  - AI image generation capability
  - Production-ready API architecture
