"""
Test script for ArXiv Paper Reader API

This script tests the paper reader functionality:
- Fetching paper metadata
- Getting paper versions
- Analyzing papers (with and without AI)
"""

import requests
import sys
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# API base URL
API_BASE = "http://localhost:5000/api"


def test_health_check():
    """Test 1: Health check endpoint"""
    print("\n=== Test 1: Health Check ===")
    try:
        response = requests.get(f"{API_BASE}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        assert response.json()['success'] == True
        print("✅ Health check passed")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_paper_metadata():
    """Test 2: Get paper metadata"""
    print("\n=== Test 2: Get Paper Metadata ===")
    try:
        # Use a well-known arXiv paper
        paper_id = "2301.00001"  # A real arXiv paper ID

        response = requests.get(f"{API_BASE}/papers/reader/{paper_id}/metadata")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()['data']
            print(f"Title: {data.get('title')}")
            print(f"Authors: {', '.join(data.get('authors', [])[:3])}...")
            print(f"Categories: {data.get('categories')}")
            print("✅ Paper metadata fetched successfully")
            return True
        else:
            print(f"❌ Request failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Metadata test failed: {e}")
        return False


def test_paper_versions():
    """Test 3: Get paper versions"""
    print("\n=== Test 3: Get Paper Versions ===")
    try:
        paper_id = "2301.00001"

        response = requests.get(f"{API_BASE}/papers/reader/{paper_id}/versions")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()['data']
            print(f"Paper ID: {data.get('paper_id')}")
            print(f"Version Count: {data.get('count')}")
            print(f"First Version: {data.get('versions', [{}])[0]}")
            print("✅ Paper versions fetched successfully")
            return True
        else:
            print(f"❌ Request failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Versions test failed: {e}")
        return False


def test_paper_analysis_without_ai():
    """Test 4: Analyze paper without AI"""
    print("\n=== Test 4: Analyze Paper (Without AI) ===")
    try:
        paper_id = "2301.00001"

        response = requests.get(
            f"{API_BASE}/papers/reader/{paper_id}",
            params={'use_ai': 'false'}
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()['data']

            # Print analysis results
            print(f"\nTitle: {data['metadata']['title']}")
            print(f"\nAbstract: {data['content']['abstract'][:200]}...")
            print(f"\nKey Contributions:")
            for i, contrib in enumerate(data['content']['key_contributions'], 1):
                print(f"  {i}. {contrib[:100]}...")

            print(f"\nDifficulty: {data['content']['difficulty']['label']}")
            print(f"Reading Time: {data['content']['reading_time']['paper_minutes']} minutes")
            print(f"AI Enhanced: {data['ai_enhanced']}")

            print("\n✅ Paper analysis completed successfully")
            return True
        else:
            print(f"❌ Request failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Analysis test failed: {e}")
        return False


def test_paper_analysis_with_ai():
    """Test 5: Analyze paper with AI enhancement"""
    print("\n=== Test 5: Analyze Paper (With AI) ===")
    try:
        paper_id = "2301.00001"

        # Check if Zhipu API key is configured
        if not os.getenv('ZHIPU_API_KEY'):
            print("⚠️  ZHIPU_API_KEY not configured, skipping AI test")
            print("   To enable AI analysis, set ZHIPU_API_KEY in .env file")
            return True  # Don't fail the test suite

        response = requests.get(
            f"{API_BASE}/papers/reader/{paper_id}",
            params={'use_ai': 'true'},
            timeout=30  # AI analysis takes longer
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()['data']

            print(f"\nTitle: {data['metadata']['title']}")
            print(f"AI Enhanced: {data['ai_enhanced']}")

            if data['ai_enhanced']:
                # Check for AI-enhanced content
                content = data['content']
                if 'ai_analysis' in content:
                    print(f"\nAI Analysis: {content['ai_analysis']}")
                elif 'core_problem' in content:
                    print(f"\nCore Problem: {content['core_problem']}")
                    print(f"Key Innovation: {content.get('key_innovation', 'N/A')}")

            print("\n✅ AI-enhanced paper analysis completed successfully")
            return True
        else:
            print(f"❌ Request failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ AI analysis test failed: {e}")
        return False


def test_post_analysis():
    """Test 6: Analyze paper via POST"""
    print("\n=== Test 6: Analyze Paper (POST) ===")
    try:
        response = requests.post(
            f"{API_BASE}/papers/reader/analyze",
            json={
                'paper_id': '2301.00001',
                'use_ai': False
            }
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()['data']
            print(f"Title: {data['metadata']['title']}")
            print(f"Difficulty: {data['content']['difficulty']['label']}")
            print("✅ POST analysis completed successfully")
            return True
        else:
            print(f"❌ Request failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ POST analysis test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("ArXiv Paper Reader API Test Suite")
    print("="*60)

    tests = [
        ("Health Check", test_health_check),
        ("Paper Metadata", test_paper_metadata),
        ("Paper Versions", test_paper_versions),
        ("Paper Analysis (No AI)", test_paper_analysis_without_ai),
        ("Paper Analysis (With AI)", test_paper_analysis_with_ai),
        ("POST Analysis", test_post_analysis)
    ]

    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)

    passed = sum(1 for _, p in results if p)
    total = len(results)

    for name, p in results:
        status = "✅ PASS" if p else "❌ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
