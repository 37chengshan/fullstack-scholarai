"""
arXiv Paper Reader Service

This service handles fetching and parsing arXiv papers for deep reading analysis.
It integrates with arXiv API and optionally uses Zhipu AI for enhanced analysis.
"""

import feedparser
import re
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArxivReader:
    """Service for reading and analyzing arXiv papers"""

    # arXiv API base URL
    ARXIV_API_URL = "http://export.arxiv.org/api/query"
    ARXIV_ABS_URL = "https://arxiv.org/abs/"
    ARXIV_PDF_URL = "https://arxiv.org/pdf/"

    # Zhipu AI API (optional for enhanced analysis)
    ZHIPU_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

    def __init__(self, zhipu_api_key: Optional[str] = None):
        """
        Initialize ArxivReader

        Args:
            zhipu_api_key: Optional Zhipu AI API key for enhanced analysis
        """
        self.zhipu_api_key = zhipu_api_key

    def fetch_paper_metadata(self, paper_id: str) -> Dict[str, Any]:
        """
        Fetch paper metadata from arXiv API

        Args:
            paper_id: arXiv paper ID (e.g., "2301.00001" or "2301.00001v1")

        Returns:
            Dictionary containing paper metadata
        """
        try:
            # Extract base ID without version
            base_id = paper_id.split('v')[0]

            # Query arXiv API
            query = f"id:{base_id}"
            url = f"{self.ARXIV_API_URL}?id_list={base_id}"

            logger.info(f"Fetching paper metadata for {paper_id}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            # Parse XML response
            feed = feedparser.parse(response.content)

            if not feed.entries:
                raise ValueError(f"Paper not found: {paper_id}")

            entry = feed.entries[0]

            # Extract metadata
            metadata = {
                "paper_id": paper_id,
                "title": entry.get("title", "").strip(),
                "authors": [author.get("name", "") for author in entry.get("authors", [])],
                "summary": entry.get("summary", "").strip(),
                "published": entry.get("published", ""),
                "updated": entry.get("updated", ""),
                "primary_category": entry.get("primary_category", ""),
                "categories": [tag.get("term") for tag in entry.get("tags", [])],
                "pdf_url": entry.get("link", "").replace("http://", "https://"),
                "abs_url": f"{self.ARXIV_ABS_URL}{paper_id}",
                "comment": entry.get("comment", ""),
                "journal_ref": entry.get("arxiv_journal_ref", ""),
                "doi": entry.get("arxiv_doi", "")
            }

            logger.info(f"Successfully fetched metadata for {paper_id}")
            return metadata

        except requests.RequestException as e:
            logger.error(f"Error fetching paper metadata: {e}")
            raise ValueError(f"Failed to fetch paper from arXiv: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

    def fetch_paper_versions(self, paper_id: str) -> List[Dict[str, Any]]:
        """
        Fetch all versions of a paper

        Args:
            paper_id: arXiv paper ID

        Returns:
            List of version dictionaries
        """
        try:
            base_id = paper_id.split('v')[0]
            url = f"{self.ARXIV_API_URL}?id_list={base_id}"

            logger.info(f"Fetching versions for {paper_id}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            feed = feedparser.parse(response.content)

            if not feed.entries:
                return []

            entry = feed.entries[0]
            versions = []

            # Parse versions from entry
            for link in entry.get("links", []):
                if "title" in link and "versions" in link.get("title", "").lower():
                    version_info = {
                        "version": link.get("title", ""),
                        "url": link.get("href", ""),
                        "date": entry.get("updated", "")
                    }
                    versions.append(version_info)

            # If no version links found, create single version
            if not versions:
                versions = [{
                    "version": "v1",
                    "url": f"{self.ARXIV_ABS_URL}{paper_id}",
                    "date": entry.get("published", "")
                }]

            logger.info(f"Found {len(versions)} versions for {paper_id}")
            return versions

        except Exception as e:
            logger.error(f"Error fetching versions: {e}")
            return []

    def estimate_reading_time(self, abstract: str, page_count: Optional[int] = None) -> Dict[str, Any]:
        """
        Estimate reading time for a paper

        Args:
            abstract: Paper abstract text
            page_count: Optional page count

        Returns:
            Dictionary with reading time estimates
        """
        # Average reading speed: 250-300 words per minute for academic papers
        words_per_minute = 200  # Conservative estimate for technical papers

        # Count words in abstract
        word_count = len(abstract.split())

        # Estimate abstract reading time
        abstract_minutes = max(1, word_count // words_per_minute)

        # Estimate full paper reading time
        if page_count:
            # Assume 2-3 minutes per page for deep reading
            paper_minutes = page_count * 2.5
        else:
            # Estimate from abstract length (full paper is typically 10-20x abstract)
            paper_minutes = abstract_minutes * 15

        # Format results
        return {
            "abstract_minutes": abstract_minutes,
            "paper_minutes": int(paper_minutes),
            "paper_hours": round(paper_minutes / 60, 1),
            "word_count": word_count
        }

    def assess_difficulty_level(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess the difficulty level of a paper

        Args:
            metadata: Paper metadata

        Returns:
            Dictionary with difficulty assessment
        """
        # Factors to consider
        factors = []

        # 1. Category-based difficulty
        category = metadata.get("primary_category", "")
        if category.startswith("cs.AI") or category.startswith("cs.LG"):
            difficulty = 3
            factors.append("AI/ML papers require mathematical background")
        elif category.startswith("cs.CR") or category.startswith("cs.DB"):
            difficulty = 2
            factors.append("Security/Database papers require domain knowledge")
        else:
            difficulty = 1

        # 2. Author count (more authors might indicate complex collaboration)
        author_count = len(metadata.get("authors", []))
        if author_count > 5:
            difficulty += 1
            factors.append(f"Large collaboration ({author_count} authors)")

        # 3. Abstract length (longer abstracts might indicate more complex work)
        abstract_length = len(metadata.get("summary", ""))
        if abstract_length > 2000:
            difficulty += 1
            factors.append("Comprehensive abstract suggests complex contribution")

        # 4. Category complexity
        categories = metadata.get("categories", [])
        if len(categories) > 3:
            difficulty += 1
            factors.append("Interdisciplinary work spans multiple fields")

        # Normalize difficulty to 1-5 scale
        difficulty = min(5, max(1, difficulty))

        # Determine difficulty label
        labels = {
            1: "Beginner Friendly",
            2: "Intermediate",
            3: "Advanced",
            4: "Expert Level",
            5: "Research Level"
        }

        return {
            "level": difficulty,
            "label": labels.get(difficulty, "Unknown"),
            "factors": factors
        }

    def extract_key_contributions(self, metadata: Dict[str, Any]) -> List[str]:
        """
        Extract key contributions from paper metadata

        Args:
            metadata: Paper metadata

        Returns:
            List of key contributions
        """
        contributions = []

        # Extract from abstract
        abstract = metadata.get("summary", "")

        # Look for contribution indicators
        contribution_patterns = [
            r"(?:We propose|Our approach|This paper presents?) ([^.]*\.)",
            r"(?:contribution|contribution)[^.]*\.",
            r"(?:main [^.]*?) (?:is|are) ([^.]*\.)",
        ]

        for pattern in contribution_patterns:
            matches = re.finditer(pattern, abstract, re.IGNORECASE)
            for match in matches:
                contribution = match.group(0).strip()
                if len(contribution) > 20 and len(contribution) < 200:
                    contributions.append(contribution)

        # If no contributions found, use first few sentences
        if not contributions:
            sentences = abstract.split(". ")
            contributions = sentences[:3]

        return contributions[:5]  # Return top 5

    def analyze_paper(self, paper_id: str, use_zhipu_ai: bool = False) -> Dict[str, Any]:
        """
        Perform complete analysis of an arXiv paper

        Args:
            paper_id: arXiv paper ID
            use_zhipu_ai: Whether to use Zhipu AI for enhanced analysis

        Returns:
            Complete paper analysis
        """
        try:
            logger.info(f"Analyzing paper {paper_id}")

            # Fetch metadata
            metadata = self.fetch_paper_metadata(paper_id)

            # Extract basic information
            abstract = metadata.get("summary", "")

            # Estimate reading time
            reading_time = self.estimate_reading_time(abstract)

            # Assess difficulty
            difficulty = self.assess_difficulty_level(metadata)

            # Extract contributions
            contributions = self.extract_key_contributions(metadata)

            # Build response
            analysis = {
                "paper_id": paper_id,
                "metadata": {
                    "title": metadata.get("title"),
                    "authors": metadata.get("authors"),
                    "published": metadata.get("published"),
                    "categories": metadata.get("categories"),
                    "primary_category": metadata.get("primary_category"),
                    "pdf_url": metadata.get("pdf_url"),
                    "abs_url": metadata.get("abs_url")
                },
                "content": {
                    "abstract": abstract,
                    "key_contributions": contributions,
                    "reading_time": reading_time,
                    "difficulty": difficulty
                },
                "ai_enhanced": False
            }

            # Optionally use Zhipu AI for enhanced analysis
            if use_zhipu_ai and self.zhipu_api_key:
                try:
                    enhanced = self._analyze_with_zhipu_ai(metadata)
                    analysis["content"].update(enhanced)
                    analysis["ai_enhanced"] = True
                except Exception as e:
                    logger.warning(f"Zhipu AI analysis failed: {e}")

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing paper: {e}")
            raise

    def _analyze_with_zhipu_ai(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Zhipu AI for enhanced paper analysis

        Args:
            metadata: Paper metadata

        Returns:
            Enhanced analysis results
        """
        if not self.zhipu_api_key:
            raise ValueError("Zhipu API key not configured")

        # Prepare prompt
        prompt = f"""
Analyze the following academic paper and provide:

1. **Core Problem**: What problem does this paper address?
2. **Key Innovation**: What is the main novelty?
3. **Methodology**: Briefly describe the approach
4. **Results**: What are the key findings?
5. **Prerequisites**: What background knowledge is needed?

**Paper Title**: {metadata.get('title')}

**Abstract**: {metadata.get('summary')}

Please provide a concise analysis in JSON format:
{{
  "core_problem": "...",
  "key_innovation": "...",
  "methodology": "...",
  "results": "...",
  "prerequisites": ["...", "..."]
}}
"""

        try:
            response = requests.post(
                self.ZHIPU_API_URL,
                headers={
                    "Authorization": f"Bearer {self.zhipu_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "glm-4-flash",  # Free model
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3
                },
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            content = result["choices"][0]["message"]["content"]

            # Try to parse JSON response
            import json
            try:
                enhanced = json.loads(content)
                return enhanced
            except json.JSONDecodeError:
                # If AI didn't return valid JSON, return as text
                return {"ai_analysis": content}

        except requests.RequestException as e:
            logger.error(f"Zhipu AI request failed: {e}")
            raise


# Convenience function for quick usage
def analyze_paper(paper_id: str, zhipu_api_key: Optional[str] = None,
                 use_ai: bool = False) -> Dict[str, Any]:
    """
    Convenience function to analyze a paper

    Args:
        paper_id: arXiv paper ID
        zhipu_api_key: Optional Zhipu AI API key
        use_ai: Whether to use AI for enhanced analysis

    Returns:
        Paper analysis dictionary
    """
    reader = ArxivReader(zhipu_api_key=zhipu_api_key)
    return reader.analyze_paper(paper_id, use_zhipu_ai=use_ai)
