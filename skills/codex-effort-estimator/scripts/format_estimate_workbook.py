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
    "トップダウン三点",
    "制約/容量",
    "制約",
    "リスクモデル",
    "コンポーネント単価",
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
    "00_結論": [24, 32, 38, 16, 24, 24],
    "01_内訳": [24, 15, 15, 13, 12, 16, 58, 24],
    "02_規模根拠": [14, 28, 14, 54, 12, 38],
    "03_WBS": [16, 34, 54, 11, 13, 11, 14, 46],
    "04_PERT": [34, 48, 11, 13, 11, 12, 10, 11, 14, 42],
    "05_単価アンカー": [26, 9, 30, 11, 11, 11, 10, 10, 10, 18, 16, 11, 11, 11, 28, 54],
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
    "18_親統合": [28, 10, 18, 18, 14, 18, 22, 64],
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

REPETITION_TERMS = (
    "地区",
    "帳票",
    "出力",
    "CSV",
    "変種",
    "類似",
    "バリアント",
    "variant",
    "report",
    "output",
)

REPETITION_EXCLUSION_TERMS = ("行", "ページ", "量", "容量", "データ行")

REPETITION_LABEL_EXCLUSIONS = ("資料ファイル", "外部システム", "対象環境")

REUSE_ASSUMPTION_TERMS = (
    "共通",
    "再利用",
    "パラメータ",
    "テンプレート",
    "skeleton",
    "variant",
    "バリアント",
    "reuse",
)

REUSE_FACTOR_PATTERNS = (
    re.compile(r"(?:variant|reuse|factor|係数|倍率)[^\d]*(0\.\d+(?:\s*[-～]\s*0\.\d+)?)", re.IGNORECASE),
    re.compile(r"(?:×|x)\s*(0\.\d+)", re.IGNORECASE),
)

AI_IMPLEMENTATION_TERMS = (
    "実装",
    "基盤",
    "UI",
    "画面",
    "CRUD",
    "CSV",
    "取込",
    "出力",
    "帳票",
    "PDF",
    "Excel",
    "テンプレ",
    "マスタ",
    "計算",
    "判定",
    "採番",
    "コード",
    "VBA",
    "script",
    "parser",
    "mapping",
)

AI_REVIEW_HEAVY_TAGS = {"複雑実装", "検証重"}

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


def extract_summary_title(ws: Any | None) -> str:
    if ws is None:
        return "見積結論"
    for row in ws.iter_rows(values_only=True):
        first = text(row[0]) if row else ""
        rest = [value for value in row[1:] if value is not None] if row else []
        if first and not rest and "見積" in first:
            return first
    return "見積結論"


def numeric_values(values: tuple[Any, ...]) -> list[float]:
    return [float(value) for value in values if isinstance(value, (int, float))]


def format_person_day(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value:g}人日"


def format_person_day_range(low: float | None, high: float | None) -> str:
    if low is None or high is None:
        return "-"
    return f"{low:g}-{high:g}人日"


def summary_range(summary: dict[str, tuple[Any, ...]], key: str) -> tuple[str, str]:
    values = summary.get(key, ())
    numbers = numeric_values(values)
    if len(numbers) >= 3:
        return format_person_day_range(numbers[0], numbers[2]), format_person_day(numbers[1])
    if len(numbers) >= 2:
        return format_person_day_range(numbers[0], numbers[-1]), "-"
    if values:
        return text(first_value(values, "-")), "-"
    return "-", "-"


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
        elif name == "トップダウン三点":
            name = "トップダウン"
        elif name == "コンポーネント単価":
            name = "単価アンカー"
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
        judgement = normalize_ai_tag(row[3] if len(row) > 3 else row[-1])
        note = "既存01_内訳由来。WBS/AI補正行を抽出できる場合はそちらを正とする。"
        ref = "01_内訳"
        rows.append([phase, ai, wbs, diff, rate, judgement, note, ref])
    return rows


def extract_wbs_ai_rows(ws: Any | None) -> list[dict[str, Any]]:
    if ws is None:
        return []
    header_row, headers = find_header_row(ws, {"分類", "作業", "Low", "AI削減区分"})
    category_col = headers.get("分類")
    task_col = headers.get("作業")
    basis_col = headers.get("根拠")
    base_col = headers.get("Most likely") or headers.get("Likely") or headers.get("Base")
    if header_row is None or base_col is None:
        header_row, headers = find_header_row(ws, {"Component", "Base", "AI削減区分"})
        category_col = None
        task_col = headers.get("Component")
        basis_col = headers.get("Basis")
        base_col = headers.get("Base")
    if header_row is None:
        return []
    low_col = headers.get("Low")
    high_col = headers.get("High")
    tag_col = headers.get("AI削減区分")
    fixed_multiplier_col = headers.get("固定倍率")
    if task_col is None or base_col is None or tag_col is None:
        return []

    rows: list[dict[str, Any]] = []
    max_row, _ = used_bounds(ws)
    for row_idx in range(header_row + 1, max_row + 1):
        task = text(ws.cell(row_idx, task_col).value)
        category = text(ws.cell(row_idx, category_col).value) if category_col else task
        basis = text(ws.cell(row_idx, basis_col).value) if basis_col else ""
        if not task or task in {"合計", "Total", "WBS由来合計"}:
            continue
        low = ws.cell(row_idx, low_col).value if low_col else None
        base = ws.cell(row_idx, base_col).value
        high = ws.cell(row_idx, high_col).value if high_col else None
        if not any(isinstance(value, (int, float)) for value in (low, base, high)):
            continue
        raw_tag = text(ws.cell(row_idx, tag_col).value)
        tag = normalize_ai_tag(raw_tag)
        expected_multiplier, rationale = ai_multiplier_for(tag)
        multiplier = numeric_cell_value(ws, row_idx, fixed_multiplier_col) if fixed_multiplier_col else None
        if multiplier is None:
            multiplier = expected_multiplier
        rows.append(
            {
                "category": category,
                "task": task,
                "basis": basis,
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


def contains_any(value: str, terms: tuple[str, ...]) -> bool:
    lower = value.lower()
    return any(term.lower() in lower for term in terms)


def extract_reuse_factor(value: str) -> str:
    for pattern in REUSE_FACTOR_PATTERNS:
        match = pattern.search(value)
        if match:
            return match.group(1).replace(" ", "")
    return ""


def is_repetition_signal(label: str, evidence: str, count: Any) -> bool:
    if not isinstance(count, (int, float)) or count <= 1:
        return False
    if contains_any(label, REPETITION_LABEL_EXCLUSIONS):
        return False
    haystack = f"{label} {evidence}"
    if contains_any(haystack, REPETITION_EXCLUSION_TERMS):
        return False
    return contains_any(haystack, REPETITION_TERMS)


def collect_reuse_context(wb: Any) -> dict[str, Any]:
    context: dict[str, Any] = {"signals": [], "assumptions": [], "factors": []}
    sizing_ws = sheet_by_label(wb, "規模根拠")
    if sizing_ws is not None:
        max_row, max_col = used_bounds(sizing_ws)
        for row in range(1, max_row + 1):
            label = text(sizing_ws.cell(row, 1).value)
            count = sizing_ws.cell(row, 2).value if max_col >= 2 else None
            evidence = text(sizing_ws.cell(row, 3).value) if max_col >= 3 else ""
            if is_repetition_signal(label, evidence, count):
                context["signals"].append(
                    {
                        "label": label,
                        "count": count,
                        "evidence": evidence,
                        "sheet": sizing_ws.title,
                    }
                )

    for ws in wb.worksheets:
        max_row, max_col = used_bounds(ws)
        for row in range(1, max_row + 1):
            for col in range(1, max_col + 1):
                value = text(ws.cell(row, col).value)
                if not value:
                    continue
                factor = extract_reuse_factor(value)
                if factor and factor not in context["factors"]:
                    context["factors"].append(factor)
                if contains_any(value, REUSE_ASSUMPTION_TERMS):
                    context["assumptions"].append(
                        {
                            "text": value,
                            "sheet": ws.title,
                            "cell": f"{get_column_letter(col)}{row}",
                        }
                    )
    return context


def count_basis_for_family(family: str, context: dict[str, Any]) -> tuple[Any, str]:
    family_lower = family.lower()
    groups: list[tuple[tuple[str, ...], tuple[str, ...]]] = [
        (("帳票", "pdf", "excel", "report", "output"), ("帳票", "出力", "pdf", "excel", "report", "output")),
        (("csv", "interface", "インターフェース"), ("csv", "変種")),
        (("workflow", "業務"), ("業務フロー",)),
        (("地区", "region"), ("地区",)),
    ]
    for family_terms, signal_terms in groups:
        if not contains_any(family_lower, family_terms):
            continue
        for signal in context["signals"]:
            label = text(signal.get("label"))
            evidence = text(signal.get("evidence"))
            if contains_any(f"{label} {evidence}", signal_terms):
                basis = f"{label}={signal.get('count')} ({evidence or signal.get('sheet')})"
                return signal.get("count"), basis
    return None, ""


def reuse_factor_for_family(family: str, count: Any, context: dict[str, Any]) -> str:
    factor = ", ".join(context["factors"])
    if factor:
        return factor
    if isinstance(count, (int, float)) and count > 1:
        return "未記載（反復検出）"
    if contains_any(family, ("reuse", "variant", "共通", "地区", "帳票", "csv")):
        return "未記載"
    return "1.00/未適用"


def extract_component_anchor_rows(ws: Any) -> list[dict[str, Any]]:
    max_row, max_col = used_bounds(ws)
    header_row = likely_table_header_row(ws)
    headers = header_map(ws, header_row, max_col)
    family_col = headers.get("Family") or headers.get("Component family") or headers.get("コンポーネント") or 1
    low_col = headers.get("Low") or headers.get("Family Low") or headers.get("楽観") or headers.get("低")
    base_col = headers.get("Base") or headers.get("Family Base") or headers.get("中心") or headers.get("普通")
    high_col = headers.get("High") or headers.get("Family High") or headers.get("悲観") or headers.get("高")
    if not (low_col and base_col and high_col):
        return []

    rows: list[dict[str, Any]] = []
    for row_idx in range(header_row + 1, max_row + 1):
        family = text(ws.cell(row_idx, family_col).value)
        if not family or family in {"合計", "Total"}:
            continue
        values = {
            "family": family,
            "low": numeric_cell_value(ws, row_idx, low_col),
            "base": numeric_cell_value(ws, row_idx, base_col),
            "high": numeric_cell_value(ws, row_idx, high_col),
            "source_row": row_idx,
        }
        if any(value is not None for value in (values["low"], values["base"], values["high"])):
            rows.append(values)
    return rows


def component_anchor_is_detailed(ws: Any) -> bool:
    max_row, max_col = used_bounds(ws)
    header_row = likely_table_header_row(ws)
    headers = {text(ws.cell(header_row, col).value).lower() for col in range(1, max_col + 1)}
    has_count = any(header in headers for header in {"件数", "count"})
    has_unit = any("unit" in header or "単価" in header for header in headers)
    has_framework = any("framework" in header or "共通" in header for header in headers)
    has_factor = any("variant" in header or "reuse" in header or "factor" in header or "係数" in header for header in headers)
    return has_count and has_unit and has_framework and has_factor


def enhance_component_anchor_sheet(ws: Any, context: dict[str, Any]) -> None:
    if component_anchor_is_detailed(ws):
        return
    rows = extract_component_anchor_rows(ws)
    if not rows:
        return

    clear_sheet(ws)
    ws.append(
        [
            "Component family",
            "件数",
            "件数根拠",
            "Framework Low",
            "Framework Base",
            "Framework High",
            "Unit Low",
            "Unit Base",
            "Unit High",
            "Variant/reuse factor",
            "Complexity factor",
            "Family Low",
            "Family Base",
            "Family High",
            "Anchor source",
            "Rationale",
        ]
    )
    for row in rows:
        count, basis = count_basis_for_family(row["family"], context)
        factor = reuse_factor_for_family(row["family"], count, context)
        rationale = (
            "元表はfamily合計のみ。framework/unit分解は生成時に未出力のため、"
            "family totalを保持して監査列を補完。"
        )
        ws.append(
            [
                row["family"],
                count,
                basis or "未抽出",
                None,
                None,
                None,
                None,
                None,
                None,
                factor,
                "未分解",
                row["low"],
                row["base"],
                row["high"],
                "既存05_単価アンカー",
                rationale,
            ]
        )

    total_row = ws.max_row + 1
    ws.append(
        [
            "合計",
            None,
            "",
            None,
            None,
            None,
            None,
            None,
            None,
            "",
            "",
            f"=SUM(L2:L{total_row - 1})",
            f"=SUM(M2:M{total_row - 1})",
            f"=SUM(N2:N{total_row - 1})",
            "",
            "family totalの再集計。分解情報があれば生成側で置き換える。",
        ]
    )


def wbs_base_for_terms(wb: Any, terms: tuple[str, ...]) -> float | None:
    ws = sheet_by_label(wb, "WBS")
    if ws is None:
        return None
    header_row, headers = find_header_row(ws, {"分類", "作業"})
    if header_row is None:
        header_row, headers = find_header_row(ws, {"Component", "Base"})
    if header_row is None:
        return None
    base_col = (
        headers.get("Most likely")
        or headers.get("Likely")
        or headers.get("Base")
        or headers.get("中心")
        or headers.get("最頻/普通")
    )
    if base_col is None:
        return None
    label_cols = [headers[name] for name in ("分類", "作業", "Component") if name in headers]
    evidence_cols = [headers[name] for name in ("根拠", "Basis") if name in headers]
    max_row, _ = used_bounds(ws)
    total = 0.0
    found = False
    for row in range(header_row + 1, max_row + 1):
        label = " ".join(text(ws.cell(row, col).value) for col in label_cols)
        evidence = " ".join(text(ws.cell(row, col).value) for col in evidence_cols)
        if not contains_any(f"{label} {evidence}", terms):
            continue
        base = numeric_cell_value(ws, row, base_col)
        if base is None:
            continue
        total += base
        found = True
    return total if found else None


def component_anchor_base_for_terms(wb: Any, terms: tuple[str, ...]) -> float | None:
    ws = sheet_by_label(wb, "単価アンカー")
    if ws is None:
        return None
    rows = extract_component_anchor_rows(ws)
    total = 0.0
    found = False
    for row in rows:
        if contains_any(text(row["family"]), terms) and row["base"] is not None:
            total += float(row["base"])
            found = True
    return total if found else None


def crosscheck_terms_for_signal(label: str, evidence: str) -> tuple[str, ...]:
    haystack = f"{label} {evidence}"
    if contains_any(haystack, ("帳票", "pdf", "excel", "出力", "report", "output")):
        return ("帳票", "pdf", "excel", "出力", "report", "output")
    if contains_any(haystack, ("csv", "変種")):
        return ("csv",)
    if contains_any(haystack, ("地区", "region")):
        return ("地区", "region")
    if contains_any(haystack, ("業務フロー", "workflow")):
        return ("業務", "workflow")
    return tuple(term for term in REPETITION_TERMS if term.lower() in haystack.lower()) or ("__no_repetition_match__",)


def parent_has_reuse_crosscheck(ws: Any) -> bool:
    max_row, max_col = used_bounds(ws)
    required = {"観点", "Bottom-up per-unit", "Anchor", "判断", "根拠"}
    for row in range(1, max_row + 1):
        headers = {text(ws.cell(row, col).value) for col in range(1, max_col + 1)}
        if required.issubset(headers):
            return True
    return False


def parent_has_method_dependence_audit(ws: Any) -> bool:
    max_row, max_col = used_bounds(ws)
    required_sets = [
        {"Cluster", "Methods", "Shared assumptions", "Independent anchors checked", "Parent treatment", "Reason"},
        {"クラスタ", "手法", "共有前提", "確認した独立アンカー", "親判断", "根拠"},
    ]
    for row in range(1, max_row + 1):
        headers = {text(ws.cell(row, col).value) for col in range(1, max_col + 1)}
        if any(required.issubset(headers) for required in required_sets):
            return True
    return False


def parent_total_method_count(ws: Any) -> int:
    max_row, max_col = used_bounds(ws)
    for row in range(1, max_row + 1):
        headers = header_map(ws, row, max_col)
        method_col = headers.get("手法") or headers.get("Method")
        if method_col is None:
            continue
        has_total_range = any(header in headers for header in ("Low", "Base", "High", "中心", "Center"))
        if not has_total_range:
            continue
        count = 0
        for check_row in range(row + 1, max_row + 1):
            method = text(ws.cell(check_row, method_col).value)
            if not method:
                break
            if method.lower() in {"source", "論点"}:
                break
            count += 1
        return count
    return 0


def check_method_dependence_audit(wb: Any) -> list[str]:
    warnings: list[str] = []
    parent_ws = sheet_by_label(wb, "親統合")
    if parent_ws is None:
        return warnings
    method_count = parent_total_method_count(parent_ws)
    if method_count >= 3 and not parent_has_method_dependence_audit(parent_ws):
        warnings.append(
            "18_親統合 compares three or more total-estimate methods but lacks a method-dependence cluster table"
        )
    return warnings


def ensure_parent_reuse_crosscheck(wb: Any, context: dict[str, Any]) -> None:
    signals = context["signals"]
    if not signals:
        return
    ws = sheet_by_label(wb, "親統合")
    if ws is None or parent_has_reuse_crosscheck(ws):
        return

    if ws.max_row and any(ws.cell(ws.max_row, col).value is not None for col in range(1, ws.max_column + 1)):
        ws.append([])
    ws.append(["規模経済トップダウン単価逆算", "", "", "", "", "", "", ""])
    ws.append(["観点", "件数", "Bottom-up per-unit", "Anchor", "差", "Variant/reuse factor", "判断", "根拠"])

    for signal in signals[:6]:
        label = text(signal.get("label"))
        count = signal.get("count")
        evidence = text(signal.get("evidence"))
        terms = crosscheck_terms_for_signal(label, evidence)
        wbs_base = wbs_base_for_terms(wb, terms)
        anchor_base = component_anchor_base_for_terms(wb, terms)
        bottom_up_per_unit = wbs_base / count if isinstance(count, (int, float)) and count and wbs_base is not None else None
        anchor_per_unit = anchor_base / count if isinstance(count, (int, float)) and count and anchor_base is not None else None
        diff = (
            bottom_up_per_unit - anchor_per_unit
            if bottom_up_per_unit is not None and anchor_per_unit is not None
            else None
        )
        factor = reuse_factor_for_family(label, count, context)
        if factor.startswith("未記載"):
            judgement = "根拠付きで高位維持"
            rationale = "反復シグナルはあるがvariant/reuse factorが未記載。下方調整せず、生成側でfactor明示が必要。"
        elif diff is not None and diff > 0:
            judgement = "繰り返し/再利用で下方調整"
            rationale = "Bottom-up per-unitが単価アンカーを上回るため、framework+variant適用を確認。"
        else:
            judgement = "整合"
            rationale = "Bottom-up per-unitとアンカーに大きな乖離なし。"
        ws.append([label, count, bottom_up_per_unit, anchor_per_unit, diff, factor, judgement, f"{evidence} / {rationale}"])


def phase_rows_from_ai_rows(ai_rows: list[dict[str, Any]]) -> list[list[Any]]:
    rows: list[list[Any]] = []
    for row in ai_rows:
        raw = row["base"] if isinstance(row["base"], (int, float)) else None
        adjusted = row["adjusted_base"] if isinstance(row["adjusted_base"], (int, float)) else None
        diff = adjusted - raw if raw is not None and adjusted is not None else None
        rate = diff / raw if raw else None
        multiplier = row["multiplier"]
        note_parts = [
            f"実AI削減区分={row['tag']}",
            f"固定倍率={multiplier:.2f}",
        ]
        if row.get("basis"):
            note_parts.append(f"根拠={row['basis']}")
        note_parts.append(row["rationale"])
        rows.append(
            [
                row["task"],
                adjusted,
                raw,
                diff,
                rate,
                row["tag"],
                " / ".join(note_parts),
                "03_WBS/10_AI補正",
            ]
        )
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


def rebuild_conclusion_sheet(ws: Any, summary: dict[str, tuple[Any, ...]], methods: list[list[Any]], title: str) -> None:
    st = base_styles()
    clear_sheet(ws)
    ws.sheet_view.showGridLines = False
    ws.freeze_panes = "A5"
    ws.merge_cells("A1:F1")
    ws["A1"] = title
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

    ai_range, ai_center = summary_range(summary, "推奨レンジ（AI補助あり）")
    if ai_range == "-":
        ai_range, ai_center = summary_range(summary, "結論")
    pre_ai_range, _ = summary_range(summary, "推奨レンジ（AI補助前）")
    high_risk_range, _ = summary_range(summary, "高リスクシナリオ")
    implementation_range, implementation_center = summary_range(summary, "実装のみ参考")
    rows = [
        ["推奨レンジ（AI補助あり）", ai_range, "元シートの結論レンジを整形表示。", "主表示", "中心値は同じ元行から取得", "00_結論（元データ）"],
        ["計画中心（AI補助あり）", ai_center, "元シートの中心値を整形表示。", "主表示", "単独数字で出す場合の代表値", "00_結論（元データ）"],
        ["推奨レンジ（AI補助前）", pre_ai_range, "元シートに値がある場合のみ表示。", "参考表示", "-", "00_結論（元データ）"],
        ["高リスクシナリオ", high_risk_range, "元シートに値がある場合のみ表示。", "参考表示", "-", "00_結論（元データ）"],
        ["実装のみ参考", implementation_range if implementation_range != "-" else implementation_center, "元シートに値がある場合のみ表示。", "参考表示", "-", "00_結論（元データ）"],
        ["見積階層", first_value(summary.get("見積階層", ("-",))), "元シートの階層表示。", "補足", first_value(summary.get("階層理由", ("-",))), "00_結論（元データ）"],
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
        row[1].alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    evidence_rows = []
    for label in ("主ドライバー", "注意"):
        if label in summary:
            evidence_rows.append([label, first_value(summary[label], "-"), "元シート由来", "", "00_結論（元データ）", ""])
    if evidence_rows:
        ws.append([])
        evidence_header = ws.max_row + 1
        ws.append(["元シート記載", "内容", "扱い", "", "参照シート", ""])
        for cell in ws[evidence_header]:
            cell.fill = fill(COLORS["header"])
            cell.font = st["section_font"]
            cell.alignment = st["center"]
            cell.border = st["header_border"]
        for row in evidence_rows:
            ws.append(row)
        for row in ws.iter_rows(min_row=evidence_header + 1, max_row=ws.max_row, min_col=1, max_col=5):
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
    ws.append(["工程/WBS作業", "AI補助後目安", "AI補助前WBS", "差分", "削減率", "AI削減区分", "主な内容/注意", "参照"])
    for cell in ws[3]:
        cell.fill = fill(COLORS["header"])
        cell.font = Font(name="Yu Gothic", size=10, bold=True, color=COLORS["header_text"])
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
        tag = normalize_ai_tag(row[5].value)
        if tag in {"削減不可", "対象外", "検証重"}:
            row[5].fill = fill(COLORS["assumption"])
        elif tag == "定型実装":
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
    ws["A2"] = "AI削減区分はWBS作成者が行ごとに判断し、倍率は参照定数を固定適用する。raw baselineは変更しない。"
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
    header_row, headers = find_header_row(ws, {"AI補助後目安", "AI補助前WBS", "差分", "削減率"})
    if header_row is None:
        return errors
    label_col = headers.get("工程/WBS作業") or headers.get("工程")
    for row in range(header_row + 1, max_row + 1):
        if label_col and text(ws.cell(row, label_col).value) in {"", "合計"}:
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


def check_breakdown_ai_tags(wb: Any) -> list[str]:
    warnings: list[str] = []
    breakdown_ws = sheet_by_label(wb, "内訳")
    ai_ws = sheet_by_label(wb, "AI補正")
    if breakdown_ws is None or ai_ws is None:
        return warnings

    breakdown_header, breakdown_headers = find_header_row(
        breakdown_ws,
        {"AI補助後目安", "AI補助前WBS", "AI削減区分"},
    )
    ai_header, ai_headers = find_header_row(ai_ws, {"WBS作業", "AI削減区分"})
    if breakdown_header is None or ai_header is None:
        return warnings
    breakdown_label_col = breakdown_headers.get("工程/WBS作業") or breakdown_headers.get("工程")
    if breakdown_label_col is None:
        return warnings

    ai_tags: dict[str, str] = {}
    max_ai_row, _ = used_bounds(ai_ws)
    for row in range(ai_header + 1, max_ai_row + 1):
        task = text(ai_ws.cell(row, ai_headers["WBS作業"]).value)
        if not task or task == "合計":
            continue
        ai_tags[task] = normalize_ai_tag(ai_ws.cell(row, ai_headers["AI削減区分"]).value)

    max_breakdown_row, _ = used_bounds(breakdown_ws)
    for row in range(breakdown_header + 1, max_breakdown_row + 1):
        task = text(breakdown_ws.cell(row, breakdown_label_col).value)
        if not task or task == "合計" or task not in ai_tags:
            continue
        breakdown_tag = normalize_ai_tag(breakdown_ws.cell(row, breakdown_headers["AI削減区分"]).value)
        if breakdown_tag != ai_tags[task]:
            warnings.append(
                f"{breakdown_ws.title}!{get_column_letter(breakdown_headers['AI削減区分'])}{row}: "
                f"AI tag `{breakdown_tag}` does not match 10_AI補正 `{ai_tags[task]}` for `{task}`"
            )
    return warnings


def check_ai_reducibility_bias(wb: Any) -> list[str]:
    warnings: list[str] = []
    ws = sheet_by_label(wb, "AI補正")
    if ws is None:
        return warnings
    header_row, headers = find_header_row(
        ws,
        {"WBS作業", "AI削減区分", "Raw Base", "Adjusted Base"},
    )
    if header_row is None:
        return warnings

    total_raw = 0.0
    total_adjusted = 0.0
    implementation_raw = 0.0
    review_heavy_raw = 0.0
    review_heavy_examples: list[str] = []
    max_row, _ = used_bounds(ws)
    for row in range(header_row + 1, max_row + 1):
        task = text(ws.cell(row, headers["WBS作業"]).value)
        if not task or task == "合計":
            continue
        raw = numeric_cell_value(ws, row, headers["Raw Base"])
        adjusted = numeric_cell_value(ws, row, headers["Adjusted Base"])
        if raw is None or raw <= 0:
            continue
        if adjusted is not None:
            total_raw += raw
            total_adjusted += adjusted
        haystack = " ".join(
            [
                task,
                text(ws.cell(row, headers.get("WBS分類", 0)).value) if "WBS分類" in headers else "",
                text(ws.cell(row, headers.get("根拠", 0)).value) if "根拠" in headers else "",
            ]
        )
        if not contains_any(haystack, AI_IMPLEMENTATION_TERMS):
            continue
        implementation_raw += raw
        tag = normalize_ai_tag(ws.cell(row, headers["AI削減区分"]).value)
        if tag in AI_REVIEW_HEAVY_TAGS:
            review_heavy_raw += raw
            if len(review_heavy_examples) < 4:
                review_heavy_examples.append(f"{task}={tag}")

    if not total_raw or not implementation_raw:
        return warnings
    reduction_rate = (total_raw - total_adjusted) / total_raw if total_raw else 0.0
    review_heavy_share = review_heavy_raw / implementation_raw
    if review_heavy_share >= 0.70 and reduction_rate < 0.15:
        examples = ", ".join(review_heavy_examples)
        warnings.append(
            "AI reducibility sanity check: implementation-like work is mostly tagged "
            f"`複雑実装/検証重` ({review_heavy_share:.0%} of implementation raw base) while "
            f"overall AI reduction is only {reduction_rate:.0%}. Re-evaluate AI削減区分 against "
            f"the current scope and implementation approach. Examples: {examples}"
        )
    return warnings


def check_reuse_audit(wb: Any) -> list[str]:
    warnings: list[str] = []
    context = collect_reuse_context(wb)
    if not context["signals"]:
        return warnings

    component_ws = sheet_by_label(wb, "単価アンカー")
    if component_ws is None:
        warnings.append("repetition/reuse signals detected but 05_単価アンカー is missing")
    elif not component_anchor_is_detailed(component_ws):
        warnings.append(
            "repetition/reuse signals detected but 05_単価アンカー lacks count/framework/unit/variant-factor audit columns"
        )
    else:
        max_row, max_col = used_bounds(component_ws)
        header_row = likely_table_header_row(component_ws)
        headers = header_map(component_ws, header_row, max_col)
        factor_col = next(
            (
                col
                for header, col in headers.items()
                if "variant" in header.lower() or "reuse" in header.lower() or "factor" in header.lower() or "係数" in header
            ),
            None,
        )
        if factor_col:
            for row in range(header_row + 1, max_row + 1):
                family = text(component_ws.cell(row, 1).value)
                if not family or family in {"合計", "Total"}:
                    continue
                factor = text(component_ws.cell(row, factor_col).value)
                if factor.startswith("未記載"):
                    warnings.append(
                        f"{component_ws.title}!{get_column_letter(factor_col)}{row}: variant/reuse factor is missing for `{family}`"
                    )

    parent_ws = sheet_by_label(wb, "親統合")
    if parent_ws is None:
        warnings.append("repetition/reuse signals detected but 18_親統合 is missing")
    elif not parent_has_reuse_crosscheck(parent_ws):
        warnings.append(
            "repetition/reuse signals detected but 18_親統合 lacks the top-down per-unit reuse cross-check table"
        )
    else:
        max_row, max_col = used_bounds(parent_ws)
        for row in range(1, max_row + 1):
            headers = header_map(parent_ws, row, max_col)
            if "Variant/reuse factor" not in headers:
                continue
            factor_col = headers["Variant/reuse factor"]
            for check_row in range(row + 1, max_row + 1):
                if not text(parent_ws.cell(check_row, 1).value):
                    break
                factor = text(parent_ws.cell(check_row, factor_col).value)
                if factor.startswith("未記載"):
                    warnings.append(
                        f"{parent_ws.title}!{get_column_letter(factor_col)}{check_row}: variant/reuse factor is missing"
                    )
            break
    return warnings


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
            if ws.title == "00_結論":
                ws.row_dimensions[row_idx].height = 46 if 3 <= row_idx <= 8 else 30
            else:
                ws.row_dimensions[row_idx].height = 32
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
                cell.fill = fill(COLORS["header"])
                cell.font = Font(name="Yu Gothic", size=10, bold=True, color=COLORS["header_text"])
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
    reuse_context = collect_reuse_context(wb)
    source_summary = sheet_by_label(wb, "結論", "サマリー")
    source_breakdown = sheet_by_label(wb, "内訳", "工程別")
    source_wbs = sheet_by_label(wb, "WBS")
    source_ai = sheet_by_label(wb, "AI補正")
    source_component = sheet_by_label(wb, "単価アンカー")
    summary = extract_summary_values(source_summary)
    title = extract_summary_title(source_summary)
    methods = extract_method_rows(source_summary)
    ai_rows = extract_wbs_ai_rows(source_wbs)
    phases = phase_rows_from_ai_rows(ai_rows) if ai_rows else extract_phase_rows(source_breakdown)

    conclusion_ws = source_summary or wb.create_sheet("00_結論", 0)
    breakdown_ws = source_breakdown or wb.create_sheet("01_内訳", 1)
    ai_ws = source_ai or wb.create_sheet("10_AI補正")
    rebuild_conclusion_sheet(conclusion_ws, summary, methods, title)
    rebuild_breakdown_sheet(breakdown_ws, phases)
    if ai_rows:
        rebuild_ai_adjustment_sheet(ai_ws, ai_rows)
    if source_component is not None:
        enhance_component_anchor_sheet(source_component, reuse_context)
    renumber_and_order_sheets(wb)
    ensure_parent_reuse_crosscheck(wb, reuse_context)
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
    warnings.extend(check_reuse_audit(wb))
    warnings.extend(check_method_dependence_audit(wb))
    warnings.extend(check_breakdown_ai_tags(wb))
    warnings.extend(check_ai_reducibility_bias(wb))
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
