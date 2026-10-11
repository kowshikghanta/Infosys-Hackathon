"""Unit tests for Pydantic schemas and data contracts."""

import pytest
from pydantic import ValidationError
from src.schemas import (
    ActionItem,
    DecisionItem,
    RiskItem,
    AccountabilityWarning,
    MeetingAnalysis,
)


def test_action_item_valid():
    """Tests normal creation of ActionItem."""
    item = ActionItem(
        id="TASK-001",
        task="Finish the API integration",
        owner="Rahul",
        deadline_text="Friday",
        priority="high",
        status="not_started",
        confidence=0.95,
        evidence="Rahul will finish the API integration by Friday.",
    )
    assert item.id == "TASK-001"
    assert item.owner == "Rahul"
    assert item.deadline_text == "Friday"
    assert item.priority == "high"
    assert item.status == "not_started"
    assert item.confidence == 0.95


def test_action_item_normalization():
    """Tests field normalization for owner, deadline, priority, status, and confidence."""
    # Test normalization of "unassigned" / "tbd" owner to None
    item = ActionItem(
        task="Write docs",
        owner="unassigned",
        deadline_text="N/A",
        priority="Urgent Critical",
        status="Needs Clarification",
        confidence=90.0,  # Given as percentage
    )
    assert item.owner is None
    assert item.deadline_text is None
    assert item.priority == "high"
    assert item.status == "needs_clarification"
    assert item.confidence == 0.90


def test_action_item_invalid_task_empty():
    """Empty task should fail validation."""
    with pytest.raises(ValidationError):
        ActionItem()


def test_decision_item_normalization():
    """DecisionItem should normalize status properly."""
    d1 = DecisionItem(
        description="Agreed to review tomorrow",
        status="Confirmed",
        evidence="Agreed tomorrow"
    )
    assert d1.status == "confirmed"

    d2 = DecisionItem(
        description="Database choice",
        status="tentative proposal",
        evidence="undecided"
    )
    assert d2.status == "tentative"


def test_meeting_analysis_task_indexing():
    """MeetingAnalysis should automatically re-index sequential TASK-00X IDs."""
    analysis = MeetingAnalysis(
        summary="Test meeting",
        action_items=[
            ActionItem(task="Task 1", owner="Alice"),
            ActionItem(task="Task 2", owner="Bob"),
        ],
    )
    assert analysis.action_items[0].id == "TASK-001"
    assert analysis.action_items[1].id == "TASK-002"
