"""Sample data and pre-computed deterministic analysis for demo mode."""

from typing import Dict, Any
from src.schemas import (
    MeetingAnalysis,
    ActionItem,
    DecisionItem,
    RiskItem,
    AccountabilityWarning,
)

SAMPLE_MEETING_NOTES = """The project team met to review the dashboard release. Rahul will finish the API integration by Friday. Priya may handle testing, but she has not confirmed yet. The team agreed to review the interface tomorrow. The database technology is still undecided. The deployment plan needs to be finalized soon."""

SAMPLE_ANALYSIS_RAW: Dict[str, Any] = {
    "meeting_title": "Dashboard Release Sync",
    "meeting_date": "2026-10-11",
    "summary": "The project team convened to evaluate readiness for the upcoming dashboard release. Core work streams reviewed include API integration, testing ownership, UI review scheduling, database technology selection, and deployment roadmap.",
    "key_topics": [
        "Dashboard Release Scope",
        "API Integration Progress",
        "QA & Testing Ownership",
        "Interface Review Schedule",
        "Database Architecture Selection",
        "Deployment Planning"
    ],
    "decisions": [
        {
            "description": "Team will conduct the interface review tomorrow",
            "status": "confirmed",
            "evidence": "The team agreed to review the interface tomorrow."
        },
        {
            "description": "Database technology selection remains open and uncommitted",
            "status": "tentative",
            "evidence": "The database technology is still undecided."
        }
    ],
    "action_items": [
        {
            "id": "TASK-001",
            "task": "Finish the API integration",
            "owner": "Rahul",
            "deadline_text": "Friday",
            "priority": "high",
            "status": "not_started",
            "confidence": 0.95,
            "evidence": "Rahul will finish the API integration by Friday.",
            "missing_information": [],
            "is_tentative": False,
            "suggested_clarification": None
        },
        {
            "id": "TASK-002",
            "task": "Handle testing for dashboard release",
            "owner": "Priya (unconfirmed)",
            "deadline_text": None,
            "priority": "medium",
            "status": "needs_clarification",
            "confidence": 0.75,
            "evidence": "Priya may handle testing, but she has not confirmed yet.",
            "missing_information": ["deadline"],
            "is_tentative": True,
            "suggested_clarification": "Can Priya confirm availability and ownership for testing, or should another QA engineer be designated?"
        },
        {
            "id": "TASK-003",
            "task": "Review the interface",
            "owner": "The team",
            "deadline_text": "tomorrow",
            "priority": "medium",
            "status": "not_started",
            "confidence": 0.90,
            "evidence": "The team agreed to review the interface tomorrow.",
            "missing_information": [],
            "is_tentative": False,
            "suggested_clarification": "What specific calendar time and meeting link will be used for tomorrow's interface review?"
        },
        {
            "id": "TASK-004",
            "task": "Finalize the deployment plan",
            "owner": None,
            "deadline_text": "soon",
            "priority": "high",
            "status": "needs_clarification",
            "confidence": 0.65,
            "evidence": "The deployment plan needs to be finalized soon.",
            "missing_information": ["owner", "deadline"],
            "is_tentative": False,
            "suggested_clarification": "Who will own drafting the deployment plan, and what is the exact target completion date?"
        }
    ],
    "risks": [
        {
            "description": "Deployment plan is unowned with an ambiguous timeline ('soon'), risking release delays",
            "evidence": "The deployment plan needs to be finalized soon.",
            "suggested_follow_up": "Appoint a release coordinator to define a release checklist and sign-off milestone."
        },
        {
            "description": "Database technology remains undecided while release preparation proceeds",
            "evidence": "The database technology is still undecided.",
            "suggested_follow_up": "Schedule an architecture spike to benchmark candidate databases and finalize selection."
        },
        {
            "description": "Testing commitment is unconfirmed, potentially creating a QA bottleneck",
            "evidence": "Priya may handle testing, but she has not confirmed yet.",
            "suggested_follow_up": "Confirm QA bandwidth with Priya or reassign to another engineer before Friday."
        }
    ],
    "open_questions": [
        "Will Priya commit to testing the release?",
        "Which database technology will be selected for production?",
        "Who is responsible for authoring and approving the deployment plan?",
        "What specific time tomorrow will the interface review occur?"
    ],
    "accountability_warnings": [
        {
            "category": "tentative_assignment",
            "task_id": "TASK-002",
            "subject": "Tentative Testing Assignment (Priya)",
            "reason": "Ownership is conditional and unconfirmed. The notes explicitly state Priya has not confirmed yet.",
            "evidence": "Priya may handle testing, but she has not confirmed yet.",
            "suggested_clarification": "Can Priya confirm ownership for testing, or should a backup QA resource be assigned?"
        },
        {
            "category": "missing_owner",
            "task_id": "TASK-004",
            "subject": "Unassigned Task: Deployment Plan",
            "reason": "The deployment plan requires finalization, but no owner is assigned to lead or complete it.",
            "evidence": "The deployment plan needs to be finalized soon.",
            "suggested_clarification": "Who will take ownership of finalizing the deployment plan?"
        },
        {
            "category": "vague_commitment",
            "task_id": "TASK-004",
            "subject": "Vague Timeline ('soon')",
            "reason": "The deployment plan deadline is stated only as 'soon', providing no accountable delivery milestone.",
            "evidence": "The deployment plan needs to be finalized soon.",
            "suggested_clarification": "What is the concrete deadline date for finalizing the deployment plan?"
        },
        {
            "category": "unresolved_decision",
            "task_id": None,
            "subject": "Undecided Database Technology",
            "reason": "The core database stack choice is unresolved, which blocks downstream persistence work.",
            "evidence": "The database technology is still undecided.",
            "suggested_clarification": "When will the database evaluation conclude, and who makes the final architectural decision?"
        }
    ],
    "is_sample_data": True,
    "source_provider": "sample_data"
}


def get_sample_meeting_text() -> str:
    """Returns the bundled realistic example notes."""
    return SAMPLE_MEETING_NOTES


def get_sample_analysis() -> MeetingAnalysis:
    """Returns the validated deterministic sample MeetingAnalysis object."""
    return MeetingAnalysis.model_validate(SAMPLE_ANALYSIS_RAW)
