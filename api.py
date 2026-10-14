"""MeetingMind AI: Standalone REST API for Postman testing and programmatic access.

Run with:
    python api.py
or:
    uvicorn api.py:app --port 8000 --reload
"""

import os
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from src.providers.qualcomm import QualcommAIProvider
from src.sample_data import get_sample_meeting_text, get_sample_analysis
from src.schemas import MeetingAnalysis

app = FastAPI(
    title="MeetingMind AI REST API",
    description="REST API for Smart Meeting Action Extractor on Qualcomm Cloud AI",
    version="1.0.0",
)

# Enable CORS for browser / Postman testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

provider = QualcommAIProvider()


class AnalyzeRequest(BaseModel):
    meeting_text: str = Field(
        ...,
        description="Raw meeting notes, transcript text, or bullet points.",
        examples=[
            "The project team met to review the dashboard release. Rahul will finish the API integration by Friday. Priya may handle testing, but she has not confirmed yet. The team agreed to review the interface tomorrow. The database technology is still undecided. The deployment plan needs to be finalized soon."
        ],
    )
    meeting_title: Optional[str] = Field(
        default=None,
        description="Optional title for the meeting.",
        examples=["Dashboard Release Sync"],
    )
    meeting_date: Optional[str] = Field(
        default=None,
        description="Optional ISO meeting date (YYYY-MM-DD).",
        examples=["2026-10-14"],
    )
    use_sample_fallback: bool = Field(
        default=False,
        description="If True, return bundled deterministic benchmark analysis without calling the cloud LLM.",
    )


@app.get("/health", tags=["Health & Diagnostics"])
def health_check() -> Dict[str, Any]:
    """Check API server health and Qualcomm Cloud AI provider configuration."""
    is_cfg, msg = provider.is_configured()
    return {
        "status": "healthy",
        "service": "MeetingMind AI REST API",
        "provider": "Qualcomm Cloud AI (Cirrascale)",
        "is_configured": is_cfg,
        "config_message": msg,
        "endpoint": provider.endpoint_url,
        "model": provider.model_name,
    }


@app.post("/health/ping", tags=["Health & Diagnostics"])
def ping_qualcomm() -> Dict[str, Any]:
    """Perform a live lightweight ping to the Cirrascale Qualcomm Cloud AI endpoint."""
    ok, diag_msg = provider.test_connection()
    return {
        "success": ok,
        "diagnostic_message": diag_msg,
        "endpoint": provider.endpoint_url,
        "model": provider.model_name,
    }


@app.get("/api/sample", tags=["Extraction"])
def get_sample() -> Dict[str, Any]:
    """Fetch bundled benchmark meeting notes and pre-computed deterministic analysis."""
    return {
        "sample_meeting_notes": get_sample_meeting_text(),
        "sample_analysis": get_sample_analysis().model_dump(),
    }


@app.post("/api/analyze", response_model=MeetingAnalysis, tags=["Extraction"])
def analyze_meeting(req: AnalyzeRequest) -> MeetingAnalysis:
    """Analyze raw meeting notes and extract structured, accountable action items,

    decisions, risks, and proactive clarification questions.
    """
    if not req.meeting_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="meeting_text cannot be empty.",
        )

    if req.use_sample_fallback:
        analysis = get_sample_analysis()
        if req.meeting_title:
            analysis.meeting_title = req.meeting_title
        if req.meeting_date:
            analysis.meeting_date = req.meeting_date
        return analysis

    is_cfg, msg = provider.is_configured()
    if not is_cfg:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Qualcomm AI Provider is not configured: {msg}. Set use_sample_fallback=True to test in offline mode.",
        )

    try:
        analysis = provider.extract_analysis(
            meeting_text=req.meeting_text,
            meeting_title=req.meeting_title,
            meeting_date=req.meeting_date,
        )
        return analysis
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Extraction failed: {str(e)}",
        )


if __name__ == "__main__":
    print("Starting MeetingMind AI REST API on http://127.0.0.1:8000 ...")
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
