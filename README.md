# MeetingMind AI — Smart Meeting Action Extractor

> **"Turn meeting conversations into accountable action."**  
> *Developed for the Infosys Hack-AI-Thon*

MeetingMind AI is an AI-powered meeting intelligence system designed to convert unstructured, messy meeting transcripts and notes into structured, accountable deliverables. It features a unique **dual-layer analysis architecture**: high-accuracy generative extraction paired with a **deterministic validation engine** that flags missing owners, vague deadlines, tentative commitments, and unresolved architecture decisions without hallucination.

### 📚 Hackathon Presentation & Technical Resources
- 🎤 **[Hackathon Presentation & Pitch Playbook](docs/HACKATHON_PRESENTATION_GUIDE.md)**: 30s & 2min elevator pitches, slide-by-slide guide, live demo script, and judge Q&A defenses.
- 📐 **[Technical Architecture & Decisions](docs/ARCHITECTURE_AND_TECHNICAL_DECISIONS.md)**: Engineering blueprint, prompt design, deterministic heuristics, and Qualcomm Cloud AI integration.

---

## 1. Problem Statement & Key Value

Modern engineering and product teams conduct numerous meetings daily, resulting in raw notes with buried action items. Common points of failure include:
- Tasks assigned to nobody (or vague entities like "we" or "someone").
- Timelines defined only as "soon", "later", or "tomorrow" with no calendar reference.
- Tentative or provisional ownership assumed to be a confirmed commitment.
- Undecided architectural choices mistaken for firm agreements.

MeetingMind AI answers:
1. **What happened in the meeting?** (Executive summary and key topics)
2. **What decisions were made?** (Strictly separating confirmed decisions from tentative proposals)
3. **What actions need to be completed?** (Action item dashboard with status workflows)
4. **Who is responsible for each action?** (Directly attributed owners, explicitly flagging unassigned work)
5. **When is each action due?** (Preserving original deadline nuances)
6. **Which commitments are unclear or incomplete?** (Missing-information & accountability warnings)
7. **What risks or unresolved questions require follow-up?** (Follow-up suggestions and risk mitigations)

---

## 2. Architecture & Data Flow

```
+-------------------------------------------------------------------------+
|                              USER INTERFACE                             |
|        Streamlit Dashboard (Search, Filter, Edit Status, Export)         |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                           PROMPT & PARSING                              |
|   Strict JSON contract, markdown fence stripping, Pydantic validation    |
+--------------------+----------------------------------------------------+
                     |
                     +---------------------------------------+
                     |                                       |
                     v                                       v
        [ LIVE AI MODE ]                            [ DEMO / SAMPLE MODE ]
+------------------------------------+    +------------------------------------+
|      QualcommAIProvider            |    |       Pre-computed Sample Data     |
| - Endpoint: Qualcomm AI Playground |    | - Deterministic benchmark notes    |
| - OpenAI-compatible Chat Compl.    |    | - Zero network or credit usage     |
| - Single-request budget protection |    | - Explicitly labeled sample data   |
| - Full error handling (401/429/etc)|    +-----------------+------------------+
+--------------------+---------------+                      |
                     |                                      |
                     +-------------------+------------------+
                                         |
                                         v
+-------------------------------------------------------------------------+
|                     DETERMINISTIC VALIDATION LAYER                      |
|  - Flags missing owners & deadlines                                     |
|  - Catches tentative words ("may", "has not confirmed yet")             |
|  - Identifies vague timelines ("soon", "asap")                          |
|  - Isolates undecided decisions ("database technology is undecided")   |
|  - Detects duplicate/overlapping tasks                                  |
|  - Generates targeted clarification questions                           |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                      STRUCTURED EXPORT & WORKFLOW                       |
|           CSV Table Export  |  JSON Analysis  |  Session State          |
+-------------------------------------------------------------------------+
```

---

## 3. Technology Stack

- **Python 3.11+** (Tested on Python 3.12)
- **Streamlit**: SaaS-style interactive dashboard
- **Pandas**: Tabular data manipulation and CSV export
- **Requests**: HTTP client for AI inference endpoints
- **Pydantic v2**: Strict schema validation and data normalization
- **Pytest**: Automated test suite
- **python-dotenv**: Secure environment configuration

---

## 4. Prerequisites & Installation

### Prerequisites
- Python 3.11 or higher installed on your system.
- Git (optional, for cloning).

### Step 1: Clone or Open Workspace
```bash
cd "d:\Infosys hackathon"
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Copy `.env.example` to `.env`:

On Windows PowerShell:
```powershell
Copy-Item .env.example .env
```
On Linux/macOS:
```bash
cp .env.example .env
```

Edit `.env` to supply your credentials (see next section).

### Step 4: Run the Application
```bash
streamlit run app.py
```
The dashboard will open automatically at `http://localhost:8501`.

---

## 5. Qualcomm Cloud AI / Cirrascale Inference Cloud Integration

### Configuration Variables (`.env`)
The application supports your Cirrascale Inference Cloud portal directly (`https://aisuite.cirrascale.com/account/api-keys`):

| Variable | Description | Default / Example |
|---|---|---|
| `INFERENCE_CLOUD_API_KEY` | Your personal API key copied from Cirrascale Inference Cloud. | `00d216...` *(Required for Live AI)* |
| `INFERENCE_CLOUD_ENDPOINT` | Base URL for the Qualcomm Cloud AI inference endpoint. | `https://aisuite.cirrascale.com/apis/v2` |
| `QUALCOMM_MODEL_NAME` | Model identifier deployed on Qualcomm hardware. | `llama-3.1-8B` |
| `QUALCOMM_TIMEOUT_SECONDS` | Network request timeout in seconds. | `45` |
| `QUALCOMM_API_KEY` | *(Alternative)* Synonym for `INFERENCE_CLOUD_API_KEY`. | `your_key_here` |
| `QUALCOMM_API_BASE_URL` | *(Alternative)* Synonym for `INFERENCE_CLOUD_ENDPOINT`. | `https://aisuite.cirrascale.com/apis/v2` |
| `IMAGINE_API_KEY` | *(Alternative)* Synonym for Imagine SDK. | `your_key_here` |
| `IMAGINE_ENDPOINT_URL` | *(Alternative)* Synonym for Imagine SDK. | `https://aisuite.cirrascale.com/apis/v2` |

### How It Works
- The `QualcommAIProvider` communicates with Qualcomm's AI Inference Suite using standard OpenAI-compatible JSON over HTTP POST (`/chat/completions`).
- **Single Request Efficiency**: To respect the **\$3 hackathon credit budget**, the application conducts **exactly one** structured extraction call per analysis. It never makes redundant calls or polling loops.
- **Fail-Safe Diagnostics**: The sidebar includes a lightweight "Test Connection Ping" button to verify credentials without processing a full meeting.

### Error Handling
- **HTTP 401 / 403**: Displays an authentication error explaining that credentials in `.env` are invalid or lack model access.
- **HTTP 429**: Displays a quota/budget alert explaining that the \$3 credit budget or rate limit was exhausted.
- **Timeouts**: Gracefully flags slow inference requests without crashing.
- **Connection Errors**: Notifies user of network/endpoint unreachability.

---

## 6. Demo / Sample Mode (Zero-Credential Verification)

If you do not have active Qualcomm AI Playground credentials, you can still evaluate the complete application:

1. Click **"📋 Load Realistic Sample Notes"** on the dashboard.
2. The benchmark meeting notes will be loaded:
   > *"The project team met to review the dashboard release. Rahul will finish the API integration by Friday. Priya may handle testing, but she has not confirmed yet. The team agreed to review the interface tomorrow. The database technology is still undecided. The deployment plan needs to be finalized soon."*
3. The dashboard executes the verified deterministic pipeline:
   - **Rahul**: Confirmed owner for API integration with Friday deadline.
   - **Priya**: Tentative assignment flagged (`Priya may handle testing, but has not confirmed yet`).
   - **Interface Review**: Confirmed decision for tomorrow.
   - **Database Technology**: Undecided decision flagged as an open blocker.
   - **Deployment Plan**: Unassigned task with vague timeline (`soon`) flagged for clarification.
4. The dashboard displays an explicit label: **`🟡 Sample Data — Not Live AI Output`**.

---

## 7. Running the Test Suite

A comprehensive test suite of 30 unit tests is included, testing:
- Pydantic schema validation & normalization
- Deterministic detection of missing owners, deadlines, tentative flags, and vague words
- Markdown JSON stripping and malformed response resilience
- Mocked Qualcomm API calls (auth failures, 429 quotas, timeouts, network drops)
- CSV and JSON export data integrity

Run tests with:
```bash
python -m pytest -v
```

---

## 8. Limitations & Known Failure Cases

1. **Credit Allocation**: Qualcomm AI Playground accounts are constrained by the \$3 credit tier. Large transcripts exceeding context windows may fail or consume credits quickly. Keep transcripts concise (under 2,500 words).
2. **Ambiguous Relative Dates**: Without a specified meeting date, expressions like "tomorrow" or "next Friday" cannot be accurately mapped to a calendar date. MeetingMind AI intentionally preserves original text rather than guessing.
3. **Session-Bound UI Edits**: Task status modifications performed in the UI are persisted in `st.session_state` during the active session. If the user refreshes or reloads the browser, overrides revert to the model's extracted state unless exported to CSV/JSON.
