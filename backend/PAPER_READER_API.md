# arXiv Paper Reader API - Implementation Guide

## Overview

The arXiv Paper Reader API provides deep analysis of academic papers from arXiv.org. It includes:
- Paper metadata fetching
- Version history tracking
- Automatic difficulty assessment
- Reading time estimation
- Optional AI-enhanced analysis using Zhipu AI

## Installation

1. Install required dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Ensure `.env` file contains:
```
ZHIPU_API_KEY=your_api_key_here  # Optional, for AI-enhanced analysis
```

3. Start the server:
```bash
cd backend
python run.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### 1. Get Paper Metadata
**GET** `/api/papers/reader/<paper_id>/metadata`

Fetch basic paper information without full analysis.

**Parameters:**
- `paper_id` (path): arXiv paper ID (e.g., "2301.00001" or "2301.00001v1")

**Response:**
```json
{
  "success": true,
  "data": {
    "paper_id": "2301.00001",
    "title": "Paper Title",
    "authors": ["Author 1", "Author 2"],
    "summary": "Paper abstract...",
    "published": "2023-01-01T00:00:00Z",
    "categories": ["cs.AI", "cs.LG"],
    "pdf_url": "https://arxiv.org/pdf/2301.00001.pdf",
    "abs_url": "https://arxiv.org/abs/2301.00001"
  }
}
```

---

### 2. Get Paper Versions
**GET** `/api/papers/reader/<paper_id>/versions`

Get all versions of a paper.

**Parameters:**
- `paper_id` (path): arXiv paper ID

**Response:**
```json
{
  "success": true,
  "data": {
    "paper_id": "2301.00001",
    "count": 2,
    "versions": [
      {
        "version": "v1",
        "url": "https://arxiv.org/abs/2301.00001v1",
        "date": "2023-01-01"
      },
      {
        "version": "v2",
        "url": "https://arxiv.org/abs/2301.00001v2",
        "date": "2023-01-15"
      }
    ]
  }
}
```

---

### 3. Analyze Paper (GET)
**GET** `/api/papers/reader/<paper_id>`

Get complete paper analysis including difficulty, reading time, and key contributions.

**Parameters:**
- `paper_id` (path): arXiv paper ID
- `use_ai` (query, optional): Set to "true" for AI-enhanced analysis (default: false)

**Response:**
```json
{
  "success": true,
  "data": {
    "paper_id": "2301.00001",
    "metadata": {
      "title": "Paper Title",
      "authors": ["Author 1", "Author 2"],
      "published": "2023-01-01T00:00:00Z",
      "categories": ["cs.AI"],
      "pdf_url": "https://arxiv.org/pdf/2301.00001.pdf"
    },
    "content": {
      "abstract": "Full abstract text...",
      "key_contributions": [
        "First key contribution...",
        "Second key contribution..."
      ],
      "reading_time": {
        "abstract_minutes": 2,
        "paper_minutes": 45,
        "paper_hours": 0.75,
        "word_count": 250
      },
      "difficulty": {
        "level": 3,
        "label": "Advanced",
        "factors": [
          "AI/ML papers require mathematical background",
          "Large collaboration (8 authors)"
        ]
      }
    },
    "ai_enhanced": false
  }
}
```

**AI-Enhanced Response (when use_ai=true):**
```json
{
  "success": true,
  "data": {
    "paper_id": "2301.00001",
    "metadata": { ... },
    "content": {
      "abstract": "...",
      "key_contributions": [ ... ],
      "reading_time": { ... },
      "difficulty": { ... },
      "core_problem": "Problem addressed by the paper",
      "key_innovation": "Main novelty",
      "methodology": "Approach description",
      "results": "Key findings",
      "prerequisites": ["Background knowledge needed"]
    },
    "ai_enhanced": true
  }
}
```

---

### 4. Analyze Paper (POST)
**POST** `/api/papers/reader/analyze`

Same as GET /reader/<paper_id> but via POST request.

**Request Body:**
```json
{
  "paper_id": "2301.00001",
  "use_ai": false
}
```

**Response:** Same as GET /reader/<paper_id>

---

## Features

### 1. Difficulty Assessment
The system automatically assesses paper difficulty on a 1-5 scale:
- **Level 1**: Beginner Friendly
- **Level 2**: Intermediate
- **Level 3**: Advanced
- **Level 4**: Expert Level
- **Level 5**: Research Level

Factors considered:
- Paper category (AI/ML papers tend to be more advanced)
- Author count (large collaborations indicate complex work)
- Abstract length and complexity
- Number of categories (interdisciplinary work)

### 2. Reading Time Estimation
- **Abstract**: 200-250 words per minute
- **Full paper**: 2-3 minutes per page (conservative for technical papers)

### 3. Key Contributions Extraction
Automatically extracts key contributions from the abstract using pattern matching:
- "We propose..."
- "Our contribution..."
- "This paper presents..."

### 4. AI-Enhanced Analysis (Optional)
When `use_ai=true`, the system uses Zhipu AI's GLM-4-Flash model (free tier) to provide:
- Core problem statement
- Key innovation/novelty
- Methodology overview
- Main results
- Prerequisites/background needed

---

## Testing

Run the test suite:
```bash
cd backend
python test_paper_reader.py
```

The test suite will verify:
1. Health check endpoint
2. Paper metadata fetching
3. Version history retrieval
4. Paper analysis (without AI)
5. Paper analysis (with AI, if API key configured)
6. POST endpoint functionality

---

## Example Usage

### cURL Examples

**Get paper metadata:**
```bash
curl "http://localhost:5000/api/papers/reader/2301.00001/metadata"
```

**Analyze paper:**
```bash
curl "http://localhost:5000/api/papers/reader/2301.00001"
```

**Analyze with AI:**
```bash
curl "http://localhost:5000/api/papers/reader/2301.00001?use_ai=true"
```

**Get versions:**
```bash
curl "http://localhost:5000/api/papers/reader/2301.00001/versions"
```

### Python Examples

```python
import requests

# Basic analysis
response = requests.get('http://localhost:5000/api/papers/reader/2301.00001')
data = response.json()['data']

print(f"Title: {data['metadata']['title']}")
print(f"Difficulty: {data['content']['difficulty']['label']}")
print(f"Reading Time: {data['content']['reading_time']['paper_minutes']} minutes")

# AI-enhanced analysis
response = requests.get(
    'http://localhost:5000/api/papers/reader/2301.00001',
    params={'use_ai': True}
)
```

---

## Error Handling

All endpoints return errors in consistent format:

**400 Bad Request:**
```json
{
  "success": false,
  "error": "Paper not found: invalid-id"
}
```

**404 Not Found:**
```json
{
  "success": false,
  "error": "Paper not found"
}
```

**500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to analyze paper. Please try again later."
}
```

---

## Implementation Details

### Files Created/Modified:

1. **backend/services/arxiv_reader.py** - Core service class
   - `ArxivReader` class with all analysis methods
   - Integration with arXiv API via feedparser
   - Optional Zhipu AI integration

2. **backend/services/__init__.py** - Services module initialization
   - Exports `ArxivReader` and `analyze_paper` convenience function

3. **backend/routes/paper_reader.py** - API routes
   - GET `/reader/<paper_id>` - Main analysis endpoint
   - GET `/reader/<paper_id>/versions` - Version history
   - GET `/reader/<paper_id>/metadata` - Metadata only
   - POST `/reader/analyze` - Alternative analysis endpoint

4. **backend/app/__init__.py** - Updated Flask configuration
   - Added Zhipu API key configuration
   - Registered paper_reader_bp blueprint with `/api/papers` prefix

5. **backend/requirements.txt** - Added dependency
   - feedparser==6.0.10 for arXiv API parsing

6. **backend/test_paper_reader.py** - Test suite
   - 6 comprehensive test cases
   - Tests with and without AI
   - Validates all endpoints

---

## Dependencies

- **feedparser**: Parse arXiv's XML-based API responses
- **requests**: HTTP client for arXiv and Zhipu AI APIs
- **flask**: Web framework for API endpoints
- **python-dotenv**: Environment variable management

---

## Limitations & Future Enhancements

### Current Limitations:
1. AI analysis rate limited by Zhipu API quotas
2. Reading time estimation is approximate
3. Version history may be incomplete for some papers
4. Difficulty assessment is heuristic-based

### Future Enhancements:
1. Cache frequently accessed papers
2. Support bulk analysis (multiple papers at once)
3. Add PDF text extraction for deeper analysis
4. Integration with citation databases (Google Scholar, Semantic Scholar)
5. User-specific difficulty adjustment based on reading history

---

## Security Notes

- Zhipu API key is loaded from environment variables (never hardcoded)
- No user authentication required for paper reading (public data)
- Rate limiting should be added for production use
- Input validation prevents injection attacks

---

## Troubleshooting

### "Paper not found" error:
- Verify the paper ID format (e.g., "2301.00001", not "arxiv:2301.00001")
- Check if the paper exists on arXiv.org

### AI analysis fails:
- Verify ZHIPU_API_KEY is set in .env
- Check API key has remaining quota
- Ensure network connectivity to Zhipu API

### Timeout errors:
- arXiv API can be slow during peak hours
- AI analysis adds ~10-30 seconds
- Consider implementing async processing for production

---

## Related Documentation

- arXiv API: https://arxiv.org/help/api/
- Zhipu AI Docs: https://open.bigmodel.cn/dev/api
- Task Definition: task-007-1 in tasks.json
