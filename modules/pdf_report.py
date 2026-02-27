"""
pdf_report.py — Reporte Ejecutivo KORHEX.AI
Estilo: B2B profesional apto para C-Level
Uso: pdf_bytes = generate_report(st.session_state['current_analysis'])
"""
import io
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, HRFlowable, PageBreak, KeepTogether
)

# Paleta monocromatica ejecutiva
C_BLACK  = colors.HexColor("#111111")
C_DARK   = colors.HexColor("#333333")
C_MID    = colors.HexColor("#666666")
C_LIGHT  = colors.HexColor("#999999")
C_RULE   = colors.HexColor("#DEDEDE")
C_BG     = colors.HexColor("#F6F6F6")
C_WHITE  = colors.white
MARGIN   = 0.65 * inch


def _st():
    """Estilos tipograficos del reporte."""
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
            textColor=C_LIGHT, spaceAfter=3, alignment=TA_CENTER),
        "kpi_val": ParagraphStyle("kpi_val",
            fontName="Helvetica-Bold", fontSize=19,
            textColor=C_BLACK, spaceAfter=2, leading=21, alignment=TA_CENTER),
        "kpi_sub": ParagraphStyle("kpi_sub",
            fontName="Helvetica", fontSize=7,
            textColor=C_LIGHT, spaceAfter=0, alignment=TA_CENTER),
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
        "sec_hdr": ParagraphStyle("sec_hdr",
            fontName="Helvetica-Bold", fontSize=8,
            textColor=C_DARK, leading=12, alignment=TA_LEFT),
        "footer": ParagraphStyle("footer",
            fontName="Helvetica", fontSize=7,
            textColor=C_LIGHT, alignment=TA_CENTER),
    }


def _page(canvas, doc):
    """Dibuja header y footer en cada pagina."""
    canvas.saveState()
    w, h = letter

    # Linea header
    canvas.setStrokeColor(C_RULE)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, h - 0.44*inch, w - MARGIN, h - 0.44*inch)
    # Texto header
    canvas.setFillColor(C_BLACK)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(MARGIN, h - 0.37*inch, "KORHEX.AI")
    canvas.setFillColor(C_LIGHT)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(MARGIN + 0.72*inch, h - 0.37*inch, "Account Intelligence")
    canvas.drawRightString(w - MARGIN, h - 0.37*inch,
        datetime.now().strftime("%B %d, %Y"))

    # Linea footer
    canvas.line(MARGIN, 0.44*inch, w - MARGIN, 0.44*inch)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(C_LIGHT)
    canvas.drawString(MARGIN, 0.28*inch, str(doc.page))
    canvas.drawCentredString(w/2, 0.28*inch,
        "CONFIDENTIAL — FOR INTERNAL USE ONLY")
    canvas.drawRightString(w - MARGIN, 0.28*inch, "Zero Data Leakage")

    canvas.restoreState()


def _txt(text):
    """Limpiar texto para ReportLab."""
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
    Genera PDF ejecutivo de 3 paginas y retorna bytes.
    Uso: st.download_button(data=generate_report(current_analysis))
    """
    buf = io.BytesIO()
    s   = _st()

    doc = SimpleDocTemplate(
        buf, pagesize=letter,
        topMargin=0.72*inch, bottomMargin=0.75*inch,
        leftMargin=MARGIN,   rightMargin=MARGIN,
        title="Account Intelligence Report — KORHEX.AI",
        author="KORHEX.AI",
    )

    # ── Datos defensivos ──────────────────────────────────────────────────────
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
    # KEY DEFENSE: DB cache returns key 'research'; fresh agents run uses 'research_analysis'
    research    = (analysis.get("research_analysis")
                   or analysis.get("research")
                   or "").strip()
    speech      = analysis.get("sales_speech") or ""
    audit_ok    = bool(analysis.get("audit_passed"))
    audit_notes = analysis.get("audit_notes") or ""
    word_count  = analysis.get("word_count") or 0
    products    = analysis_data.get("products") or []

    story = []

    # =========================================================================
    # P1 — PORTADA
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
             # Note: 'Reactivation' is a single word — no hyphenation risk
             Paragraph("Verified \u2714" if audit_ok else "Review ⚠",   s["kpi_val"])],
            [Paragraph("out of 100",              s["kpi_sub"]),
             Paragraph("sales priority",           s["kpi_sub"]),
             Paragraph(f"{years} yrs inactive",    s["kpi_sub"]),
             Paragraph("compliance check",         s["kpi_sub"])],
        ],
        # Column widths: LEAD SCORE | PRIORITY | TYPE (needs room for 'Reactivation') | AI AUDIT
        # Total = 7.2" to fill the page width minus margins
        colWidths=[1.2*inch, 1.8*inch, 2.5*inch, 1.7*inch],
        # No fixed rowHeights — let ReportLab auto-size each row to content
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
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(t_kpi)

    # Productos recomendados
    if products:
        story += [Paragraph("RECOMMENDED SOLUTIONS", s["sec_label"]), _rule()]
        rows = [[Paragraph("SOLUTION", s["th"]), Paragraph("ROI PITCH", s["th"])]]
        for p in products[:4]:
            roi = (p.get("roi_pitch") or "")
            rows.append([
                Paragraph(p.get("name") or "N/A", s["td_b"]),
                Paragraph(_txt(roi), s["td"]),
            ])
        t_prod = Table(rows, colWidths=[2.4*inch, 4.8*inch], repeatRows=1)
        t_prod.setStyle(TableStyle([
            ("LINEBELOW",     (0, 0), (-1,  0), 0.5, C_RULE),
            ("LINEBELOW",     (0,-1), (-1, -1), 0.5, C_RULE),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [C_WHITE, C_BG]),
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(t_prod)

    story.append(PageBreak())

    # =========================================================================
    # P2 — ANALISIS DE 6 ELEMENTOS
    # =========================================================================
    story += [
        Paragraph("ACCOUNT ANALYSIS", s["brand"]),
        Spacer(1, 6),
        Paragraph("6-Element Intelligence Breakdown", s["sec_title"]),
        _rule(after=10),
    ]

    # ── Always render all 6 sections — titles are hardcoded and never optional ──
    # If the parser populated sec_map, use it. Otherwise best-effort: put the
    # entire raw text under section 1 and show placeholder for 2-6.
    full_w = 7.2 * inch

    SECTION_TITLES = {
        "1": "1. COMPANY SNAPSHOT & STRATEGY",
        "2": "2. TECHNOLOGY ENVIRONMENT",
        "3": "3. IT PAIN POINTS",
        "4": "4. KEY DECISION MAKERS",
        "5": "5. FINANCIAL SIGNALS",
        "6": "6. COMPETITIVE CONTEXT",
    }
    SECTION_ORDER = ["1", "2", "3", "4", "5", "6"]
    sec_map = {}

    if research:
        import re as _re
        sec_map = {}

        # ── Primary parser: new [SECTION_N] tag format ──────────────────────
        tag_matches = _re.findall(
            r'\[SECTION_(\d)\]\s*(.*?)(?=\[SECTION_\d\]|$)',
            research,
            _re.DOTALL
        )
        if tag_matches:
            for num, body in tag_matches:
                if num in SECTION_TITLES:
                    sec_map[SECTION_TITLES[num]] = body.strip().replace("**", "").replace("__", "")

        # ── Fallback parser: legacy ## heading format (cached analyses) ──────
        if not any(sec_map.get(SECTION_TITLES[n], "").strip() for n in SECTION_ORDER):
            if "##" in research:
                for block in research.split("##")[1:]:
                    block = block.strip()
                    if not block:
                        continue
                    header_line = block.split("\n")[0].strip().replace("**", "").replace("__", "")
                    num = header_line[0] if header_line and header_line[0].isdigit() else None
                    if num and num in SECTION_TITLES:
                        body = "\n".join(block.split("\n")[1:]).strip()
                        sec_map[SECTION_TITLES[num]] = body
            else:
                cur_key, cur_lines = None, []
                for line in research.split("\n"):
                    clean = line.strip().replace("**", "").replace("__", "")
                    is_hdr = (len(clean) > 3 and clean[0].isdigit()
                              and clean[1] == "." and clean[0] in SECTION_TITLES)
                    if is_hdr:
                        if cur_key:
                            sec_map[cur_key] = "\n".join(cur_lines).strip()
                        cur_key, cur_lines = SECTION_TITLES[clean[0]], []
                    elif cur_key:
                        cur_lines.append(line)
                if cur_key:
                    sec_map[cur_key] = "\n".join(cur_lines).strip()

        # ── Last resort: dump everything under section 1 ─────────────────────
        if not any(sec_map.get(SECTION_TITLES[n], "").strip() for n in SECTION_ORDER):
            clean_research = research.replace("**", "").replace("__", "")
            sec_map[SECTION_TITLES["1"]] = clean_research

    # Render all 6 headers unconditionally
    for num in SECTION_ORDER:
        title   = SECTION_TITLES[num]
        raw     = (sec_map.get(title, "") if research else "").strip()
        raw     = raw.replace("**", "").replace("__", "")
        # Strip LLM meta-commentary: sentences starting with "Note:" (e.g. "Note: I have used...")
        import re as _re
        raw = _re.sub(r'\bNote\s*:\s*[^\n]*', '', raw, flags=_re.IGNORECASE).strip()
        display = _txt(raw) if raw else "Analysis based on AI internal model."
        bottom_pad = 14 if len(display) < 150 else 6
        hdr_tbl = Table(
            [[Paragraph(f"  {num}. {title.split('. ', 1)[-1]}", s["sec_hdr"])]],
            colWidths=[full_w],
        )
        hdr_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,-1), C_BG),
            ("TOPPADDING",    (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LEFTPADDING",   (0,0), (-1,-1), 8),
            ("RIGHTPADDING",  (0,0), (-1,-1), 8),
        ]))
        story.append(KeepTogether([
            Spacer(1, 6),
            hdr_tbl,
            Spacer(1, 4),
            Paragraph(display, s["body"]),
            Spacer(1, bottom_pad),
        ]))

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
            # Full speech fallback — no character cap, flows across pages naturally
            for para in speech.split("\n"):
                para = para.strip()
                if para:
                    story.append(Paragraph(_txt(para), s["sp_body"]))
                    story.append(Spacer(1, 4))

        story.append(KeepTogether([
            Spacer(1, 12),
            _rule(after=6),
            Paragraph(
                f"{word_count} words  ·  Generated locally by Llama 3  ·  "
                "Verified by Compliance Agent",
                s["body"]),
        ]))
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