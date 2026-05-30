"""Estilos compartilhados para os relatórios PDF (reportlab Platypus)."""
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

# Paleta
NAVY = colors.HexColor("#0B2545")
TEAL = colors.HexColor("#1B998B")
GREY = colors.HexColor("#444444")
LIGHT = colors.HexColor("#EEF2F6")
CODEBG = colors.HexColor("#F4F4F4")


def build_styles():
    ss = getSampleStyleSheet()
    styles = {}
    styles["title"] = ParagraphStyle(
        "title", parent=ss["Title"], fontName="Helvetica-Bold",
        fontSize=20, leading=24, textColor=NAVY, spaceAfter=4, alignment=TA_LEFT)
    styles["subtitle"] = ParagraphStyle(
        "subtitle", parent=ss["Normal"], fontSize=11, leading=15,
        textColor=TEAL, spaceAfter=2, fontName="Helvetica-Bold")
    styles["meta"] = ParagraphStyle(
        "meta", parent=ss["Normal"], fontSize=9, leading=12, textColor=GREY)
    styles["h1"] = ParagraphStyle(
        "h1", parent=ss["Heading1"], fontName="Helvetica-Bold",
        fontSize=13, leading=16, textColor=NAVY, spaceBefore=12, spaceAfter=5)
    styles["h2"] = ParagraphStyle(
        "h2", parent=ss["Heading2"], fontName="Helvetica-Bold",
        fontSize=11, leading=14, textColor=TEAL, spaceBefore=8, spaceAfter=3)
    styles["body"] = ParagraphStyle(
        "body", parent=ss["Normal"], fontSize=9.7, leading=14,
        alignment=TA_JUSTIFY, textColor=colors.HexColor("#1a1a1a"), spaceAfter=6)
    styles["bullet"] = ParagraphStyle(
        "bullet", parent=styles["body"], leftIndent=14, bulletIndent=4,
        spaceAfter=3)
    styles["code"] = ParagraphStyle(
        "code", parent=ss["Code"], fontName="Courier", fontSize=8,
        leading=10.5, textColor=colors.HexColor("#222222"),
        backColor=CODEBG, borderPadding=6, leftIndent=2, spaceAfter=6)
    styles["caption"] = ParagraphStyle(
        "caption", parent=ss["Normal"], fontSize=8, leading=10,
        textColor=GREY, alignment=TA_CENTER, spaceAfter=8)
    return styles


def header_band(title, subtitle, meta_lines, styles):
    """Faixa de cabeçalho no topo da primeira página."""
    inner = [
        [Paragraph(title, styles["title"])],
        [Paragraph(subtitle, styles["subtitle"])],
    ]
    for m in meta_lines:
        inner.append([Paragraph(m, styles["meta"])])
    t = Table(inner, colWidths=[16.8 * cm])
    t.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (0, 0), 12),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 12),
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
        ("LINEBELOW", (0, 0), (-1, -1), 0, LIGHT),
        ("LINEBEFORE", (0, 0), (0, -1), 3, TEAL),
    ]))
    return t


def data_table(rows, styles, col_widths=None, header=True):
    body = styles["body"]
    cell = ParagraphStyle("cell", parent=body, fontSize=8.6, leading=11,
                          spaceAfter=0)
    cellh = ParagraphStyle("cellh", parent=cell, textColor=colors.white,
                           fontName="Helvetica-Bold")
    data = []
    for i, r in enumerate(rows):
        st = cellh if (header and i == 0) else cell
        data.append([Paragraph(str(c), st) for c in r])
    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    style = [
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    ]
    if header:
        style.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
    t.setStyle(TableStyle(style))
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(GREY)
    canvas.drawString(2 * cm, 1.1 * cm, "Pedidos Veloz — Loja Veloz")
    canvas.drawRightString(19 * cm, 1.1 * cm, f"Página {doc.page}")
    canvas.setStrokeColor(LIGHT)
    canvas.line(2 * cm, 1.4 * cm, 19 * cm, 1.4 * cm)
    canvas.restoreState()
