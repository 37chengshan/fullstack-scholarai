"""
AI Enhanced Paper Search Routes
Provides intelligent features on top of arXiv search results:
- AI Q&A about papers
- Paper comparison
- Related paper recommendations
- Batch summary generation
"""

from flask import Blueprint, request, jsonify, Response, stream_with_context
from services.arxiv_client import ArxivClient
from services.zhipu_client import ZhipuClient
import json

papers_ai_bp = Blueprint('papers_ai', __name__, url_prefix='/api/papers-ai')


def get_papers_context(paper_ids: list) -> str:
    """Build context string from paper IDs for AI prompts."""
    client = ArxivClient()
    papers_data = []

    for paper_id in paper_ids:
        try:
            paper = client.get_paper_details(paper_id)
            if paper:
                papers_data.append(f"""
Paper ID: {paper.get('id', 'N/A')}
Title: {paper.get('title', 'N/A')}
Authors: {', '.join(paper.get('authors', []))}
Abstract: {paper.get('abstract', 'N/A')}
Published: {paper.get('published', 'N/A')}
Categories: {', '.join(paper.get('categories', []))}
""")
        except Exception as e:
            continue

    return '\n\n'.join(papers_data)


@papers_ai_bp.route('/ask', methods=['POST'])
def ask_about_papers():
    """
    AI Q&A about papers or search results.

    Request body:
    {
        "question": "What are the main differences between these approaches?",
        "paper_id": "2301.00001",  // Optional: ask about specific paper
        "search_context": {         // Optional: ask about search results
            "query": "deep learning",
            "field": "cs.AI"
        },
        "stream": false,            // Optional: enable SSE streaming
        "api_config": {             // Optional: custom API config
            "api_key": "...",
            "model": "glm-4-flash",
            "temperature": 0.7
        }
    }

    Response:
    {
        "success": true,
        "data": {
            "answer": "Based on the papers...",
            "papers_referenced": ["2301.00001", "2301.00002"]
        }
    }
    """
    try:
        data = request.get_json()

        # Validate required fields
        if not data or 'question' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: question'
            }), 400

        question = data['question']
        paper_id = data.get('paper_id')
        search_context = data.get('search_context')
        stream = data.get('stream', False)
        api_config = data.get('api_config', {})

        # Get API configuration
        api_key = api_config.get('api_key')
        model = api_config.get('model', 'glm-4-flash')
        temperature = api_config.get('temperature', 0.7)

        # Initialize AI client
        ai_client = ZhipuClient(api_key=api_key)

        # Build context
        context_parts = ["You are a helpful research assistant."]

        if paper_id:
            # Get specific paper details
            arxiv_client = ArxivClient()
            try:
                paper = arxiv_client.get_paper_details(paper_id)
                if paper:
                    context_parts.append(f"""
Focus on this paper:
Title: {paper.get('title', 'N/A')}
Authors: {', '.join(paper.get('authors', []))}
Abstract: {paper.get('abstract', 'N/A')}
""")
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Failed to fetch paper: {str(e)}'
                }), 404

        elif search_context:
            # Perform search and include top results
            arxiv_client = ArxivClient()
            try:
                search_results = arxiv_client.search_papers(
                    query=search_context.get('query', ''),
                    field=search_context.get('field'),
                    year_min=search_context.get('year_min'),
                    year_max=search_context.get('year_max'),
                    venue=search_context.get('venue'),
                    page=1,
                    page_size=5
                )
                papers = search_results.get('papers', [])
                context_parts.append("Consider these search results:")
                for paper in papers[:5]:
                    context_parts.append(f"""
- {paper.get('title', 'N/A')} ({paper.get('id', 'N/A')})
  Abstract: {paper.get('abstract', 'N/A')[:200]}...
""")
            except Exception as e:
                context_parts.append(f"Note: Could not fetch search results: {str(e)}")

        context_parts.append(f"\nUser question: {question}")
        context = '\n'.join(context_parts)

        if stream:
            # Streaming response
            def generate():
                try:
                    for chunk in ai_client.chat_completion_stream(
                        messages=[{"role": "user", "content": context}],
                        temperature=temperature,
                        top_p=0.9,
                        max_tokens=2000
                    ):
                        if chunk:
                            yield f"data: {json.dumps({'content': chunk})}\n\n"
                    yield "data: [DONE]\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"

            return Response(
                stream_with_context(generate()),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'X-Accel-Buffering': 'no'
                }
            )
        else:
            # Non-streaming response
            response = ai_client.chat_completion(
                messages=[{"role": "user", "content": context}],
                stream=False
            )

            if not response.get('success'):
                return jsonify({
                    'success': False,
                    'error': response.get('error', 'AI request failed')
                }), 500

            answer = response['data']['choices'][0]['message']['content']

            return jsonify({
                'success': True,
                'data': {
                    'answer': answer,
                    'papers_referenced': [paper_id] if paper_id else []
                }
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@papers_ai_bp.route('/compare', methods=['POST'])
def compare_papers():
    """
    Compare multiple papers (max 3).

    Request body:
    {
        "paper_ids": ["2301.00001", "2301.00002", "2301.00003"],
        "stream": false,            // Optional
        "api_config": { ... }       // Optional
    }

    Response:
    {
        "success": true,
        "data": {
            "comparison": "Detailed comparison text...",
            "table": {
                "headers": ["Paper", "Approach", "Dataset", "Results"],
                "rows": [...]
            }
        }
    }
    """
    try:
        data = request.get_json()

        if not data or 'paper_ids' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: paper_ids'
            }), 400

        paper_ids = data['paper_ids']

        if not isinstance(paper_ids, list) or len(paper_ids) < 2:
            return jsonify({
                'success': False,
                'error': 'Please provide at least 2 paper IDs to compare'
            }), 400

        if len(paper_ids) > 3:
            return jsonify({
                'success': False,
                'error': 'Maximum 3 papers can be compared at once'
            }), 400

        stream = data.get('stream', False)
        api_config = data.get('api_config', {})

        # Get papers context
        papers_context = get_papers_context(paper_ids)

        if not papers_context:
            return jsonify({
                'success': False,
                'error': 'Could not fetch paper details'
            }), 404

        # Build comparison prompt
        prompt = f"""You are a research assistant specializing in paper comparison.

Here are the papers to compare:

{papers_context}

Please provide:
1. A detailed comparison highlighting:
   - Key similarities and differences
   - Methodological approaches
   - Main contributions
   - Strengths and weaknesses of each
   - Potential use cases for each approach

2. A comparison table in JSON format with these columns:
   - Paper ID
   - Title
   - Main Approach
   - Key Innovation
   - Dataset (if mentioned)
   - Performance (if mentioned)

Format the table as a JSON object with "headers" and "rows" keys."""

        # Initialize AI client
        ai_client = ZhipuClient(api_key=api_config.get('api_key'))

        if stream:
            def generate():
                try:
                    for chunk in ai_client.chat_completion_stream(
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7,
                        top_p=0.9,
                        max_tokens=3000
                    ):
                        if chunk:
                            yield f"data: {json.dumps({'content': chunk})}\n\n"
                    yield "data: [DONE]\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"

            return Response(
                stream_with_context(generate()),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'X-Accel-Buffering': 'no'
                }
            )
        else:
            response = ai_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                stream=False
            )

            if not response.get('success'):
                return jsonify({
                    'success': False,
                    'error': response.get('error', 'AI request failed')
                }), 500

            comparison_text = response['data']['choices'][0]['message']['content']

            # Try to extract table from response
            table = None
            try:
                # Look for JSON table in response
                import re
                table_match = re.search(r'\{[\s\S]*"headers"[\s\S]*"rows"[\s\S]*\}', comparison_text)
                if table_match:
                    table = json.loads(table_match.group())
            except:
                pass

            return jsonify({
                'success': True,
                'data': {
                    'comparison': comparison_text,
                    'table': table
                }
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@papers_ai_bp.route('/recommend', methods=['POST'])
def recommend_papers():
    """
    Recommend related papers based on a given paper.

    Request body:
    {
        "paper_id": "2301.00001",
        "count": 5,                 // Optional, default 5
        "api_config": { ... }        // Optional
    }

    Response:
    {
        "success": true,
        "data": {
            "recommendations": [
                {
                    "paper_id": "2301.00002",
                    "title": "...",
                    "reason": "This paper builds upon..."
                }
            ]
        }
    }
    """
    try:
        data = request.get_json()

        if not data or 'paper_id' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: paper_id'
            }), 400

        paper_id = data['paper_id']
        count = data.get('count', 5)
        api_config = data.get('api_config', {})

        if count < 1 or count > 10:
            return jsonify({
                'success': False,
                'error': 'count must be between 1 and 10'
            }), 400

        # Get source paper details
        arxiv_client = ArxivClient()
        try:
            source_paper = arxiv_client.get_paper_details(paper_id)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to fetch paper: {str(e)}'
            }), 404

        if not source_paper:
            return jsonify({
                'success': False,
                'error': 'Paper not found'
            }), 404

        # Build prompt for recommendations
        prompt = f"""You are a research assistant specializing in academic paper recommendations.

Based on the following paper, suggest {count} related papers that researchers interested in this topic should read.

Source Paper:
Title: {source_paper.get('title', 'N/A')}
Authors: {', '.join(source_paper.get('authors', []))}
Abstract: {source_paper.get('abstract', 'N/A')}
Categories: {', '.join(source_paper.get('categories', []))}

For each recommendation, provide:
1. Paper ID (use arXiv ID format like 2301.00001)
2. Title (your best estimate if exact paper doesn't exist)
3. A brief reason why it's relevant

Return ONLY a JSON array of objects with this exact structure:
[
  {{
    "paper_id": "2301.00001",
    "title": "Paper Title",
    "reason": "Reason for recommendation..."
  }}
]

Focus on:
- Papers cited by this work
- Papers that cite this work
- Papers in the same field with similar approaches
- Seminal works in this area
- Recent advances on this topic"""

        # Initialize AI client
        ai_client = ZhipuClient(api_key=api_config.get('api_key'))

        response = ai_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            stream=False
        )

        if not response.get('success'):
            return jsonify({
                'success': False,
                'error': response.get('error', 'AI request failed')
            }), 500

        content = response['data']['choices'][0]['message']['content']

        # Parse recommendations
        try:
            # Try to extract JSON array
            import re
            json_match = re.search(r'\[[\s\S]*?\]', content)
            if json_match:
                recommendations = json.loads(json_match.group())
            else:
                recommendations = json.loads(content)

            # Validate structure
            if not isinstance(recommendations, list):
                raise ValueError('Response is not a list')

            for rec in recommendations:
                if not all(k in rec for k in ['paper_id', 'title', 'reason']):
                    raise ValueError('Missing required fields in recommendation')

        except Exception as e:
            # Fallback: create basic structure from AI text
            recommendations = []
            lines = content.split('\n')
            current_rec = {}
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if 'paper_id' in line.lower() or line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
                    if current_rec:
                        recommendations.append(current_rec)
                    current_rec = {'paper_id': 'N/A', 'title': 'See response text', 'reason': line}
                elif current_rec:
                    current_rec['reason'] = current_rec.get('reason', '') + ' ' + line

            if current_rec:
                recommendations.append(current_rec)

        return jsonify({
            'success': True,
            'data': {
                'recommendations': recommendations[:count]
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@papers_ai_bp.route('/summarize', methods=['POST'])
def summarize_papers():
    """
    Generate summaries for multiple papers in batch.

    Request body:
    {
        "paper_ids": ["2301.00001", "2301.00002"],
        "length": "medium",          // Optional: short, medium, long
        "stream": false,              // Optional
        "api_config": { ... }         // Optional
    }

    Response:
    {
        "success": true,
        "data": {
            "summaries": [
                {
                    "paper_id": "2301.00001",
                    "title": "...",
                    "summary": "...",
                    "key_points": ["...", "..."]
                }
            ]
        }
    }
    """
    try:
        data = request.get_json()

        if not data or 'paper_ids' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: paper_ids'
            }), 400

        paper_ids = data['paper_ids']
        length = data.get('length', 'medium')
        stream = data.get('stream', False)
        api_config = data.get('api_config', {})

        if not isinstance(paper_ids, list) or len(paper_ids) < 1:
            return jsonify({
                'success': False,
                'error': 'Please provide at least 1 paper ID'
            }), 400

        if len(paper_ids) > 10:
            return jsonify({
                'success': False,
                'error': 'Maximum 10 papers can be summarized at once'
            }), 400

        # Define length constraints
        length_guides = {
            'short': '100-150 words',
            'medium': '200-300 words',
            'long': '400-500 words'
        }

        if length not in length_guides:
            length = 'medium'

        # Get papers details
        arxiv_client = ArxivClient()
        papers_data = []
        for paper_id in paper_ids:
            try:
                paper = arxiv_client.get_paper_details(paper_id)
                if paper:
                    papers_data.append(paper)
            except Exception as e:
                continue

        if not papers_data:
            return jsonify({
                'success': False,
                'error': 'Could not fetch any paper details'
            }), 404

        # Initialize AI client
        ai_client = ZhipuClient(api_key=api_config.get('api_key'))

        if stream:
            # Streaming: provide one summary at a time
            def generate():
                for paper in papers_data:
                    try:
                        prompt = f"""Summarize this paper in {length_guides[length]}:

Title: {paper.get('title', 'N/A')}
Authors: {', '.join(paper.get('authors', []))}
Abstract: {paper.get('abstract', 'N/A')}

Provide:
1. A concise summary
2. 3-5 key bullet points

Format as:
**Summary**: [your summary]

**Key Points**:
- [point 1]
- [point 2]
..."""

                        for chunk in ai_client.chat_completion_stream(
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.7,
                            top_p=0.9,
                            max_tokens=1500
                        ):
                            if chunk:
                                yield f"data: {json.dumps({{'paper_id': paper.get('id'), 'content': chunk}})}\n\n"

                        yield f"data: {json.dumps({{'paper_id': paper.get('id'), 'done': True}})}\n\n"

                    except Exception as e:
                        yield f"data: {json.dumps({{'paper_id': paper.get('id'), 'error': str(e)}})}\n\n"

                yield "data: [DONE]\n\n"

            return Response(
                stream_with_context(generate()),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'X-Accel-Buffering': 'no'
                }
            )

        else:
            # Non-streaming: generate all summaries
            summaries = []

            for paper in papers_data:
                prompt = f"""Summarize this paper in {length_guides[length]}:

Title: {paper.get('title', 'N/A')}
Authors: {', '.join(paper.get('authors', []))}
Abstract: {paper.get('abstract', 'N/A')}

Provide:
1. A concise summary
2. 3-5 key bullet points

Return as JSON:
{{
  "summary": "summary text",
  "key_points": ["point 1", "point 2", "point 3"]
}}"""

                response = ai_client.chat_completion(
                    messages=[{"role": "user", "content": prompt}],
                    stream=False
                )

                if response.get('success'):
                    content = response['data']['choices'][0]['message']['content']
                    try:
                        # Try to parse JSON response
                        import re
                        json_match = re.search(r'\{[\s\S]*?\}', content)
                        if json_match:
                            summary_data = json.loads(json_match.group())
                        else:
                            summary_data = json.loads(content)

                        summary = summary_data.get('summary', content)
                        key_points = summary_data.get('key_points', [])
                    except:
                        summary = content
                        key_points = []

                    summaries.append({
                        'paper_id': paper.get('id'),
                        'title': paper.get('title'),
                        'summary': summary,
                        'key_points': key_points
                    })

            return jsonify({
                'success': True,
                'data': {
                    'summaries': summaries
                }
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
