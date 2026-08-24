from __future__ import annotations

import os
import sys
from pathlib import Path

import pymupdf


def patch_pdf(path: Path) -> None:
    font_path = Path(r"C:\Windows\Fonts\arial.ttf")
    if not font_path.exists():
        raise RuntimeError(f"Arial font was not found at {font_path}")

    document = pymupdf.open(path)
    page_count = len(document)
    gray = (0xAA / 255, 0xAA / 255, 0xAA / 255)

    for index, page in enumerate(document):
        width = page.rect.width
        height = page.rect.height
        margin = 1037 / 20
        footer_top = height - 43
        baseline = height - 20

        page.add_redact_annot(
            pymupdf.Rect(0, footer_top, width, height),
            fill=(1, 1, 1),
        )
        page.apply_redactions()
        page.insert_font(fontname="ArialCV", fontfile=str(font_path))
        page.insert_text(
            pymupdf.Point(margin, baseline),
            "CV ID 20260823_005",
            fontname="ArialCV",
            fontsize=8,
            color=gray,
            overlay=True,
        )
        page.insert_textbox(
            pymupdf.Rect(margin, footer_top + 9, width - margin, height - 8),
            f"JOÃO JOSÉ  |  CURRICULUM VITAE  |  {index + 1}/{page_count}",
            fontname="ArialCV",
            fontsize=8,
            color=gray,
            align=pymupdf.TEXT_ALIGN_RIGHT,
            overlay=True,
        )

    temp_path = path.with_suffix(".footer-fix.tmp.pdf")
    document.save(temp_path, garbage=4, deflate=True)
    document.close()
    os.replace(temp_path, path)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: fix_cv_pdf_footer.py <document.pdf>")
    patch_pdf(Path(sys.argv[1]).resolve())
