"""Prompt engineering, JSON extraction sanitization, and structured parsing logic."""

import json
import re
from typing import Optional, Dict, Any, Tuple
from src.schemas import MeetingAnalysis
from src.validation import run_deterministic_validation

SYSTEM_EXTRACTION_PROMPT = """You are MeetingMind AI, an objective, rigorous meeting intelligence extractor for engineering and product teams.

Your task is to transform raw meeting notes into structured, accountable information.

CRITICAL EXTRACTION RULES:
1. STRICT FACTUAL ACCURACY:
   - Never invent, fabricate, or assume an owner, deadline, decision, or commitment that is not explicitly in the notes.
   - If an owner is not explicitly assigned, set "owner": null.
   - If a deadline is not specified, set "deadline_text": null.
   - Preserve original deadline phrasing verbatim (e.g., "Friday", "tomorrow", "soon"). Do NOT guess calendar dates unless unambiguous.

2. CONFIRMED VS TENTATIVE COMMITMENTS:
   - Distinguish confirmed tasks from tentative proposals. If notes say "Priya may handle testing, but she has not confirmed yet", mark "is_tentative": true, "status": "needs_clarification", and include the proposed owner with qualification.
   - Do NOT treat suggestions or discussions as confirmed decisions. If something is "still undecided" (e.g., "database technology is still undecided"), mark decision "status": "tentative" or record in risks/open questions.

3. VAGUE COMMITMENTS:
   - Identify vague commitments like "needs to be finalized soon" or "we should do this". Set "missing_information": ["owner", "deadline"] and generate targeted clarification questions.

4. EVIDENCE CITATIONS:
   - For every action item, decision, and risk, provide a short verbatim evidence excerpt from the source text.

5. CONFIDENCE INDICATION:
   - Provide a realistic confidence value between 0.0 and 1.0 based on clarity and certainty of the source notes.

6. REASONING CONCISENESS:
   - Keep any internal thinking/reasoning under 50 words. Proceed directly to outputting the JSON object.

You MUST respond ONLY with valid JSON conforming to the following structure:
{
  "meeting_title": "string or null",
  "meeting_date": "string or null",
  "summary": "Concise executive overview of the meeting",
  "key_topics": ["string"],
  "decisions": [
    {
      "description": "string",
      "status": "confirmed or tentative",
      "evidence": "exact quote"
    }
  ],
  "action_items": [
    {
      "id": "TASK-001",
      "task": "Actionable task statement",
      "owner": "string or null",
      "deadline_text": "string or null",
      "priority": "high, medium, low, or unknown",
      "status": "not_started, in_progress, completed, or needs_clarification",
      "confidence": 0.85,
      "evidence": "exact quote",
      "missing_information": ["owner", "deadline"],
      "is_tentative": false,
      "suggested_clarification": "string or null"
    }
  ],
  "risks": [
    {
      "description": "string",
      "evidence": "exact quote",
      "suggested_follow_up": "string"
    }
  ],
  "open_questions": ["string"]
}
"""


def build_extraction_prompt(
    transcript: str,
    meeting_title: Optional[str] = None,
    meeting_date: Optional[str] = None,
) -> Tuple[str, str]:
    """Constructs system and user prompt strings for LLM extraction."""
    user_prompt_lines = [
        "Please extract structured action items, decisions, risks, and missing information from the following meeting notes.",
        ""
    ]
    if meeting_title:
        user_prompt_lines.append(f"Meeting Title: {meeting_title.strip()}")
    if meeting_date:
        user_prompt_lines.append(f"Meeting Date: {meeting_date.strip()}")

    user_prompt_lines.append("")
    user_prompt_lines.append("SOURCE MEETING NOTES:")
    user_prompt_lines.append("```")
    user_prompt_lines.append(transcript.strip())
    user_prompt_lines.append("```")
    user_prompt_lines.append("")
    user_prompt_lines.append("CRITICAL: Keep your internal reasoning under 50 words. Return ONLY the JSON object. Do not enclose in conversational commentary.")

    return SYSTEM_EXTRACTION_PROMPT, "\n".join(user_prompt_lines)


def clean_and_parse_json_response(raw_text: str) -> Dict[str, Any]:
    """Extracts and parses JSON from raw LLM output, handling markdown code fences."""
    if not raw_text or not raw_text.strip():
        raise ValueError("Model returned an empty response.")

    cleaned = raw_text.strip()

    # Strip reasoning tags like <think> ... </think> from reasoning models (e.g. DeepSeek-R1)
    cleaned = re.sub(r"<think>[\s\S]*?</think>", "", cleaned).strip()

    # Strip markdown code blocks like ```json ... ``` or ``` ... ```
    if "```" in cleaned:
        # Match ```json ... ``` or ``` ... ```
        pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
        match = re.search(pattern, cleaned)
        if match:
            cleaned = match.group(1).strip()

    # Sometimes models include leading/trailing non-JSON commentary; find outermost { ... }
    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        cleaned = cleaned[first_brace : last_brace + 1]

    try:
        data = json.loads(cleaned)
        if not isinstance(data, dict):
            raise ValueError(f"Expected JSON object, got {type(data).__name__}")
        return data
    except json.JSONDecodeError as err:
        raise ValueError(f"Failed to parse LLM JSON: {err}. Raw output was: {raw_text[:200]}...")


def extract_structured_analysis(
    raw_json_str: str,
    source_transcript: str = "",
    meeting_title: Optional[str] = None,
    meeting_date: Optional[str] = None,
    source_provider: str = "qualcomm",
) -> MeetingAnalysis:
    """Parses raw JSON, validates against Pydantic schema, and runs deterministic validation layer."""
    raw_dict = clean_and_parse_json_response(raw_json_str)

    # Override or fill title and date if supplied by user in UI
    if meeting_title and not raw_dict.get("meeting_title"):
        raw_dict["meeting_title"] = meeting_title
    if meeting_date and not raw_dict.get("meeting_date"):
        raw_dict["meeting_date"] = meeting_date

    raw_dict["source_provider"] = source_provider
    raw_dict["is_sample_data"] = False

    # Validate against schema
    analysis = MeetingAnalysis.model_validate(raw_dict)

    # Execute deterministic validation layer
    enriched_analysis = run_deterministic_validation(analysis, source_transcript)
    return enriched_analysis
