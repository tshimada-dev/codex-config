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
    from openpyxl.utils import get_column_letter, range_boundaries
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

AI_MULTIPLIERS = {
    "定型実装": (
        0.70,
        "WBS作成者が削減可能と判定。係数は参照定数で固定し、補正パス側で値引き裁量を持たない。",
    ),
    "コード隣接": (
        0.85,
        "実装補助は効くが設計判断・レビュー・結合確認が残るため中程度の固定係数を適用。",
    ),
    "複雑実装": (
        0.90,
        "複雑な業務ルールやデバッグはAI支援より検証・判断が支配的なため保守的に適用。",
    ),
    "検証重": (
        0.95,
        "帳票忠実度、旧新比較、受入証跡など検証中心の作業はほぼ削らない。",
    ),
    "削減不可": (
        1.00,
        "要件、受入、調整、説明責任などAIコーディングで削らない作業。",
    ),
    "対象外": (
        1.00,
        "AI補正対象外。raw baselineをそのまま保持。",
    ),
}

AI_TAG_ALIASES = {
    "削減あり": "コード隣接",
    "一部削減": "コード隣接",
    "削減困難": "削減不可",
    "削りすぎ注意": "検証重",
    "非削減": "削減不可",
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
    "10_AI補正": [16, 34, 14, 11, 11, 11, 11, 12, 12, 12, 12, 18, 36, 54],
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
    "Raw Low",
    "Raw Base",
    "Raw High",
    "固定倍率",
    "Adjusted Low",
    "Adjusted Base",
    "Adjusted High",
    "Base差分",
}

FORMULA_ERRORS = {"#REF!", "#VALUE!", "#DIV/0!", "#NAME?", "#N/A"}

NON_ADDITIVE_HEADERS = {
    "",
    "倍率",
    "固定倍率",
    "削減率",
    "確率",
    "係数",
    "集中係数",
    "SD",
    "Total SD",
    "90% CI Low",
    "90% CI High",
}


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


def formula_numeric_value(ws: Any, formula: str, seen: set[tuple[int, int]] | None = None) -> float | None:
    expr = formula.strip()
    if expr.startswith("="):
        expr = expr[1:].strip()

    sum_match = re.fullmatch(r"SUM\(([A-Z]+\d+):([A-Z]+\d+)\)", expr, flags=re.IGNORECASE)
    if sum_match:
        min_col, min_row, max_col, max_row = range_boundaries(f"{sum_match.group(1)}:{sum_match.group(2)}")
        total = 0.0
        found = False
        for row in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):
                value = numeric_cell_value(ws, row, col, seen)
                if value is not None:
                    total += value
                    found = True
        return total if found else None

    binary_match = re.fullmatch(r"([A-Z]+\d+)\s*([+\-*/])\s*([A-Z]+\d+)", expr)
    if binary_match:
        left = numeric_ref_value(ws, binary_match.group(1), seen)
        right = numeric_ref_value(ws, binary_match.group(3), seen)
        if left is None or right is None:
            return None
        operator = binary_match.group(2)
        if operator == "+":
            return left + right
        if operator == "-":
            return left - right
        if operator == "*":
            return left * right
        if operator == "/" and right != 0:
            return left / right
        return None

    ref_match = re.fullmatch(r"([A-Z]+\d+)", expr)
    if ref_match:
        return numeric_ref_value(ws, ref_match.group(1), seen)

    return None


def numeric_ref_value(ws: Any, ref: str, seen: set[tuple[int, int]] | None = None) -> float | None:
    match = re.fullmatch(r"([A-Z]+)(\d+)", ref)
    if not match:
        return None
    col = 0
    for char in match.group(1):
        col = col * 26 + (ord(char) - ord("A") + 1)
    return numeric_cell_value(ws, int(match.group(2)), col, seen)


def numeric_cell_value(ws: Any, row: int, col: int, seen: set[tuple[int, int]] | None = None) -> float | None:
    cell_key = (row, col)
    seen = seen or set()
    if cell_key in seen:
        return None
    seen.add(cell_key)
    value = ws.cell(row, col).value
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str) and value.startswith("="):
        return formula_numeric_value(ws, value, seen)
    return None


def close_enough(actual: float, expected: float) -> bool:
    tolerance = max(0.15, abs(expected) * 0.001)
    return abs(actual - expected) <= tolerance


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


def normalize_ai_tag(value: Any) -> str:
    tag = text(value) or "対象外"
    return AI_TAG_ALIASES.get(tag, tag)


def ai_multiplier_for(tag: str) -> tuple[float, str]:
    normalized = normalize_ai_tag(tag)
    if normalized in AI_MULTIPLIERS:
        return AI_MULTIPLIERS[normalized]
    return (
        1.00,
        f"未定義のAI削減区分 `{tag}`。係数裁量を避けるため保守的に1.00を適用し、区分定義の確認を要求。",
    )


def find_header_row(ws: Any, required: set[str]) -> tuple[int | None, dict[str, int]]:
    max_row, max_col = used_bounds(ws)
    for row in range(1, min(max_row, 20) + 1):
        headers = {text(ws.cell(row, col).value): col for col in range(1, max_col + 1)}
        if required.issubset(set(headers)):
            return row, headers
    return None, {}


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


def extract_wbs_ai_rows(ws: Any | None) -> list[dict[str, Any]]:
    if ws is None:
        return []
    header_row, headers = find_header_row(
        ws,
        {"分類", "作業", "Low", "Most likely", "High", "AI削減区分"},
    )
    if header_row is None:
        return []

    rows: list[dict[str, Any]] = []
    max_row, _ = used_bounds(ws)
    for row_idx in range(header_row + 1, max_row + 1):
        category = text(ws.cell(row_idx, headers["分類"]).value)
        task = text(ws.cell(row_idx, headers["作業"]).value)
        if not category or category in {"合計", "Total", "WBS由来合計"}:
            continue
        low = ws.cell(row_idx, headers["Low"]).value
        base = ws.cell(row_idx, headers["Most likely"]).value
        high = ws.cell(row_idx, headers["High"]).value
        if not any(isinstance(value, (int, float)) for value in (low, base, high)):
            continue
        raw_tag = text(ws.cell(row_idx, headers["AI削減区分"]).value)
        tag = normalize_ai_tag(raw_tag)
        multiplier, rationale = ai_multiplier_for(tag)
        rows.append(
            {
                "category": category,
                "task": task,
                "tag": tag,
                "raw_tag": raw_tag or tag,
                "low": low,
                "base": base,
                "high": high,
                "multiplier": multiplier,
                "adjusted_low": low * multiplier if isinstance(low, (int, float)) else None,
                "adjusted_base": base * multiplier if isinstance(base, (int, float)) else None,
                "adjusted_high": high * multiplier if isinstance(high, (int, float)) else None,
                "delta_base": (base * multiplier - base) if isinstance(base, (int, float)) else None,
                "rationale": rationale,
            }
        )
    return rows


def phase_rows_from_ai_rows(ai_rows: list[dict[str, Any]]) -> list[list[Any]]:
    by_category: dict[str, dict[str, float]] = {}
    for row in ai_rows:
        category = row["category"]
        bucket = by_category.setdefault(category, {"raw": 0.0, "adjusted": 0.0})
        if isinstance(row["base"], (int, float)):
            bucket["raw"] += float(row["base"])
        if isinstance(row["adjusted_base"], (int, float)):
            bucket["adjusted"] += float(row["adjusted_base"])

    rows: list[list[Any]] = []
    for category, values in by_category.items():
        raw = values["raw"]
        adjusted = values["adjusted"]
        diff = adjusted - raw
        rate = diff / raw if raw else None
        judgement, note, ref = PHASE_NOTES.get(
            category,
            ("確認", "WBS行のAI削減区分と固定係数から集計。", "03_WBS/10_AI補正"),
        )
        rows.append([category, adjusted, raw, diff, rate, judgement, note, ref])
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


def rebuild_ai_adjustment_sheet(ws: Any, ai_rows: list[dict[str, Any]]) -> None:
    st = base_styles()
    clear_sheet(ws)
    ws.sheet_view.showGridLines = False
    ws.freeze_panes = "A5"
    ws.merge_cells("A1:N1")
    ws["A1"] = "AI補正 行レベル監査"
    ws["A1"].fill = fill(COLORS["header"])
    ws["A1"].font = st["title_font"]
    ws["A1"].alignment = Alignment(horizontal="left", vertical="center")
    ws["A2"] = "削減可否はWBS作成者が行ごとに判断し、倍率は参照定数を固定適用する。raw baselineは変更しない。"
    ws["A2"].font = st["note_font"]
    ws.merge_cells("A2:N2")
    ws.append([])
    ws.append(
        [
            "WBS分類",
            "WBS作業",
            "AI削減区分",
            "Raw Low",
            "Raw Base",
            "Raw High",
            "固定倍率",
            "Adjusted Low",
            "Adjusted Base",
            "Adjusted High",
            "Base差分",
            "判断者",
            "係数権限",
            "根拠",
        ]
    )
    for cell in ws[4]:
        cell.fill = fill(COLORS["subtle_header"])
        cell.font = st["header_font"]
        cell.alignment = st["center"]
        cell.border = st["header_border"]

    for row in ai_rows:
        next_row = ws.max_row + 1
        ws.append(
            [
                row["category"],
                row["task"],
                row["tag"],
                row["low"],
                row["base"],
                row["high"],
                row["multiplier"],
                f"=D{next_row}*G{next_row}",
                f"=E{next_row}*G{next_row}",
                f"=F{next_row}*G{next_row}",
                f"=I{next_row}-E{next_row}",
                "WBS作成者",
                "固定係数（参照定数）",
                row["rationale"],
            ]
        )

    if ai_rows:
        total_row = ws.max_row + 1
        ws.append(
            [
                "合計",
                "",
                "",
                f"=SUM(D5:D{total_row - 1})",
                f"=SUM(E5:E{total_row - 1})",
                f"=SUM(F5:F{total_row - 1})",
                "",
                f"=SUM(H5:H{total_row - 1})",
                f"=SUM(I5:I{total_row - 1})",
                f"=SUM(J5:J{total_row - 1})",
                f"=SUM(K5:K{total_row - 1})",
                "",
                "固定係数",
                "合計はWBS raw baselineとAI補正後を別掲する監査線。",
            ]
        )

    for row in ws.iter_rows(min_row=5, max_row=ws.max_row, min_col=1, max_col=14):
        for cell in row:
            cell.font = st["body_font"]
            cell.alignment = st["left"] if cell.column in (1, 2, 3, 12, 13, 14) else st["right"]
            cell.border = st["border"]
            if cell.column in (4, 5, 6, 8, 9, 10, 11):
                cell.number_format = "0.0"
            elif cell.column == 7:
                cell.number_format = "0.00"
        if row[0].value == "合計":
            for cell in row:
                cell.font = st["bold_font"]
                cell.fill = fill(COLORS["total"])
        elif row[2].value in {"削減不可", "対象外", "検証重"}:
            row[2].fill = fill(COLORS["assumption"])
        elif row[2].value == "定型実装":
            row[2].fill = fill(COLORS["total"])
        else:
            row[2].fill = fill(COLORS["neutral"])

    if ws.max_row >= 5:
        ws.auto_filter.ref = f"A4:N{ws.max_row}"


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


def mark_wbs_derived_pert(wb: Any) -> None:
    ws = sheet_by_label(wb, "PERT")
    if ws is None:
        return
    max_row, max_col = used_bounds(ws)
    is_wbs_derived = any(
        "WBS由来CI" in text(ws.cell(row, col).value)
        or "derived from WBS" in text(ws.cell(row, col).value)
        for row in range(1, max_row + 1)
        for col in range(1, max_col + 1)
    )
    if not is_wbs_derived:
        return
    ws["A3"] = "注意: このPERTは独立見積ではなく、03_WBSの三点値から算出したWBS由来CIです。方法比較では独立観測として扱わないでください。"
    ws["A3"].fill = fill(COLORS["assumption"])
    ws["A3"].font = Font(name="Yu Gothic", size=10, bold=True, color=COLORS["text"])
    ws["A3"].alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
    ws.row_dimensions[3].height = 32


def likely_table_header_row(ws: Any) -> int:
    max_row, max_col = used_bounds(ws)
    header_terms = {
        "分類",
        "作業",
        "工程",
        "観点",
        "Pass",
        "Low",
        "Base",
        "High",
        "Most likely",
        "AI削減区分",
        "WBS分類",
        "Raw Base",
    }
    best_row = 1
    best_score = -1
    for row in range(1, min(max_row, 8) + 1):
        values = [text(ws.cell(row, col).value) for col in range(1, max_col + 1)]
        non_empty = sum(1 for value in values if value)
        term_hits = sum(1 for value in values if value in header_terms)
        if values and values[0] == "案件":
            term_hits -= 2
        score = non_empty + term_hits * 3
        if score > best_score:
            best_row = row
            best_score = score
    return best_row


def header_map(ws: Any, header_row: int, max_col: int) -> dict[str, int]:
    return {text(ws.cell(header_row, col).value): col for col in range(1, max_col + 1)}


def check_total_crossfoot(ws: Any) -> list[str]:
    errors: list[str] = []
    max_row, max_col = used_bounds(ws)
    if max_row < 3 or max_col < 2:
        return errors
    header_row = likely_table_header_row(ws)
    headers = header_map(ws, header_row, max_col)
    for total_row in range(header_row + 1, max_row + 1):
        label = text(ws.cell(total_row, 1).value)
        if label not in {"合計", "Total", "WBS由来合計", "WBS由来CI"}:
            continue
        for col in range(2, max_col + 1):
            header = text(ws.cell(header_row, col).value)
            if header in NON_ADDITIVE_HEADERS or header.endswith("率"):
                continue
            total_value = numeric_cell_value(ws, total_row, col)
            if total_value is None:
                continue
            values = [
                numeric_cell_value(ws, row, col)
                for row in range(header_row + 1, total_row)
                if text(ws.cell(row, 1).value) not in {"合計", "Total", "WBS由来合計", "WBS由来CI"}
            ]
            numeric_values = [value for value in values if value is not None]
            if not numeric_values:
                continue
            expected = sum(numeric_values)
            if not close_enough(total_value, expected):
                errors.append(
                    f"{ws.title}!{get_column_letter(col)}{total_row}: total {total_value:.3f} "
                    f"does not match sum {expected:.3f} for `{header}`"
                )
    return errors


def check_ai_adjustment_crossfoot(ws: Any) -> list[str]:
    errors: list[str] = []
    max_row, max_col = used_bounds(ws)
    header_row, headers = find_header_row(
        ws,
        {"WBS分類", "WBS作業", "AI削減区分", "Raw Base", "固定倍率", "Adjusted Base", "Base差分"},
    )
    if header_row is None:
        return errors

    for row in range(header_row + 1, max_row + 1):
        if text(ws.cell(row, headers["WBS分類"]).value) in {"", "合計"}:
            continue
        tag = text(ws.cell(row, headers["AI削減区分"]).value)
        multiplier = numeric_cell_value(ws, row, headers["固定倍率"])
        expected_multiplier, _ = ai_multiplier_for(tag)
        if multiplier is None or not close_enough(multiplier, expected_multiplier):
            errors.append(
                f"{ws.title}!{get_column_letter(headers['固定倍率'])}{row}: multiplier "
                f"{multiplier} does not match fixed coefficient {expected_multiplier:.2f} for `{tag}`"
            )

        for raw_header, adjusted_header in [
            ("Raw Low", "Adjusted Low"),
            ("Raw Base", "Adjusted Base"),
            ("Raw High", "Adjusted High"),
        ]:
            if raw_header not in headers or adjusted_header not in headers or multiplier is None:
                continue
            raw = numeric_cell_value(ws, row, headers[raw_header])
            adjusted = numeric_cell_value(ws, row, headers[adjusted_header])
            if raw is None or adjusted is None:
                continue
            expected_adjusted = raw * multiplier
            if not close_enough(adjusted, expected_adjusted):
                errors.append(
                    f"{ws.title}!{get_column_letter(headers[adjusted_header])}{row}: adjusted "
                    f"{adjusted:.3f} does not match {raw_header} * multiplier {expected_adjusted:.3f}"
                )

        if "Base差分" in headers and "Raw Base" in headers and "Adjusted Base" in headers:
            raw_base = numeric_cell_value(ws, row, headers["Raw Base"])
            adjusted_base = numeric_cell_value(ws, row, headers["Adjusted Base"])
            delta = numeric_cell_value(ws, row, headers["Base差分"])
            if raw_base is not None and adjusted_base is not None and delta is not None:
                expected_delta = adjusted_base - raw_base
                if not close_enough(delta, expected_delta):
                    errors.append(
                        f"{ws.title}!{get_column_letter(headers['Base差分'])}{row}: delta "
                        f"{delta:.3f} does not match adjusted-base minus raw-base {expected_delta:.3f}"
                    )

        judge = text(ws.cell(row, headers.get("判断者", 0)).value) if "判断者" in headers else ""
        authority = text(ws.cell(row, headers.get("係数権限", 0)).value) if "係数権限" in headers else ""
        if not judge or not authority:
            errors.append(f"{ws.title}!A{row}: missing judgment/authority audit fields")
    return errors


def check_breakdown_crossfoot(ws: Any) -> list[str]:
    errors: list[str] = []
    max_row, max_col = used_bounds(ws)
    header_row, headers = find_header_row(ws, {"工程", "AI補助後目安", "AI補助前WBS", "差分", "削減率"})
    if header_row is None:
        return errors
    for row in range(header_row + 1, max_row + 1):
        if text(ws.cell(row, headers["工程"]).value) in {"", "合計"}:
            continue
        adjusted = numeric_cell_value(ws, row, headers["AI補助後目安"])
        raw = numeric_cell_value(ws, row, headers["AI補助前WBS"])
        diff = numeric_cell_value(ws, row, headers["差分"])
        rate = numeric_cell_value(ws, row, headers["削減率"])
        if adjusted is not None and raw is not None and diff is not None:
            expected_diff = adjusted - raw
            if not close_enough(diff, expected_diff):
                errors.append(
                    f"{ws.title}!{get_column_letter(headers['差分'])}{row}: diff "
                    f"{diff:.3f} does not match adjusted minus raw {expected_diff:.3f}"
                )
        if raw not in (None, 0) and diff is not None and rate is not None:
            expected_rate = diff / raw
            if not close_enough(rate, expected_rate):
                errors.append(
                    f"{ws.title}!{get_column_letter(headers['削減率'])}{row}: rate "
                    f"{rate:.3f} does not match diff/raw {expected_rate:.3f}"
                )
    return errors


def style_generic_sheet(ws: Any) -> None:
    st = base_styles()
    ws._charts = []
    ws.sheet_view.showGridLines = False
    max_row, max_col = used_bounds(ws)
    widths = WIDTHS.get(ws.title, [])
    for col in range(1, max(max_col, len(widths)) + 1):
        ws.column_dimensions[get_column_letter(col)].width = widths[col - 1] if col <= len(widths) else 16
    if ws.title in {"00_結論", "01_内訳"}:
        for row_idx in range(1, max_row + 1):
            ws.row_dimensions[row_idx].height = 30 if ws.title == "00_結論" else 32
        return

    header_row = likely_table_header_row(ws)
    ws.freeze_panes = f"A{header_row + 1}"
    if max_row >= 1:
        for cell in ws[1]:
            cell.fill = fill(COLORS["header"])
            cell.font = st["section_font"]
            cell.alignment = st["left"]
            cell.border = st["header_border"]
        ws.row_dimensions[1].height = 28
    if max_row >= 2:
        for cell in ws[2]:
            cell.fill = fill(COLORS["neutral"])

    for row in range(1, max_row + 1):
        first_value = text(ws.cell(row, 1).value)
        row_is_header = row == header_row
        row_is_total = first_value in {"合計", "Total", "WBS由来合計"} or "最終推奨" in first_value
        for col in range(1, max_col + 1):
            cell = ws.cell(row, col)
            if row == 1:
                cell.font = st["section_font"]
            elif row_is_header:
                cell.font = st["header_font"]
            elif row_is_total:
                cell.font = st["bold_font"]
            else:
                cell.font = st["body_font"]
            cell.border = st["border"]
            if row_is_header:
                cell.fill = fill(COLORS["subtle_header"])
                cell.alignment = st["center"]
            elif row_is_total:
                cell.fill = fill(COLORS["total"])
                cell.alignment = st["right"] if isinstance(cell.value, (int, float)) else st["left"]
            else:
                cell.alignment = st["right"] if isinstance(cell.value, (int, float)) else st["left"]
            if isinstance(cell.value, (int, float)):
                cell.number_format = "0.0"
        ws.row_dimensions[row].height = 28
    if max_col and max_row:
        ws.auto_filter.ref = f"A{header_row}:{get_column_letter(max_col)}{max_row}"


def normalize_presentation_workbook(wb: Any) -> None:
    source_summary = sheet_by_label(wb, "結論", "サマリー")
    source_breakdown = sheet_by_label(wb, "内訳", "工程別")
    source_wbs = sheet_by_label(wb, "WBS")
    source_ai = sheet_by_label(wb, "AI補正")
    summary = extract_summary_values(source_summary)
    methods = extract_method_rows(source_summary)
    ai_rows = extract_wbs_ai_rows(source_wbs)
    phases = phase_rows_from_ai_rows(ai_rows) if ai_rows else extract_phase_rows(source_breakdown)

    conclusion_ws = source_summary or wb.create_sheet("00_結論", 0)
    breakdown_ws = source_breakdown or wb.create_sheet("01_内訳", 1)
    ai_ws = source_ai or wb.create_sheet("10_AI補正")
    rebuild_conclusion_sheet(conclusion_ws, summary, methods)
    rebuild_breakdown_sheet(breakdown_ws, phases)
    if ai_rows:
        rebuild_ai_adjustment_sheet(ai_ws, ai_rows)
    renumber_and_order_sheets(wb)
    mark_wbs_derived_pert(wb)
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
        errors.extend(check_total_crossfoot(ws))
        if ws.title == "10_AI補正":
            errors.extend(check_ai_adjustment_crossfoot(ws))
        if ws.title == "01_内訳":
            errors.extend(check_breakdown_crossfoot(ws))
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
