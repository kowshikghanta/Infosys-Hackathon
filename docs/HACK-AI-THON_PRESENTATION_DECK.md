# Infosys Hack-AI-Thon 2026 — Official Solution Presentation Deck

> **Track:** Engagement Platforms (Track 3)  
> **Problem Statement ID:** EP-01  
> **Title:** Smart Meeting Action Extractor  
> **Product Name:** MeetingMind AI  
> **Qualcomm Platform:** Qualcomm Cloud AI Playground (Cirrascale Inference Cloud)  
> **Presentation PPTX File:** [`MeetingMind_AI_Presentation.pptx`](file:///d:/Infosys%20hackathon/MeetingMind_AI_Presentation.pptx)

---

## Slide 1: Team Introduction
**Suggested Time:** 0:20

### Slide Content:
- **Event:** HACK-AI-THON 2026
- **Team Name:** Team MeetingMind
- **College / Institution:** [College Name | City]
- **Team Members:**
  - Kowshik Ghanta *(Full-Stack & AI Systems Lead)*
  - [Team Member 2] *(AI & Model Engineer)*
  - [Team Member 3] *(Product & QA Engineer)*
- **Selected Problem Statement:** EP-01: Smart Meeting Action Extractor
- **Technology Track:** Qualcomm Cloud AI Playground (Cirrascale Inference Cloud)

### Core Product Identity:
- **Product Name:** **MeetingMind AI**
- **Tagline:** *"Turn meeting conversations into accountable action."*
- **One-Line Scope:** A dual-layer intelligence platform that eliminates meeting ambiguity by combining Qualcomm Cloud AI generative extraction with a deterministic Python validation engine to enforce strict ownership, deadline accountability, and zero hallucination.

### 🎙️ WHAT TO SAY (Speaker Script — 20s):
> *"Good morning, esteemed judges! We are Team MeetingMind, presenting Problem Statement EP-01: Smart Meeting Action Extractor in the Qualcomm Cloud AI track. We built MeetingMind AI to solve the massive accountability gap in post-meeting follow-ups using Qualcomm hardware and a deterministic zero-hallucination engine. Today, we're excited to demonstrate our fully functional prototype connected live to Qualcomm Cloud AI."*

---

## Slide 2: Problem Statement
**Suggested Time:** 0:50

### Actual Problem Statement:
**EP-01: Smart Meeting Action Extractor**  
*Convert unstructured, messy meeting transcripts into structured decisions, accountable action items, designated owners, unambiguous deadlines, and project risks.*

### Who is Affected?
- Engineering teams, sprint leads, product managers, scrum masters, and cross-functional enterprise stakeholders.

### Why Does It Matter?
- Over **30% of employee time** is spent in meetings.
- Up to **40% of critical deliverables** are delayed or lost because meeting notes lack explicit owners, timelines are ambiguous (*"soon"*, *"next sprint"*), or casual proposals are mistaken for confirmed commitments.

### Current Gap / Pain Point:
- Existing tools (Zoom AI Companion, Microsoft Copilot, generic LLMs) generate passive narrative summaries.
- When forced to extract tasks, standard LLMs exhibit **"eager sycophancy"**—they hallucinate owners who never volunteered, fabricate dates, and smooth over unconfirmed commitments.

### Evidence / Scenario:
- **Benchmark Notes:**  
  > *"Rahul will finish the API integration by Friday. Priya may handle testing, but she has not confirmed yet. The team agreed to review the interface tomorrow. The database technology is still undecided. The deployment plan needs to be finalized soon."*
- **Baseline AI Failure:** Generic LLMs assign Priya as the confirmed testing owner and invent a calendar date for the deployment plan, masking severe project risk.

### Success Definition:
1. **Verbatim Evidence Citations:** Every extracted entity grounded in direct quotes.
2. **Explicit Null Handling:** Missing owners and dates marked `null`—never fabricated.
3. **Proactive Clarification:** Auto-formulates targeted questions to resolve ambiguities.
4. **Export Readiness:** One-click Jira/Asana CSV and schema-validated JSON.

### 🎙️ WHAT TO SAY (Speaker Script — 50s):
> *"Meetings produce unstructured chaos. But the biggest issue isn't summarizing what happened—it's establishing real accountability. When notes say 'Priya may test, but hasn't confirmed yet' and 'we need a deployment plan soon', a typical LLM tries to be 'helpful' by guessing that Priya is the owner and fabricating a deadline. That creates catastrophic blind spots. For EP-01, success means refusing to guess, enforcing strict ownership, isolating undecided architecture forks, and delivering actionable deliverables."*

---

## Slide 3: Proposed Solution
**Suggested Time:** 0:55

### Solution in One Sentence:
> **MeetingMind AI uses Qualcomm Cloud AI coupled with a deterministic Python validation engine to convert messy meeting notes into structured, accountable action items with zero hallucination.**

### 3-Step User Journey:
```
[ 1. INPUT ] ───> [ 2. PROCESS ] ───> [ 3. OUTPUT ]
```

#### 1. INPUT (User Data)
- Raw messy notes, transcripts, or discussion bullets pasted into the dashboard.
- Optional meeting title and calendar date for relative time grounding.
- 1-Click bundled benchmark notes for immediate zero-token evaluation.

#### 2. PROCESS (Dual-Layer Intelligence)
- **Layer 1: Qualcomm Cloud AI Inference**: Hardware-accelerated generative extraction using `DeepSeek-R1-Distill-Llama-70B` and `Llama-3.1-8B` with strict negative constraints.
- **Layer 2: Deterministic Python Validation**: Pure algorithmic rules engine auditing missing owners, unstated deadlines, tentative expressions, and vague timelines.
- **Budget Guard**: Strictly **1 inference call per analysis** to respect the \$3 budget.

#### 3. OUTPUT (Accountability Dashboard)
- **Interactive Action Table:** Filterable by priority, owner, and status with in-session triage.
- **Accountability Warnings:** Flags unassigned tasks and unconfirmed commitments.
- **Clarification Generator:** Auto-generates exact questions to eliminate ambiguities.
- **Decisions & Risks:** Separates confirmed decisions from tentative proposals.
- **Export:** RFC-compliant CSV for Jira/Asana import and structured JSON.

### Key Value / Differentiator:
- **The "Anti-Hallucination" Accountability Layer:** Rather than guessing missing information, MeetingMind AI flags the accountability gap and formulates the exact clarification question for the team lead.

### 🎙️ WHAT TO SAY (Speaker Script — 55s):
> *"Our solution follows a 3-step pipeline: Input, Dual-Layer Processing, and Actionable Output. The user pastes notes into our Streamlit dashboard. The text routes to Cirrascale Qualcomm Cloud AI hardware for evidence-backed entity extraction. Then, our deterministic Python layer steps in to audit the output. The key differentiator is that instead of hallucinating missing data, MeetingMind AI detects the ambiguity and generates the exact question the manager needs to ask."*

---

## Slide 4: Architecture & Technical Design
**Suggested Time:** 0:55

### End-to-End System Diagram:
```
+--------------------+      +--------------------+      +--------------------+      +--------------------+
|   USER / CLIENT    |      | APPLICATION LOGIC  |      |   AI / INFERENCE   |      |  OUTPUT & ACTION   |
+--------------------+      +--------------------+      +--------------------+      +--------------------+
| • Streamlit UI     | ───> | • BaseAIProvider   | ───> | • Cirrascale Cloud | ───> | • Action Dashboard |
| • SaaS Controls    |      | • Pydantic v2      |      | • DeepSeek-R1-70B  |      | • Jira / Asana CSV |
| • Session State    |      | • Rules Engine     |      | • Llama-3.1-8B     |      | • Structured JSON  |
| • Live Filters     |      | • Pandas Pipeline  |      | • Qualcomm NPU/AI  |      | • Clarification Qs |
+--------------------+      +--------------------+      +--------------------+      +--------------------+
```

### Technology Choices:
- **Frontend:** Streamlit 1.42+ (Rapid interactive prototyping, session-bound state triage).
- **Validation:** Pydantic v2.10+ (Type normalization, enum validation, confidence bounds).
- **AI Backend:** Qualcomm AI Inference Suite on Cirrascale Cloud (`/apis/v2/chat/completions`).
- **Data Engine:** Pandas 2.2+ (RFC-compliant CSV generation and in-memory filtering).
- **Test Framework:** Pytest 9.1+ (Automated unit and resilience test suite).

### Engineering Rationale:
1. **Single-Request Invariant:** To protect the hackathon's \$3 credit budget, each analysis consumes strictly **one** inference call. No multi-agent chatter or redundant loops.
2. **Dual-Layer Separation of Concerns:** LLMs are exceptional at semantic linguistics, but unreliable at business invariants. We delegate parsing to the LLM and business rule auditing to deterministic Python code.

### Validation, Testing & Reliability:
- **30 Automated Pytest Unit Tests (100% Pass Rate):**
  - Schema normalization, enums, confidence bounds.
  - Heuristic checks: missing owners, missing deadlines, tentative assignments, vague words.
  - Mocked network tests: HTTP 401 Unauthorized, HTTP 429 Rate Limits, timeouts, malformed JSON.
- **Fail-Safe Offline Mode:** Complete benchmark dataset runs deterministically without an internet connection or credit burn.

### 🎙️ WHAT TO SAY (Speaker Script — 55s):
> *"Walking left to right through our technical design: the user interacts with our Streamlit frontend. The request routes to Cirrascale's Qualcomm Cloud AI hardware running DeepSeek-R1. We enforce an architectural Single-Request Invariant to protect the $3 budget. Once extracted, our deterministic validation layer audits the output before rendering. Our engineering depth is backed by 30 automated unit tests covering network drops, 401s, 429s, and edge cases, passing at 100%."*

---

## Slide 5: AI Usage & Innovation
**Suggested Time:** 0:45

### AI Capability Used:
- **Qualcomm Cloud AI Inference Suite (Cirrascale Cloud):** Hardware-accelerated generative inference via OpenAI-compliant REST endpoints.
- **Models Verified:**
  - `DeepSeek-R1-Distill-Llama-70B` *(Default: Deep reasoning & structured extraction)*
  - `Llama-3.1-8B` *(Edge fallback: Fast inference)*

### Innovation & Technical Differentiation:
- **Dual-Layer Hybrid Intelligence:** Combines stochastic generative AI with deterministic symbolic verification. Solves the core trade-off between semantic flexibility and strict compliance.
- **Active Clarification vs. Passive Summarization:** Shifts the paradigm from passive reading to proactive project risk mitigation.

### Official Cirrascale Cloud Pricing & Unit Economics:
| Model | Context | Input Cost / 1M | Output Cost / 1M | Cost Per Meeting Analysis |
|---|---|---|---|---|
| **Llama3.1-8B** | 8K | **\$0.02** | **\$0.22** | **~\$0.00023** *(0.023¢)* |
| **Qwen-QwQ-32B** | 8K | **\$0.08** | **\$0.36** | **~\$0.00040** *(0.040¢)* |
| **DeepSeek-R1-70B** | 8K | **\$0.19** | **\$0.69** | **~\$0.00078** *(0.078¢)* |

### Grounding & Quality Control:
- **Verbatim Citations:** All extracted tasks, decisions, and risks must cite source quotes.
- **Reasoning Optimization:** Prompt constrained to `<50 words` of thinking, slashing latency from **75s down to 25s**.
- **Financial Viability:** Over **3,820 meeting analyses** possible within the \$3 budget. For an enterprise running 1,000 monthly meetings, the total AI compute bill is **under \$1.00 / month**.

### 🎙️ WHAT TO SAY (Speaker Script — 45s):
> *"We integrated directly with Cirrascale Qualcomm Cloud AI running DeepSeek-R1-Distill-70B for deep reasoning and Llama-3.1-8B for edge speed. By constraining the thinking phase to under 50 words, we reduced extraction time from 75 seconds to just 25 seconds. And look at the unit economics: on Cirrascale's official pricing, an entire meeting analysis costs less than a tenth of a cent. For a company running 1,000 meetings a month, the total AI compute bill is under $1.00!"*

---

## Slide 6: Future Enhancements, Scalability & Security
**Suggested Time:** 0:35

### Next Enhancements (Roadmap):
1. **Live Audio & On-Device NPU Transcription:** Integrate Whisper models running locally on Snapdragon X Elite NPU hardware.
2. **Two-Way Enterprise Integration:** Direct REST API connectors for Jira, Linear, Asana, and GitHub Issues.
3. **Automated Slack / Teams Bot:** Proactively pings owners on Slack to confirm tentative assignments or clarify vague deadlines.

### Scalability:
1. **Edge Deployment:** Export compiled models (ONNX / QNN) via Qualcomm AI Hub to run 100% on laptop NPUs with zero cloud costs.
2. **Stateless Microservices:** Containerized Docker deployment scaling horizontally on Kubernetes.
3. **Token Bucket Rate-Limiting:** Enterprise middleware handling 10,000+ concurrent summaries with exponential backoff.

### Security & Responsible AI:
1. **Zero Data Retention:** Transcripts parsed in-memory and immediately discarded. Never stored or used for model training.
2. **Credential Isolation:** Strict `.env` isolation; zero secrets committed to version control.
3. **Human-in-the-Loop Triage:** AI confidence indicators and manual status sign-off before downstream ticketing.

### 🎙️ WHAT TO SAY (Speaker Script — 35s):
> *"For enterprise scalability, MeetingMind AI is built with zero persistent transcript storage for complete GDPR compliance. On Qualcomm Snapdragon X Elite laptops, this can even run entirely on-device on the NPU with zero cloud exposure. Our immediate roadmap includes two-way ticketing synchronization into Jira and an automated Slack bot for follow-up nudges."*

---

## Slide 7: Live Demonstration (DEMO)
**Suggested Time:** 1:30–2:00

### Step-by-Step Live Walkthrough Checklist:
- [ ] **1. Health Check:** Show the sidebar status badge: **`🟢 Live AI: Configured`** connected to Cirrascale Qualcomm Cloud AI.
- [ ] **2. Model Selection:** Point out the active model dropdown (`DeepSeek-R1-Distill-Llama-70B` or `Llama-3.1-8B`).
- [ ] **3. Input Notes:** Paste the benchmark messy notes with tentative offers and vague dates.
- [ ] **4. Analyze:** Click **"🚀 Analyze Meeting"** (takes ~25–30s on live Qualcomm AI).
- [ ] **5. Action Items Tab:** Walk through the extracted tasks:
  - `Rahul`: Confirmed for Friday.
  - `Priya`: Marked tentative with status *Needs Clarification*.
  - `Deployment Plan`: Unassigned owner with deadline *"soon"*.
- [ ] **6. Accountability Tab (The Winning Feature):** Show the 4 flagged alerts and the generated clarification questions.
- [ ] **7. Decisions Tab:** Show how *Interface Review* is a Confirmed Decision, while *Database Selection* is flagged as an Undecided Proposal.
- [ ] **8. Status Triage:** Change a task status to *In Progress* directly in the dashboard.
- [ ] **9. Export:** Click **Download CSV** and **Download JSON** to show Jira/Asana readiness.

### Benchmark Verification Matrix (For Judges):
| Meeting Element | Raw Note Text | MeetingMind AI Output | Verification Status |
|---|---|---|---|
| **API Integration** | *"Rahul will finish the API integration by Friday."* | Owner: `Rahul` \| Due: `Friday` | ✅ **Confirmed** |
| **Testing** | *"Priya may handle testing, but has not confirmed yet."* | Owner: `Priya` \| Tentative: `True` | ⚠️ **Needs Clarification** |
| **Interface Review** | *"The team agreed to review the interface tomorrow."* | Status: `Confirmed Decision` | ✅ **Confirmed** |
| **Database Selection** | *"The database technology is still undecided."* | Status: `Undecided Technical Decision` | ⚠️ **Open Blocker** |
| **Deployment Plan** | *"The deployment plan needs to be finalized soon."* | Owner: `None` \| Due: `soon` | ⚠️ **Missing Owner & Vague Date** |

### 🎙️ TRANSITION TO LIVE DEMO:
> *"We will now switch directly to our running prototype at localhost:8501 to demonstrate live end-to-end extraction on Cirrascale Qualcomm Cloud AI hardware."*
