#!/usr/bin/env python3
"""Apply the codex-effort-estimator workbook format to an .xlsx file.

This deterministic post-processor normalizes workbook shape, cell styles,
column widths, and basic QA checks after an estimate workbook has been
generated. It does not create estimate content or change numeric values.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    from openpyxl import load_workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
except ImportError as exc:
    raise SystemExit(
        "openpyxl is required. Use the bundled Codex Python runtime or install openpyxl."
    ) from exc


COLORS = {
    "header": "1F4E78",
    "header_text": "FFFFFF",
    "total": "E2F0D9",
    "assumption": "FFF2CC",
    "risk": "FCE4D6",
    "neutral": "F2F2F2",
    "border": "D9E1F2",
}

STANDARD_SHEETS = [
    "00_サマリー",
    "01_工程別",
    "02_規模根拠",
    "03_WBS",
    "04_PERT",
    "05_類推補正",
    "06_Discovery",
    "07_AI補正",
    "08_公共レビュー",
    "09_Repo",
    "10_親統合",
    "11_前提リスク",
]

REQUIRED_SHEETS = {
    "00_サマリー",
    "01_工程別",
    "02_規模根拠",
    "03_WBS",
    "04_PERT",
    "10_親統合",
    "11_前提リスク",
}

EXPECTED_COLUMNS = {
    "00_サマリー": ["項目", "値", "補足"],
    "01_工程別": ["工程", "WBS", "PERT", "AI補正後", "親最終", "メモ"],
    "02_規模根拠": ["分類", "項目", "数量", "根拠", "確度", "WBS/PERTへの反映"],
    "03_WBS": ["分類", "作業", "根拠", "Low", "Most likely", "High", "AI削減区分", "メモ"],
    "04_PERT": ["タスク", "根拠", "楽観", "最頻/普通", "悲観", "期待値", "SD", "分散", "AI削減区分", "メモ"],
    "05_類推補正": ["比較対象", "類似点", "差分", "実績/見積", "信頼度", "補正示唆"],
    "06_Discovery": ["調査項目", "目的", "Low", "Likely", "High", "成果物", "実装見積への影響"],
    "07_AI補正": ["分類", "工程", "ベースライン", "倍率", "補正後", "削減可否", "根拠"],
    "08_公共レビュー": ["観点", "根拠", "分類", "影響", "非重複の追加候補"],
    "09_Repo": ["領域", "測定事実", "推定", "Low", "Base", "High", "メモ"],
    "10_親統合": ["Pass", "状態", "理由", "根拠"],
    "11_前提リスク": ["種別", "内容", "影響", "確認/対応"],
}

WIDTHS = {
    "00_サマリー": [18, 22, 48, 14, 14, 48],
    "01_工程別": [18, 12, 12, 14, 14, 50],
    "02_規模根拠": [14, 26, 11, 48, 12, 36],
    "03_WBS": [14, 28, 48, 11, 13, 11, 14, 42],
    "04_PERT": [30, 42, 11, 13, 11, 12, 10, 11, 14, 40],
    "05_類推補正": [26, 36, 36, 14, 13, 40],
    "06_Discovery": [26, 38, 11, 11, 11, 30, 40],
    "07_AI補正": [14, 28, 13, 11, 13, 14, 48],
    "08_公共レビュー": [20, 52, 14, 48, 20],
    "09_Repo": [20, 48, 20, 11, 11, 11, 40],
    "10_親統合": [22, 22, 48, 38, 13, 13, 40, 40],
    "11_前提リスク": [12, 58, 38, 42],
}

NUMERIC_HEADERS = {
    "Low",
    "Most likely",
    "Likely",
    "High",
    "Base",
    "WBS",
    "PERT",
    "AI補正後",
    "親最終",
    "数量",
    "楽観",
    "最頻/普通",
    "悲観",
    "期待値",
    "SD",
    "分散",
    "ベースライン",
    "倍率",
    "補正後",
    "Final Low",
    "Final Base",
    "Final High",
    "Most likely total",
    "Expected total",
    "Total SD",
    "90% CI Low",
    "90% CI High",
    "Endpoint Low",
    "Endpoint High",
}

FORMULA_ERRORS = {"#REF!", "#VALUE!", "#DIV/0!", "#NAME?", "#N/A"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize a codex-effort-estimator .xlsx workbook format."
    )
    parser.add_argument("workbook", type=Path, help="Input .xlsx workbook.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output path. Defaults to <input stem>_formatted.xlsx.",
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Overwrite the input workbook instead of writing a formatted copy.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when validation warnings are found.",
    )
    return parser.parse_args()


def fill(color: str) -> PatternFill:
    return PatternFill(fill_type="solid", fgColor=color)


def text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def used_bounds(ws: Any) -> tuple[int, int]:
    max_row = ws.max_row or 1
    max_col = ws.max_column or 1
    while max_row > 1 and all(ws.cell(max_row, col).value is None for col in range(1, max_col + 1)):
        max_row -= 1
    while max_col > 1 and all(ws.cell(row, max_col).value is None for row in range(1, max_row + 1)):
        max_col -= 1
    return max_row, max_col


def row_values(ws: Any, row: int, max_col: int) -> list[str]:
    return [text(ws.cell(row, col).value) for col in range(1, max_col + 1)]


def find_header_row(ws: Any, expected: list[str]) -> int:
    expected_set = set(expected)
    best_row = 4
    best_score = -1
    for row in range(1, min(ws.max_row or 1, 15) + 1):
        values = set(row_values(ws, row, max(ws.max_column or 1, len(expected))))
        score = len(values & expected_set)
        if score > best_score:
            best_row = row
            best_score = score
    return best_row


def set_full_recalc(wb: Any) -> None:
    calc = getattr(wb, "calculation", None)
    if calc is not None:
        calc.fullCalcOnLoad = True
        calc.forceFullCalc = True


def apply_sheet_layout(ws: Any, sheet_name: str, warnings: list[str]) -> None:
    max_row, max_col = used_bounds(ws)
    widths = WIDTHS.get(sheet_name, [])

    ws.sheet_view.showGridLines = False
    ws.freeze_panes = "A5"

    if ws["A1"].value is None:
        ws["A1"] = sheet_name
    ws["A1"].font = Font(name="Yu Gothic", size=14, bold=True)
    ws["A1"].alignment = Alignment(wrap_text=True, vertical="top")

    if ws["A2"].value is not None:
        ws["A2"].fill = fill(COLORS["neutral"])

    for idx in range(1, max(max_col, len(widths)) + 1):
        width = widths[idx - 1] if idx <= len(widths) else 16
        ws.column_dimensions[get_column_letter(idx)].width = width

    expected = EXPECTED_COLUMNS.get(sheet_name, [])
    header_row = find_header_row(ws, expected) if expected else 4
    headers = row_values(ws, header_row, max_col)
    if expected and headers[: len(expected)] != expected:
        missing = [col for col in expected if col not in headers]
        if missing:
            warnings.append(f"{sheet_name}: missing expected columns: {', '.join(missing)}")

    thin = Side(style="thin", color=COLORS["border"])
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    numeric_cols = {
        idx
        for idx, header in enumerate(headers, start=1)
        if header in NUMERIC_HEADERS
        or header.endswith("Low")
        or header.endswith("High")
        or header.endswith("Base")
        or header.endswith("total")
        or header.endswith("SD")
    }

    for row in range(1, max_row + 1):
        first_value = text(ws.cell(row, 1).value)
        row_is_header = row == header_row
        row_is_total = first_value in {"合計", "Total", "WBS由来合計"} or "最終推奨" in first_value
        row_kind = text(ws.cell(row, 1).value)

        for col in range(1, max_col + 1):
            cell = ws.cell(row, col)
            cell.font = Font(
                name="Yu Gothic",
                size=10,
                bold=row_is_header or row_is_total or row == 1,
                color=COLORS["header_text"] if row_is_header else "000000",
            )
            cell.border = border
            cell.alignment = Alignment(
                wrap_text=True,
                vertical="top",
                horizontal="right" if col in numeric_cols and row > header_row else "left",
            )

            if row_is_header:
                cell.fill = fill(COLORS["header"])
            elif row_is_total:
                cell.fill = fill(COLORS["total"])
            elif sheet_name == "11_前提リスク" and row > header_row:
                if row_kind == "リスク":
                    cell.fill = fill(COLORS["risk"])
                elif row_kind in {"前提", "確認"}:
                    cell.fill = fill(COLORS["assumption"])
                elif row_kind == "除外":
                    cell.fill = fill(COLORS["neutral"])

            if col in numeric_cols and row > header_row:
                if text(cell.value).endswith("%"):
                    cell.number_format = "0%"
                elif headers[col - 1] == "倍率":
                    cell.number_format = "0.00"
                else:
                    cell.number_format = "0.0"


def validate_and_format(wb: Any) -> tuple[list[str], list[str]]:
    warnings: list[str] = []
    errors: list[str] = []
    names = wb.sheetnames

    for sheet in REQUIRED_SHEETS:
        if sheet not in names:
            errors.append(f"missing required sheet: {sheet}")

    unknown = [name for name in names if name not in STANDARD_SHEETS]
    if unknown:
        warnings.append(f"unknown sheet names: {', '.join(unknown)}")

    positions = {name: idx for idx, name in enumerate(STANDARD_SHEETS)}
    seen = [name for name in names if name in positions]
    if seen != sorted(seen, key=lambda name: positions[name]):
        warnings.append("standard sheets are not in the expected order")

    for ws in wb.worksheets:
        apply_sheet_layout(ws, ws.title, warnings)
        max_row, max_col = used_bounds(ws)
        for row in range(1, max_row + 1):
            for col in range(1, max_col + 1):
                value = text(ws.cell(row, col).value)
                if value in FORMULA_ERRORS:
                    errors.append(f"{ws.title}!{get_column_letter(col)}{row}: {value}")

    return warnings, errors


def main() -> int:
    args = parse_args()
    input_path = args.workbook
    if not input_path.exists():
        print(f"Workbook not found: {input_path}", file=sys.stderr)
        return 2
    if input_path.suffix.lower() != ".xlsx":
        print(f"Expected an .xlsx file: {input_path}", file=sys.stderr)
        return 2
    if args.output and args.in_place:
        print("Use either --output or --in-place, not both.", file=sys.stderr)
        return 2

    output_path = args.output
    if output_path is None:
        output_path = input_path if args.in_place else input_path.with_name(f"{input_path.stem}_formatted.xlsx")

    wb = load_workbook(input_path)
    set_full_recalc(wb)
    warnings, errors = validate_and_format(wb)
    wb.save(output_path)

    report = {
        "input": str(input_path),
        "output": str(output_path),
        "sheets": wb.sheetnames,
        "warnings": warnings,
        "errors": errors,
        "representative_visual_check_sheets": [
            name for name in ["00_サマリー", "04_PERT", "07_AI補正", "10_親統合"] if name in wb.sheetnames
        ],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
