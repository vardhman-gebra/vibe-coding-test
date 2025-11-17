# Vibe Coding - 1 Hour Hands-On Assignment

## Overview

Welcome to the Vibe Coding hands-on exercise! This assignment is designed to assess your ability to understand existing code, implement new features, and integrate frontend and backend components.

**Time Allocation: 60 minutes**

## Background

You're working on a CRO (Conversion Rate Optimization) Analyzer application. The application currently has:
- A FastAPI backend with a web scraping service
- A React + TypeScript frontend with a URL input form
- Basic infrastructure for analyzing websites

## Your Task

Implement a **CRO Score Calculator** feature that analyzes a website and provides a score from 0-100 based on conversion optimization best practices.

## Requirements

### Part 1: Backend Implementation (30-35 minutes)

**Goal:** Implement the CRO scoring logic in the `/api/cro/recommendations` endpoint.

#### Scoring Criteria (implement these checks):

1. **Title Quality (20 points)**
   - Has a title: +10 points
   - Title length between 30-60 characters: +10 points

2. **Meta Description (15 points)**
   - Has meta description: +10 points
   - Meta description length between 120-160 characters: +5 points

3. **H1 Tags (15 points)**
   - Has at least one H1 tag: +10 points
   - Has exactly one H1 tag (SEO best practice): +5 points

4. **Call-to-Action (CTAs) (25 points)**
   - Has at least one CTA button: +15 points
   - Has 2 or more CTAs: +10 points

5. **Forms (15 points)**
   - Has at least one form: +15 points

6. **Content Length (10 points)**
   - Content length > 300 words (~1800 characters): +10 points

#### Implementation Steps:

1. Modify `backend/routes/cro.py` to:
   - Call the `extract_html_content()` function from `services/scraper.py`
   - Implement the scoring logic based on the criteria above
   - Return a response with:
     - `score`: integer (0-100)
     - `breakdown`: object with individual category scores
     - `recommendations`: array of strings with improvement suggestions

2. Update `backend/models.py` to:
   - Create a `CROAnalysis` response model with appropriate fields
   - Ensure proper type hints and validation

#### Example Response Format:

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
    "Add more content to your page (current: 250 words, recommended: 300+)",
    "Consider adding another H1 tag is detected, stick to one for better SEO"
  ]
}
```

### Part 2: Frontend Integration (20-25 minutes)

**Goal:** Display the CRO analysis results in the React frontend.

#### Implementation Steps:

1. Modify `frontend/src/App.tsx` to:
   - Make an API call to `/api/cro/recommendations` when form is submitted
   - Display the results in a user-friendly format
   - Show the overall score prominently
   - Display the breakdown by category
   - List the recommendations

2. UI Requirements:
   - Show a loading state while analyzing
   - Display errors appropriately if the API fails
   - Make the results visually appealing (use existing Tailwind classes)
   - Show the score with a visual indicator (e.g., color-coded: red < 50, yellow 50-75, green > 75)

### Part 3: Testing & Polish (5-10 minutes)

1. Test your implementation with a real URL (e.g., https://example.com)
2. Verify error handling works correctly
3. Ensure the UI is responsive and user-friendly

## Evaluation Criteria

Your submission will be evaluated on:

1. **Functionality (40%)**
   - Does the scoring logic work correctly?
   - Are all scoring criteria implemented?
   - Does the API return the expected response format?

2. **Code Quality (30%)**
   - Clean, readable code
   - Proper error handling
   - Good variable naming and structure
   - Type safety (TypeScript/Pydantic)

3. **Problem-Solving Approach (20%)**
   - Logical breakdown of the task
   - Efficient implementation
   - Creative solutions to challenges

4. **Integration & UX (10%)**
   - Frontend displays data correctly
   - Good user experience
   - Visual polish

## Getting Started

### Prerequisites
- Python 3.8+ installed
- Node.js 18+ installed
- Review the existing codebase structure

### Setup

1. **Backend Setup:**
   ```bash
   cd backend
   pip install -r requirements.txt
   playwright install chromium
   uvicorn main:app --reload
   ```

2. **Frontend Setup (in a new terminal):**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Verify setup:**
   - Backend: http://localhost:8000/docs
   - Frontend: http://localhost:5173

## Submission

When complete, you should have:
- A working backend endpoint that calculates CRO scores
- A frontend that displays the analysis results
- Both services running and integrated

## Tips

- Start by understanding the existing `scraper.py` service
- The scraper already extracts most data you need
- Focus on getting core functionality working before polish
- Use TypeScript types to catch errors early
- Test incrementally - don't wait until the end

## Questions?

During the interview, feel free to ask clarifying questions. In a real work environment, asking questions is encouraged!

Good luck! 🚀
