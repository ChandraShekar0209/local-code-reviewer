# src/reporter.py
# Generates PDF report of all reviews and benchmarks

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os
import tempfile


def generate_pdf_report(
    metadata,
    results: dict,
    comparison: dict,
    scores: dict
) -> str:
    """
    Generate a PDF report of all reviews and benchmarks
    Returns path to the generated PDF file
    """

    # create temp file for PDF
    tmp = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf",
        prefix="code_review_"
    )
    pdf_path = tmp.name
    tmp.close()

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=18*mm,
        rightMargin=18*mm,
        topMargin=16*mm,
        bottomMargin=16*mm
    )

    # colors
    DARK    = colors.HexColor("#1A1A1A")
    TEAL    = colors.HexColor("#1D9E75")
    BLUE    = colors.HexColor("#378ADD")
    AMBER   = colors.HexColor("#BA7517")
    RED     = colors.HexColor("#D85A30")
    LIGHT   = colors.HexColor("#F7F7F5")
    BORDER  = colors.HexColor("#DDDBD3")
    WHITE   = colors.white

    def sty(name, **kw):
        return ParagraphStyle(name, **kw)

    H1   = sty("H1",   fontName="Helvetica-Bold", fontSize=20, textColor=DARK,  spaceAfter=4,  leading=24)
    H2   = sty("H2",   fontName="Helvetica-Bold", fontSize=13, textColor=TEAL,  spaceAfter=6,  leading=16)
    H3   = sty("H3",   fontName="Helvetica-Bold", fontSize=10, textColor=DARK,  spaceAfter=4,  leading=13)
    BODY = sty("BODY", fontName="Helvetica",      fontSize=9,  textColor=DARK,  spaceAfter=3,  leading=13)
    SMALL= sty("SMALL",fontName="Helvetica",      fontSize=8,  textColor=colors.HexColor("#5A5A56"), spaceAfter=2, leading=11)
    W9   = sty("W9",   fontName="Helvetica-Bold", fontSize=9,  textColor=WHITE, leading=13)
    W8   = sty("W8",   fontName="Helvetica",      fontSize=8,  textColor=WHITE, leading=11)

    story = []

    # title
    story.append(Paragraph("🔍 Local AI Code Review Report", H1))
    story.append(Paragraph("Privacy-first code analysis using local LLMs — no data leaves your machine", SMALL))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=10))

    # code metadata
    story.append(Paragraph("Code Analysis", H2))
    meta_data = [
        ["Lines of code", str(metadata.lines_of_code)],
        ["Functions", ", ".join(metadata.functions) or "None"],
        ["Classes", ", ".join(metadata.classes) or "None"],
        ["Imports", ", ".join(metadata.imports) or "None"],
        ["Complexity", metadata.complexity],
        ["Has docstrings", str(metadata.has_docstrings)],
        ["Has type hints", str(metadata.has_type_hints)],
        ["Pre-detected issues", str(len(metadata.potential_issues))],
    ]
    meta_tbl = Table(meta_data, colWidths=[50*mm, None])
    meta_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(0,-1), LIGHT),
        ("FONTNAME",      (0,0),(0,-1), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,-1), 9),
        ("GRID",          (0,0),(-1,-1), 0.5, BORDER),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("RIGHTPADDING",  (0,0),(-1,-1), 8),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 10))

    # pre detected issues
    if metadata.potential_issues:
        story.append(Paragraph("Pre-detected Issues (AST Analysis)", H3))
        for issue in metadata.potential_issues:
            story.append(Paragraph(f"• {issue}", BODY))
        story.append(Spacer(1, 8))

    # model reviews
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=8))
    story.append(Paragraph("Model Reviews", H2))

    model_colors = [TEAL, BLUE, AMBER]

    for idx, (model_id, result) in enumerate(results.items()):
        c = model_colors[idx % len(model_colors)]
        review = result["review"]
        metrics = result["metrics"]

        # model header
        hdr = Table([[
            Paragraph(model_id, W9),
            Paragraph(
                f"Score: {review.get('overall_score', 0)}/10  |  "
                f"Time: {metrics['time_taken']}s  |  "
                f"{metrics['tokens_per_sec']} tokens/s",
                W8
            )
        ]], colWidths=[60*mm, None])
        hdr.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), c),
            ("TOPPADDING",    (0,0),(-1,-1), 7),
            ("BOTTOMPADDING", (0,0),(-1,-1), 7),
            ("LEFTPADDING",   (0,0),(-1,-1), 8),
            ("RIGHTPADDING",  (0,0),(-1,-1), 8),
            ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ]))
        story.append(hdr)

        # review categories
        categories = {
            "Bugs":        review.get("bugs", []),
            "Security":    review.get("security", []),
            "Performance": review.get("performance", []),
            "Style":       review.get("style", []),
        }

        for cat_name, items in categories.items():
            if items:
                story.append(Paragraph(f"{cat_name}:", H3))
                for item in items:
                    story.append(Paragraph(f"  • {item}", BODY))

        # summary
        if review.get("summary"):
            story.append(Paragraph("Summary:", H3))
            story.append(Paragraph(review["summary"], BODY))

        # priority fix
        if review.get("priority_fix"):
            story.append(Paragraph(
                f"Priority fix: {review['priority_fix']}",
                sty("pf", fontName="Helvetica-Bold", fontSize=9,
                    textColor=RED, leading=13, spaceAfter=3)
            ))

        story.append(Spacer(1, 10))

    # benchmark comparison
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=8))
    story.append(Paragraph("Benchmark Comparison", H2))

    bench_header = ["Model", "Time", "Tokens/s", "Score"]
    bench_rows   = [bench_header]

    for model_id, summary in comparison.get("summary", {}).items():
        bench_rows.append([
            model_id,
            summary["time_taken"],
            summary["tokens_per_sec"],
            summary["overall_score"]
        ])

    bench_tbl = Table(bench_rows, colWidths=[70*mm, 30*mm, 35*mm, 30*mm])
    bench_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0), TEAL),
        ("TEXTCOLOR",     (0,0),(-1,0), WHITE),
        ("FONTNAME",      (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,-1), 9),
        ("GRID",          (0,0),(-1,-1), 0.5, BORDER),
        ("BACKGROUND",    (0,1),(-1,-1), LIGHT),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("RIGHTPADDING",  (0,0),(-1,-1), 8),
        ("ALIGN",         (1,0),(-1,-1), "CENTER"),
    ]))
    story.append(bench_tbl)
    story.append(Spacer(1, 8))

    # winner
    winner = scores.get("winner", "N/A")
    reasoning = scores.get("reasoning", "N/A")
    story.append(Paragraph(f"Winner: {winner}", H3))
    story.append(Paragraph(f"Reason: {reasoning}", BODY))

    # footer
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=6))
    story.append(Paragraph(
        "Generated by Local AI Code Reviewer — github.com/ChandraShekar0209/local-code-reviewer",
        SMALL
    ))

    doc.build(story)
    return pdf_path