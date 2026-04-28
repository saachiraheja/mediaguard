import imagehash, io, base64, pyotp, secrets, string
import numpy as np
from PIL import Image, ImageChops, ImageEnhance
from skimage.metrics import structural_similarity as ssim_fn
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from datetime import datetime

try:
    import pillow_avif
except ImportError:
    pass


# ══════════════════════════════════════════════════════════
# FILE VALIDATION
# ══════════════════════════════════════════════════════════

ALLOWED_SIGNATURES = {
    b'\xff\xd8\xff': 'jpeg',
    b'\x89PNG':      'png',
    b'RIFF':         'webp',
    b'\x00\x00\x00': 'avif',
}

def validate_bytes(file_bytes):
    header = file_bytes[:12]
    for sig, fmt in ALLOWED_SIGNATURES.items():
        if header[:len(sig)] == sig:
            return True, fmt
    return False, None

def safe_open_image(file_bytes):
    return Image.open(io.BytesIO(file_bytes))


# ══════════════════════════════════════════════════════════
# HASHING
# ══════════════════════════════════════════════════════════

def get_hashes(img_bytes):
    img = safe_open_image(img_bytes).convert('RGB')
    return {
        "phash": str(imagehash.phash(img)),
        "ahash": str(imagehash.average_hash(img)),
        "dhash": str(imagehash.dhash(img)),
    }

def compare_hashes(h1, h2):
    p = max(0, 100 - (imagehash.hex_to_hash(h1["phash"]) - imagehash.hex_to_hash(h2["phash"])) / 64 * 100)
    a = max(0, 100 - (imagehash.hex_to_hash(h1["ahash"]) - imagehash.hex_to_hash(h2["ahash"])) / 64 * 100)
    d = max(0, 100 - (imagehash.hex_to_hash(h1["dhash"]) - imagehash.hex_to_hash(h2["dhash"])) / 64 * 100)
    return p, a, d


# ══════════════════════════════════════════════════════════
# SSIM
# ══════════════════════════════════════════════════════════

def calculate_ssim(bytes1, bytes2):
    try:
        i1 = Image.open(io.BytesIO(bytes1)).convert('L').resize((256, 256))
        i2 = Image.open(io.BytesIO(bytes2)).convert('L').resize((256, 256))
        return round(ssim_fn(np.array(i1), np.array(i2)) * 100, 2)
    except Exception:
        return 0.0


# ══════════════════════════════════════════════════════════
# ELA
# ══════════════════════════════════════════════════════════

def perform_ela(img, quality=90):
    img_rgb = img.convert("RGB")
    buf = io.BytesIO()
    img_rgb.save(buf, format='JPEG', quality=quality)
    buf.seek(0)
    compressed = Image.open(buf).convert("RGB")
    ela = ImageChops.difference(img_rgb, compressed)
    extrema = ela.getextrema()
    max_diff = max([ex[1] for ex in extrema])
    scale = 255.0 / max_diff if max_diff != 0 else 1
    ela = ImageEnhance.Brightness(ela).enhance(scale)
    score = float(np.mean(np.array(ela)))
    return ela, score

def get_manipulation_verdict(score):
    if score > 15:
        return "HIGH — Significant manipulation detected", "#e05252", "HIGH"
    elif score > 8:
        return "MODERATE — Possible editing detected", "#d97706", "MODERATE"
    else:
        return "LOW — Image appears authentic", "#34d399", "LOW"


# ══════════════════════════════════════════════════════════
# WEIGHTED SCORE & VERDICT
# ══════════════════════════════════════════════════════════

def calculate_weighted_similarity(p, a, d, ssim_score, has_original=False):
    if has_original and ssim_score > 0:
        hash_score = (p * 0.45) + (a * 0.35) + (d * 0.20)
        return round((hash_score * 0.7) + (ssim_score * 0.3), 2)
    return round((p * 0.45) + (a * 0.40) + (d * 0.15), 2)

def get_violation_verdict(sim):
    if sim >= 85:
        return ("HIGH VIOLATION — Likely Unauthorized Copy", "#e05252", "HIGH",
                "This image is very likely an unauthorized copy of registered official media.")
    elif sim >= 65:
        return ("MODERATE RISK — Possible Misappropriation", "#d97706", "MODERATE",
                "This image shows significant similarity and may have been misappropriated.")
    elif sim >= 45:
        return ("LOW-MODERATE — Similar Content Detected", "#fbbf24", "LOW-MODERATE",
                "This image has some similarity to registered media. Worth investigating further.")
    else:
        return ("LOW RISK — No Strong Match Found", "#34d399", "LOW",
                "This image does not appear to match any registered media in the vault.")


# ══════════════════════════════════════════════════════════
# 2FA & ACCESS CODE
# ══════════════════════════════════════════════════════════

def generate_totp_secret():
    return pyotp.random_base32()

def verify_totp(secret, code):
    return pyotp.TOTP(secret).verify(code.strip(), valid_window=2)

def get_totp_uri(secret, org_name):
    return pyotp.TOTP(secret).provisioning_uri(name=org_name, issuer_name="MediaGuard")

def generate_access_code():
    chars = string.ascii_uppercase + string.digits
    return "MG-" + "".join(secrets.choice(chars) for _ in range(8))


# ══════════════════════════════════════════════════════════
# PDF DESIGN TOKENS
# ══════════════════════════════════════════════════════════

W, H = A4

C_BG          = colors.HexColor("#06070a")
C_SURFACE     = colors.HexColor("#0c0f14")
C_RAISED      = colors.HexColor("#111520")
C_BORDER      = colors.HexColor("#1c2230")
C_ACCENT      = colors.HexColor("#3d7fff")
C_ACCENT_DIM  = colors.HexColor("#0d1a35")
C_TEXT_1      = colors.HexColor("#f0f2f5")
C_TEXT_2      = colors.HexColor("#8d95a3")
C_TEXT_3      = colors.HexColor("#4d5666")
C_RED         = colors.HexColor("#e05252")
C_RED_DIM     = colors.HexColor("#2a1215")
C_ORANGE      = colors.HexColor("#d97706")
C_ORANGE_DIM  = colors.HexColor("#241a08")
C_GREEN       = colors.HexColor("#34d399")
C_GREEN_DIM   = colors.HexColor("#0a2018")
C_YELLOW      = colors.HexColor("#fbbf24")
C_YELLOW_DIM  = colors.HexColor("#211c08")

MARGIN_L  = 44
MARGIN_R  = 44
CONTENT_W = W - MARGIN_L - MARGIN_R

F_REG  = "Helvetica"
F_BOLD = "Helvetica-Bold"
F_OBL  = "Helvetica-Oblique"


# ══════════════════════════════════════════════════════════
# PDF PRIMITIVE HELPERS
# ══════════════════════════════════════════════════════════

def _rect(c, x, y, w, h, fill=None, stroke=None, radius=0):
    c.setLineWidth(0.5)
    if fill:   c.setFillColor(fill)
    if stroke: c.setStrokeColor(stroke)
    else:      c.setStrokeColor(colors.transparent)
    if radius > 0:
        c.roundRect(x, y, w, h, radius,
                    fill=1 if fill else 0,
                    stroke=1 if stroke else 0)
    else:
        c.rect(x, y, w, h,
               fill=1 if fill else 0,
               stroke=1 if stroke else 0)

def _text(c, x, y, txt, font=F_REG, size=10, color=C_TEXT_2, align="left"):
    c.setFillColor(color)
    c.setFont(font, size)
    s = str(txt)
    if align == "center": c.drawCentredString(x, y, s)
    elif align == "right": c.drawRightString(x, y, s)
    else: c.drawString(x, y, s)

def _line(c, x1, y1, x2, y2, color=C_BORDER, width=0.5):
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(x1, y1, x2, y2)

def _score_color(pct):
    if pct >= 80: return C_RED
    if pct >= 60: return C_ORANGE
    if pct >= 40: return C_YELLOW
    return C_GREEN


# ══════════════════════════════════════════════════════════
# PDF COMPONENT DRAWERS
# ══════════════════════════════════════════════════════════

def _draw_background(c):
    _rect(c, 0, 0, W, H, fill=C_BG)
    c.setStrokeColor(colors.HexColor("#0f1218"))
    c.setLineWidth(0.25)
    for yy in range(0, int(H), 80):
        c.line(0, yy, W, yy)


def _draw_header(c, report_no, generated_at):
    _rect(c, 0, H - 70, W, 70, fill=C_SURFACE)
    _line(c, 0, H - 70, W, H - 70, color=C_BORDER, width=0.75)
    _rect(c, 0, H - 70, 3, 70, fill=C_ACCENT)

    _text(c, MARGIN_L, H - 28, "MEDIAGUARD",
          font=F_BOLD, size=17, color=C_TEXT_1)
    _text(c, MARGIN_L, H - 44, "FORENSIC EVIDENCE REPORT",
          font=F_REG, size=8, color=C_ACCENT)
    _text(c, MARGIN_L, H - 58, "Digital Asset Protection Platform",
          font=F_REG, size=7.5, color=C_TEXT_3)

    rx = W - MARGIN_R
    _text(c, rx, H - 26, "Report No.", font=F_REG, size=7, color=C_TEXT_3, align="right")
    _text(c, rx, H - 38, report_no,    font=F_BOLD, size=9.5, color=C_TEXT_1, align="right")
    _text(c, rx, H - 52, generated_at, font=F_REG, size=7.5, color=C_TEXT_3, align="right")
    _text(c, rx, H - 64, "CONFIDENTIAL", font=F_BOLD, size=7, color=C_RED, align="right")


def _draw_footer(c, report_no, page_num):
    _line(c, MARGIN_L, 36, W - MARGIN_R, 36, color=C_BORDER)
    _text(c, MARGIN_L, 22,
          "MediaGuard — Digital Asset Protection Platform",
          font=F_BOLD, size=6.5, color=C_TEXT_3)
    _text(c, W / 2, 22, f"Report {report_no}",
          font=F_REG, size=6.5, color=C_TEXT_3, align="center")
    _text(c, W - MARGIN_R, 22, f"Page {page_num}",
          font=F_REG, size=6.5, color=C_TEXT_3, align="right")


def _draw_section_header(c, y, number, title):
    _text(c, MARGIN_L, y, f"{number}", font=F_BOLD, size=7.5, color=C_ACCENT)
    _text(c, MARGIN_L + 20, y, title, font=F_BOLD, size=10, color=C_TEXT_1)
    _line(c, MARGIN_L, y - 6, W - MARGIN_R, y - 6, color=C_BORDER)
    return y - 20


def _draw_verdict_banner(c, sim, risk_level, risk_color, risk_dim, plain_text, y):
    bh = 80
    _rect(c, MARGIN_L, y - bh, CONTENT_W, bh, fill=risk_dim, radius=8)
    _rect(c, MARGIN_L, y - bh, CONTENT_W, bh, stroke=risk_color, radius=8)
    _rect(c, MARGIN_L, y - bh, 4, bh, fill=risk_color)

    # Dot indicator
    c.setFillColor(risk_color)
    c.circle(MARGIN_L + 20, y - 20, 4, fill=1, stroke=0)

    _text(c, MARGIN_L + 32, y - 24, risk_level,
          font=F_BOLD, size=13, color=risk_color)
    _text(c, MARGIN_L + 14, y - 40, plain_text,
          font=F_REG, size=8, color=C_TEXT_2)

    # Score block on right
    score_x = W - MARGIN_R - 90
    _text(c, score_x, y - 18, f"{sim:.1f}%",
          font=F_BOLD, size=28, color=risk_color)
    _text(c, score_x, y - 34, "SIMILARITY", font=F_REG, size=7, color=C_TEXT_3)
    _text(c, score_x, y - 44, "SCORE",      font=F_REG, size=7, color=C_TEXT_3)

    # Vertical separator
    _line(c, score_x - 12, y - 12, score_x - 12, y - bh + 12,
          color=C_BORDER, width=0.5)

    return y - bh - 14


def _draw_kv_table(c, y, rows, col_split=0.36):
    row_h = 22
    total_h = len(rows) * row_h
    key_w = CONTENT_W * col_split
    val_x = MARGIN_L + key_w + 12

    _rect(c, MARGIN_L, y - total_h, CONTENT_W, total_h, stroke=C_BORDER, radius=6)

    for i, (k, v) in enumerate(rows):
        ry = y - (i + 1) * row_h
        if i % 2 == 0:
            _rect(c, MARGIN_L, ry, CONTENT_W, row_h,
                  fill=colors.HexColor("#0d1018"))
        _rect(c, MARGIN_L, ry, key_w, row_h, fill=C_RAISED)
        _text(c, MARGIN_L + 10, ry + 7, k,
              font=F_BOLD, size=7.5, color=C_TEXT_3)
        _text(c, val_x, ry + 7, v,
              font=F_REG, size=8.5, color=C_TEXT_1)
        if i < len(rows) - 1:
            _line(c, MARGIN_L, ry, W - MARGIN_R, ry,
                  color=C_BORDER, width=0.3)

    return y - total_h - 14


def _draw_score_table(c, y, score_rows, risk_color):
    col_w = [118, 62, 68, CONTENT_W - 248]
    headers = ["ALGORITHM", "SCORE", "SIGNAL", "WHAT IT EXAMINES"]
    hdr_h, row_h = 20, 23

    # Header
    _rect(c, MARGIN_L, y - hdr_h, CONTENT_W, hdr_h, fill=C_RAISED)
    cx = MARGIN_L + 10
    for i, h in enumerate(headers):
        _text(c, cx, y - hdr_h + 6, h, font=F_BOLD, size=7, color=C_TEXT_3)
        cx += col_w[i]

    # Rows
    for ri, (label, pct, signal, desc, is_total) in enumerate(score_rows):
        ry = y - hdr_h - (ri + 1) * row_h
        bg = C_ACCENT_DIM if is_total else (colors.HexColor("#0d1018") if ri % 2 == 0 else C_SURFACE)
        _rect(c, MARGIN_L, ry, CONTENT_W, row_h, fill=bg)
        if not is_total:
            _line(c, MARGIN_L, ry, W - MARGIN_R, ry, color=C_BORDER, width=0.25)

        cx = MARGIN_L + 10
        fn = F_BOLD if is_total else F_REG
        tc = C_ACCENT if is_total else C_TEXT_1
        sc = risk_color if is_total else _score_color(pct)

        _text(c, cx, ry + 7, label, font=fn, size=8.5, color=tc)
        cx += col_w[0]

        _text(c, cx, ry + 7, f"{pct:.1f}%", font=F_BOLD, size=8.5, color=sc)
        # mini bar
        _rect(c, cx, ry + 3, 48, 3, fill=C_BORDER)
        bar = int(min(pct, 100) / 100 * 48)
        if bar > 0:
            _rect(c, cx, ry + 3, bar, 3, fill=sc)
        cx += col_w[1]

        _text(c, cx, ry + 7, signal, font=fn, size=8, color=sc)
        cx += col_w[2]

        _text(c, cx, ry + 7, desc, font=F_REG, size=8, color=C_TEXT_2)

    total_h = hdr_h + len(score_rows) * row_h
    _rect(c, MARGIN_L, y - total_h, CONTENT_W, total_h, stroke=C_BORDER, radius=6)
    return y - total_h - 14


def _draw_manip_row(c, y, score, level, verdict_text, manip_color, manip_dim):
    bh = 52
    _rect(c, MARGIN_L, y - bh, CONTENT_W, bh, fill=manip_dim, radius=6)
    _rect(c, MARGIN_L, y - bh, CONTENT_W, bh, stroke=manip_color, radius=6)
    _rect(c, MARGIN_L, y - bh, 4, bh, fill=manip_color)

    _text(c, MARGIN_L + 16, y - 16, f"ELA SCORE: {score:.2f}",
          font=F_BOLD, size=9, color=C_TEXT_1)
    _text(c, MARGIN_L + 16, y - 29, level,
          font=F_BOLD, size=8.5, color=manip_color)
    _text(c, MARGIN_L + 16, y - 42, verdict_text,
          font=F_REG, size=7.5, color=C_TEXT_2)

    score_x = W - MARGIN_R - 70
    _text(c, score_x, y - 18, f"{score:.1f}",
          font=F_BOLD, size=22, color=manip_color, align="right")
    _text(c, score_x, y - 33, "ELA", font=F_REG, size=7, color=C_TEXT_3, align="right")

    return y - bh - 14


def _draw_summary_box(c, y, lines):
    line_h = 14
    pad = 14
    bh = len(lines) * line_h + pad * 2
    _rect(c, MARGIN_L, y - bh, CONTENT_W, bh,
          fill=colors.HexColor("#0a0d15"), radius=6)
    _rect(c, MARGIN_L, y - bh, CONTENT_W, bh, stroke=C_BORDER, radius=6)
    _rect(c, MARGIN_L, y - 3,  CONTENT_W, 3,  fill=C_ACCENT)
    for i, tl in enumerate(lines):
        _text(c, MARGIN_L + pad, y - pad - 3 - i * line_h,
              tl, font=F_REG, size=8.5, color=C_TEXT_2)
    return y - bh - 14


def _draw_legal_item(c, y, title, body_text):
    # Title strip
    _rect(c, MARGIN_L, y - 20, CONTENT_W, 20, fill=C_RAISED)
    _rect(c, MARGIN_L, y - 20, 3, 20, fill=C_ACCENT)
    _text(c, MARGIN_L + 12, y - 14, title, font=F_BOLD, size=8, color=C_ACCENT)

    # Body — word-wrap via Paragraph
    style = ParagraphStyle("b", fontName=F_REG, fontSize=8,
                            textColor=C_TEXT_2, leading=13)
    para = Paragraph(body_text, style)
    pw = CONTENT_W - 24
    _, body_h = para.wrap(pw, 999)
    body_h += 16

    _rect(c, MARGIN_L, y - 20 - body_h, CONTENT_W, body_h, fill=C_SURFACE)
    _rect(c, MARGIN_L, y - 20 - body_h, CONTENT_W, 20 + body_h,
          stroke=C_BORDER, radius=4)
    para.drawOn(c, MARGIN_L + 12, y - 20 - body_h + 8)

    return y - 20 - body_h - 10


def _new_page(c, report_no, generated_at, page_num):
    c.showPage()
    _draw_background(c)
    _draw_header(c, report_no, generated_at)
    _draw_footer(c, report_no, page_num)
    return H - 90


# ══════════════════════════════════════════════════════════
# MAIN PDF GENERATOR
# ══════════════════════════════════════════════════════════

def generate_report_pdf(best, sim, risk_level, manip_verdict, manip_score, filename):
    """
    Generate a premium dark-theme forensic evidence PDF.
    Identical signature to original — drop-in replacement.

    Args:
        best        : dict with keys asset_name, org_name, registered_at,
                      p_sim, a_sim, d_sim, ssim_sim
        sim         : float — weighted overall similarity score
        risk_level  : str — "HIGH" | "MODERATE" | "LOW-MODERATE" | "LOW"
        manip_verdict: str — human-readable manipulation verdict
        manip_score : float — ELA score
        filename    : str — original uploaded file name

    Returns:
        BytesIO — ready for st.download_button or file.write()
    """
    buffer     = io.BytesIO()
    report_no  = f"MG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    generated  = datetime.now().strftime("%d %B %Y  •  %H:%M IST")

    # Color maps
    RISK_MAP = {
        "HIGH":         (C_RED,    C_RED_DIM),
        "MODERATE":     (C_ORANGE, C_ORANGE_DIM),
        "LOW-MODERATE": (C_YELLOW, C_YELLOW_DIM),
        "LOW":          (C_GREEN,  C_GREEN_DIM),
    }
    risk_color, risk_dim = RISK_MAP.get(risk_level, (C_ACCENT, C_ACCENT_DIM))

    if manip_score > 15:
        manip_color, manip_dim, manip_level = C_RED,    C_RED_DIM,    "HIGH"
    elif manip_score > 8:
        manip_color, manip_dim, manip_level = C_ORANGE, C_ORANGE_DIM, "MODERATE"
    else:
        manip_color, manip_dim, manip_level = C_GREEN,  C_GREEN_DIM,  "LOW"

    RISK_PLAIN = {
        "HIGH":         "strongly indicates an unauthorized copy",
        "MODERATE":     "suggests possible misappropriation",
        "LOW-MODERATE": "shows some similarity worth investigating",
        "LOW":          "does not match any registered media",
    }
    MANIP_PLAIN = {
        "HIGH":     "Significant manipulation / AI editing detected.",
        "MODERATE": "Minor manipulation indicators found.",
        "LOW":      "No manipulation detected — image appears authentic.",
    }

    def signal(pct):
        if pct >= 70: return "HIGH"
        if pct >= 40: return "MEDIUM"
        return "LOW"

    cv = canvas.Canvas(buffer, pagesize=A4)
    cv.setTitle(f"MediaGuard Forensic Report — {report_no}")
    cv.setAuthor("MediaGuard Digital Asset Protection Platform")
    cv.setSubject("Forensic Evidence Report — Confidential")

    # ── PAGE 1 ──────────────────────────────────────────────
    _draw_background(cv)
    _draw_header(cv, report_no, generated)
    _draw_footer(cv, report_no, 1)

    y = H - 90

    # ── SECTION 01: FINDING SUMMARY ─────────────────────────
    y = _draw_section_header(cv, y, "01", "FINDING SUMMARY")

    summary_lines = [
        f"Exhibit File:  {filename}",
        f"Finding:       This image {RISK_PLAIN.get(risk_level, '')}",
        f"               of officially registered media.",
        f"Rights Holder: {best['org_name']}",
        f"Matched Asset: {best['asset_name']}",
        f"Registered On: {best['registered_at'][:10]}",
        f"Manipulation:  {MANIP_PLAIN.get(manip_level, '')}",
    ]
    y = _draw_summary_box(cv, y, summary_lines)
    y -= 6

    # Verdict banner
    y = _draw_verdict_banner(cv, sim, risk_level, risk_color, risk_dim,
                             RISK_PLAIN.get(risk_level, ""), y)

    # ── SECTION 02: CASE DETAILS ─────────────────────────────
    y = _draw_section_header(cv, y, "02", "CASE DETAILS")

    case_rows = [
        ("Exhibit File Name",            filename),
        ("Matched Registered Asset",     best["asset_name"]),
        ("Rights Holder / Organisation", best["org_name"]),
        ("Asset Registration Date",      best["registered_at"][:10]),
        ("Analysis Timestamp",           datetime.now().strftime("%d %B %Y, %H:%M:%S IST")),
        ("Report Reference No.",         report_no),
        ("Overall Risk Assessment",      risk_level),
    ]
    y = _draw_kv_table(cv, y, case_rows)

    # ── SECTION 03: TECHNICAL ANALYSIS ───────────────────────
    if y < 180:
        y = _new_page(cv, report_no, generated, 2)

    y = _draw_section_header(cv, y, "03", "TECHNICAL SIMILARITY ANALYSIS")

    score_rows = [
        ("Perceptual Hash  (pHash)", best["p_sim"],    signal(best["p_sim"]),
         "Overall visual structure & composition", False),
        ("Average Hash     (aHash)", best["a_sim"],    signal(best["a_sim"]),
         "Brightness & tone distribution", False),
        ("Difference Hash  (dHash)", best["d_sim"],    signal(best["d_sim"]),
         "Edge patterns & gradients", False),
        ("Structural Sim.  (SSIM)",  best["ssim_sim"], signal(best["ssim_sim"]),
         "Pixel-level match vs stored original", False),
        ("WEIGHTED FINAL SCORE",     sim,              risk_level,
         "Combined — 70% fingerprint hashing + 30% SSIM", True),
    ]
    y = _draw_score_table(cv, y, score_rows, risk_color)

    # ── SECTION 04: MANIPULATION DETECTION ───────────────────
    if y < 120:
        y = _new_page(cv, report_no, generated, 2)

    y = _draw_section_header(cv, y, "04", "MANIPULATION & AI EDIT DETECTION  (ELA)")
    y = _draw_manip_row(cv, y, manip_score, manip_level, manip_verdict,
                        manip_color, manip_dim)

    # ── SECTION 05: LEGAL REFERENCES ─────────────────────────
    if y < 260:
        y = _new_page(cv, report_no, generated, 2)

    y = _draw_section_header(cv, y, "05", "APPLICABLE LAW & LEGAL BASIS")

    legal_items = [
        ("IT Act 2000 — Section 66",
         "Any person who knowingly or intentionally copies, reproduces, or distributes a digital "
         "asset without consent of the rightful owner commits an offence punishable with "
         "imprisonment up to 3 years and/or a fine up to Rs. 5,00,000."),
        ("Copyright Act 1957 — Intellectual Property",
         "Official sports media including photographs, video clips, and broadcast content generated "
         "by recognised rights holders (BCCI, FIFA, IPL etc.) is protected under copyright. "
         "Any unauthorized reproduction, redistribution, or commercial use without a valid licence "
         "constitutes infringement."),
        ("Bharatiya Sakshya Adhiniyam 2023 — Section 63",
         "Electronic records and digital forensic reports generated through automated systems with "
         "verifiable methodology are admissible as evidence in legal proceedings. This report, "
         "generated by the MediaGuard platform, qualifies as electronic evidence and may be "
         "submitted to any court or authority in India."),
    ]

    for title, body in legal_items:
        if y < 130:
            y = _new_page(cv, report_no, generated, 2)
        y = _draw_legal_item(cv, y, title, body)

    # ── DISCLAIMER ────────────────────────────────────────────
    if y < 70:
        y = _new_page(cv, report_no, generated, 2)

    _text(cv, MARGIN_L, y - 10,
          "DISCLAIMER: This report is generated automatically by MediaGuard. Scores are indicative. "
          "Review by a qualified forensic examiner is recommended before sole legal use.",
          font=F_REG, size=6.5, color=C_TEXT_3)

    cv.save()
    buffer.seek(0)
    return buffer