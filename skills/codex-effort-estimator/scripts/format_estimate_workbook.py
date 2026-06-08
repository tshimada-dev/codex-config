#!/usr/bin/env python3
"""Apply the codex-effort-estimator presentation workbook format.

The formatter is intentionally deterministic. It can take the raw estimator
workbook shape or an already formatted workbook, then rebuild the first two
sheets for readability, remove charts, renumber sheets by tab order, apply
stable widths/styles, and run lightweight validation.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    from openpyxl import load_workbook
    from openpyxl.formatting.rule import ColorScaleRule
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
except ImportError as exc:
    raise SystemExit(
        "openpyxl is required. Use the bundled Codex Python runtime or install openpyxl."
    ) from exc


COLORS = {
    "header": "1F4E79",
    "header_text": "FFFFFF",
    "subtle_header": "DDEBF7",
    "total": "E2F0D9",
    "assumption": "FFF2CC",
    "risk": "FCE4D6",
    "neutral": "F2F2F2",
    "border": "D9E2F3",
    "text": "1F1F1F",
    "muted": "666666",
}

PRESENTATION_LABELS = [
    "結論",
    "内訳",
    "規模根拠",
    "WBS",
    "PERT",
    "単価アンカー",
    "パラメトリック",
    "FP",
    "UCP",
    "トップダウン",
    "AI補正",
    "公共レビュー",
    "リスクモデル",
    "制約",
    "Discovery",
    "前提リスク",
    "類推補正",
    "Repo",
    "親統合",
]

LABEL_ALIASES = {
    "サマリー": "結論",
    "工程別": "内訳",
    "単価契約": "単価アンカー",
}

METHOD_NAMES = {
    "WBS",
    "単価アンカー",
    "パラメトリック",
    "FP",
    "UCP",
    "トップダウン",
    "制約/容量",
    "制約",
    "リスクモデル",
}

PHASE_NOTES = {
    "PM/管理": ("削りすぎ注意", "会議、進捗、課題管理、受入調整。公共案件では固定費化しやすい。", "03_WBS/11_公共レビュー"),
    "要件/業務分析": ("削減困難", "既存資料確認、業務ヒアリング、例外ルール整理。AIで代替しにくい。", "02_規模根拠"),
    "設計": ("一部削減", "設計書たたき台やレビュー観点整理は補助可能。", "04_PERT/10_AI補正"),
    "基盤実装": ("削減余地大", "定型CRUD、認証、共通部品、環境構築は補助効果が出やすい。", "10_AI補正"),
    "データ取込/出力": ("一部削減", "CSV/Excel入出力は定型化できるが、文字コードと照合は残る。", "10_AI補正/15_前提リスク"),
    "計算/業務ルール": ("削りすぎ注意", "計算式実装は補助可能。ただし検算・制度確認は人手中心。", "11_公共レビュー"),
    "業務フロー実装": ("削減余地あり", "画面/ワークフローの実装補助は効くが、業務確認は残る。", "08_UCP"),
    "外部連携": ("一部削減", "IF仕様の確定と接続試験の不確実性に注意。", "06_パラメトリック"),
    "Excel/PDF帳票": ("削りすぎ注意", "帳票再現・印字位置・受入比較が重い。実装補助より検証が支配的。", "05_単価アンカー/11_公共レビュー"),
    "NFR/セキュリティ": ("削減困難", "セキュリティ、監査、運用要件は確認とレビューが中心。", "15_前提リスク"),
    "テスト/受入": ("削りすぎ注意", "テスト生成は補助可能だが、証跡・受入比較・修正確認は残る。", "11_公共レビュー/12_リスクモデル"),
    "研修/マニュアル/納品": ("一部削減", "ドラフト生成は効くが、顧客向け整備と納品確認は必要。", "03_WBS"),
}

WIDTHS = {
    "00_結論": [24, 18, 42, 18, 28, 28],
    "01_内訳": [24, 15, 15, 13, 12, 16, 58, 24],
    "02_規模根拠": [14, 28, 14, 54, 12, 38],
    "03_WBS": [16, 34, 54, 11, 13, 11, 14, 46],
    "04_PERT": [34, 48, 11, 13, 11, 12, 10, 11, 14, 42],
    "05_単価アンカー": [24, 12, 12, 12, 40, 44],
    "06_パラメトリック": [28, 12, 12, 12, 12, 58],
    "07_FP": [24, 12, 12, 12, 58],
    "08_UCP": [24, 12, 12, 12, 58],
    "09_トップダウン": [24, 12, 12, 12, 12, 64],
    "10_AI補正": [16, 30, 14, 11, 14, 14, 56],
    "11_公共レビュー": [22, 58, 16, 54, 24],
    "12_リスクモデル": [28, 20, 62, 18],
    "13_制約": [24, 12, 22, 58],
    "14_Discovery": [28, 42, 11, 11, 11, 32, 46],
    "15_前提リスク": [12, 64, 42, 46],
    "16_類推補正": [26, 38, 38, 16, 13, 42],
    "17_Repo": [22, 54, 22, 11, 11, 11, 44],
    "18_親統合": [28, 20, 58, 58],
}

TAB_COLORS = {
    "00_結論": "70AD47",
    "01_内訳": "5B9BD5",
    "02_規模根拠": "9EADCC",
    "03_WBS": "4472C4",
    "04_PERT": "4472C4",
    "05_単価アンカー": "A9D18E",
    "06_パラメトリック": "A9D18E",
    "07_FP": "A9D18E",
    "08_UCP": "A9D18E",
    "09_トップダウン": "A9D18E",
    "10_AI補正": "F4B183",
    "11_公共レビュー": "F4B183",
    "12_リスクモデル": "C65911",
    "13_制約": "C65911",
    "14_Discovery": "FFD966",
    "15_前提リスク": "C65911",
    "16_類推補正": "B4C6E7",
    "17_Repo": "B4C6E7",
    "18_親統合": "B4C6E7",
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
    "楽観/Low",
    "普通/Base",
    "悲観/High",
    "中心/期待値",
    "AI補助後目安",
    "AI補助前WBS",
    "差分",
    "削減率",
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


def label_for(title: str) -> str:
    label = re.sub(r"^\d+_", "", title)
    return LABEL_ALIASES.get(label, label)


def sheet_by_label(wb: Any, *labels: str) -> Any | None:
    wanted = set(labels)
    for ws in wb.worksheets:
        if label_for(ws.title) in wanted:
            return ws
    return None


def used_bounds(ws: Any) -> tuple[int, int]:
    max_row = ws.max_row or 1
    max_col = ws.max_column or 1
    while max_row > 1 and all(ws.cell(max_row, col).value is None for col in range(1, max_col + 1)):
        max_row -= 1
    while max_col > 1 and all(ws.cell(row, max_col).value is None for row in range(1, max_row + 1)):
        max_col -= 1
    return max_row, max_col


def clear_sheet(ws: Any) -> None:
    if ws.max_row:
        ws.delete_rows(1, ws.max_row)
    if ws.max_column:
        ws.delete_cols(1, ws.max_column)
    ws._charts = []
    ws.conditional_formatting._cf_rules.clear()
    ws.auto_filter.ref = None


def first_value(values: tuple[Any, ...], default: Any = None) -> Any:
    return values[0] if values else default


def extract_summary_values(ws: Any | None) -> dict[str, tuple[Any, ...]]:
    values: dict[str, tuple[Any, ...]] = {}
    if ws is None:
        return values
    for row in ws.iter_rows(values_only=True):
        if row and row[0]:
            values[text(row[0])] = row[1:]
    return values


def extract_method_rows(ws: Any | None) -> list[list[Any]]:
    rows: list[list[Any]] = []
    if ws is None:
        return rows
    table_kind = ""
    for row in ws.iter_rows(values_only=True):
        if row and text(row[0]) in {"手法", "方法別レンジ"}:
            table_kind = "readable" if text(row[0]) == "方法別レンジ" else "raw"
            continue
        if not row or text(row[0]) not in METHOD_NAMES:
            continue
        name = text(row[0])
        if name == "制約":
            name = "制約/容量"
        opt = row[1] if len(row) > 1 else None
        if table_kind == "readable":
            center = row[2] if len(row) > 2 else None
            high = row[3] if len(row) > 3 else None
            note = row[5] if len(row) > 5 else None
        elif table_kind == "raw" and len(row) > 5:
            center = row[4]
            high = row[3] if len(row) > 3 else None
            note = row[5]
        else:
            center = row[2] if len(row) > 2 else None
            high = row[3] if len(row) > 3 else None
            note = row[5] if len(row) > 5 else None
        width = high - opt if isinstance(opt, (int, float)) and isinstance(high, (int, float)) else None
        rows.append([name, opt, center, high, width, note])
    return rows


def extract_phase_rows(ws: Any | None) -> list[list[Any]]:
    rows: list[list[Any]] = []
    if ws is None:
        return rows
    for row in ws.iter_rows(values_only=True):
        if not row or not row[0]:
            continue
        phase = text(row[0])
        if phase not in PHASE_NOTES:
            continue
        if len(row) > 5 and isinstance(row[1], (int, float)) and isinstance(row[5], (int, float)):
            wbs = row[1]
            ai = row[5]
        elif len(row) > 2 and isinstance(row[1], (int, float)) and isinstance(row[2], (int, float)):
            ai = row[1]
            wbs = row[2]
        else:
            continue
        diff = ai - wbs if isinstance(wbs, (int, float)) and isinstance(ai, (int, float)) else None
        rate = diff / wbs if isinstance(diff, (int, float)) and wbs else None
        judgement, note, ref = PHASE_NOTES[phase]
        rows.append([phase, ai, wbs, diff, rate, judgement, note, ref])
    return rows


def base_styles() -> dict[str, Any]:
    thin = Side(style="thin", color=COLORS["border"])
    medium = Side(style="medium", color=COLORS["header"])
    return {
        "border": Border(top=thin, bottom=thin, left=thin, right=thin),
        "header_border": Border(top=medium, bottom=thin, left=thin, right=thin),
        "title_font": Font(name="Yu Gothic", size=18, bold=True, color=COLORS["header_text"]),
        "section_font": Font(name="Yu Gothic", size=12, bold=True, color=COLORS["header_text"]),
        "header_font": Font(name="Yu Gothic", size=10, bold=True, color=COLORS["text"]),
        "body_font": Font(name="Yu Gothic", size=10, color=COLORS["text"]),
        "bold_font": Font(name="Yu Gothic", size=10, bold=True, color=COLORS["text"]),
        "note_font": Font(name="Yu Gothic", size=9, color=COLORS["muted"]),
        "big_font": Font(name="Yu Gothic", size=14, bold=True, color=COLORS["header"]),
        "center": Alignment(horizontal="center", vertical="center", wrap_text=True),
        "left": Alignment(horizontal="left", vertical="top", wrap_text=True),
        "right": Alignment(horizontal="right", vertical="center", wrap_text=True),
    }


def rebuild_conclusion_sheet(ws: Any, summary: dict[str, tuple[Any, ...]], methods: list[list[Any]]) -> None:
    st = base_styles()
    clear_sheet(ws)
    ws.sheet_view.showGridLines = False
    ws.freeze_panes = "A5"
    ws.merge_cells("A1:F1")
    ws["A1"] = "配水課案件 見積結論"
    ws["A1"].fill = fill(COLORS["header"])
    ws["A1"].font = st["title_font"]
    ws["A1"].alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[1].height = 30

    ws.append(["結論", "値", "読み方", "提出時の扱い", "補足", "確認観点"])
    for cell in ws[2]:
        cell.fill = fill(COLORS["subtle_header"])
        cell.font = st["header_font"]
        cell.alignment = st["center"]
        cell.border = st["header_border"]

    rows = [
        ["推奨レンジ（AI補助あり）", first_value(summary.get("推奨レンジ（AI補助あり）", ("370-560人日",))), "提出用の主レンジ。実装効率化を織り込んだ現実線。", "主表示", "中心値は下段の計画中心を使用", "レンジ幅と前提を明記"],
        ["計画中心（AI補助あり）", first_value(summary.get("計画中心（AI補助あり）", ("460人日",))), "計画・体制検討で使う中心値。", "主表示", "単独数字で出す場合の代表値", "工期/体制との整合"],
        ["推奨レンジ（AI補助前）", first_value(summary.get("推奨レンジ（AI補助前）", ("420-620人日",))), "AI補助を保守的に見た場合の比較線。", "参考表示", "顧客説明では差分根拠として利用", "削減根拠の説明"],
        ["Discovery別枠", first_value(summary.get("Discovery別枠", ("28/51/81人日",))), "要件確定前に切り出す調査・確認枠。", "別枠表示", "本体見積に混ぜない", "契約範囲の明確化"],
        ["体制目安", first_value(summary.get("体制目安", ("3FTE前後",))), "並行度とレビュー負荷を踏まえた体制感。", "補足", "過密投入よりレビュー品質を優先", "納期制約"],
        ["信頼度", first_value(summary.get("信頼度", ("中",))), "資料ベース見積としての確度。", "補足", "受入比較・帳票再現が主要不確実性", "追加資料で更新"],
    ]
    for row in rows:
        ws.append(row)
    for row in ws.iter_rows(min_row=3, max_row=8, min_col=1, max_col=6):
        for cell in row:
            cell.font = st["body_font"]
            cell.alignment = st["left"] if cell.column != 2 else st["center"]
            cell.border = st["border"]
        row[0].font = st["bold_font"]
        row[1].font = st["big_font"]
        row[1].fill = fill(COLORS["total"])

    ws.append([])
    ws.append(["結論の根拠", "要点", "影響", "扱い", "参照シート", ""])
    for cell in ws[10]:
        cell.fill = fill(COLORS["header"])
        cell.font = st["section_font"]
        cell.alignment = st["center"]
        cell.border = st["header_border"]
    basis_rows = [
        ["WBS/PERT", "工程積上げを主アンカーにする。", "全体規模の基礎", "主根拠", "03_WBS / 04_PERT", ""],
        ["複数独立観点", "単価アンカー、パラメトリック、UCP、トップダウン等で横串確認。", "WBS一本依存を緩和", "妥当性確認", "05-13系シート", ""],
        ["AI補正", "定型実装・帳票・テスト補助は削減、要件/照合は削りすぎない。", "提出中心を調整", "補正根拠", "10_AI補正", ""],
        ["公共案件レビュー", "受入比較、帳票忠実度、文字コード、制度改正を厚めに確認。", "リスク過小評価を抑制", "レビュー根拠", "11_公共レビュー / 15_前提リスク", ""],
    ]
    for row in basis_rows:
        ws.append(row)
    for row in ws.iter_rows(min_row=11, max_row=14, min_col=1, max_col=5):
        for cell in row:
            cell.font = st["body_font"]
            cell.alignment = st["left"]
            cell.border = st["border"]
        row[0].font = st["bold_font"]

    ws.append([])
    start = ws.max_row + 1
    ws.append(["方法別レンジ", "楽観", "中心/平均", "悲観", "幅", "メモ"])
    for cell in ws[start]:
        cell.fill = fill(COLORS["subtle_header"])
        cell.font = st["header_font"]
        cell.alignment = st["center"]
        cell.border = st["header_border"]
    for row in methods:
        ws.append(row)
    for row in ws.iter_rows(min_row=start + 1, max_row=ws.max_row, min_col=1, max_col=6):
        for cell in row:
            cell.font = st["body_font"]
            cell.alignment = st["left"] if cell.column in (1, 6) else st["right"]
            cell.border = st["border"]
            if cell.column in (2, 3, 4, 5):
                cell.number_format = "0.0"
        row[0].font = st["bold_font"]


def rebuild_breakdown_sheet(ws: Any, phases: list[list[Any]]) -> None:
    st = base_styles()
    clear_sheet(ws)
    ws.sheet_view.showGridLines = False
    ws.freeze_panes = "A4"
    ws.merge_cells("A1:H1")
    ws["A1"] = "工程別 内訳"
    ws["A1"].fill = fill(COLORS["header"])
    ws["A1"].font = st["title_font"]
    ws["A1"].alignment = Alignment(horizontal="left", vertical="center")
    ws["A2"] = "AI補助後の提出中心に対して、どの工程でどれだけ差が出ているかを確認するシート。"
    ws["A2"].font = st["note_font"]
    ws.merge_cells("A2:H2")
    ws.append(["工程", "AI補助後目安", "AI補助前WBS", "差分", "削減率", "削減可否", "主な内容/注意", "参照"])
    for cell in ws[3]:
        cell.fill = fill(COLORS["subtle_header"])
        cell.font = st["header_font"]
        cell.alignment = st["center"]
        cell.border = st["header_border"]
    for row in phases:
        ws.append(row)
    last = ws.max_row
    ws.append([
        "合計",
        f"=SUM(B4:B{last})",
        f"=SUM(C4:C{last})",
        f"=SUM(D4:D{last})",
        f"=D{last + 1}/C{last + 1}",
        "",
        "提出中心値は結論シートの計画中心を優先。工程内訳は丸め前の目安。",
        "00_結論",
    ])
    for row in ws.iter_rows(min_row=4, max_row=ws.max_row, min_col=1, max_col=8):
        for cell in row:
            cell.font = st["body_font"]
            cell.alignment = st["left"] if cell.column in (1, 6, 7, 8) else st["right"]
            cell.border = st["border"]
            if cell.column == 5:
                cell.number_format = "0.0%"
            elif cell.column in (2, 3, 4):
                cell.number_format = "0.0"
        row[0].font = st["bold_font"]
        if row[5].value in {"削減困難", "削りすぎ注意"}:
            row[5].fill = fill(COLORS["assumption"])
        elif row[5].value in {"削減余地大", "削減余地あり"}:
            row[5].fill = fill(COLORS["total"])
        else:
            row[5].fill = fill(COLORS["neutral"])
    for cell in ws[ws.max_row]:
        cell.font = st["bold_font"]
        cell.fill = fill(COLORS["neutral"])
    if last >= 4:
        ws.conditional_formatting.add(
            f"D4:D{last}",
            ColorScaleRule(
                start_type="min",
                start_color="63BE7B",
                mid_type="percentile",
                mid_value=50,
                mid_color="FFEB84",
                end_type="max",
                end_color="F8696B",
            ),
        )
    ws.auto_filter.ref = f"A3:H{ws.max_row}"


def renumber_and_order_sheets(wb: Any) -> None:
    by_label: dict[str, Any] = {}
    for ws in wb.worksheets:
        label = label_for(ws.title)
        if label in PRESENTATION_LABELS and label not in by_label:
            by_label[label] = ws

    for idx, (label, ws) in enumerate(by_label.items()):
        ws.title = f"_tmp_{idx:02d}_{label}"

    ordered = []
    for idx, label in enumerate(PRESENTATION_LABELS):
        ws = by_label.get(label)
        if ws is None:
            continue
        ws.title = f"{idx:02d}_{label}"
        ordered.append(ws)
    ordered_ids = {id(ws) for ws in ordered}
    ordered.extend(ws for ws in wb.worksheets if id(ws) not in ordered_ids)
    wb._sheets = ordered


def style_generic_sheet(ws: Any) -> None:
    st = base_styles()
    ws._charts = []
    ws.sheet_view.showGridLines = False
    max_row, max_col = used_bounds(ws)
    widths = WIDTHS.get(ws.title, [])
    for col in range(1, max(max_col, len(widths)) + 1):
        ws.column_dimensions[get_column_letter(col)].width = widths[col - 1] if col <= len(widths) else 16
    if ws.title not in {"00_結論", "01_内訳"}:
        ws.freeze_panes = "A2"
        if max_row >= 1:
            for cell in ws[1]:
                cell.fill = fill(COLORS["header"])
                cell.font = st["section_font"]
                cell.alignment = st["center"]
                cell.border = st["header_border"]
            ws.row_dimensions[1].height = 28
        for row in ws.iter_rows(min_row=2, max_row=max_row, min_col=1, max_col=max_col):
            for cell in row:
                cell.font = st["body_font"]
                cell.alignment = st["right"] if isinstance(cell.value, (int, float)) else st["left"]
                cell.border = st["border"]
                if isinstance(cell.value, (int, float)):
                    cell.number_format = "0.0"
            ws.row_dimensions[row[0].row].height = 28
        if max_col and max_row:
            ws.auto_filter.ref = f"A1:{get_column_letter(max_col)}{max_row}"
    else:
        for row_idx in range(1, max_row + 1):
            ws.row_dimensions[row_idx].height = 30 if ws.title == "00_結論" else 32


def normalize_presentation_workbook(wb: Any) -> None:
    source_summary = sheet_by_label(wb, "結論", "サマリー")
    source_breakdown = sheet_by_label(wb, "内訳", "工程別")
    summary = extract_summary_values(source_summary)
    methods = extract_method_rows(source_summary)
    phases = extract_phase_rows(source_breakdown)

    conclusion_ws = source_summary or wb.create_sheet("00_結論", 0)
    breakdown_ws = source_breakdown or wb.create_sheet("01_内訳", 1)
    rebuild_conclusion_sheet(conclusion_ws, summary, methods)
    rebuild_breakdown_sheet(breakdown_ws, phases)
    renumber_and_order_sheets(wb)
    for ws in wb.worksheets:
        style_generic_sheet(ws)
        ws.sheet_properties.tabColor = TAB_COLORS.get(ws.title, COLORS["border"])


def set_full_recalc(wb: Any) -> None:
    calc = getattr(wb, "calculation", None)
    if calc is not None:
        calc.fullCalcOnLoad = True
        calc.forceFullCalc = True


def validate_workbook(wb: Any) -> tuple[list[str], list[str]]:
    warnings: list[str] = []
    errors: list[str] = []
    expected_present = [f"{idx:02d}_{label}" for idx, label in enumerate(PRESENTATION_LABELS)]
    seen_standard = [name for name in wb.sheetnames if name in expected_present]
    if seen_standard != [name for name in expected_present if name in seen_standard]:
        warnings.append("standard sheets are not in the expected presentation order")

    for required in ["00_結論", "01_内訳", "02_規模根拠", "03_WBS", "04_PERT", "18_親統合", "15_前提リスク"]:
        if required not in wb.sheetnames:
            warnings.append(f"missing expected sheet after formatting: {required}")

    for ws in wb.worksheets:
        if ws._charts:
            errors.append(f"{ws.title}: charts were not removed")
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
    normalize_presentation_workbook(wb)
    warnings, errors = validate_workbook(wb)
    wb.active = 0
    wb.save(output_path)

    report = {
        "input": str(input_path),
        "output": str(output_path),
        "sheets": wb.sheetnames,
        "warnings": warnings,
        "errors": errors,
        "representative_visual_check_sheets": [
            name for name in ["00_結論", "01_内訳", "03_WBS", "10_AI補正", "18_親統合"] if name in wb.sheetnames
        ],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
