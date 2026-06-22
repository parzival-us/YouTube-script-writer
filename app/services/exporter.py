"""TXT and PDF export helpers."""

from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer


def build_text_export(script: dict) -> bytes:
    titles = "\n".join(f"{index}. {title}" for index, title in enumerate(script["titles"], 1))
    thumbnails = "\n".join(
        f"{index}. {idea}" for index, idea in enumerate(script["thumbnail_ideas"], 1)
    )
    document = f"""SCRIPT FOR: {script['topic']}
Style: {script['style']} | Length: {script['length']}
Words: {script['word_count']} | Estimated runtime: {script['estimated_minutes']} min

{script['full_script']}

YOUTUBE TITLE IDEAS
{titles}

THUMBNAIL TEXT IDEAS
{thumbnails}
"""
    return document.encode("utf-8")


def build_pdf_export(script: dict) -> bytes:
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.7 * inch,
        leftMargin=0.7 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title=f"YouTube Script - {script['topic']}",
        author="ScriptForge AI",
    )
    base = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=base["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=27,
        textColor=HexColor("#15111f"),
        alignment=TA_CENTER,
        spaceAfter=10,
    )
    metadata_style = ParagraphStyle(
        "Metadata",
        parent=base["Normal"],
        fontSize=9,
        textColor=HexColor("#6b6475"),
        alignment=TA_CENTER,
        spaceAfter=22,
    )
    heading_style = ParagraphStyle(
        "Section",
        parent=base["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=HexColor("#7c3aed"),
        spaceBefore=14,
        spaceAfter=7,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=base["BodyText"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=16,
        textColor=HexColor("#2d2933"),
        spaceAfter=9,
    )
    list_style = ParagraphStyle("List", parent=body_style, leftIndent=12, firstLineIndent=-10)

    story = [
        Paragraph(escape(script["topic"]), title_style),
        Paragraph(
            escape(
                f"{script['style']} · {script['length']} · {script['word_count']} words · "
                f"~{script['estimated_minutes']} min"
            ),
            metadata_style,
        ),
    ]
    sections = [
        ("Hook", script["hook"]),
        ("Introduction", script["introduction"]),
        ("Main Content", script["main_content"]),
        ("Call to Action", script["call_to_action"]),
    ]
    for heading, text in sections:
        story.append(Paragraph(heading.upper(), heading_style))
        for paragraph in text.split("\n\n"):
            story.append(Paragraph(escape(paragraph).replace("\n", "<br/>"), body_style))

    story.extend([PageBreak(), Paragraph("YOUTUBE TITLE IDEAS", heading_style)])
    for index, title in enumerate(script["titles"], 1):
        story.append(Paragraph(f"{index}. {escape(title)}", list_style))
    story.extend([Spacer(1, 12), Paragraph("THUMBNAIL TEXT IDEAS", heading_style)])
    for index, idea in enumerate(script["thumbnail_ideas"], 1):
        story.append(Paragraph(f"{index}. {escape(idea)}", list_style))

    document.build(story)
    return buffer.getvalue()

