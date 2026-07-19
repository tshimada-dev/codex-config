#!/usr/bin/env python3
"""Render a field investigation state bundle to workbook.xlsx.

The canonical state remains STATE.md, CSV files, and command-log.jsonl.
This script creates a human-readable XLSX view without requiring third-party
packages.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


SHEETS = [
    ("概要", "STATE.md", "markdown"),
    ("確認項目", "checks.csv", "csv"),
    ("コマンドログ", "command-log.jsonl", "jsonl"),
    ("仮説一覧", "hypotheses.csv", "csv"),
    ("時系列", "timeline.csv", "csv"),
    ("接続情報", "connections.csv", "csv"),
]

COMMAND_LOG_LEADING_COLUMNS = ["occurred_at", "recorded_at"]
INVALID_XML_CHARACTER = re.compile(
    "[\\x00-\\x08\\x0b\\x0c\\x0e-\\x1f\\ud800-\\udfff\\ufffe\\uffff]"
)
MAX_EXCEL_CELL_LENGTH = 32_767


def read_csv(path: Path) -> list[list[str]]:
    if not path.exists():
        return [["Missing file"], [path.name]]
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [list(row) for row in csv.reader(handle)] or [["Empty file"], [path.name]]


def read_jsonl(path: Path) -> list[list[str]]:
    if not path.exists():
        return [["Missing file"], [path.name]]

    rows: list[dict[str, object]] = []
    keys: list[str] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                item = {"Line": line_number, "Parse error": str(exc), "Raw": line}
            if not isinstance(item, dict):
                item = {"Line": line_number, "Value": item}
            rows.append(item)
            for key in item:
                if key not in keys:
                    keys.append(key)

    if not rows:
        return [["Empty file"], [path.name]]
    keys = COMMAND_LOG_LEADING_COLUMNS + [
        key for key in keys if key not in COMMAND_LOG_LEADING_COLUMNS
    ]
    return [keys] + [[stringify(row.get(key, "")) for key in keys] for row in rows]


def read_markdown(path: Path) -> list[list[str]]:
    if not path.exists():
        return [["Missing file"], [path.name]]

    rows: list[list[str]] = []
    in_table = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if line.startswith("|") and line.endswith("|"):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
                in_table = True
                continue
            rows.append(cells)
            in_table = True
            continue
        in_table = False
        if line:
            rows.append([line])
        elif rows and not in_table:
            rows.append([""])

    return rows or [["Empty file"], [path.name]]


def stringify(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def column_name(index: int) -> str:
    name = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name


def sanitize_xml_text(value: object) -> str:
    return INVALID_XML_CHARACTER.sub("", str(value))[:MAX_EXCEL_CELL_LENGTH]


def column_widths(rows: list[list[str]]) -> list[float]:
    column_count = max((len(row) for row in rows), default=1)
    widths = []
    for column_index in range(column_count):
        longest = max(
            (
                max((len(line) for line in sanitize_xml_text(row[column_index]).splitlines()), default=0)
                for row in rows
                if column_index < len(row)
            ),
            default=0,
        )
        widths.append(float(min(60, max(10, longest + 2))))
    return widths


def sheet_xml(rows: list[list[str]], header_rows: Iterable[int] = (1,)) -> str:
    header_row_numbers = set(header_rows)
    columns = "".join(
        f'<col min="{index}" max="{index}" width="{width:g}" customWidth="1"/>'
        for index, width in enumerate(column_widths(rows), start=1)
    )
    out = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">',
        '<sheetViews><sheetView workbookViewId="0">'
        '<pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/>'
        '</sheetView></sheetViews>',
        f"<cols>{columns}</cols>",
        "<sheetData>",
    ]
    for row_index, row in enumerate(rows, start=1):
        out.append(f'<row r="{row_index}">')
        for col_index, value in enumerate(row, start=1):
            ref = f"{column_name(col_index)}{row_index}"
            sanitized = sanitize_xml_text(value)
            escaped = html.escape(sanitized, quote=False)
            style = ' s="1"' if row_index in header_row_numbers else ""
            preserve_space = (
                ' xml:space="preserve"'
                if sanitized[:1].isspace() or sanitized[-1:].isspace()
                else ""
            )
            out.append(
                f'<c r="{ref}" t="inlineStr"{style}><is><t{preserve_space}>'
                f"{escaped}</t></is></c>"
            )
        out.append("</row>")
    out.extend(["</sheetData>", "</worksheet>"])
    return "".join(out)


def workbook_xml(sheet_names: Iterable[str]) -> str:
    sheets_xml = []
    for index, name in enumerate(sheet_names, start=1):
        escaped = html.escape(name, quote=True)
        sheets_xml.append(
            f'<sheet name="{escaped}" sheetId="{index}" r:id="rId{index}"/>'
        )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f"<sheets>{''.join(sheets_xml)}</sheets>"
        "</workbook>"
    )


def workbook_rels_xml(count: int) -> str:
    rels = []
    for index in range(1, count + 1):
        rels.append(
            f'<Relationship Id="rId{index}" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
            f'Target="worksheets/sheet{index}.xml"/>'
        )
    rels.append(
        f'<Relationship Id="rId{count + 1}" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
        'Target="styles.xml"/>'
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f"{''.join(rels)}"
        "</Relationships>"
    )


def content_types_xml(count: int) -> str:
    overrides = [
        '<Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
        '<Override PartName="/xl/styles.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>',
    ]
    for index in range(1, count + 1):
        overrides.append(
            f'<Override PartName="/xl/worksheets/sheet{index}.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        f"{''.join(overrides)}"
        "</Types>"
    )


def styles_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<fonts count="2">'
        '<font><sz val="11"/><name val="Calibri"/><family val="2"/></font>'
        '<font><b/><color rgb="FFFFFFFF"/><sz val="11"/><name val="Calibri"/><family val="2"/></font>'
        '</fonts>'
        '<fills count="3">'
        '<fill><patternFill patternType="none"/></fill>'
        '<fill><patternFill patternType="gray125"/></fill>'
        '<fill><patternFill patternType="solid"><fgColor rgb="FF1F4E78"/>'
        '<bgColor indexed="64"/></patternFill></fill>'
        '</fills>'
        '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
        '<cellXfs count="2">'
        '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
        '<xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" '
        'applyFont="1" applyFill="1"/>'
        '</cellXfs>'
        '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
        '</styleSheet>'
    )


def root_rels_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="xl/workbook.xml"/>'
        "</Relationships>"
    )


def load_sheet(bundle_dir: Path, filename: str, kind: str) -> list[list[str]]:
    path = bundle_dir / filename
    if kind == "csv":
        return read_csv(path)
    if kind == "jsonl":
        return read_jsonl(path)
    if kind == "markdown":
        return read_markdown(path)
    raise ValueError(f"unsupported sheet kind: {kind}")


def source_line_count(path: Path) -> str:
    if not path.exists():
        return "Missing"
    return str(len(path.read_text(encoding="utf-8-sig").splitlines()))


def summary_rows(bundle_dir: Path, captured_at: datetime) -> list[list[str]]:
    metadata = [
        ["Snapshot timestamp (UTC)", captured_at.astimezone(timezone.utc).isoformat(timespec="seconds")],
        ["Source file", "Line count"],
    ]
    metadata.extend(
        [filename, source_line_count(bundle_dir / filename)] for _, filename, _ in SHEETS
    )
    metadata.append([""])
    return metadata + read_markdown(bundle_dir / "STATE.md")


def render(bundle_dir: Path, output: Path, captured_at: datetime | None = None) -> None:
    snapshot_at = captured_at or datetime.now(timezone.utc)
    sheet_rows = [
        (
            sheet_name,
            summary_rows(bundle_dir, snapshot_at)
            if filename == "STATE.md"
            else load_sheet(bundle_dir, filename, kind),
        )
        for sheet_name, filename, kind in SHEETS
    ]

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types_xml(len(sheet_rows)))
        archive.writestr("_rels/.rels", root_rels_xml())
        archive.writestr("xl/workbook.xml", workbook_xml(name for name, _ in sheet_rows))
        archive.writestr("xl/_rels/workbook.xml.rels", workbook_rels_xml(len(sheet_rows)))
        archive.writestr("xl/styles.xml", styles_xml())
        for index, (_, rows) in enumerate(sheet_rows, start=1):
            header_rows = (1, 2) if index == 1 else (1,)
            archive.writestr(
                f"xl/worksheets/sheet{index}.xml", sheet_xml(rows, header_rows)
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render an investigation state bundle to workbook.xlsx."
    )
    parser.add_argument("bundle_dir", type=Path)
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output .xlsx path. Defaults to <bundle-dir>/workbook.xlsx.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    bundle_dir = args.bundle_dir.resolve()
    if not bundle_dir.exists() or not bundle_dir.is_dir():
        print(f"Bundle directory not found: {bundle_dir}", file=sys.stderr)
        return 2
    output = (args.output or (bundle_dir / "workbook.xlsx")).resolve()
    render(bundle_dir, output)
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
