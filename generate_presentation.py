"""Script to generate the official Infosys Hack-AI-Thon PPTX Presentation.

Follows the official 7-slide Hack-AI-Thon template:
Slide 1: Team Introduction
Slide 2: Problem Statement
Slide 3: Proposed Solution
Slide 4: Architecture & Technical Design
Slide 5: AI Usage & Innovation
Slide 6: Future Enhancements, Scalability & Security
Slide 7: DEMO
"""

import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# 16:9 Widescreen dimensions
SLIDE_WIDTH = Inches(13.333)
SLIDE_HEIGHT = Inches(7.5)

# Color Palette (Corporate Modern SaaS)
COLOR_DARK_NAVY = RGBColor(15, 23, 42)      # #0F172A - Headers/Banners
COLOR_PRIMARY = RGBColor(79, 70, 229)       # #4F46E5 - Brand Indigo
COLOR_SECONDARY = RGBColor(37, 99, 235)     # #2563EB - Accent Blue
COLOR_SLATE_BG = RGBColor(248, 250, 252)    # #F8FAFC - Card Background
COLOR_WHITE = RGBColor(255, 255, 255)       # #FFFFFF
COLOR_BORDER = RGBColor(226, 232, 240)      # #E2E8F0 - Subtle Card Border
COLOR_TEXT_MAIN = RGBColor(30, 41, 59)      # #1E293B - Charcoal Dark
COLOR_TEXT_MUTED = RGBColor(100, 116, 139)  # #64748B - Subtext
COLOR_SUCCESS = RGBColor(22, 163, 74)       # #16A34A - Green
COLOR_WARNING = RGBColor(217, 119, 6)       # #D97706 - Amber/Warning
COLOR_CARD_BORDER = RGBColor(203, 213, 225) # #CBD5E1


def create_presentation():
    prs = Presentation()
    prs.slide_width = SLIDE_WIDTH
    prs.slide_height = SLIDE_HEIGHT
    blank_layout = prs.slide_layouts[6]  # completely blank layout

    def add_header(slide, title_text, category_text="HACK-AI-THON 2026", time_text=""):
        # Header background banner
        header_shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), SLIDE_WIDTH, Inches(1.1)
        )
        header_shape.fill.solid()
        header_shape.fill.fore_color.rgb = COLOR_DARK_NAVY
        header_shape.line.color.rgb = COLOR_DARK_NAVY

        # Category pill text
        tf_cat = slide.shapes.add_textbox(Inches(0.8), Inches(0.12), Inches(6), Inches(0.3)).text_frame
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = f"{category_text.upper()} • TRACK 3: ENGAGEMENT PLATFORMS"
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = COLOR_PRIMARY

        # Main Title text
        tf_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.38), Inches(9), Inches(0.6)).text_frame
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_WHITE

        # Time budget pill (right side)
        if time_text:
            tf_time = slide.shapes.add_textbox(Inches(9.8), Inches(0.35), Inches(2.8), Inches(0.4)).text_frame
            p_time = tf_time.paragraphs[0]
            p_time.alignment = PP_ALIGN.RIGHT
            p_time.text = f"SUGGESTED TIME: {time_text}"
            p_time.font.size = Pt(11)
            p_time.font.bold = True
            p_time.font.color.rgb = RGBColor(253, 224, 71)  # Yellow Accent

    def add_card(slide, left, top, width, height, title, bg_color=COLOR_SLATE_BG, border_color=COLOR_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.2)

        # Title strip
        if title:
            tf_t = slide.shapes.add_textbox(left + Inches(0.15), top + Inches(0.1), width - Inches(0.3), Inches(0.35)).text_frame
            p_t = tf_t.paragraphs[0]
            p_t.text = title.upper()
            p_t.font.size = Pt(11)
            p_t.font.bold = True
            p_t.font.color.rgb = COLOR_PRIMARY

        # Return text frame positioned below title
        tf_body = slide.shapes.add_textbox(
            left + Inches(0.18),
            top + (Inches(0.42) if title else Inches(0.12)),
            width - Inches(0.36),
            height - (Inches(0.5) if title else Inches(0.24))
        ).text_frame
        tf_body.word_wrap = True
        return tf_body

    def set_speaker_notes(slide, notes_text):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = notes_text

    # =========================================================================
    # SLIDE 1: Team Introduction (0:20)
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    add_header(slide1, "Team Introduction & Project Overview", "HACK-AI-THON 2026", "0:20")

    # Hero card on Left
    card_hero = add_card(slide1, Inches(0.8), Inches(1.4), Inches(6.8), Inches(4.5), "Project Identity", bg_color=COLOR_WHITE)
    p = card_hero.paragraphs[0]
    p.text = "MeetingMind AI"
    p.font.size = Pt(30)
    p.font.bold = True
    p.font.color.rgb = COLOR_DARK_NAVY

    p2 = card_hero.add_paragraph()
    p2.text = "“Turn meeting conversations into accountable action.”"
    p2.font.size = Pt(14)
    p2.font.italic = True
    p2.font.color.rgb = COLOR_PRIMARY
    p2.space_after = Pt(14)

    p3 = card_hero.add_paragraph()
    p3.text = "A dual-layer intelligence platform that eliminates meeting ambiguity. Combines Qualcomm Cloud AI generative extraction with a deterministic Python validation engine to enforce strict ownership, deadline accountability, and zero hallucination."
    p3.font.size = Pt(12)
    p3.font.color.rgb = COLOR_TEXT_MAIN
    p3.space_after = Pt(14)

    p4 = card_hero.add_paragraph()
    p4.text = "SELECTED PROBLEM STATEMENT: EP-01 (Smart Meeting Action Extractor)"
    p4.font.size = Pt(12)
    p4.font.bold = True
    p4.font.color.rgb = COLOR_DARK_NAVY

    p5 = card_hero.add_paragraph()
    p5.text = "TECHNOLOGY TRACK: Qualcomm Cloud AI Playground (Cirrascale Inference Cloud)"
    p5.font.size = Pt(12)
    p5.font.bold = True
    p5.font.color.rgb = COLOR_SUCCESS

    # Team Card on Right
    card_team = add_card(slide1, Inches(7.8), Inches(1.4), Inches(4.7), Inches(4.5), "Team Profile & Track Info", bg_color=COLOR_WHITE)
    pt1 = card_team.paragraphs[0]
    pt1.text = "TEAM NAME: Team MeetingMind"
    pt1.font.size = Pt(14)
    pt1.font.bold = True
    pt1.font.color.rgb = COLOR_DARK_NAVY
    pt1.space_after = Pt(10)

    pt2 = card_team.add_paragraph()
    pt2.text = "TEAM MEMBERS:"
    pt2.font.size = Pt(12)
    pt2.font.bold = True
    pt2.font.color.rgb = COLOR_TEXT_MUTED

    members = [
        "• Kowshik Ghanta (Full-Stack & AI Systems Lead)",
        "• Team Member 2 (AI Engineer)",
        "• Team Member 3 (Product & QA)"
    ]
    for m in members:
        pm = card_team.add_paragraph()
        pm.text = m
        pm.font.size = Pt(11)
        pm.font.color.rgb = COLOR_TEXT_MAIN

    pt3 = card_team.add_paragraph()
    pt3.text = "\nCOLLEGE / INSTITUTION:"
    pt3.font.size = Pt(12)
    pt3.font.bold = True
    pt3.font.color.rgb = COLOR_TEXT_MUTED

    pinst = card_team.add_paragraph()
    pinst.text = "Infosys IGNITE ENG NEXT 2026 • Hack-AI-Thon"
    pinst.font.size = Pt(11)
    pinst.font.color.rgb = COLOR_TEXT_MAIN

    # Bottom Banner (What to Say)
    card_wts1 = add_card(slide1, Inches(0.8), Inches(6.1), Inches(11.7), Inches(1.0), "WHAT TO SAY (20 SECONDS)", bg_color=COLOR_DARK_NAVY, border_color=COLOR_PRIMARY)
    pw1 = card_wts1.paragraphs[0]
    pw1.text = "“Good morning judges! We are Team MeetingMind presenting Problem EP-01: Smart Meeting Action Extractor in the Qualcomm Cloud AI track. We built MeetingMind AI to solve the massive accountability gap in post-meeting follow-ups using Qualcomm hardware and a deterministic zero-hallucination engine.”"
    pw1.font.size = Pt(11)
    pw1.font.color.rgb = COLOR_WHITE

    set_speaker_notes(slide1, "Introduce your team, problem statement EP-01, and Qualcomm track under 20 seconds. Emphasize that you have a functional, tested prototype connected live to Qualcomm Cloud AI.")

    # =========================================================================
    # SLIDE 2: Problem Statement (0:50)
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, "Problem Statement: The Accountability Crisis in Meeting Notes", "EP-01 FOCUS", "0:50")

    # Grid of 4 Cards
    c1 = add_card(slide2, Inches(0.8), Inches(1.3), Inches(5.7), Inches(2.3), "Actual Problem Statement & Scope", bg_color=COLOR_WHITE)
    p = c1.paragraphs[0]
    p.text = "EP-01: Smart Meeting Action Extractor"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_DARK_NAVY
    p_sub = c1.add_paragraph()
    p_sub.text = "Convert unstructured, messy meeting transcripts into structured decisions, accountable action items, designated owners, unambiguous deadlines, and project risks."
    p_sub.font.size = Pt(11)
    p_sub.font.color.rgb = COLOR_TEXT_MAIN

    c2 = add_card(slide2, Inches(6.8), Inches(1.3), Inches(5.7), Inches(2.3), "Who is Affected & Why It Matters", bg_color=COLOR_WHITE)
    p = c2.paragraphs[0]
    p.text = "• Primary Stakeholders: Engineering teams, sprint leads, project managers, enterprise stakeholders."
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_TEXT_MAIN
    p2 = c2.add_paragraph()
    p2.text = "• Business Impact: Over 30% of employee time is spent in meetings. Up to 40% of deliverables are delayed because notes lack explicit owners, deadlines are vague, or proposals are mistaken for agreements."
    p2.font.size = Pt(11)
    p2.font.color.rgb = COLOR_TEXT_MAIN

    c3 = add_card(slide2, Inches(0.8), Inches(3.8), Inches(5.7), Inches(2.1), "Current Gap & Baseline Evidence", bg_color=COLOR_WHITE)
    p = c3.paragraphs[0]
    p.text = "• Current Gap: Existing tools (Zoom AI, standard LLMs) generate generic narrative summaries. When forced to extract tasks, they hallucinate owners or guess dates."
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_TEXT_MAIN
    p2 = c3.add_paragraph()
    p2.text = "• Scenario: 'Priya may handle testing, but hasn't confirmed yet. Deployment plan needed soon.' Baseline AI marks Priya as confirmed owner and invents a calendar date."
    p2.font.size = Pt(10.5)
    p2.font.color.rgb = COLOR_WARNING

    c4 = add_card(slide2, Inches(6.8), Inches(3.8), Inches(5.7), Inches(2.1), "Definition of Success", bg_color=COLOR_WHITE)
    p = c4.paragraphs[0]
    p.text = "1. Strict Zero-Hallucination Extraction: Verbatim evidence citations.\n2. Explicit Null-Handling: Unassigned owners & unstated dates marked null.\n3. Proactive Clarification: Auto-generates targeted follow-up questions.\n4. Export Readiness: One-click Jira/Asana CSV and schema-validated JSON."
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_TEXT_MAIN

    card_wts2 = add_card(slide2, Inches(0.8), Inches(6.1), Inches(11.7), Inches(1.0), "WHAT TO SAY (50 SECONDS)", bg_color=COLOR_DARK_NAVY, border_color=COLOR_PRIMARY)
    pw = card_wts2.paragraphs[0]
    pw.text = "“Meetings produce unstructured chaos. Standard LLMs try to be 'helpful' by guessing missing owners and fabricating dates. For EP-01, success isn't just summarizing text—it's establishing real accountability. We prove this with a real scenario where tentative offers and undecided architecture forks are caught deterministically.”"
    pw.font.size = Pt(11)
    pw.font.color.rgb = COLOR_WHITE

    set_speaker_notes(slide2, "Focus on the current gap: existing AI tools invent facts when notes are messy. Highlight the benchmark meeting notes and how MeetingMind AI refuses to guess.")

    # =========================================================================
    # SLIDE 3: Proposed Solution (0:55)
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, "Proposed Solution: MeetingMind AI", "END-TO-END WORKFLOW", "0:55")

    # Banner: Solution in one sentence
    banner = add_card(slide3, Inches(0.8), Inches(1.3), Inches(11.7), Inches(0.8), "", bg_color=COLOR_PRIMARY)
    pb = banner.paragraphs[0]
    pb.text = "SOLUTION IN ONE SENTENCE: An AI-powered SaaS dashboard that pairs Qualcomm Cloud AI extraction with a deterministic Python validation engine to convert messy meeting notes into accountable action items with zero hallucination."
    pb.font.size = Pt(12)
    pb.font.bold = True
    pb.font.color.rgb = COLOR_WHITE

    # 3 Column Process Flow
    col_w = Inches(3.7)
    gap = Inches(0.3)

    # Step 1: Input
    c_in = add_card(slide3, Inches(0.8), Inches(2.3), col_w, Inches(3.6), "1. INPUT (User Data)", bg_color=COLOR_WHITE)
    p = c_in.paragraphs[0]
    p.text = "• Raw Unstructured Text:\n  Meeting notes, voice transcript excerpts, chat snippets, or bullet points.\n\n• Optional Metadata:\n  Meeting Title & Calendar Date.\n\n• Zero-Token Demo Mode:\n  1-click bundled benchmark notes for immediate offline evaluation."
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_TEXT_MAIN

    # Step 2: Process
    c_proc = add_card(slide3, Inches(0.8) + col_w + gap, Inches(2.3), col_w, Inches(3.6), "2. PROCESS (Dual Layer)", bg_color=COLOR_WHITE)
    p = c_proc.paragraphs[0]
    p.text = "• Layer 1: Qualcomm Cloud AI\n  Hardware-accelerated generative inference (DeepSeek-R1-70B / Llama-3.1-8B) with negative constraints.\n\n• Layer 2: Deterministic Validation\n  Independent Python rules engine auditing owners, deadlines, tentative flags, and vague words.\n\n• Budget Guard:\n  Strictly 1 inference call per run ($3 budget protection)."
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_TEXT_MAIN

    # Step 3: Output
    c_out = add_card(slide3, Inches(0.8) + (col_w + gap) * 2, Inches(2.3), col_w, Inches(3.6), "3. OUTPUT (Accountability)", bg_color=COLOR_WHITE)
    p = c_out.paragraphs[0]
    p.text = "• Interactive Action Table:\n  Searchable, filterable by priority/owner, with in-session status triage.\n\n• Accountability Warnings:\n  Identifies unassigned tasks & generates exact clarification questions.\n\n• Decision Isolation:\n  Separates confirmed decisions from tentative proposals.\n\n• Export: CSV (Jira/Asana) & JSON."
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_TEXT_MAIN

    card_wts3 = add_card(slide3, Inches(0.8), Inches(6.1), Inches(11.7), Inches(1.0), "WHAT TO SAY (55 SECONDS)", bg_color=COLOR_DARK_NAVY, border_color=COLOR_PRIMARY)
    pw = card_wts3.paragraphs[0]
    pw.text = "“Our solution takes raw transcripts, processes them through a dual-layer engine, and delivers interactive action tables. The AI extracts evidence-backed entities; then our deterministic layer audits the output. The key differentiator is that instead of hallucinating missing data, it alerts the manager with the exact question to ask.”"
    pw.font.size = Pt(11)
    pw.font.color.rgb = COLOR_WHITE

    set_speaker_notes(slide3, "Explain the 3-step pipeline: Input -> Dual-Layer Process -> Actionable Output. Emphasize that the working prototype is live and demonstrable today.")

    # =========================================================================
    # SLIDE 4: Architecture & Technical Design (0:55)
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, "Architecture & Technical Design", "SYSTEM ARCHITECTURE", "0:55")

    # 4 Architecture Blocks
    b_w = Inches(2.75)
    b_gap = Inches(0.2)

    b1 = add_card(slide4, Inches(0.8), Inches(1.3), b_w, Inches(2.4), "USER / CLIENT", bg_color=COLOR_WHITE)
    p = b1.paragraphs[0]
    p.text = "• Streamlit UI\n• Responsive SaaS Layout\n• Session State Manager\n• Real-Time Task Filters\n• In-Browser Status Editing"
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_TEXT_MAIN

    b2 = add_card(slide4, Inches(0.8) + (b_w + b_gap), Inches(1.3), b_w, Inches(2.4), "APPLICATION LOGIC", bg_color=COLOR_WHITE)
    p = b2.paragraphs[0]
    p.text = "• BaseAIProvider Interface\n• Pydantic v2 Schema Layer\n• Deterministic Rules Engine\n• Lexical Pattern Matchers\n• Pandas Tabular Pipeline"
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_TEXT_MAIN

    b3 = add_card(slide4, Inches(0.8) + (b_w + b_gap) * 2, Inches(1.3), b_w, Inches(2.4), "AI / INFERENCE LAYER", bg_color=COLOR_WHITE)
    p = b3.paragraphs[0]
    p.text = "• Cirrascale Qualcomm Cloud\n• DeepSeek-R1-Distill-70B\n• Llama-3.1-8B Edge Fallback\n• OpenAI-Compliant REST API\n• Dual Auth (Bearer + x-api-key)"
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_TEXT_MAIN

    b4 = add_card(slide4, Inches(0.8) + (b_w + b_gap) * 3, Inches(1.3), b_w, Inches(2.4), "OUTPUT & ACTION", bg_color=COLOR_WHITE)
    p = b4.paragraphs[0]
    p.text = "• Triage Action Dashboard\n• Jira / Asana CSV Export\n• Machine-Readable JSON\n• Clarification Question Box\n• Session-Bound State Store"
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_TEXT_MAIN

    # Bottom Row: Engineering Rationale & Validation
    c_rat = add_card(slide4, Inches(0.8), Inches(3.9), Inches(5.7), Inches(2.0), "Engineering Choices & Rationale", bg_color=COLOR_WHITE)
    p = c_rat.paragraphs[0]
    p.text = "• Streamlit + Python 3.12: Fast native execution without microservice latency.\n• Single-Request Invariant: Guarantees staying within the $3 budget by enforcing exactly 1 inference request per meeting analysis.\n• Dual-Layer Separation: LLM handles linguistics; deterministic code enforces business integrity."
    p.font.size = Pt(10.5)
    p.font.color.rgb = COLOR_TEXT_MAIN

    c_val = add_card(slide4, Inches(6.8), Inches(3.9), Inches(5.7), Inches(2.0), "Validation, Testing & Reliability", bg_color=COLOR_WHITE)
    p = c_val.paragraphs[0]
    p.text = "• 30 Automated Pytest Tests (100% Pass Rate):\n  - Tests schemas, missing owners, vague deadlines, duplicate detection.\n  - Mocked network tests: 401 Unauthorized, 429 Rate Limit, timeouts.\n• Resilient Fallback: If network drops, offline benchmark mode activates with zero token cost."
    p.font.size = Pt(10.5)
    p.font.color.rgb = COLOR_TEXT_MAIN

    card_wts4 = add_card(slide4, Inches(0.8), Inches(6.1), Inches(11.7), Inches(1.0), "WHAT TO SAY (55 SECONDS)", bg_color=COLOR_DARK_NAVY, border_color=COLOR_PRIMARY)
    pw = card_wts4.paragraphs[0]
    pw.text = "“Walking left to right through our architecture: the user interacts with our Streamlit frontend. The request routes to Cirrascale's Qualcomm Cloud AI hardware running DeepSeek-R1. We enforce a Single-Request Invariant to protect the $3 budget. Our test suite includes 30 unit tests covering network drops, 401s, 429s, and edge cases.”"
    pw.font.size = Pt(11)
    pw.font.color.rgb = COLOR_WHITE

    set_speaker_notes(slide4, "Highlight the 4 architectural blocks. Mention the 30 Pytest unit tests and the Single-Request Invariant designed specifically to respect the $3 hackathon budget.")

    # =========================================================================
    # SLIDE 5: AI Usage & Innovation (0:45)
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, "AI Usage, Innovation & Unit Economics", "QUALCOMM CLOUD AI DEEP DIVE", "0:45")

    # 4 Cards Grid
    ai1 = add_card(slide5, Inches(0.8), Inches(1.3), Inches(5.7), Inches(2.3), "AI Capability & Hardware Integration", bg_color=COLOR_WHITE)
    p = ai1.paragraphs[0]
    p.text = "• Qualcomm Cloud AI (Cirrascale Inference Cloud):\n  Connected to live hardware-accelerated OpenAI-compliant endpoints.\n• Models Deployed & Verified:\n  1. DeepSeek-R1-Distill-Llama-70B (Deep reasoning & structured extraction)\n  2. Llama-3.1-8B (High-throughput edge tier)\n• Hardware Advantage: High inference throughput and low energy per token."
    p.font.size = Pt(10.5)
    p.font.color.rgb = COLOR_TEXT_MAIN

    ai2 = add_card(slide5, Inches(6.8), Inches(1.3), Inches(5.7), Inches(2.3), "Core Technical Innovation", bg_color=COLOR_WHITE)
    p = ai2.paragraphs[0]
    p.text = "• Dual-Layer Hybrid Intelligence:\n  Pure LLMs hallucinate; pure regex fails at semantic understanding. We combine both: LLM extracts verbatim context; deterministic code enforces accountability.\n• Active Clarification vs Passive Summary:\n  Instead of generating text, it formulates targeted questions for unresolved technical forks and ambiguous owners."
    p.font.size = Pt(10.5)
    p.font.color.rgb = COLOR_TEXT_MAIN

    ai3 = add_card(slide5, Inches(0.8), Inches(3.8), Inches(5.7), Inches(2.1), "Cirrascale Live Pricing & Unit Economics", bg_color=COLOR_WHITE)
    p = ai3.paragraphs[0]
    p.text = "• Official Cirrascale Cloud Pricing:\n  - Llama3.1-8B: $0.02 / 1M input | $0.22 / 1M output\n  - DeepSeek-R1-70B: $0.19 / 1M input | $0.69 / 1M output\n• Cost Per Meeting: ~$0.00078 on 70B (< 1/10th of a cent!)\n• Budget Capacity: Over 3,820 meeting runs within the $3 budget!\n• 1,000 monthly meetings cost under $1.00 in AI compute."
    p.font.size = Pt(10.5)
    p.font.color.rgb = COLOR_TEXT_MAIN

    ai4 = add_card(slide5, Inches(6.8), Inches(3.8), Inches(5.7), Inches(2.1), "Quality Check & Grounding", bg_color=COLOR_WHITE)
    p = ai4.paragraphs[0]
    p.text = "• Verbatim Citation Enforcement: Every task, decision, and risk must quote original note sentences.\n• Reasoning Optimization: Prompt constrained to <50 words of thinking, cutting latency from 75s to 25s.\n• Pydantic Type Enforcement: Automatic normalization of dates, priorities, confidence scores, and enums."
    p.font.size = Pt(10.5)
    p.font.color.rgb = COLOR_TEXT_MAIN

    card_wts5 = add_card(slide5, Inches(0.8), Inches(6.1), Inches(11.7), Inches(1.0), "WHAT TO SAY (45 SECONDS)", bg_color=COLOR_DARK_NAVY, border_color=COLOR_PRIMARY)
    pw = card_wts5.paragraphs[0]
    pw.text = "“We use Qualcomm Cloud AI running DeepSeek-R1-Distill-70B for deep reasoning and Llama-3.1-8B for edge speed. Because we optimized prompt conciseness, extraction completes in 25 seconds. And look at the unit economics: on Cirrascale's official pricing, an entire meeting analysis costs less than a tenth of a cent—under $1 a month for 1,000 meetings!”"
    pw.font.size = Pt(11)
    pw.font.color.rgb = COLOR_WHITE

    set_speaker_notes(slide5, "Deliver the unit economics punchline: $0.00078 per meeting on Qualcomm hardware. Explain why pure rules or pure LLMs fail, and why this hybrid approach wins.")

    # =========================================================================
    # SLIDE 6: Future Enhancements, Scalability & Security (0:35)
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    add_header(slide6, "Scalability, Security & Future Roadmap", "PRODUCTION HORIZON", "0:35")

    # 3 Vertical Columns
    c_w = Inches(3.7)
    c_gap = Inches(0.3)

    # Next Enhancements
    r1 = add_card(slide6, Inches(0.8), Inches(1.3), c_w, Inches(4.6), "Next Enhancements", bg_color=COLOR_WHITE)
    p = r1.paragraphs[0]
    p.text = "1. Live Audio & Real-Time NPU Transcription:\nIntegrate on-device Whisper transcription running locally on Snapdragon X Elite NPU hardware.\n\n2. Two-Way Enterprise Sync:\nDirect API integrations to push action items into Jira, Linear, Asana, and GitHub Issues.\n\n3. Automated Slack / Teams Bot:\nNudges owners directly on Slack to confirm tentative commitments or clarify vague deadlines."
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_TEXT_MAIN

    # Scalability
    r2 = add_card(slide6, Inches(0.8) + c_w + c_gap, Inches(1.3), c_w, Inches(4.6), "Scalability & Deployment", bg_color=COLOR_WHITE)
    p = r2.paragraphs[0]
    p.text = "1. Microservice Containerization:\nDockerized stateless architecture deployable on Kubernetes across multi-tenant enterprise clusters.\n\n2. Edge & On-Device Processing:\nExport compiled ONNX/QNN models to run entirely on laptop NPUs via Qualcomm AI Hub with 0 cloud cost.\n\n3. High Throughput Rate-Limiting:\nToken bucket algorithm with exponential backoff handling 10,000+ concurrent meeting summaries."
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_TEXT_MAIN

    # Security & Responsible AI
    r3 = add_card(slide6, Inches(0.8) + (c_w + c_gap) * 2, Inches(1.3), c_w, Inches(4.6), "Security & Responsible AI", bg_color=COLOR_WHITE)
    p = r3.paragraphs[0]
    p.text = "1. Zero Data Retention:\nTranscripts are parsed in-memory and immediately purged. No meeting data stored or used for retraining.\n\n2. Credential Isolation:\nAll Qualcomm API keys encrypted via environment variables with zero secrets committed.\n\n3. Transparent Confidence & Human Triage:\nEvery AI-suggested task requires human status sign-off before downstream ticketing export."
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_TEXT_MAIN

    card_wts6 = add_card(slide6, Inches(0.8), Inches(6.1), Inches(11.7), Inches(1.0), "WHAT TO SAY (35 SECONDS)", bg_color=COLOR_DARK_NAVY, border_color=COLOR_PRIMARY)
    pw = card_wts6.paragraphs[0]
    pw.text = "“For enterprise scalability, we designed MeetingMind AI with zero persistent transcript storage for GDPR compliance. On Qualcomm Snapdragon X Elite devices, this can even run 100% on-device on the NPU. Our next milestone is two-way synchronization into Jira and a Slack clarification bot.”"
    pw.font.size = Pt(11)
    pw.font.color.rgb = COLOR_WHITE

    set_speaker_notes(slide6, "Highlight data privacy (zero transcript retention) and edge scalability (running on Snapdragon NPUs). Present a realistic next step: Slack integration and Jira API sync.")

    # =========================================================================
    # SLIDE 7: Live Demonstration (DEMO)
    # =========================================================================
    slide7 = prs.slides.add_slide(blank_layout)
    add_header(slide7, "LIVE DEMONSTRATION: MeetingMind AI in Action", "PROTOTYPE SHOWCASE", "DEMO TIME")

    # Left: Demo Checklist & Steps
    d_left = add_card(slide7, Inches(0.8), Inches(1.3), Inches(6.8), Inches(4.6), "Live Demo Walkthrough Checklist", bg_color=COLOR_WHITE)
    p = d_left.paragraphs[0]
    p.text = "STEP-BY-STEP LIVE VERIFICATION (http://localhost:8501):"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_DARK_NAVY

    demo_steps = [
        "1. Sidebar Health Check: Live AI Configured with Cirrascale Qualcomm Cloud AI.",
        "2. Input Notes: Load messy benchmark notes with unassigned work & ambiguous dates.",
        "3. Live Inference: Execute extraction using DeepSeek-R1 on Qualcomm hardware.",
        "4. Action Dashboard: Review Task Table with Priority, Owner, and Status filters.",
        "5. Accountability Tab: Highlight flagged unassigned tasks & generated questions.",
        "6. Decision Triage: Review confirmed decisions vs undecided technical forks.",
        "7. Export Deliverables: 1-click download of Jira-ready CSV and JSON schema."
    ]
    for s in demo_steps:
        ps = d_left.add_paragraph()
        ps.text = s
        ps.font.size = Pt(10.5)
        ps.font.color.rgb = COLOR_TEXT_MAIN
        ps.space_after = Pt(4)

    # Right: Benchmark Expected Outcomes
    d_right = add_card(slide7, Inches(7.8), Inches(1.3), Inches(4.7), Inches(4.6), "Benchmark Verification Matrix", bg_color=COLOR_WHITE)
    p = d_right.paragraphs[0]
    p.text = "WHAT THE JUDGES WILL SEE:"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY

    matrix = [
        ("Rahul (API Integration)", "Confirmed (Due: Friday)", COLOR_SUCCESS),
        ("Priya (Testing)", "Tentative Flag ('Not confirmed')", COLOR_WARNING),
        ("Deployment Plan", "Missing Owner + Vague Date ('soon')", COLOR_WARNING),
        ("Database Tech", "Undecided Technical Decision", COLOR_WARNING),
        ("Interface Review", "Confirmed Decision ('tomorrow')", COLOR_SUCCESS),
        ("Test Suite", "30 Pytest Tests Passing (100%)", COLOR_SUCCESS),
    ]
    for item, status, col in matrix:
        pm = d_right.add_paragraph()
        pm.text = f"• {item}: "
        pm.font.size = Pt(10.5)
        pm.font.color.rgb = COLOR_TEXT_MAIN
        # add colored status
        run = pm.add_run()
        run.text = status
        run.font.bold = True
        run.font.color.rgb = col
        pm.space_after = Pt(6)

    card_wts7 = add_card(slide7, Inches(0.8), Inches(6.1), Inches(11.7), Inches(1.0), "TRANSITION TO LIVE DEMO", bg_color=COLOR_DARK_NAVY, border_color=COLOR_PRIMARY)
    pw = card_wts7.paragraphs[0]
    pw.text = "“We will now switch directly to our running prototype at localhost:8501 to demonstrate live end-to-end extraction on Cirrascale Qualcomm Cloud AI hardware.”"
    pw.font.size = Pt(12)
    pw.font.bold = True
    pw.font.color.rgb = RGBColor(253, 224, 71)

    set_speaker_notes(slide7, "Switch screens to localhost:8501. Click 'Load Realistic Sample Notes' or paste notes, click 'Analyze Meeting', and walk through the tabs.")

    # Save presentation
    output_path = "MeetingMind_AI_Presentation.pptx"
    prs.save(output_path)
    print(f"Presentation saved successfully to: {output_path}")


if __name__ == "__main__":
    create_presentation()
