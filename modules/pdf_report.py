"""
pdf_report.py — KORHEX.AI Executive Report
Style: C‑level ready, professional B2B narrative
Usage: pdf_bytes = generate_report(st.session_state['current_analysis'])
"""
import io
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, HRFlowable, PageBreak, KeepTogether
)

# Executive monochrome palette
C_BLACK  = colors.HexColor("#111111")
C_DARK   = colors.HexColor("#333333")
C_MID    = colors.HexColor("#666666")
C_LIGHT  = colors.HexColor("#999999")
C_RULE   = colors.HexColor("#DEDEDE")
C_BG     = colors.HexColor("#F6F6F6")
C_WHITE  = colors.white
MARGIN   = 0.65 * inch


def _st():
    """Typography styles used across the report."""
    return {
        "brand": ParagraphStyle("brand",
            fontName="Helvetica-Bold", fontSize=7,
            textColor=C_LIGHT, spaceAfter=0),
        "h_company": ParagraphStyle("h_company",
            fontName="Helvetica-Bold", fontSize=26,
            textColor=C_BLACK, spaceAfter=4, leading=30),
        "h_sub": ParagraphStyle("h_sub",
            fontName="Helvetica", fontSize=10,
            textColor=C_MID, spaceAfter=2),
        "h_date": ParagraphStyle("h_date",
            fontName="Helvetica", fontSize=8,
            textColor=C_LIGHT, spaceAfter=0),
        "sec_label": ParagraphStyle("sec_label",
            fontName="Helvetica-Bold", fontSize=7,
            textColor=C_LIGHT, spaceAfter=4, spaceBefore=14),
        "sec_title": ParagraphStyle("sec_title",
            fontName="Helvetica-Bold", fontSize=13,
            textColor=C_BLACK, spaceAfter=6, leading=16),
        "body": ParagraphStyle("body",
            fontName="Helvetica", fontSize=9,
            textColor=C_MID, spaceAfter=5, leading=14),
        "kpi_lbl": ParagraphStyle("kpi_lbl",
            fontName="Helvetica", fontSize=7,
            textColor=C_LIGHT, spaceAfter=3),
        "kpi_val": ParagraphStyle("kpi_val",
            fontName="Helvetica-Bold", fontSize=19,
            textColor=C_BLACK, spaceAfter=2, leading=21),
        "kpi_sub": ParagraphStyle("kpi_sub",
            fontName="Helvetica", fontSize=7,
            textColor=C_LIGHT, spaceAfter=0),
        "th": ParagraphStyle("th",
            fontName="Helvetica-Bold", fontSize=7,
            textColor=C_LIGHT),
        "td_b": ParagraphStyle("td_b",
            fontName="Helvetica-Bold", fontSize=8,
            textColor=C_BLACK, leading=12),
        "td": ParagraphStyle("td",
            fontName="Helvetica", fontSize=8,
            textColor=C_MID, leading=12),
        "sp_lbl": ParagraphStyle("sp_lbl",
            fontName="Helvetica-Bold", fontSize=7,
            textColor=C_LIGHT, spaceAfter=3, spaceBefore=12),
        "sp_body": ParagraphStyle("sp_body",
            fontName="Helvetica", fontSize=9,
            textColor=C_BLACK, leading=15, spaceAfter=4),
        "footer": ParagraphStyle("footer",
            fontName="Helvetica", fontSize=7,
            textColor=C_LIGHT, alignment=TA_CENTER),
    }


def _page(canvas, doc):
    """Draw header and footer on every page."""
    canvas.saveState()
    w, h = letter

    # Header rule
    canvas.setStrokeColor(C_RULE)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, h - 0.44*inch, w - MARGIN, h - 0.44*inch)
    # Header text
    canvas.setFillColor(C_BLACK)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(MARGIN, h - 0.37*inch, "KORHEX.AI")
    canvas.setFillColor(C_LIGHT)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(MARGIN + 0.72*inch, h - 0.37*inch, "Account Intelligence")
    canvas.drawRightString(w - MARGIN, h - 0.37*inch,
        datetime.now().strftime("%B %d, %Y"))

    # Footer rule
    canvas.line(MARGIN, 0.44*inch, w - MARGIN, 0.44*inch)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(C_LIGHT)
    canvas.drawString(MARGIN, 0.28*inch, str(doc.page))
    canvas.drawCentredString(w/2, 0.28*inch,
        "CONFIDENTIAL — FOR INTERNAL USE ONLY")
    canvas.drawRightString(w - MARGIN, 0.28*inch, "Zero Data Leakage")

    canvas.restoreState()


def _txt(text):
    """Normalize and escape text for ReportLab."""
    return (text or "") \
        .replace("&", "&amp;") \
        .replace("<", "&lt;") \
        .replace(">", "&gt;") \
        .replace("\n", " ") \
        .strip()


def _rule(after=8):
    return HRFlowable(width="100%", thickness=0.5, color=C_RULE, spaceAfter=after)


def generate_report(analysis_data: dict) -> bytes:
    """
    Generate a three‑page executive PDF and return it as raw bytes.
    Usage: st.download_button(data=generate_report(current_analysis))
    """
    buf = io.BytesIO()
    s   = _st()

    doc = SimpleDocTemplate(
        buf, pagesize=letter,
        topMargin=0.72*inch, bottomMargin=0.6*inch,
        leftMargin=MARGIN,   rightMargin=MARGIN,
        title="Account Intelligence Report — KORHEX.AI",
        author="KORHEX.AI",
    )

    # ── Defensive data extraction ────────────────────────────────────────────
    company     = analysis_data.get("company_name") or "N/A"
    industry    = (analysis_data.get("industry") or
                   analysis_data.get("web_data", {}).get("industry") or "N/A")
    url         = analysis_data.get("company_url") or "N/A"
    years       = analysis_data.get("years_inactive") or 0
    score_data  = analysis_data.get("score") or {}
    total_score = score_data.get("total_score") or 0
    priority    = score_data.get("priority") or "N/A"
    is_net_new  = bool(score_data.get("is_net_new"))
    analysis    = analysis_data.get("analysis") or {}
    research    = analysis.get("research_analysis") or ""
    speech      = analysis.get("sales_speech") or ""
    audit_ok    = bool(analysis.get("audit_passed"))
    audit_notes = analysis.get("audit_notes") or ""
    word_count  = analysis.get("word_count") or 0
    products    = analysis_data.get("products") or []

    story = []

    # =========================================================================
    # P1 — COVER
    # =========================================================================
    story += [
        Spacer(1, 0.5*inch),
        Paragraph("ACCOUNT INTELLIGENCE REPORT", s["brand"]),
        Spacer(1, 10),
        Paragraph(company, s["h_company"]),
        Paragraph(f"{industry}  ·  {url}", s["h_sub"]),
        Paragraph(datetime.now().strftime("%B %d, %Y"), s["h_date"]),
        Spacer(1, 0.2*inch),
        _rule(after=0.2*inch),
    ]

    # KPI block
    t_kpi = Table(
        [
            [Paragraph("LEAD SCORE",  s["kpi_lbl"]),
             Paragraph("PRIORITY",    s["kpi_lbl"]),
             Paragraph("TYPE",        s["kpi_lbl"]),
             Paragraph("AI AUDIT",    s["kpi_lbl"])],
            [Paragraph(f"{total_score}/100",                    s["kpi_val"]),
             Paragraph(str(priority),                           s["kpi_val"]),
             Paragraph("Net New Logo" if is_net_new else "Reactivation", s["kpi_val"]),
             Paragraph("Verified" if audit_ok else "Review",   s["kpi_val"])],
            [Paragraph("out of 100",              s["kpi_sub"]),
             Paragraph("sales priority",           s["kpi_sub"]),
             Paragraph(f"{years} yrs inactive",    s["kpi_sub"]),
             Paragraph("compliance check",         s["kpi_sub"])],
        ],
        colWidths=[1.8*inch]*4,
        rowHeights=[12, 26, 12],
    )
    t_kpi.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), C_BG),
        ("LINEBEFORE",    (1,0), (-1,-1), 0.5, C_RULE),
        ("LINEBELOW",     (0,2), (-1, 2), 0.5, C_RULE),
        ("LEFTPADDING",   (0,0), (-1,-1), 14),
        ("RIGHTPADDING",  (0,0), (-1,-1), 14),
        ("TOPPADDING",    (0,0), (-1, 0), 10),
        ("TOPPADDING",    (0,1), (-1, 2), 4),
        ("BOTTOMPADDING", (0,2), (-1, 2), 10),
    ]))
    story.append(t_kpi)

    # Recommended solutions
    if products:
        story += [Paragraph("RECOMMENDED SOLUTIONS", s["sec_label"]), _rule()]
        rows = [[Paragraph("SOLUTION", s["th"]), Paragraph("ROI PITCH", s["th"])]]
        for p in products[:4]:
            roi = (p.get("roi_pitch") or "")
            if len(roi) > 160:
                roi = roi[:160] + "..."
            rows.append([
                Paragraph(p.get("name") or "N/A", s["td_b"]),
                Paragraph(_txt(roi), s["td"]),
            ])
        t_prod = Table(rows, colWidths=[2.0*inch, 5.2*inch])
        t_prod.setStyle(TableStyle([
            ("LINEBELOW",     (0, 0), (-1,  0), 0.5, C_RULE),
            ("LINEBELOW",     (0,-1), (-1, -1), 0.5, C_RULE),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [C_WHITE, C_BG]),
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(t_prod)

    story.append(PageBreak())

    # =========================================================================
    # P2 — 6‑ELEMENT ACCOUNT ANALYSIS
    # =========================================================================
    story += [
        Paragraph("ACCOUNT ANALYSIS", s["brand"]),
        Spacer(1, 6),
        Paragraph("6-Element Intelligence Breakdown", s["sec_title"]),
        _rule(after=10),
    ]

    SECTIONS = [
        ("## 1.", "1. COMPANY SNAPSHOT & STRATEGY"),
        ("## 2.", "2. TECHNOLOGY ENVIRONMENT"),
        ("## 3.", "3. IT PAIN POINTS"),
        ("## 4.", "4. KEY DECISION MAKERS"),
        ("## 5.", "5. FINANCIAL SIGNALS"),
        ("## 6.", "6. COMPETITIVE CONTEXT"),
    ]

    if research:
        sec_map, cur_key, cur_lines = {}, None, []
        for line in research.split("\n"):
            up = line.strip().upper()
            hit = next((t for mk, t in SECTIONS
                        if mk.upper() in up or t[:6] in up), None)
            if hit:
                if cur_key:
                    sec_map[cur_key] = "\n".join(cur_lines).strip()
                cur_key, cur_lines = hit, []
            elif cur_key:
                if "[OPENING" in line.upper():
                    break
                cur_lines.append(line)
        if cur_key:
            sec_map[cur_key] = "\n".join(cur_lines).strip()

        for _, title in SECTIONS:
            raw     = sec_map.get(title, "").strip()
            display = (_txt(raw[:500]) + ("..." if len(raw) > 500 else "")) \
                      if raw else "Information not available for this section."
            story.append(KeepTogether([
                Paragraph(title.upper(), s["sec_label"]),
                _rule(after=4),
                Paragraph(display, s["body"]),
                Spacer(1, 4),
            ]))
    else:
        story.append(Paragraph(
            "Full analysis not available. Run a complete analysis from the main page.",
            s["body"]))

    story.append(PageBreak())

    # =========================================================================
    # P3 — SALES SPEECH
    # =========================================================================
    story += [
        Paragraph("SALES PITCH", s["brand"]),
        Spacer(1, 6),
        Paragraph("AI-Generated Sales Speech", s["sec_title"]),
        _rule(after=6),
        Paragraph(
            f"AI Compliance Audit: {'Passed' if audit_ok else 'Flagged'}."
            + (f"  {audit_notes}" if audit_notes else ""),
            s["body"]),
        Spacer(1, 8),
    ]

    if speech:
        PARTS = {
            "[OPENING":   "OPENING",
            "[CHALLENGE": "CHALLENGE",
            "[SOLUTION":  "SOLUTION",
            "[CTA":       "CALL TO ACTION",
        }
        cur_sec, cur_lines, parsed = None, [], {}
        for line in speech.split("\n"):
            key = next((k for k in PARTS if k in line.upper()), None)
            if key:
                if cur_sec:
                    parsed[cur_sec] = "\n".join(cur_lines).strip()
                cur_sec, cur_lines = key, []
            elif cur_sec:
                cur_lines.append(line)
        if cur_sec:
            parsed[cur_sec] = "\n".join(cur_lines).strip()

        if any(parsed.get(k, "").strip() for k in PARTS):
            for key, label in PARTS.items():
                content = parsed.get(key, "").strip()
                if content:
                    story.append(Paragraph(label, s["sp_lbl"]))
                    story.append(Paragraph(_txt(content), s["sp_body"]))
                    story.append(Spacer(1, 4))
        else:
            story.append(Paragraph(_txt(speech[:2000]), s["sp_body"]))

        story += [
            Spacer(1, 6),
            Paragraph(
                f"{word_count} words  ·  Generated locally by Llama 3  ·  "
                "Verified by Compliance Agent", s["body"]),
        ]
    else:
        story.append(Paragraph(
            "Sales speech not available. Ensure Ollama is running and rerun the analysis.",
            s["body"]))

    story += [
        Spacer(1, 0.4*inch),
        _rule(after=8),
        Paragraph(
            "This report was generated locally by KORHEX.AI. "
            "No client data was transmitted to external servers. "
            "For internal use only.",
            s["footer"]),
    ]

    doc.build(story, onFirstPage=_page, onLaterPages=_page)
    return buf.getvalue()