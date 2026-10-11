"""Pydantic schemas and data contracts for MeetingMind AI."""

from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class DecisionItem(BaseModel):
    """Represents a confirmed or tentative decision made during a meeting."""
    description: str = Field(..., description="Description of the decision")
    status: Literal["confirmed", "tentative"] = Field(
        default="confirmed",
        description="Whether the decision is firmly confirmed or tentative"
    )
    evidence: str = Field(
        default="",
        description="Direct quote or snippet from notes evidencing this decision"
    )

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, v: str) -> str:
        if isinstance(v, str):
            v_clean = v.strip().lower()
            if "tentative" in v_clean or "proposed" in v_clean:
                return "tentative"
            return "confirmed"
        return "confirmed"


class ActionItem(BaseModel):
    """Represents an actionable task extracted from the meeting notes."""
    id: str = Field(default="TASK-001", description="Unique identifier for the task")
    task: str = Field(..., description="Actionable task statement")
    owner: Optional[str] = Field(
        default=None,
        description="Directly assigned person or team, None if unassigned"
    )
    deadline_text: Optional[str] = Field(
        default=None,
        description="Verbatim or original deadline mention. None if omitted."
    )
    priority: Literal["high", "medium", "low", "unknown"] = Field(
        default="unknown",
        description="Priority level based on meeting urgency"
    )
    status: Literal["not_started", "in_progress", "completed", "needs_clarification"] = Field(
        default="not_started",
        description="Current workflow progress status"
    )
    confidence: float = Field(
        default=0.85,
        ge=0.0,
        le=1.0,
        description="Indicative AI confidence score (0.0 to 1.0, not calibrated probability)"
    )
    evidence: str = Field(
        default="",
        description="Exact quote or phrase from source notes supporting this task"
    )
    missing_information: list[str] = Field(
        default_factory=list,
        description="List of detected gaps (e.g. missing owner, missing deadline)"
    )
    is_tentative: bool = Field(
        default=False,
        description="True if assignment or commitment is tentative/unconfirmed"
    )
    suggested_clarification: Optional[str] = Field(
        default=None,
        description="Targeted question to ask to resolve ambiguities"
    )

    @field_validator("owner", mode="before")
    @classmethod
    def normalize_owner(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if isinstance(v, str):
            clean = v.strip()
            if not clean or clean.lower() in {"none", "null", "unassigned", "n/a", "tbd", "unknown", "nobody"}:
                return None
            return clean
        return str(v)

    @field_validator("deadline_text", mode="before")
    @classmethod
    def normalize_deadline(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if isinstance(v, str):
            clean = v.strip()
            if not clean or clean.lower() in {"none", "null", "no deadline", "n/a", "tbd", "unknown"}:
                return None
            return clean
        return str(v)

    @field_validator("priority", mode="before")
    @classmethod
    def normalize_priority(cls, v: str) -> str:
        if isinstance(v, str):
            clean = v.strip().lower()
            if "high" in clean or "urgent" in clean or "critical" in clean:
                return "high"
            if "med" in clean:
                return "medium"
            if "low" in clean:
                return "low"
            return "unknown"
        return "unknown"

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, v: str) -> str:
        if isinstance(v, str):
            clean = v.strip().lower().replace(" ", "_").replace("-", "_")
            if "clarif" in clean or "tentative" in clean or "unconfirmed" in clean:
                return "needs_clarification"
            if "progress" in clean or "ongoing" in clean:
                return "in_progress"
            if "done" in clean or "complete" in clean or "finished" in clean:
                return "completed"
            return "not_started"
        return "not_started"

    @field_validator("confidence", mode="before")
    @classmethod
    def normalize_confidence(cls, v: float) -> float:
        try:
            val = float(v)
            # If the model produced a percentage (e.g. 85 instead of 0.85)
            if val > 1.0 and val <= 100.0:
                val = val / 100.0
            val = max(0.0, min(1.0, val))
            return round(val, 2)
        except (ValueError, TypeError):
            return 0.80


class RiskItem(BaseModel):
    """Represents a potential project risk or blocker identified in discussions."""
    description: str = Field(..., description="Description of the risk or blocker")
    evidence: str = Field(default="", description="Snippet supporting the risk")
    suggested_follow_up: str = Field(
        default="",
        description="Recommended mitigation or follow-up action"
    )


class AccountabilityWarning(BaseModel):
    """Represents a missing-information flag, accountability gap, or ambiguity."""
    category: Literal[
        "missing_owner",
        "missing_deadline",
        "tentative_assignment",
        "vague_commitment",
        "conflicting_information",
        "unresolved_decision"
    ] = Field(..., description="Warning type")
    task_id: Optional[str] = Field(default=None, description="Related Task ID if applicable")
    subject: str = Field(..., description="Short title or subject of the concern")
    reason: str = Field(..., description="Clear explanation of why this warning was raised")
    evidence: str = Field(default="", description="Relevant quote from meeting notes")
    suggested_clarification: str = Field(
        ...,
        description="Concrete question to ask the team to resolve the ambiguity"
    )


class MeetingAnalysis(BaseModel):
    """Root contract for structured meeting action extraction."""
    meeting_title: Optional[str] = Field(
        default="Meeting Notes Analysis",
        description="Title of the meeting"
    )
    meeting_date: Optional[str] = Field(
        default=None,
        description="Optional meeting date"
    )
    summary: str = Field(..., description="Concise executive summary of discussions")
    key_topics: list[str] = Field(
        default_factory=list,
        description="Main topics and themes discussed"
    )
    decisions: list[DecisionItem] = Field(
        default_factory=list,
        description="Confirmed decisions and tentative proposals"
    )
    action_items: list[ActionItem] = Field(
        default_factory=list,
        description="Structured action items extracted from the notes"
    )
    risks: list[RiskItem] = Field(
        default_factory=list,
        description="Identified risks, blockers, and dependencies"
    )
    open_questions: list[str] = Field(
        default_factory=list,
        description="Unresolved questions requiring clarification"
    )
    accountability_warnings: list[AccountabilityWarning] = Field(
        default_factory=list,
        description="Flagged gaps, missing owners, vague deadlines, or unconfirmed tasks"
    )
    is_sample_data: bool = Field(
        default=False,
        description="Flag indicating if this represents pre-computed demo sample data"
    )
    source_provider: str = Field(
        default="qualcomm",
        description="Name of the AI provider or 'sample_data'"
    )

    @model_validator(mode="after")
    def ensure_task_ids(self) -> "MeetingAnalysis":
        """Assign sequential TASK-XXX identifiers if not present or duplicate."""
        seen = set()
        for idx, item in enumerate(self.action_items, start=1):
            if not item.id or item.id in seen or item.id == "TASK-001":
                new_id = f"TASK-{idx:03d}"
                item.id = new_id
            seen.add(item.id)
        return self
