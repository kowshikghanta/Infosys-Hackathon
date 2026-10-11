"""Deterministic validation layer for meeting action extraction.

This layer inspects extracted entities using deterministic heuristic rules,
ensuring that accountability gaps, missing owners, vague deadlines, and
tentative assignments are caught reliably without hallucination.
"""

from typing import List, Set
import re
from src.schemas import (
    ActionItem,
    DecisionItem,
    AccountabilityWarning,
    MeetingAnalysis,
)

TENTATIVE_KEYWORDS = [
    "may",
    "might",
    "could",
    "tentative",
    "unconfirmed",
    "not confirmed",
    "has not confirmed",
    "haven't confirmed",
    "pending confirmation",
    "conditional",
    "if time permits",
    "maybe",
    "considering",
    "exploring",
]

VAGUE_DEADLINE_KEYWORDS = [
    "soon",
    "asap",
    "later",
    "eventually",
    "sometime",
    "shortly",
    "down the road",
    "in the future",
    "when possible",
    "at some point",
]

VAGUE_COMMITMENT_PHRASES = [
    "we should",
    "someone should",
    "needs to be",
    "need to",
    "ought to",
    "team should",
    "looking into",
    "ought to look into",
]

UNDECIDED_DECISION_KEYWORDS = [
    "undecided",
    "tbd",
    "pending",
    "not decided",
    "open for discussion",
    "to be determined",
    "up in the air",
    "yet to decide",
    "tabled",
]


def _text_contains_any(text: str, keywords: List[str]) -> bool:
    """Case-insensitive check for presence of any keyword substring or word."""
    if not text:
        return False
    lower_text = text.lower()
    for kw in keywords:
        pattern = r"\b" + re.escape(kw.lower()) + r"\b"
        if re.search(pattern, lower_text):
            return True
    return False


def _calculate_token_overlap(s1: str, s2: str) -> float:
    """Computes Jaccard similarity between two token sets for duplicate detection."""
    tokens1 = set(re.findall(r"\w+", s1.lower()))
    tokens2 = set(re.findall(r"\w+", s2.lower()))
    if not tokens1 or not tokens2:
        return 0.0
    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)
    return len(intersection) / len(union)


def validate_action_items(
    action_items: List[ActionItem],
    source_transcript: str = "",
) -> List[AccountabilityWarning]:
    """Deterministically detects missing information and accountability risks in action items."""
    warnings: List[AccountabilityWarning] = []
    seen_warnings: Set[str] = set()

    for item in action_items:
        task_id = item.id or "TASK-UNASSIGNED"
        task_text = item.task or ""
        evidence_text = item.evidence or ""
        combined_text = f"{task_text} {evidence_text}".lower()

        # 1. Check for Missing Owner
        if not item.owner:
            if "owner" not in item.missing_information:
                item.missing_information.append("owner")
            
            dedup_key = f"{task_id}:missing_owner"
            if dedup_key not in seen_warnings:
                seen_warnings.add(dedup_key)
                warnings.append(
                    AccountabilityWarning(
                        category="missing_owner",
                        task_id=task_id,
                        subject=f"Unassigned Task: {task_text[:40]}...",
                        reason=(
                            f"The task '{task_text}' has no explicitly named individual or team owner. "
                            "Unassigned tasks have a high risk of being overlooked."
                        ),
                        evidence=evidence_text,
                        suggested_clarification=f"Who is the designated owner accountable for '{task_text}'?",
                    )
                )

        # 2. Check for Missing Deadline
        if not item.deadline_text:
            if "deadline" not in item.missing_information:
                item.missing_information.append("deadline")

            dedup_key = f"{task_id}:missing_deadline"
            if dedup_key not in seen_warnings:
                seen_warnings.add(dedup_key)
                warnings.append(
                    AccountabilityWarning(
                        category="missing_deadline",
                        task_id=task_id,
                        subject=f"Missing Deadline: {task_text[:40]}...",
                        reason=(
                            f"The task '{task_text}' does not have an agreed completion date or time constraint."
                        ),
                        evidence=evidence_text,
                        suggested_clarification=f"What is the target delivery date or milestone for '{task_text}'?",
                    )
                )

        # 3. Check for Tentative Assignment or Conditional Ownership
        is_tentative = (
            item.is_tentative
            or (item.owner and _text_contains_any(item.owner, TENTATIVE_KEYWORDS))
            or _text_contains_any(evidence_text, TENTATIVE_KEYWORDS)
            or _text_contains_any(task_text, TENTATIVE_KEYWORDS)
        )

        if is_tentative:
            item.is_tentative = True
            if item.status == "not_started":
                item.status = "needs_clarification"

            owner_label = item.owner or "The proposed owner"
            dedup_key = f"{task_id}:tentative_assignment"
            if dedup_key not in seen_warnings:
                seen_warnings.add(dedup_key)
                warnings.append(
                    AccountabilityWarning(
                        category="tentative_assignment",
                        task_id=task_id,
                        subject=f"Unconfirmed Commitment: {owner_label}",
                        reason=(
                            f"Ownership for '{task_text}' appears provisional or unconfirmed "
                            f"(e.g., '{evidence_text}'). No firm commitment was recorded."
                        ),
                        evidence=evidence_text,
                        suggested_clarification=(
                            f"Can {owner_label} confirm commitment for '{task_text}', "
                            "or should an alternative lead be assigned?"
                        ),
                    )
                )

        # 4. Check for Vague Deadlines or Commitments
        has_vague_deadline = bool(
            item.deadline_text and _text_contains_any(item.deadline_text, VAGUE_DEADLINE_KEYWORDS)
        )
        has_vague_commitment = _text_contains_any(combined_text, VAGUE_COMMITMENT_PHRASES)

        if has_vague_deadline or has_vague_commitment:
            dedup_key = f"{task_id}:vague_commitment"
            if dedup_key not in seen_warnings:
                seen_warnings.add(dedup_key)
                deadline_note = f" (stated as '{item.deadline_text}')" if item.deadline_text else ""
                warnings.append(
                    AccountabilityWarning(
                        category="vague_commitment",
                        task_id=task_id,
                        subject=f"Vague Commitment: {task_text[:40]}...",
                        reason=(
                            f"The task '{task_text}' lacks actionable specificity{deadline_note}. "
                            "Vague timelines frequently lead to delivery delays."
                        ),
                        evidence=evidence_text,
                        suggested_clarification=(
                            f"Could the team define a specific date and acceptance criteria for '{task_text}'?"
                        ),
                    )
                )

        # 5. Missing Evidence Warning
        if not item.evidence.strip():
            # If evidence is absent, flag for reviewer attention
            dedup_key = f"{task_id}:missing_evidence"
            if dedup_key not in seen_warnings:
                seen_warnings.add(dedup_key)
                warnings.append(
                    AccountabilityWarning(
                        category="vague_commitment",
                        task_id=task_id,
                        subject=f"Unverified Task: {task_text[:40]}...",
                        reason=(
                            f"Task '{task_text}' was generated without a direct citation from meeting notes."
                        ),
                        evidence="(No direct quote identified)",
                        suggested_clarification="Verify whether this action item was explicitly discussed.",
                    )
                )

    # 6. Check for Potential Duplicate or Conflicting Tasks
    n = len(action_items)
    for i in range(n):
        for j in range(i + 1, n):
            sim = _calculate_token_overlap(action_items[i].task, action_items[j].task)
            if sim >= 0.70:
                t1 = action_items[i]
                t2 = action_items[j]
                dedup_key = f"{t1.id}:{t2.id}:duplicate"
                if dedup_key not in seen_warnings:
                    seen_warnings.add(dedup_key)
                    warnings.append(
                        AccountabilityWarning(
                            category="conflicting_information",
                            task_id=t1.id,
                            subject=f"Potential Duplicate Tasks: {t1.id} & {t2.id}",
                            reason=(
                                f"Task '{t1.task}' overlaps significantly with '{t2.task}' (similarity: {sim:.0%})."
                            ),
                            evidence=f"{t1.id}: {t1.evidence} | {t2.id}: {t2.evidence}",
                            suggested_clarification=(
                                f"Are {t1.id} and {t2.id} the same deliverable or distinct subtasks?"
                            ),
                        )
                    )

    return warnings


def validate_decisions(decisions: List[DecisionItem]) -> List[AccountabilityWarning]:
    """Detects unresolved decisions, tentative proposals, and undecided matters."""
    warnings: List[AccountabilityWarning] = []
    seen: Set[str] = set()

    for idx, d in enumerate(decisions, start=1):
        desc = d.description or ""
        evidence = d.evidence or ""
        full_text = f"{desc} {evidence}".lower()

        is_undecided = (
            d.status == "tentative"
            or _text_contains_any(full_text, UNDECIDED_DECISION_KEYWORDS)
            or _text_contains_any(full_text, TENTATIVE_KEYWORDS)
        )

        if is_undecided:
            key = f"decision:{idx}:{desc[:30]}"
            if key not in seen:
                seen.add(key)
                warnings.append(
                    AccountabilityWarning(
                        category="unresolved_decision",
                        task_id=None,
                        subject=f"Unresolved Decision: {desc[:40]}...",
                        reason=(
                            f"Decision '{desc}' was marked tentative or undecided. "
                            "Unresolved decisions block downstream planning and implementation."
                        ),
                        evidence=evidence,
                        suggested_clarification=(
                            f"What specific blockers or evaluations must conclude before finalizing the decision on '{desc}'?"
                        ),
                    )
                )

    return warnings


def run_deterministic_validation(
    analysis: MeetingAnalysis,
    source_transcript: str = "",
) -> MeetingAnalysis:
    """Executes the complete deterministic validation pipeline on a MeetingAnalysis model.
    
    Ensures:
    1. Sequential and unique TASK IDs
    2. Missing owners flagged
    3. Missing deadlines flagged
    4. Tentative assignments marked and flagged
    5. Vague commitments flagged
    6. Unresolved decisions flagged
    7. Deduplication of warnings
    8. Preserves original source integrity without fabricating data
    """
    # 1. Re-index task IDs cleanly
    for idx, item in enumerate(analysis.action_items, start=1):
        item.id = f"TASK-{idx:03d}"

    # 2. Extract deterministic warnings
    task_warnings = validate_action_items(analysis.action_items, source_transcript)
    decision_warnings = validate_decisions(analysis.decisions)

    new_warnings = task_warnings + decision_warnings

    # 3. Merge with any existing warnings without duplicating
    existing_subjects = {w.subject.lower() for w in analysis.accountability_warnings}
    merged_warnings = list(analysis.accountability_warnings)

    for w in new_warnings:
        if w.subject.lower() not in existing_subjects:
            merged_warnings.append(w)
            existing_subjects.add(w.subject.lower())

    analysis.accountability_warnings = merged_warnings
    return analysis
