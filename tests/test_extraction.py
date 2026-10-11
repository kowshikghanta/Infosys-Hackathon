"""Unit tests for prompt construction, markdown JSON stripping, and parser logic."""

import pytest
from src.extraction import (
    build_extraction_prompt,
    clean_and_parse_json_response,
    extract_structured_analysis,
)


def test_build_extraction_prompt():
    """Prompt builder should include title, date, notes, and strict rules."""
    sys_prompt, user_prompt = build_extraction_prompt(
        transcript="Rahul will finish the API integration by Friday.",
        meeting_title="Sprint 4 Review",
        meeting_date="2026-10-11",
    )
    assert "MeetingMind AI" in sys_prompt
    assert "Sprint 4 Review" in user_prompt
    assert "2026-10-11" in user_prompt
    assert "Rahul will finish the API integration by Friday." in user_prompt


def test_clean_and_parse_json_clean_raw():
    """Direct JSON string parsing."""
    raw = '{"summary": "Quick sync", "action_items": []}'
    parsed = clean_and_parse_json_response(raw)
    assert parsed["summary"] == "Quick sync"


def test_clean_and_parse_json_with_markdown_fences():
    """Markdown code fences (```json ... ```) should be stripped cleanly."""
    raw = """Here is the result:
```json
{
  "summary": "Meeting on Friday",
  "key_topics": ["Dev", "QA"],
  "action_items": []
}
```
Let me know if you need anything else!"""
    parsed = clean_and_parse_json_response(raw)
    assert parsed["summary"] == "Meeting on Friday"
    assert "Dev" in parsed["key_topics"]


def test_clean_and_parse_json_invalid_syntax():
    """Invalid JSON syntax must raise ValueError."""
    with pytest.raises(ValueError, match="Failed to parse LLM JSON"):
        clean_and_parse_json_response("{invalid_json: 123,")


def test_clean_and_parse_json_empty_text():
    """Empty string must raise ValueError."""
    with pytest.raises(ValueError, match="empty response"):
        clean_and_parse_json_response("   ")


def test_extract_structured_analysis_end_to_end():
    """End-to-end extraction from JSON string with deterministic enrichment."""
    raw_json = """
    {
      "summary": "Discussed dashboard rollout",
      "key_topics": ["Release"],
      "decisions": [],
      "action_items": [
        {
          "task": "Deploy service",
          "owner": null,
          "deadline_text": null,
          "evidence": "We need to deploy service."
        }
      ],
      "risks": [],
      "open_questions": []
    }
    """
    analysis = extract_structured_analysis(raw_json, source_transcript="We need to deploy service.")
    assert analysis.summary == "Discussed dashboard rollout"
    assert len(analysis.action_items) == 1
    assert analysis.action_items[0].id == "TASK-001"
    # Deterministic layer must catch missing owner & missing deadline
    assert any(w.category == "missing_owner" for w in analysis.accountability_warnings)
    assert any(w.category == "missing_deadline" for w in analysis.accountability_warnings)
