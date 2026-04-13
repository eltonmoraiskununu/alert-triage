"""Generate the AlertTriage AI Day 1-pager PDF."""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_LEFT, TA_CENTER

W, H = A4  # 595.3 x 841.9 pt
M = 14 * mm  # margin

# ── Palette ────────────────────────────────────────────────────
NR_GREEN   = colors.HexColor("#00AC69")
NR_DARK    = colors.HexColor("#1D252C")
TEAMS_BLUE = colors.HexColor("#0078D4")
LIGHT_BG   = colors.HexColor("#F4F6F8")
LIGHT_GRN  = colors.HexColor("#E8F7F1")
LIGHT_BLU  = colors.HexColor("#EBF4FD")
LIGHT_YLW  = colors.HexColor("#FFFBE6")
MID_GREY   = colors.HexColor("#485563")
PALE_GREY  = colors.HexColor("#8899AA")
WHITE      = colors.white


# ── Helpers ────────────────────────────────────────────────────

def rrect(c, x, y, w, h, r, fill, stroke=None, sw=0.5):
    c.saveState()
    c.setFillColor(fill)
    c.setStrokeColor(stroke or fill)
    c.setLineWidth(sw)
    c.roundRect(x, y, w, h, r, fill=1, stroke=1 if stroke else 0)
    c.restoreState()


def bullet_dot(c, x, cy, color):
    """Draw a filled circle bullet."""
    c.setFillColor(color)
    c.circle(x, cy, 2, fill=1, stroke=0)


def section_label(c, x, y, text, color):
    c.setFillColor(color)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x, y, text.upper())


def para(c, html, x, y, w, size=8.5, color=NR_DARK, leading=13, font="Helvetica", align=TA_LEFT):
    style = ParagraphStyle("p", fontName=font, fontSize=size,
                           textColor=color, leading=leading, alignment=align)
    p = Paragraph(html, style)
    pw, ph = p.wrap(w, 9999)
    p.drawOn(c, x, y - ph)
    return ph  # height consumed


def hline(c, x, y, w, color, lw=0.5):
    c.setStrokeColor(color)
    c.setLineWidth(lw)
    c.line(x, y, x + w, y)


# ── Main ───────────────────────────────────────────────────────

def generate(path="AlertTriage_OnePager.pdf"):
    c = canvas.Canvas(path, pagesize=A4)
    c.setTitle("AlertTriage — AI Day 2026")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # HEADER
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    HDR_H = 34 * mm
    c.setFillColor(NR_DARK)
    c.rect(0, H - HDR_H, W, HDR_H, fill=1, stroke=0)

    # Green left accent bar
    c.setFillColor(NR_GREEN)
    c.rect(0, H - HDR_H, 3.5 * mm, HDR_H, fill=1, stroke=0)

    # Logo box
    rrect(c, M, H - HDR_H + 6 * mm, 20 * mm, 20 * mm, 2 * mm, NR_GREEN)
    c.setFillColor(NR_DARK)
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(M + 10 * mm, H - HDR_H + 11 * mm, "AT")

    # Title
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 23)
    c.drawString(M + 25 * mm, H - 16 * mm, "AlertTriage")
    c.setFillColor(NR_GREEN)
    c.setFont("Helvetica", 10.5)
    c.drawString(M + 25 * mm, H - 24 * mm, "AI-Powered Alert Investigation for Microsoft Teams")

    # Right tags
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawRightString(W - M, H - 14 * mm, "AI Day 2026  |  POC by Elton Morais")
    c.setFillColor(PALE_GREY)
    c.setFont("Helvetica", 8)
    c.drawRightString(W - M, H - 21.5 * mm, "New Relic  |  Google Gemini  |  Microsoft Teams")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CONTENT AREA — two columns
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    GAP = 4.5 * mm
    COL_W_L = 78 * mm
    COL_W_R = W - 2 * M - GAP - COL_W_L
    CX_L = M
    CX_R = M + COL_W_L + GAP

    CONTENT_TOP = H - HDR_H - 5 * mm   # ~700 pt
    FOOTER_H = 8 * mm
    ARCH_H = 27 * mm
    ARCH_Y = FOOTER_H + FOOTER_H + ARCH_H  # bottom of arch section
    CONTENT_BOT = FOOTER_H + ARCH_H + 6 * mm  # ~120 pt

    # Available column height
    COL_H = CONTENT_TOP - CONTENT_BOT  # ~580 pt

    # ── LEFT COLUMN ─────────────────────────────────────────────
    y = CONTENT_TOP

    # ·· PROBLEM ··
    BOX_PAD = 3 * mm
    PROB_H = 36 * mm
    rrect(c, CX_L, y - PROB_H, COL_W_L, PROB_H, 2 * mm, LIGHT_BG)
    # Coloured top bar
    rrect(c, CX_L, y - 5.5 * mm, COL_W_L, 5.5 * mm, 2 * mm, NR_DARK)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(CX_L + BOX_PAD, y - 4 * mm, "THE PROBLEM")

    problem_txt = (
        "When an alert fires, engineers manually open New Relic, "
        "navigate dashboards, cross-reference logs, and piece together a root cause "
        "— <b>often taking 10–15 minutes before the first real insight</b>. "
        "During an active incident, every minute counts."
    )
    para(c, problem_txt, CX_L + BOX_PAD, y - 7.5 * mm,
         COL_W_L - 2 * BOX_PAD, size=8.5, color=NR_DARK)

    y -= PROB_H + 3 * mm

    # ·· SOLUTION ··
    SOL_H = 47 * mm
    rrect(c, CX_L, y - SOL_H, COL_W_L, SOL_H, 2 * mm, LIGHT_GRN,
          stroke=NR_GREEN, sw=0.8)
    rrect(c, CX_L, y - 5.5 * mm, COL_W_L, 5.5 * mm, 2 * mm, NR_GREEN)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(CX_L + BOX_PAD, y - 4 * mm, "THE SOLUTION")

    sol_intro = (
        "<b>AlertTriage</b> is a Teams bot that sits in your alert channel. "
        "Tag <b>@AlertTriage</b> in a thread under an alert card:"
    )
    h = para(c, sol_intro, CX_L + BOX_PAD, y - 7.5 * mm,
             COL_W_L - 2 * BOX_PAD, size=8.5, color=NR_DARK)

    steps = [
        "Reads the alert card (entity + timestamps)",
        "Queries live New Relic data via NerdGraph",
        "Gemini AI synthesises triage brief or RCA",
        "Posts reply in the same Teams thread",
    ]
    sy = y - 7.5 * mm - h - 2 * mm
    for step in steps:
        bullet_dot(c, CX_L + BOX_PAD + 1.5 * mm, sy + 2.5 * mm, NR_GREEN)
        c.setFillColor(NR_DARK)
        c.setFont("Helvetica", 8.5)
        c.drawString(CX_L + BOX_PAD + 4 * mm, sy, step)
        sy -= 6.8 * mm

    y -= SOL_H + 3 * mm

    # ·· IMPACT ··
    IMP_H = 28 * mm
    rrect(c, CX_L, y - IMP_H, COL_W_L, IMP_H, 2 * mm, LIGHT_YLW,
          stroke=colors.HexColor("#FFB800"), sw=0.8)
    rrect(c, CX_L, y - 5.5 * mm, COL_W_L, 5.5 * mm, 2 * mm,
          colors.HexColor("#FFB800"))
    c.setFillColor(NR_DARK)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(CX_L + BOX_PAD, y - 4 * mm, "IMPACT")

    stats = [
        ("10–15 min", "manual triage", NR_DARK),
        ("~30 sec", "with AlertTriage", NR_GREEN),
        ("3 types", "APM / SM / SL", TEAMS_BLUE),
    ]
    sw_each = COL_W_L / 3
    for i, (big, small, col) in enumerate(stats):
        sx = CX_L + i * sw_each + sw_each / 2
        c.setFillColor(col)
        c.setFont("Helvetica-Bold", 12 if i == 0 else 14)
        c.drawCentredString(sx, y - 14 * mm, big)
        c.setFillColor(MID_GREY)
        c.setFont("Helvetica", 7)
        c.drawCentredString(sx, y - 19.5 * mm, small)

    y -= IMP_H + 3 * mm

    # ·· SUPPORTED ENTITIES — stretch to fill remaining left column ··
    ENT_H = CONTENT_TOP - (PROB_H + SOL_H + IMP_H + 3 * 3 * mm) - CONTENT_BOT
    rrect(c, CX_L, CONTENT_BOT, COL_W_L, ENT_H, 2 * mm, LIGHT_BLU,
          stroke=TEAMS_BLUE, sw=0.8)
    rrect(c, CX_L, y - 5.5 * mm, COL_W_L, 5.5 * mm, 2 * mm, TEAMS_BLUE)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(CX_L + BOX_PAD, y - 4 * mm, "SUPPORTED ENTITY TYPES")

    entities = [
        ("APM",
         "Error rate, avg/p95 latency,\nthroughput (RPM), slowest transactions,\nexternal deps, trace -> log correlation"),
        ("Synthetic Monitor",
         "Failure rate, per-location breakdown,\nfailure timeline (5-min buckets),\nerror messages, HTTP response codes"),
        ("Service Level",
         "SLI definition replay (bad/good events),\ntraceId extraction -> log correlation,\nWeb Core Vitals: LCP / INP / CLS"),
    ]

    # Distribute entity boxes evenly — fill from header to bottom with 1mm gaps
    N_ENT = len(entities)
    GAP_ENT = 1.5 * mm
    inner_top = y - 6.5 * mm   # just below the header bar
    inner_bot = CONTENT_BOT + 1.5 * mm
    ebox_h = (inner_top - inner_bot - (N_ENT - 1) * GAP_ENT) / N_ENT
    ey = inner_top
    for etype, desc in entities:
        rrect(c, CX_L + BOX_PAD, ey - ebox_h,
              COL_W_L - 2 * BOX_PAD, ebox_h, 1.5 * mm,
              colors.HexColor("#D8E8F6"), stroke=TEAMS_BLUE, sw=0.4)
        c.setFillColor(TEAMS_BLUE)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(CX_L + 2 * BOX_PAD, ey - 5 * mm, etype)
        c.setFillColor(MID_GREY)
        c.setFont("Helvetica", 7.8)
        for j, line in enumerate(desc.split("\n")):
            c.drawString(CX_L + 2 * BOX_PAD, ey - 10 * mm - j * 4.5 * mm, line)
        ey -= ebox_h + GAP_ENT

    # ── RIGHT COLUMN — HOW AI IS LEVERAGED ──────────────────────
    rrect(c, CX_R, CONTENT_BOT, COL_W_R, COL_H, 2 * mm, LIGHT_BLU,
          stroke=TEAMS_BLUE, sw=0.8)

    # Header bar
    rrect(c, CX_R, CONTENT_TOP - 5.5 * mm, COL_W_R, 5.5 * mm, 2 * mm, TEAMS_BLUE)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(CX_R + BOX_PAD, CONTENT_TOP - 4 * mm, "HOW AI IS LEVERAGED")

    ai_points = [
        (
            "1.  Intent & Entity Extraction",
            "Gemini reads unstructured alert text or the user's Teams reply and extracts: "
            "<b>service name, entity type</b> (APM / Synthetic Monitor / Service Level), "
            "<b>severity</b>, and whether the user wants a quick <i>triage</i> or a deep "
            "<i>investigation</i> — no structured input required.",
        ),
        (
            "2.  Smart Entity Resolution",
            "Progressive fuzzy search across NR entity types with AI-extracted type hints "
            "(e.g. 'SM' maps to MONITOR searches). Handles bracket notation, partial names, "
            "and status suffixes like 'is Down' as part of the monitor name. "
            "Falls back through shorter patterns before widening the search.",
        ),
        (
            "3.  Triage Synthesis",
            "Gemini receives live NR data — burn rates, error counts, failure locations, "
            "compliance scores — and writes a concise, <b>entity-type-aware triage brief</b>: "
            "different narrative and metrics for APM vs Synthetic Monitor vs Service Level.",
        ),
        (
            "4.  Root Cause Investigation Chain",
            "For deep investigations, the AI follows an automated evidence chain: "
            "<b>SLI definition</b> (fetch the actual NRQL that defines 'bad') "
            "<b>-> bad event replay</b> (re-run against the window) "
            "<b>-> traceId extraction -> log correlation</b> (find the exact error in logs). "
            "For Web Core Vitals, identifies specific page elements causing LCP/INP/CLS issues.",
        ),
        (
            "5.  Contextual Reasoning",
            "Gemini correlates across 6-10 NR data sources simultaneously — alert incidents, "
            "deployments, external service latency, error traces, and correlated logs — "
            "into a single, actionable narrative with concrete recommended next steps.",
        ),
    ]

    # ── Distribute AI points evenly across the available height ──
    CALLOUT_H = 20 * mm
    RIGHT_HEADER = 8 * mm
    FIXED_TOP_GAP = 3 * mm  # small fixed gap below the header bar

    # Pre-render each body paragraph to get its height
    rendered = []
    for title, body in ai_points:
        style = ParagraphStyle("p", fontName="Helvetica", fontSize=8.2,
                               textColor=MID_GREY, leading=12.5, alignment=TA_LEFT)
        p = Paragraph(body, style)
        _, ph = p.wrap(COL_W_R - 2 * BOX_PAD - 2 * mm, 9999)
        rendered.append((title, body, ph))

    TITLE_H = 5 * mm
    total_content = sum(TITLE_H + ph for _, _, ph in rendered)
    # Space available between fixed top gap and callout
    available_h = COL_H - RIGHT_HEADER - FIXED_TOP_GAP - CALLOUT_H - 4 * mm
    # Gaps only BETWEEN points (n-1) plus one gap before callout = n gaps total
    n_gaps = len(rendered)
    gap = max(2 * mm, (available_h - total_content) / n_gaps)

    ay = CONTENT_TOP - RIGHT_HEADER - FIXED_TOP_GAP
    for i, (title, body, ph) in enumerate(rendered):
        # Title
        c.setFillColor(TEAMS_BLUE)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(CX_R + BOX_PAD, ay, title)
        ay -= TITLE_H
        # Body
        style = ParagraphStyle("p", fontName="Helvetica", fontSize=8.2,
                               textColor=MID_GREY, leading=12.5, alignment=TA_LEFT)
        p = Paragraph(body, style)
        p.wrap(COL_W_R - 2 * BOX_PAD - 2 * mm, 9999)
        p.drawOn(c, CX_R + BOX_PAD + 2 * mm, ay - ph)
        ay -= ph + gap
        # Separator (except after last)
        if i < len(rendered) - 1:
            hline(c, CX_R + BOX_PAD, ay + gap * 0.5,
                  COL_W_R - 2 * BOX_PAD, colors.HexColor("#C5D8EE"), 0.4)

    # ── Callout pinned to bottom ──────────────────────────────
    rrect(c, CX_R + BOX_PAD, CONTENT_BOT + 2 * mm,
          COL_W_R - 2 * BOX_PAD, CALLOUT_H, 2 * mm,
          colors.HexColor("#E8F7F1"), stroke=NR_GREEN, sw=0.6)
    callout = (
        "<b>Built in one AI Day.</b>  End-to-end working POC: "
        "Teams bot + Gemini AI + live New Relic NerdGraph queries. "
        "15 tests passing. Thread-aware architecture ready for Teams registration."
    )
    style = ParagraphStyle("co", fontName="Helvetica", fontSize=8,
                           textColor=NR_GREEN, leading=12.5, alignment=TA_CENTER)
    p = Paragraph(callout, style)
    _, ph = p.wrap(COL_W_R - 4 * BOX_PAD, 9999)
    text_top = CONTENT_BOT + 2 * mm + CALLOUT_H - (CALLOUT_H - ph) / 2
    p.drawOn(c, CX_R + 2 * BOX_PAD, text_top - ph)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ARCHITECTURE BAND — full width
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ARCH_TOP = CONTENT_BOT - 3 * mm
    rrect(c, M, ARCH_TOP - ARCH_H, W - 2 * M, ARCH_H, 2 * mm, NR_DARK)

    # Header label
    c.setFillColor(NR_GREEN)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(M + BOX_PAD, ARCH_TOP - 4.5 * mm, "FLOW")
    hline(c, M + BOX_PAD + 12 * mm, ARCH_TOP - 3.5 * mm,
          W - 2 * M - 2 * BOX_PAD - 12 * mm, colors.HexColor("#2E3F4F"), 0.5)

    boxes = [
        ("Alert Card",    "NR alert posted\nin Teams channel",   NR_DARK,    colors.HexColor("#2E4A5A")),
        ("@AlertTriage",  "Engineer tags\nbot in thread",        NR_DARK,    colors.HexColor("#2E4A5A")),
        ("Gemini AI",     "Extracts entity,\nintent, window",    NR_GREEN,   NR_DARK),
        ("NerdGraph API", "Live queries\nNR EU endpoint",        NR_DARK,    colors.HexColor("#2E4A5A")),
        ("AI Synthesis",  "RCA / Triage\nbrief generated",       NR_GREEN,   NR_DARK),
        ("Thread Reply",  "Posted back\nin same thread",         TEAMS_BLUE, NR_DARK),
    ]

    box_area_w = W - 2 * M - 2 * BOX_PAD
    bw = (box_area_w - 5 * 3 * mm) / len(boxes)
    bx = M + BOX_PAD
    by_top = ARCH_TOP - 7 * mm

    for i, (title, desc, bg, txt_col) in enumerate(boxes):
        rrect(c, bx, by_top - 17 * mm, bw, 17 * mm, 1.5 * mm, bg)
        c.setFillColor(txt_col if bg == NR_GREEN or bg == TEAMS_BLUE else WHITE)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawCentredString(bx + bw / 2, by_top - 6.5 * mm, title)
        c.setFont("Helvetica", 6.5)
        fc = NR_DARK if bg in (NR_GREEN, TEAMS_BLUE) else colors.HexColor("#99BBCC")
        c.setFillColor(fc)
        for j, line in enumerate(desc.split("\n")):
            c.drawCentredString(bx + bw / 2, by_top - 11.5 * mm - j * 4 * mm, line)

        if i < len(boxes) - 1:
            c.setFillColor(NR_GREEN)
            c.setFont("Helvetica-Bold", 9)
            c.drawCentredString(bx + bw + 1.5 * mm, by_top - 10 * mm, ">")

        bx += bw + 3 * mm

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # FOOTER
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    c.setFillColor(NR_DARK)
    c.rect(0, 0, W, FOOTER_H, fill=1, stroke=0)
    c.setFillColor(NR_GREEN)
    c.rect(0, FOOTER_H - 1 * mm, W, 1 * mm, fill=1, stroke=0)

    c.setFillColor(PALE_GREY)
    c.setFont("Helvetica", 7)
    c.drawString(M, 3 * mm,
                 "Python  |  aiohttp  |  Bot Framework SDK v4  |  Google Gemini gemini-3.1-flash-lite  "
                 "|  New Relic NerdGraph EU  |  Microsoft Teams")
    c.setFillColor(NR_GREEN)
    c.drawRightString(W - M, 3 * mm, "github.com/your-org/alert-triage")

    c.save()
    print(f"Saved: {path}")


if __name__ == "__main__":
    generate()
