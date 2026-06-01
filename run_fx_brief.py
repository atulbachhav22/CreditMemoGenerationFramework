#!/usr/bin/env python
"""
Run the FX Market Brief skill - demonstrates MCP integration with mcp-server-fetch.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")
sys.path.insert(0, str(Path(__file__).parent))

from skill_engine.processor.skill_processor import SkillProcessor

def main():
    provider = os.getenv("DEFAULT_LLM_PROVIDER", "anthropic")
    model    = os.getenv("DEFAULT_MODEL_NAME", "claude-haiku-4-5-20251001")
    api_key  = (
        os.getenv("ANTHROPIC_API_KEY") if provider == "anthropic"
        else os.getenv("OPENAI_API_KEY")
    )

    print(f"Provider : {provider}")
    print(f"Model    : {model}")
    print(f"Skill    : skills/fx_market_brief.md")
    print("-" * 60)

    processor = SkillProcessor(
        llm_provider=provider,
        model_name=model,
        api_key=api_key,
        base_path=str(Path(__file__).parent),
        verbose=True,
    )

    skill_path = str(Path(__file__).parent / "skills" / "fx_market_brief.md")
    luggage = processor.execute_skill_file(skill_path)

    print("\n" + "=" * 60)
    print("FINAL OUTPUT")
    print("=" * 60)
    final = processor.get_final_output(luggage)
    print(final)

    out_path = Path(__file__).parent / "output" / "fx_market_brief_result.md"
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(final, encoding="utf-8")
    print(f"\nSaved to: {out_path}")

if __name__ == "__main__":
    main()
