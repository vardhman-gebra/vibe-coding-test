# CRO Analyzer Backend

A FastAPI-based backend service that analyzes websites for Conversion Rate Optimization (CRO) best practices and provides actionable recommendations.

## Features

- **Web Scraping**: Uses Playwright to extract HTML content from any URL
- **CRO Scoring**: Analyzes websites against 6 key CRO criteria
- **Detailed Recommendations**: Provides specific, actionable suggestions for improvement
- **RESTful API**: Clean, documented API endpoints with Pydantic validation

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **Playwright**: Browser automation for reliable web scraping
- **BeautifulSoup4**: HTML parsing and content extraction
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: ASGI server implementation

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers**:
   ```bash
   playwright install chromium
   ```

## Running the Server

### Development Mode

```bash
uvicorn main:app --reload
```

The server will start at `http://localhost:8000`

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running, access the interactive API documentation at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Root Endpoint

**GET** `/`

Returns a welcome message.

**Response**:
```json
{
  "message": "Welcome to Vibe Coding API"
}
```

### CRO Recommendations

**POST** `/api/cro/recommendations`

Analyzes a website URL and returns a comprehensive CRO score with breakdown and recommendations.

**Request Body**:
```json
{
  "url": "https://example.com"
}
```

**Response** (200 OK):
```json
{
  "url": "https://example.com",
  "score": 75,
  "breakdown": {
    "title": 20,
    "meta_description": 15,
    "h1_tags": 10,
    "ctas": 15,
    "forms": 15,
    "content": 0
  },
  "recommendations": [
    "👍 Good job! A few improvements can make your page even better.",
    "Multiple H1 tags detected (2). Stick to one H1 tag for better SEO.",
    "Consider adding more CTA buttons to increase conversion opportunities (currently: 1).",
    "Add more content to your page (current: ~250 words, recommended: 300+ words)."
  ]
}
```

**Error Responses**:

- **400 Bad Request**: Invalid URL or failed to extract content
- **408 Request Timeout**: Page took too long to load
- **500 Internal Server Error**: Server-side error during analysis

## CRO Scoring Criteria

The CRO score is calculated out of 100 points based on the following criteria:

### 1. Title Quality (20 points)
- **+10 points**: Has a title tag
- **+10 points**: Title length between 30-60 characters (SEO best practice)

### 2. Meta Description (15 points)
- **+10 points**: Has a meta description
- **+5 points**: Meta description length between 120-160 characters

### 3. H1 Tags (15 points)
- **+10 points**: Has at least one H1 tag
- **+5 points**: Has exactly one H1 tag (SEO best practice)

### 4. Call-to-Action Buttons (25 points)
- **+15 points**: Has at least one CTA button
- **+10 points**: Has 2 or more CTA buttons

### 5. Forms (15 points)
- **+15 points**: Has at least one form element

### 6. Content Length (10 points)
- **+10 points**: Content length > 300 words (~1800 characters)

## Score Interpretation

- **80-100**: Excellent - Website follows most CRO best practices
- **60-79**: Good - Some improvements recommended
- **50-59**: Fair - Multiple improvements needed
- **0-49**: Poor - Significant optimization required

## Project Structure

```
backend/
├── config.py              # Configuration settings (CORS, API info)
├── main.py                # FastAPI application entry point
├── models.py              # Pydantic models for request/response
├── requirements.txt       # Python dependencies
├── routes/
│   ├── __init__.py       # Router exports
│   ├── cro.py            # CRO analysis endpoints
│   └── seo.py            # SEO endpoints (future expansion)
└── services/
    ├── __init__.py       # Service exports
    └── scraper.py        # Web scraping functionality
```

## Key Components

### Models (`models.py`)

- **URLRequest**: Validates incoming URL requests
- **CROBreakdown**: Detailed score breakdown by category
- **CROAnalysis**: Complete analysis response with score, breakdown, and recommendations

### Routes (`routes/cro.py`)

- **calculate_cro_score()**: Core scoring logic function
- **get_cro_recommendations()**: API endpoint handler

### Services (`services/scraper.py`)

- **extract_html_content()**: Extracts and parses HTML content using Playwright

## Configuration

Environment variables and CORS settings are configured in `config.py`:

```python
# CORS Origins (for frontend integration)
CORS_ORIGINS = ["http://localhost:5173", "http://localhost:3000"]
```

## Error Handling

The API includes comprehensive error handling:

- **Timeout Protection**: 15-second timeout for page loading
- **Validation**: Pydantic models ensure data integrity
- **Logging**: Detailed error logging for debugging
- **User-Friendly Messages**: Clear error messages for client consumption

## Testing the API

### Using curl

```bash
curl -X POST "http://localhost:8000/api/cro/recommendations" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/cro/recommendations",
    json={"url": "https://example.com"}
)

print(response.json())
```

### Using JavaScript/Fetch

```javascript
const response = await fetch('http://localhost:8000/api/cro/recommendations', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ url: 'https://example.com' })
});

const data = await response.json();
console.log(data);
```

## Development

### Adding New Scoring Criteria

1. Update the `calculate_cro_score()` function in `routes/cro.py`
2. Add the new field to `CROBreakdown` model in `models.py`
3. Update the total possible score calculation
4. Add appropriate recommendations

### Adding New Endpoints

1. Create a new router file in `routes/`
2. Define your endpoints using FastAPI decorators
3. Import and register the router in `main.py`

## Troubleshooting

### Playwright Installation Issues

If you encounter issues with Playwright:

```bash
# Install with system dependencies
playwright install chromium --with-deps

# Or install all browsers
playwright install
```

### CORS Errors

If you're getting CORS errors from your frontend:

1. Check that your frontend URL is listed in `CORS_ORIGINS` in `config.py`
2. Restart the backend server after making changes

### Module Import Errors

Ensure you're in the backend directory and the virtual environment is activated:

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## Performance Considerations

- **Page Load Timeout**: Set to 15 seconds to prevent hanging requests
- **Content Limit**: Text content limited to 5000 characters for processing efficiency
- **Headless Browser**: Chromium runs in headless mode for better performance

## Security

- **Input Validation**: All URLs are validated through Pydantic models
- **CORS Protection**: Configurable CORS origins
- **Timeout Protection**: Prevents long-running requests
- **Error Sanitization**: Sensitive information not exposed in error messages

## Future Enhancements

Potential areas for expansion:

- [ ] Image optimization analysis
- [ ] Mobile responsiveness scoring
- [ ] Page speed metrics integration
- [ ] A/B testing recommendations
- [ ] Accessibility (a11y) scoring
- [ ] Analytics tracking verification
- [ ] SSL/HTTPS verification
- [ ] Social media meta tags analysis

## Contributing

When contributing to this project:

1. Follow PEP 8 style guidelines
2. Add type hints to all functions
3. Update this README with any new features
4. Test endpoints before committing

## License

This project is part of the Vibe Coding hands-on exercise.

## Support

For issues or questions:
- Check the API documentation at `/docs`
- Review error messages in the API response
- Check server logs for detailed error information

---

**Built with ❤️ using FastAPI, Playwright, and Python**

