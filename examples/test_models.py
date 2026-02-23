"""
Test which Claude models are available with your API key.

This script tries different Claude model names to see which ones work.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()


def test_model(model_name: str, api_key: str) -> bool:
    """Test if a specific model works."""
    try:
        from langchain_anthropic import ChatAnthropic
        from langchain_core.messages import HumanMessage

        llm = ChatAnthropic(
            model=model_name,
            anthropic_api_key=api_key,
            temperature=0.0
        )

        # Try a simple test message
        response = llm.invoke([HumanMessage(content="Say 'OK' if you can read this.")])
        print(f"✅ {model_name:40} - WORKS")
        return True

    except Exception as e:
        error_msg = str(e)
        if "not_found_error" in error_msg or "404" in error_msg:
            print(f"❌ {model_name:40} - NOT AVAILABLE")
        elif "rate_limit" in error_msg:
            print(f"⚠️  {model_name:40} - RATE LIMITED (but exists)")
            return True
        else:
            print(f"❌ {model_name:40} - ERROR: {error_msg[:50]}")
        return False


def main():
    """Test all common Claude models."""
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        print("Error: ANTHROPIC_API_KEY not found in environment")
        print("Please set it in your .env file")
        return

    print("Testing Claude models with your API key...")
    print("=" * 80)
    print()

    # List of models to test (ordered by likelihood of working)
    models_to_test = [
        # Claude 3.5 Sonnet
        "claude-3-5-sonnet-20240620",
        "claude-3-5-sonnet-20241022",

        # Claude 3 Opus
        "claude-3-opus-20240229",

        # Claude 3 Sonnet
        "claude-3-sonnet-20240229",

        # Claude 3 Haiku
        "claude-3-haiku-20240307",

        # Older models (less likely)
        "claude-2.1",
        "claude-2.0",
        "claude-instant-1.2",
    ]

    working_models = []

    for model in models_to_test:
        if test_model(model, api_key):
            working_models.append(model)

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    if working_models:
        print(f"\n✅ Found {len(working_models)} working model(s):\n")
        for model in working_models:
            print(f"   - {model}")

        print(f"\n💡 Recommended: Use '{working_models[0]}' in your scripts")
        print(f"\nUpdate examples/run_credit_memo.py with:")
        print(f'   model_name="{working_models[0]}"')
    else:
        print("\n❌ No working models found!")
        print("\nPossible issues:")
        print("  1. API key is invalid")
        print("  2. Account doesn't have access to Claude API")
        print("  3. Network/firewall issues")
        print("\nCheck your API key at: https://console.anthropic.com/")


if __name__ == "__main__":
    main()
