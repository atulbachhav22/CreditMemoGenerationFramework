"""
Test script for API Context feature.

Tests:
1. Parsing of API Context sections in skill markdown
2. ApiCaller HTTP requests against a public API
3. JSONPath extraction
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from skill_engine.parser.markdown_parser import SkillMarkdownParser
from skill_engine.utils.api_caller import ApiCaller, ApiCallError
from skill_engine.models.skill import ApiContextDefinition, HttpMethod
from skill_engine.models.luggage import SkillLuggage


def test_parsing():
    """Test parsing of API context sections."""
    print("=" * 60)
    print("TEST 1: Parsing API Context from Markdown")
    print("=" * 60)

    parser = SkillMarkdownParser()
    skill = parser.parse_file("skills/api_context_example.md")

    print(f"\nSkill: {skill.metadata.name}")
    print(f"Total Steps: {skill.get_total_steps()}")

    # Check global API context
    print(f"\nGlobal API Context ({len(skill.global_api_context)} definitions):")
    for api_def in skill.global_api_context:
        print(f"  - Alias: {api_def.alias}")
        print(f"    Endpoint: {api_def.endpoint}")
        print(f"    Method: {api_def.method.value}")
        if api_def.query_params:
            print(f"    Query Params: {api_def.query_params}")
        if api_def.extract:
            print(f"    Extract: {api_def.extract}")
        if api_def.description:
            print(f"    Description: {api_def.description}")
        print()

    # Check step-level API context
    print("Step-level API Context:")
    for step in skill.steps:
        if step.api_context:
            print(f"  Step {step.step_number} ({step.name}):")
            for api_def in step.api_context:
                print(f"    - Alias: {api_def.alias}")
                print(f"      Endpoint: {api_def.endpoint}")
                print(f"      Method: {api_def.method.value}")
                if api_def.query_params:
                    print(f"      Query Params: {api_def.query_params}")
                if api_def.extract:
                    print(f"      Extract: {api_def.extract}")
                print()
        else:
            print(f"  Step {step.step_number} ({step.name}): No API context")

    # Assertions
    assert len(skill.global_api_context) == 2, f"Expected 2 global APIs, got {len(skill.global_api_context)}"
    assert skill.global_api_context[0].alias == "user_profile"
    assert skill.global_api_context[1].alias == "user_posts"
    assert skill.global_api_context[1].query_params == "userId=1"

    # Step 3 should have step-level API context
    step3 = skill.get_step(3)
    assert step3 is not None
    assert len(step3.api_context) == 1
    assert step3.api_context[0].alias == "sample_comment"
    assert step3.api_context[0].extract == "$.0"

    print("[SUCCESS] Parsing test passed!")
    return True


def test_api_caller():
    """Test ApiCaller with a public API."""
    print("\n" + "=" * 60)
    print("TEST 2: ApiCaller HTTP Requests")
    print("=" * 60)

    caller = ApiCaller()

    # Test 1: Simple GET
    print("\n--- Test GET request ---")
    api_def = ApiContextDefinition(
        alias="test_post",
        endpoint="https://jsonplaceholder.typicode.com/posts/1",
        method=HttpMethod.GET,
    )
    result = caller.call_api(api_def)
    print(f"Response type: {type(result).__name__}")
    print(f"Post title: {result.get('title', 'N/A')}")
    assert isinstance(result, dict)
    assert "title" in result
    print("[SUCCESS] GET request passed!")

    # Test 2: GET with query params
    print("\n--- Test GET with query params ---")
    api_def = ApiContextDefinition(
        alias="test_comments",
        endpoint="https://jsonplaceholder.typicode.com/comments",
        method=HttpMethod.GET,
        query_params="postId=1",
    )
    result = caller.call_api(api_def)
    print(f"Response type: {type(result).__name__}")
    print(f"Number of comments: {len(result)}")
    assert isinstance(result, list)
    assert len(result) > 0
    print("[SUCCESS] GET with query params passed!")

    # Test 3: JSONPath extraction
    print("\n--- Test JSONPath extraction ---")
    api_def = ApiContextDefinition(
        alias="test_extract",
        endpoint="https://jsonplaceholder.typicode.com/users/1",
        method=HttpMethod.GET,
        extract="$.address.city",
    )
    result = caller.call_api(api_def)
    print(f"Extracted city: {result}")
    assert isinstance(result, str)
    print("[SUCCESS] JSONPath extraction passed!")

    # Test 4: POST request
    print("\n--- Test POST request ---")
    api_def = ApiContextDefinition(
        alias="test_create",
        endpoint="https://jsonplaceholder.typicode.com/posts",
        method=HttpMethod.POST,
        body='{"title": "test", "body": "test body", "userId": 1}',
    )
    result = caller.call_api(api_def)
    print(f"Created post ID: {result.get('id', 'N/A')}")
    assert isinstance(result, dict)
    assert "id" in result
    print("[SUCCESS] POST request passed!")

    # Test 5: Error handling
    print("\n--- Test error handling ---")
    api_def = ApiContextDefinition(
        alias="test_error",
        endpoint="https://jsonplaceholder.typicode.com/nonexistent/999999",
        method=HttpMethod.GET,
    )
    try:
        caller.call_api(api_def)
        print("[WARNING] Expected an error but none raised")
    except ApiCallError as e:
        print(f"Caught expected error: {e}")
        print(f"  Alias: {e.alias}")
        print(f"  Status code: {e.status_code}")
        print("[SUCCESS] Error handling passed!")

    return True


def test_luggage_integration():
    """Test that API responses are properly stored and summarized in luggage."""
    print("\n" + "=" * 60)
    print("TEST 3: Luggage Integration")
    print("=" * 60)

    luggage = SkillLuggage(skill_name="Test Skill")

    # Store API responses
    luggage.store_api_response("user_data", {"name": "John", "email": "john@example.com"})
    luggage.store_api_response("posts", [{"id": 1, "title": "Hello"}, {"id": 2, "title": "World"}])

    # Retrieve
    user = luggage.get_api_response("user_data")
    assert user["name"] == "John"
    print(f"Retrieved user: {user}")

    posts = luggage.get_api_response("posts")
    assert len(posts) == 2
    print(f"Retrieved {len(posts)} posts")

    # Check context summary includes API data
    summary = luggage.get_context_summary()
    assert "API Context Data" in summary
    assert "user_data" in summary
    assert "posts" in summary
    print(f"\nContext summary includes API data: [SUCCESS]")
    print(f"Summary length: {len(summary)} chars")

    # Test missing alias
    missing = luggage.get_api_response("nonexistent")
    assert missing is None
    print("Missing alias returns None: [SUCCESS]")

    print("\n[SUCCESS] Luggage integration test passed!")
    return True


if __name__ == "__main__":
    print("SkillEngine API Context Feature Tests")
    print("=" * 60)

    all_passed = True

    try:
        all_passed = test_parsing() and all_passed
    except Exception as e:
        print(f"\n[ERROR] Parsing test failed: {e}")
        all_passed = False

    try:
        all_passed = test_api_caller() and all_passed
    except Exception as e:
        print(f"\n[ERROR] API caller test failed: {e}")
        all_passed = False

    try:
        all_passed = test_luggage_integration() and all_passed
    except Exception as e:
        print(f"\n[ERROR] Luggage integration test failed: {e}")
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] All tests passed!")
    else:
        print("[ERROR] Some tests failed!")
    print("=" * 60)
