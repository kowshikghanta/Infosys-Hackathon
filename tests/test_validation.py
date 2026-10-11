"""Unit tests for the deterministic validation layer."""

from src.schemas import (
    ActionItem,
    DecisionItem,
    MeetingAnalysis,
)
from src.validation import (
    run_deterministic_validation,
    validate_action_items,
    validate_decisions,
)


def test_missing_owner_detection():
    """Unassigned tasks should be flagged with missing_owner warnings and clarification questions."""
    items = [
        ActionItem(
            task="Finalize deployment plan",
            owner=None,
            deadline_text="Friday",
            evidence="The deployment plan needs to be finalized.",
        )
    ]
    warnings = validate_action_items(items)
    assert any(w.category == "missing_owner" for w in warnings)
    warning = next(w for w in warnings if w.category == "missing_owner")
    assert "Who is the designated owner" in warning.suggested_clarification
    assert "owner" in items[0].missing_information


def test_missing_deadline_detection():
    """Tasks without deadlines should be flagged with missing_deadline."""
    items = [
        ActionItem(
            task="Handle QA testing",
            owner="Priya",
            deadline_text=None,
            evidence="Priya will test.",
        )
    ]
    warnings = validate_action_items(items)
    assert any(w.category == "missing_deadline" for w in warnings)
    warning = next(w for w in warnings if w.category == "missing_deadline")
    assert "target delivery date" in warning.suggested_clarification
    assert "deadline" in items[0].missing_information


def test_tentative_assignment_detection():
    """Tentative expressions such as 'may handle', 'not confirmed' must be flagged."""
    items = [
        ActionItem(
            task="Handle testing",
            owner="Priya",
            evidence="Priya may handle testing, but she has not confirmed yet.",
        )
    ]
    warnings = validate_action_items(items)
    assert any(w.category == "tentative_assignment" for w in warnings)
    assert items[0].is_tentative is True
    assert items[0].status == "needs_clarification"


def test_vague_commitment_detection():
    """Vague deadlines like 'soon' or vague phrases like 'needs to be' must trigger vague_commitment warnings."""
    items = [
        ActionItem(
            task="Deployment plan needs to be finalized soon",
            owner=None,
            deadline_text="soon",
            evidence="The deployment plan needs to be finalized soon.",
        )
    ]
    warnings = validate_action_items(items)
    assert any(w.category == "vague_commitment" for w in warnings)


def test_unresolved_decision_detection():
    """Undecided decisions must be flagged as unresolved_decision."""
    decisions = [
        DecisionItem(
            description="Database technology is still undecided",
            status="tentative",
            evidence="The database technology is still undecided.",
        )
    ]
    warnings = validate_decisions(decisions)
    assert len(warnings) == 1
    assert warnings[0].category == "unresolved_decision"
    assert "undecided" in warnings[0].reason.lower()


def test_duplicate_task_detection():
    """Tasks with heavy token overlap should trigger potential duplicate warnings."""
    items = [
        ActionItem(id="TASK-001", task="Finish API integration for dashboard release", owner="Rahul"),
        ActionItem(id="TASK-002", task="Finish the API integration for dashboard", owner="Rahul"),
    ]
    warnings = validate_action_items(items)
    assert any(w.category == "conflicting_information" for w in warnings)


def test_full_pipeline_on_sample_meeting():
    """End-to-end check on the sample meeting notes."""
    analysis = MeetingAnalysis(
        summary="Sync on release",
        decisions=[
            DecisionItem(
                description="Database technology is undecided",
                status="tentative",
                evidence="The database technology is still undecided.",
            ),
            DecisionItem(
                description="Review interface tomorrow",
                status="confirmed",
                evidence="The team agreed to review the interface tomorrow.",
            ),
        ],
        action_items=[
            ActionItem(
                task="Finish API integration",
                owner="Rahul",
                deadline_text="Friday",
                evidence="Rahul will finish the API integration by Friday.",
            ),
            ActionItem(
                task="Handle testing",
                owner="Priya (unconfirmed)",
                deadline_text=None,
                evidence="Priya may handle testing, but she has not confirmed yet.",
            ),
            ActionItem(
                task="Finalize deployment plan",
                owner=None,
                deadline_text="soon",
                evidence="The deployment plan needs to be finalized soon.",
            ),
        ],
    )
    validated = run_deterministic_validation(analysis)
    categories = [w.category for w in validated.accountability_warnings]

    assert "tentative_assignment" in categories
    assert "missing_owner" in categories
    assert "missing_deadline" in categories
    assert "vague_commitment" in categories
    assert "unresolved_decision" in categories
