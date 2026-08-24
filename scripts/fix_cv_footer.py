from __future__ import annotations

import os
import sys
import zipfile
from pathlib import Path


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def run_properties() -> str:
    return (
        '<w:rPr>'
        '<w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Arial" w:cs="Arial"/>'
        '<w:color w:val="AAAAAA"/>'
        '<w:sz w:val="16"/><w:szCs w:val="16"/>'
        '</w:rPr>'
    )


def text_run(text: str) -> str:
    escaped = (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    return f'<w:r>{run_properties()}<w:t xml:space="preserve">{escaped}</w:t></w:r>'


def field_run(instruction: str, cached_value: str) -> str:
    props = run_properties()
    return (
        f'<w:r>{props}<w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r>'
        f'<w:r>{props}<w:instrText xml:space="preserve"> {instruction} </w:instrText></w:r>'
        f'<w:r>{props}<w:fldChar w:fldCharType="separate"/></w:r>'
        f'<w:r>{props}<w:t>{cached_value}</w:t></w:r>'
        f'<w:r>{props}<w:fldChar w:fldCharType="end"/></w:r>'
    )


def paragraph(alignment: str, content: str) -> str:
    return (
        '<w:p><w:pPr><w:pStyle w:val="Footer"/>'
        '<w:spacing w:before="0" w:after="0"/>'
        f'<w:jc w:val="{alignment}"/></w:pPr>{content}</w:p>'
    )


def cell(width: int, alignment: str, content: str) -> str:
    return (
        '<w:tc><w:tcPr>'
        f'<w:tcW w:w="{width}" w:type="dxa"/>'
        '<w:tcMar>'
        '<w:top w:w="0" w:type="dxa"/><w:left w:w="0" w:type="dxa"/>'
        '<w:bottom w:w="0" w:type="dxa"/><w:right w:w="0" w:type="dxa"/>'
        '</w:tcMar><w:vAlign w:val="center"/></w:tcPr>'
        f'{paragraph(alignment, content)}'
        '</w:tc>'
    )


def footer_xml() -> bytes:
    left_width = 3000
    right_width = 6831
    left = text_run("CV ID 20260823_005")
    right = (
        text_run("JOÃO JOSÉ  |  CURRICULUM VITAE  |  ")
        + field_run("PAGE", "1")
        + text_run("/")
        + field_run("NUMPAGES", "2")
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:ftr xmlns:w="{W_NS}">'
        '<w:tbl><w:tblPr>'
        '<w:tblW w:w="9831" w:type="dxa"/>'
        '<w:jc w:val="left"/><w:tblInd w:w="0" w:type="dxa"/>'
        '<w:tblBorders>'
        '<w:top w:val="nil"/><w:left w:val="nil"/><w:bottom w:val="nil"/>'
        '<w:right w:val="nil"/><w:insideH w:val="nil"/><w:insideV w:val="nil"/>'
        '</w:tblBorders>'
        '<w:tblLayout w:type="fixed"/>'
        '<w:tblCellMar>'
        '<w:top w:w="0" w:type="dxa"/><w:left w:w="0" w:type="dxa"/>'
        '<w:bottom w:w="0" w:type="dxa"/><w:right w:w="0" w:type="dxa"/>'
        '</w:tblCellMar>'
        '</w:tblPr>'
        f'<w:tblGrid><w:gridCol w:w="{left_width}"/><w:gridCol w:w="{right_width}"/></w:tblGrid>'
        f'<w:tr>{cell(left_width, "left", left)}{cell(right_width, "right", right)}</w:tr>'
        '</w:tbl>'
        '<w:p><w:pPr><w:spacing w:before="0" w:after="0"/></w:pPr></w:p>'
        '</w:ftr>'
    )
    return xml.encode("utf-8")


def update_settings(data: bytes) -> bytes:
    text = data.decode("utf-8")
    if "<w:updateFields" in text:
        return data
    return text.replace(
        "</w:settings>", '<w:updateFields w:val="true"/></w:settings>'
    ).encode("utf-8")


def patch_docx(path: Path) -> None:
    temp_path = path.with_suffix(".footer-fix.tmp.docx")
    with zipfile.ZipFile(path, "r") as source, zipfile.ZipFile(
        temp_path, "w", zipfile.ZIP_DEFLATED
    ) as target:
        names = set(source.namelist())
        if "word/footer1.xml" not in names:
            raise RuntimeError("word/footer1.xml was not found")

        for item in source.infolist():
            data = source.read(item.filename)
            if item.filename == "word/footer1.xml":
                data = footer_xml()
            elif item.filename == "word/settings.xml":
                data = update_settings(data)
            target.writestr(item, data)

    os.replace(temp_path, path)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: fix_cv_footer.py <document.docx>")
    patch_docx(Path(sys.argv[1]).resolve())
