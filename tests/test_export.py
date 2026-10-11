"""Unit tests for CSV and JSON export functions and sample mode."""

import io
import json
import pandas as pd
from src.sample_data import get_sample_analysis, get_sample_meeting_text
from src.schemas import MeetingAnalysis


def test_sample_data_integrity():
    """Sample data must load without errors, be marked sample data, and have all required fields."""
    sample_text = get_sample_meeting_text()
    assert "Rahul will finish the API integration by Friday." in sample_text

    analysis = get_sample_analysis()
    assert isinstance(analysis, MeetingAnalysis)
    assert analysis.is_sample_data is True
    assert analysis.source_provider == "sample_data"
    assert len(analysis.action_items) == 4
    assert len(analysis.decisions) == 2
    assert len(analysis.accountability_warnings) >= 4


def test_export_action_items_to_csv():
    """Action items must serialize to valid tabular CSV."""
    analysis = get_sample_analysis()

    data = [
        {
            "Task ID": item.id,
            "Task Description": item.task,
            "Owner": item.owner or "Unassigned",
            "Deadline": item.deadline_text or "Not stated",
            "Priority": item.priority.capitalize(),
            "Status": item.status.replace("_", " ").capitalize(),
            "Confidence": f"{item.confidence:.0%}",
            "Evidence": item.evidence,
        }
        for item in analysis.action_items
    ]

    df = pd.DataFrame(data)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_str = csv_buffer.getvalue()

    assert "Task ID,Task Description,Owner,Deadline,Priority,Status,Confidence,Evidence" in csv_str
    assert "Rahul" in csv_str
    assert "TASK-001" in csv_str

    # Verify re-parsing with pandas
    read_df = pd.read_csv(io.StringIO(csv_str))
    assert len(read_df) == 4
    assert list(read_df.columns) == [
        "Task ID", "Task Description", "Owner", "Deadline", "Priority", "Status", "Confidence", "Evidence"
    ]


def test_export_analysis_to_json():
    """Meeting analysis must serialize to valid, conformant JSON."""
    analysis = get_sample_analysis()
    json_str = analysis.model_dump_json(indent=2)
    parsed = json.loads(json_str)

    assert parsed["meeting_title"] == "Dashboard Release Sync"
    assert parsed["is_sample_data"] is True
    assert len(parsed["action_items"]) == 4

    # Verify re-instantiation from dumped JSON
    rebuilt = MeetingAnalysis.model_validate(parsed)
    assert rebuilt.summary == analysis.summary
    assert len(rebuilt.accountability_warnings) == len(analysis.accountability_warnings)
