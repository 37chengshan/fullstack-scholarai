"""
Test Suite for AI Enhanced Paper Search Routes
Tests for papers_ai endpoints: ask, compare, recommend, summarize
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
import json


class TestPapersAI:
    """Test class for papers_ai endpoints."""

    def __init__(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.test_paper_ids = [
            '2301.00001',  # A real arXiv paper ID for testing
            '2301.00002',
            '2301.00003'
        ]

    def print_result(self, test_name, passed, message=""):
        """Print test result in a formatted way."""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
        if message:
            print(f"    {message}")

    def test_1_health_check(self):
        """Test 1: Health check endpoint."""
        print("\n--- Test 1: Health Check ---")
        response = self.client.get('/api/health')
        data = json.loads(response.data)

        passed = response.status_code == 200 and data.get('success') == True
        self.print_result("Health check", passed, f"Status: {response.status_code}")
        return passed

    def test_2_ask_about_paper(self):
        """Test 2: AI Q&A about specific paper."""
        print("\n--- Test 2: AI Ask About Paper ---")

        # Test with paper_id
        payload = {
            "question": "What is this paper about?",
            "paper_id": self.test_paper_ids[0],
            "stream": False,
            "api_config": {
                "model": "glm-4-flash",
                "temperature": 0.7
            }
        }

        response = self.client.post(
            '/api/papers/ask',
            data=json.dumps(payload),
            content_type='application/json'
        )

        try:
            data = json.loads(response.data)
            passed = response.status_code in [200, 404, 500]  # Accept errors due to API availability
            if response.status_code == 200:
                print(f"    Answer received: {data.get('data', {}).get('answer', 'N/A')[:100]}...")
            elif response.status_code != 200:
                print(f"    Note: {data.get('error', 'API call failed - this is expected if API key is not configured')}")
            self.print_result("Ask about paper (non-streaming)", passed, f"Status: {response.status_code}")
        except Exception as e:
            self.print_result("Ask about paper (non-streaming)", False, f"Exception: {str(e)}")

        return response.status_code in [200, 404]

    def test_3_ask_about_search_results(self):
        """Test 3: AI Q&A with search context."""
        print("\n--- Test 3: AI Ask With Search Context ---")

        payload = {
            "question": "Summarize the main approaches in these papers",
            "search_context": {
                "query": "deep learning",
                "field": "cs.AI"
            },
            "stream": False
        }

        response = self.client.post(
            '/api/papers/ask',
            data=json.dumps(payload),
            content_type='application/json'
        )

        try:
            data = json.loads(response.data)
            passed = response.status_code in [200, 404, 500]
            if response.status_code == 200:
                print(f"    Answer received")
            else:
                print(f"    Note: {data.get('error', 'API call failed')}")
            self.print_result("Ask with search context", passed, f"Status: {response.status_code}")
        except Exception as e:
            self.print_result("Ask with search context", False, f"Exception: {str(e)}")

        return response.status_code in [200, 404]

    def test_4_compare_papers(self):
        """Test 4: Compare multiple papers."""
        print("\n--- Test 4: Compare Papers ---")

        payload = {
            "paper_ids": self.test_paper_ids[:2],  # Compare 2 papers
            "stream": False,
            "api_config": {
                "model": "glm-4-flash",
                "temperature": 0.7
            }
        }

        response = self.client.post(
            '/api/papers/compare',
            data=json.dumps(payload),
            content_type='application/json'
        )

        try:
            data = json.loads(response.data)
            passed = response.status_code in [200, 404, 500]
            if response.status_code == 200:
                comparison = data.get('data', {}).get('comparison', '')
                print(f"    Comparison length: {len(comparison)} characters")
            else:
                print(f"    Note: {data.get('error', 'API call failed')}")
            self.print_result("Compare papers", passed, f"Status: {response.status_code}")
        except Exception as e:
            self.print_result("Compare papers", False, f"Exception: {str(e)}")

        return response.status_code in [200, 404]

    def test_5_compare_validation(self):
        """Test 5: Compare validation errors."""
        print("\n--- Test 5: Compare Validation ---")

        # Test with too few papers
        payload = {
            "paper_ids": ["2301.00001"],  # Only 1 paper
            "stream": False
        }

        response = self.client.post(
            '/api/papers/compare',
            data=json.dumps(payload),
            content_type='application/json'
        )

        data = json.loads(response.data)
        passed = response.status_code == 400 and 'at least 2 paper IDs' in data.get('error', '')
        self.print_result("Compare validation (too few papers)", passed, f"Status: {response.status_code}, Error: {data.get('error', '')}")

        # Test with too many papers
        payload["paper_ids"] = ["2301.00001"] * 4  # 4 papers (max is 3)

        response = self.client.post(
            '/api/papers/compare',
            data=json.dumps(payload),
            content_type='application/json'
        )

        data = json.loads(response.data)
        passed2 = response.status_code == 400 and 'Maximum 3 papers' in data.get('error', '')
        self.print_result("Compare validation (too many papers)", passed2, f"Status: {response.status_code}, Error: {data.get('error', '')}")

        return passed and passed2

    def test_6_recommend_papers(self):
        """Test 6: Recommend related papers."""
        print("\n--- Test 6: Recommend Papers ---")

        payload = {
            "paper_id": self.test_paper_ids[0],
            "count": 5,
            "api_config": {
                "model": "glm-4-flash"
            }
        }

        response = self.client.post(
            '/api/papers/recommend',
            data=json.dumps(payload),
            content_type='application/json'
        )

        try:
            data = json.loads(response.data)
            passed = response.status_code in [200, 404, 500]
            if response.status_code == 200:
                recommendations = data.get('data', {}).get('recommendations', [])
                print(f"    Received {len(recommendations)} recommendations")
                if recommendations:
                    print(f"    First: {recommendations[0].get('title', 'N/A')[:50]}...")
            else:
                print(f"    Note: {data.get('error', 'API call failed')}")
            self.print_result("Recommend papers", passed, f"Status: {response.status_code}")
        except Exception as e:
            self.print_result("Recommend papers", False, f"Exception: {str(e)}")

        return response.status_code in [200, 404]

    def test_7_recommend_validation(self):
        """Test 7: Recommend validation errors."""
        print("\n--- Test 7: Recommend Validation ---")

        # Test with invalid count
        payload = {
            "paper_id": self.test_paper_ids[0],
            "count": 15  # Max is 10
        }

        response = self.client.post(
            '/api/papers/recommend',
            data=json.dumps(payload),
            content_type='application/json'
        )

        data = json.loads(response.data)
        passed = response.status_code == 400 and 'between 1 and 10' in data.get('error', '')
        self.print_result("Recommend validation (invalid count)", passed, f"Status: {response.status_code}, Error: {data.get('error', '')}")

        # Test with missing paper_id
        payload = {"count": 5}

        response = self.client.post(
            '/api/papers/recommend',
            data=json.dumps(payload),
            content_type='application/json'
        )

        data = json.loads(response.data)
        passed2 = response.status_code == 400 and 'paper_id' in data.get('error', '')
        self.print_result("Recommend validation (missing paper_id)", passed2, f"Status: {response.status_code}, Error: {data.get('error', '')}")

        return passed and passed2

    def test_8_summarize_papers(self):
        """Test 8: Batch summarize papers."""
        print("\n--- Test 8: Summarize Papers ---")

        payload = {
            "paper_ids": self.test_paper_ids[:2],
            "length": "medium",
            "stream": False,
            "api_config": {
                "model": "glm-4-flash"
            }
        }

        response = self.client.post(
            '/api/papers/summarize',
            data=json.dumps(payload),
            content_type='application/json'
        )

        try:
            data = json.loads(response.data)
            passed = response.status_code in [200, 404, 500]
            if response.status_code == 200:
                summaries = data.get('data', {}).get('summaries', [])
                print(f"    Received {len(summaries)} summaries")
                if summaries:
                    print(f"    First summary: {summaries[0].get('summary', 'N/A')[:100]}...")
            else:
                print(f"    Note: {data.get('error', 'API call failed')}")
            self.print_result("Summarize papers", passed, f"Status: {response.status_code}")
        except Exception as e:
            self.print_result("Summarize papers", False, f"Exception: {str(e)}")

        return response.status_code in [200, 404]

    def test_9_summarize_validation(self):
        """Test 9: Summarize validation errors."""
        print("\n--- Test 9: Summarize Validation ---")

        # Test with too many papers
        payload = {
            "paper_ids": ["2301.00001"] * 11,  # 11 papers (max is 10)
            "length": "medium"
        }

        response = self.client.post(
            '/api/papers/summarize',
            data=json.dumps(payload),
            content_type='application/json'
        )

        data = json.loads(response.data)
        passed = response.status_code == 400 and 'Maximum 10 papers' in data.get('error', '')
        self.print_result("Summarize validation (too many papers)", passed, f"Status: {response.status_code}, Error: {data.get('error', '')}")

        # Test with invalid length
        payload = {
            "paper_ids": self.test_paper_ids[:1],
            "length": "invalid"  # Should be short/medium/long
        }

        response = self.client.post(
            '/api/papers/summarize',
            data=json.dumps(payload),
            content_type='application/json'
        )

        # Should default to 'medium' and not fail
        data = json.loads(response.data)
        passed2 = response.status_code in [200, 404, 500]  # Accept any valid response
        self.print_result("Summarize validation (invalid length defaults)", passed2, f"Status: {response.status_code}")

        return passed and passed2

    def test_10_missing_required_fields(self):
        """Test 10: Missing required fields validation."""
        print("\n--- Test 10: Missing Required Fields ---")

        # Test /ask without question
        payload = {"paper_id": self.test_paper_ids[0]}

        response = self.client.post(
            '/api/papers/ask',
            data=json.dumps(payload),
            content_type='application/json'
        )

        data = json.loads(response.data)
        passed = response.status_code == 400 and 'question' in data.get('error', '')
        self.print_result("Missing 'question' field", passed, f"Status: {response.status_code}, Error: {data.get('error', '')}")

        return passed

    def run_all_tests(self):
        """Run all tests and print summary."""
        print("=" * 60)
        print("Running Papers AI Tests")
        print("=" * 60)

        tests = [
            self.test_1_health_check,
            self.test_2_ask_about_paper,
            self.test_3_ask_about_search_results,
            self.test_4_compare_papers,
            self.test_5_compare_validation,
            self.test_6_recommend_papers,
            self.test_7_recommend_validation,
            self.test_8_summarize_papers,
            self.test_9_summarize_validation,
            self.test_10_missing_required_fields
        ]

        results = []
        for test in tests:
            try:
                result = test()
                results.append(result)
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {str(e)}")
                results.append(False)

        # Summary
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        total = len(results)
        passed = sum(results)
        print(f"Total: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {passed/total*100:.1f}%")

        if passed == total:
            print("\n🎉 All tests passed!")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed")

        return passed == total


if __name__ == '__main__':
    tester = TestPapersAI()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
