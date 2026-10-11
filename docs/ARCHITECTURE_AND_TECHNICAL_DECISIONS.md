# MeetingMind AI — Technical Architecture & Engineering Decisions

**Infosys Hack-AI-Thon Technical Whitepaper**  
*Product Name:* MeetingMind AI  
*Tagline:* "Turn meeting conversations into accountable action."

---

## 1. Executive Summary & Core Engineering Philosophy

Most AI meeting assistants summarize transcripts passively or generate bullet points that obscure accountability. When asked to produce action items, standard LLM applications suffer from three critical failure modes:
1. **Hallucination of Ownership**: Inventing responsible parties or assuming someone volunteered when discussions were ambiguous.
2. **False Temporal Precision**: Converting relative or vague deadlines (e.g., "soon", "next sprint", "tomorrow") into ungrounded calendar dates without date grounding.
3. **Equating Proposals with Decisions**: Treating tentative ideas (*"Priya may test if time permits"*) as confirmed commitments.

MeetingMind AI solves this with a **Dual-Layer Intelligence Architecture**:
- **Layer 1: Generative Extraction** (LLM inference on Qualcomm Cloud AI hardware) strictly constrained to verbatim citations and structured JSON extraction.
- **Layer 2: Deterministic Validation Engine** (Pure Python heuristic layer) that inspects extracted fields, enforces semantic invariants, flags missing data, and generates targeted clarification questions.

---

## 2. Technical Stack & Architectural Decisions

| Component | Selected Technology | Technical Rationale & Alternatives Rejected |
|---|---|---|
| **Frontend / Dashboard** | **Streamlit (v1.42+)** | **Decision:** Rapid interactive prototyping with native Python state handling (`st.session_state`). Clean, professional SaaS layout.<br>**Rejected:** React + FastAPI decoupled microservices. A separate React app introduces CORS complexity, redundant build pipelines, and unnecessary infrastructure overhead for an MVP presentation. |
| **Data Validation** | **Pydantic (v2.10+)** | **Decision:** Strict type validation, automated enum normalization, confidence bounds enforcement (`0.0 - 1.0`), and task indexing.<br>**Rejected:** Plain dictionaries or raw JSON schemas. Pydantic ensures corrupted model outputs fail fast with explicit recovery paths. |
| **AI Inference Provider** | **Qualcomm AI Inference Suite (Cirrascale Cloud)** | **Decision:** Hardware-accelerated inference hosted on Qualcomm Cloud AI hardware via OpenAI-compatible endpoints (`/apis/v2/chat/completions`).<br>**Models Tested:** `DeepSeek-R1-Distill-Llama-70B` (primary for reasoning), `Llama-3.1-8B` (lightweight fallback). |
| **Tabular Processing** | **Pandas (v2.2+)** | **Decision:** Fast filtering, in-memory table joins, and RFC-compliant CSV serialization for Jira/Asana import. |
| **Testing** | **Pytest (v9.1+)** | **Decision:** 30 automated unit tests with mocked API endpoints. 100% deterministic test coverage without paid API token consumption. |

---

## 3. The Dual-Layer Workflow

```
[ Raw Meeting Transcript ]
           │
           ▼
[ Layer 1: Generative Extraction (Qualcomm AI) ]
   - Strict System Prompt (Zero-hallucination policy)
   - Verbatim Evidence Extraction
   - Single-Inference Budget Guard ($3 allocation protection)
           │
           ▼
[ Intermediate Structured JSON ]
   - meeting_title, summary, key_topics
   - decisions (confirmed vs tentative)
   - action_items (task, owner, deadline, evidence)
   - risks, open_questions
           │
           ▼
[ Layer 2: Deterministic Python Validation Layer ]
   - Rule 1: Missing Owner Detector (flags None, "we", "team", "someone")
   - Rule 2: Missing Deadline Detector (flags unstated timelines)
   - Rule 3: Tentative Commitment Scanner ("may", "might", "unconfirmed")
   - Rule 4: Vague Phrase Heuristics ("soon", "asap", "needs to be")
   - Rule 5: Undecided Architecture Watchdog ("undecided", "TBD")
   - Rule 6: Duplicate Deliverable Token-Overlap (Jaccard similarity > 70%)
           │
           ▼
[ Enriched MeetingAnalysis Model ]
   - Action Items with Session Workflow Status
   - Accountability Warnings with Clarification Questions
   - Export Artifacts (CSV + JSON)
```

---

## 4. Prompt Engineering & Role Definition

### The Role Assigned to the Model
The model is instructed as an **objective, adversarial executive assistant and engineering intelligence auditor**. It is explicitly warned **not** to be helpful by guessing or smoothing over gaps.

### Exact System Prompt Contract
```text
You are MeetingMind AI, an objective, rigorous meeting intelligence extractor for engineering and product teams.

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
```

### Why This Prompt Design Succeeds
1. **Verbatim Evidence Requirement**: Forcing the model to quote direct sentences prevents abstract fabrications.
2. **Explicit Null States**: Teaching the model that `owner: null` and `deadline_text: null` are preferred states when data is missing removes the LLM's natural compulsion to be "helpful" by guessing.
3. **Separation of Reasoning & Output**: The parser handles `<think> ... </think>` chains and markdown code fences cleanly without choking on extraneous tokens.

---

## 5. Deterministic Validation Engine (Rules & Heuristics)

The validation layer (`src/validation.py`) enforces business rules that LLMs frequently miss:

```python
# Lexical & Semantic Dictionaries
TENTATIVE_KEYWORDS = [
    "may", "might", "could", "tentative", "unconfirmed",
    "not confirmed", "has not confirmed", "conditional", "if time permits"
]

VAGUE_DEADLINE_KEYWORDS = [
    "soon", "asap", "later", "eventually", "sometime", "shortly", "at some point"
]

VAGUE_COMMITMENT_PHRASES = [
    "we should", "someone should", "needs to be", "need to", "ought to"
]

UNDECIDED_DECISION_KEYWORDS = [
    "undecided", "tbd", "pending", "not decided", "open for discussion"
]
```

### Clarification Question Generation
For every flagged gap, the engine automatically formulates a targeted clarification question:
- **Missing Owner**: *"Who is the designated owner accountable for '{task}'?"*
- **Missing Deadline**: *"What is the target delivery date or milestone for '{task}'?"*
- **Tentative Assignment**: *"Can {owner} confirm commitment for '{task}', or should an alternative lead be assigned?"*
- **Vague Commitment**: *"Could the team define a specific date and acceptance criteria for '{task}'?"*
- **Unresolved Decision**: *"What specific blockers or evaluations must conclude before finalizing the decision on '{decision}'?"*

---

## 6. Budget & Resource Optimization ($3 Hackathon Cap) & Unit Economics

MeetingMind AI is engineered for production-grade cost efficiency on Cirrascale Qualcomm Cloud AI hardware.

### Cirrascale Inference Cloud Official Pricing Matrix
Based on the live Cirrascale platform pricing:

| Model | Architecture | Context | Input Cost / 1M Tokens | Output Cost / 1M Tokens | Cost per Meeting Analysis |
|---|---|---|---|---|---|
| **Llama3.1-8B** | 8B Parameters | 8K | **$0.02** | **$0.22** | **~$0.00023** (0.023¢) |
| **Qwen-QwQ-32B** | 32B Parameters | 8K | **$0.08** | **$0.36** | **~$0.00040** (0.040¢) |
| **Llama-3.3-70B** | 70B Parameters | 8K | **$0.19** | **$0.69** | **~$0.00078** (0.078¢) |
| **DeepSeek-R1-Distill-Llama-70B** | 70B Parameters | 8K | **$0.19** | **$0.69** | **~$0.00078** (0.078¢) |

### Unit Economics Breakdown
For an average meeting (~500 input tokens, ~1,000 output tokens):
- **On DeepSeek-R1-Distill-Llama-70B (Primary Model)**:
  - Input Cost: $500 \times (\$0.19 / 1,000,000) = \$0.000095$
  - Output Cost: $1,000 \times (\$0.69 / 1,000,000) = \$0.000690$
  - **Total Cost per Meeting**: **~$0.000785** *(Less than one-tenth of a single US cent!)*
  - **$3 Hackathon Budget Capacity**: **~3,820 complete meeting extractions**!

- **On Llama3.1-8B (Edge/Fast Model)**:
  - Input Cost: $500 \times (\$0.02 / 1,000,000) = \$0.000010$
  - Output Cost: $1,000 \times (\$0.22 / 1,000,000) = \$0.000220$
  - **Total Cost per Meeting**: **~$0.000230** *(Less than one-fortieth of a cent!)*
  - **$3 Hackathon Budget Capacity**: **~13,040 complete meeting extractions**!

### Architectural Budget Guards
1. **Single-Request Invariant**: Each meeting analysis consumes **exactly 1 inference call**. No multi-agent chatter, no iterative retries, and no conversational loops.
2. **Zero-Token Startup**: The app never pings the AI on launch or page reload.
3. **Session Persistence**: User edits (e.g. changing task status from *Not started* to *In progress*) are preserved in Streamlit's `session_state` without making secondary API calls.
4. **Standalone Demo Mode**: Bundled benchmark meeting can run completely offline with zero credit burn.

---

## 7. Qualcomm Cloud AI Integration Specifics

- **Host Platform**: Cirrascale Inference Cloud (`https://aisuite.cirrascale.com/apis/v2`)
- **Protocol**: OpenAI-compliant REST HTTP POST (`/chat/completions`)
- **Headers**: Dual-mode authentication (`Authorization: Bearer <key>` + `x-api-key: <key>`)
- **Payload Design**: `"stream": false`, `"temperature": 0.1` for deterministic outputs.
- **Model Selection**: Direct support for Cirrascale's Qualcomm-compiled models:
  - `DeepSeek-R1-Distill-Llama-70B` (Default for deep structured reasoning)
  - `Llama-3.1-8B` (Fast edge-style inference)
  - `Llama-3.3-70B` & `Qwen-QwQ-32B`
