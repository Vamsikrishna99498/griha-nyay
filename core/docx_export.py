"""Turn a code-built draft (the Markdown the templates produce) into a Word document a homebuyer can open in
Word or Google Docs, fill in the [brackets], print and send. Pure formatting: no wording is added, removed
or changed, so the legal text in the Word file is exactly the verified text on screen.

Handles only what the templates and the case summary use: '# ' / '## ' headings, '> ' note lines, '- ' bullets
(indented for a second level), '- [ ] ' checklist items, numbered paragraphs, **bold**, _italic_, runs of plain
lines (an address block), and ```json blocks of calculator figures, shown as a readable list."""
from __future__ import annotations

import io
import json
import re

from docx import Document
from docx.enum.text import WD_COLOR_INDEX
from docx.shared import Pt, RGBColor

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
INLINE_RE = re.compile(r"(\*\*.+?\*\*|(?<![\w\[])_[^_\n]+?_(?![\w\]]))")
BRACKET_RE = re.compile(r"(\[[^\]\n]+\])")
NOTE_GREY = RGBColor(0x55, 0x5F, 0x6B)


def _runs(paragraph, text: str, *, bold: bool = False, italic: bool = False, colour: RGBColor | None = None) -> None:
    """Add text with **bold** and _italic_ marks turned into formatting; every [bracket] to fill in is highlighted."""
    for part in INLINE_RE.split(text):
        if not part:
            continue
        b, i, inner = bold, italic, part
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            b, inner = True, part[2:-2]
        elif part.startswith("_") and part.endswith("_") and len(part) > 2:
            i, inner = True, part[1:-1]
        for piece in BRACKET_RE.split(inner):
            if not piece:
                continue
            run = paragraph.add_run(piece)
            run.bold, run.italic = b, i
            if colour is not None:
                run.font.color.rgb = colour
            if BRACKET_RE.fullmatch(piece):
                run.font.highlight_color = WD_COLOR_INDEX.YELLOW


# Plain names for the calculator's fields in the downloaded summary. Unknown fields get their key with '_' as spaces.
FIELD_NAMES = {
    "as_of": "Worked out on", "promised_possession_date": "Promised possession date", "possession_handed_over_date": "Possession received on",
    "delay": "Delay", "interest_rate": "Interest rate", "amount_paid": "Amount paid",
    "option_stay_monthly_interest": "If you stay: interest per month", "option_stay_interest_accrued_so_far": "If you stay: interest so far",
    "option_refund_interest_so_far": "If you withdraw: interest so far", "option_refund_total_so_far": "If you withdraw: total refund so far",
    "delay_interest_per_month": "Delay interest per month", "delay_interest_for_the_whole_delay": "Delay interest for the whole delay",
    "refund_figures": "Refund figures", "possession_handed_over": "Possession received on", "five_year_window_ends": "Five-year defect period ends",
    "within_five_year_window": "Within the five-year period", "defects_reported_to_builder_on": "Defects reported to the builder on",
    "builder_30_day_fix_deadline": "Builder's 30 days to repair end on", "builder_past_30_days": "Builder past the 30 days", "notes": "Notes",
}


def _value(v) -> str:
    if v is None:
        return "not known"
    if isinstance(v, bool):
        return "yes" if v else "no"
    return str(v)


def _figures(doc, lines: list) -> None:
    """A ```json block of calculator figures becomes 'Name: value' bullets (lists as sub-bullets). Values are
    shown exactly as computed; if the block isn't a JSON object it is kept as plain lines."""
    try:
        data = json.loads("\n".join(lines))
    except json.JSONDecodeError:
        data = None
    if not isinstance(data, dict):
        for line in lines:
            doc.add_paragraph(line)
        return
    for key, v in data.items():
        name = FIELD_NAMES.get(key, key.replace("_", " ").capitalize())
        p = doc.add_paragraph(style="List Bullet")
        p.add_run(f"{name}: ").bold = True
        if isinstance(v, list):
            for item in v:
                doc.add_paragraph(_value(item), style="List Bullet 2")
        else:
            p.add_run(_value(v))


def markdown_to_docx(text: str) -> bytes:
    doc = Document()
    normal = doc.styles["Normal"]
    normal.font.name, normal.font.size = "Calibri", Pt(11)
    normal.paragraph_format.space_after = Pt(6)
    block: list[str] = []   # consecutive plain lines (an address block) stay together, one per line

    def flush() -> None:
        if block:
            p = doc.add_paragraph()
            for k, line in enumerate(block):
                if k:
                    p.add_run().add_break()
                _runs(p, line)
            block.clear()

    fence: list | None = None   # lines inside a ``` block
    for raw in text.splitlines():
        line = raw.rstrip()
        if line.startswith("```"):
            flush()
            if fence is None:
                fence = []
            else:
                _figures(doc, fence)
                fence = None
            continue
        if fence is not None:
            fence.append(line)
            continue
        if not line.strip():
            flush()
            continue
        if line.startswith("> "):            # the DRAFT note at the top: grey, smaller, set apart
            flush()
            note = line[2:]
            p = doc.add_paragraph(style="List Bullet" if note.startswith("- ") else None)
            p.paragraph_format.space_after = Pt(2)
            _runs(p, note[2:] if note.startswith("- ") else note, colour=NOTE_GREY)
            for r in p.runs:
                r.font.size = Pt(9.5)
            continue
        if line.startswith("## "):
            flush()
            doc.add_heading(line[3:].strip("* "), level=2)
            continue
        if line.startswith("# "):
            flush()
            doc.add_heading(line[2:].strip("* "), level=1)
            continue
        bullet = re.match(r"^(\s*)- (.*)$", line)
        if bullet:
            flush()
            item = bullet.group(2)
            if item.startswith("[ ] "):        # a checklist item: a box to tick, not a [bracket] to fill in
                _runs(doc.add_paragraph(), "☐ " + item[4:])
                continue
            p = doc.add_paragraph(style="List Bullet 2" if len(bullet.group(1)) >= 2 else "List Bullet")
            _runs(p, item)
            continue
        if re.match(r"^\d+\.\s", line):      # numbered paragraphs keep the number the template gave them
            flush()
            _runs(doc.add_paragraph(), line)
            continue
        block.append(line.strip())
    flush()
    out = io.BytesIO()
    doc.save(out)
    return out.getvalue()
