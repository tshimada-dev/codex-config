import json
import re
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import render_workbook


class RenderWorkbookTest(unittest.TestCase):
    @staticmethod
    def make_bundle(root: Path, state_text: str = "# Current state\nReady\n") -> None:
        (root / "STATE.md").write_text(state_text, encoding="utf-8")
        (root / "checks.csv").write_text("ID,Status\nC1,done\n", encoding="utf-8")
        (root / "command-log.jsonl").write_text(
            json.dumps({"occurred_at": "2026-07-19T00:00:00+00:00", "Result": "ok"})
            + "\n",
            encoding="utf-8",
        )
        (root / "hypotheses.csv").write_text("ID,Status\nH1,supported\n", encoding="utf-8")
        (root / "timeline.csv").write_text("Timestamp,Event\nnow,started\n", encoding="utf-8")
        (root / "connections.csv").write_text("Item,Value\nhost,example\n", encoding="utf-8")

    @staticmethod
    def read_inline_strings(xml_bytes: bytes) -> list[str]:
        namespace = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        root = ET.fromstring(xml_bytes)
        return [node.text or "" for node in root.findall(".//main:t", namespace)]

    def test_command_log_places_event_and_record_times_first(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            command_log = Path(temp_dir) / "command-log.jsonl"
            command_log.write_text(
                json.dumps(
                    {
                        "recorded_at": "2026-07-17T10:01:00+09:00",
                        "Result": "reachable",
                        "occurred_at": "2026-07-17T09:59:00+09:00",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            rows = render_workbook.read_jsonl(command_log)

        self.assertEqual(["occurred_at", "recorded_at"], rows[0][:2])
        self.assertEqual(
            ["2026-07-17T09:59:00+09:00", "2026-07-17T10:01:00+09:00"],
            rows[1][:2],
        )

    def test_legacy_command_log_keeps_timestamp_after_empty_new_time_columns(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            command_log = Path(temp_dir) / "command-log.jsonl"
            command_log.write_text(
                json.dumps(
                    {
                        "Timestamp": "2026-07-17 09:59 JST",
                        "Result": "legacy row",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            rows = render_workbook.read_jsonl(command_log)

        self.assertEqual(
            ["occurred_at", "recorded_at", "Timestamp"], rows[0][:3]
        )
        self.assertEqual(["", "", "2026-07-17 09:59 JST"], rows[1][:3])

    def test_summary_starts_with_snapshot_time_and_source_line_counts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            bundle = Path(temp_dir)
            self.make_bundle(bundle)
            output = bundle / "workbook.xlsx"

            render_workbook.render(bundle, output)

            with zipfile.ZipFile(output) as workbook:
                strings = self.read_inline_strings(workbook.read("xl/worksheets/sheet1.xml"))

        self.assertEqual("Snapshot timestamp (UTC)", strings[0])
        self.assertRegex(strings[1], re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?\+00:00$"))
        self.assertEqual(["Source file", "Line count", "STATE.md", "2"], strings[2:6])

    def test_control_characters_are_sanitized_to_valid_xml(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            bundle = Path(temp_dir)
            self.make_bundle(bundle)
            (bundle / "checks.csv").write_text(
                'ID,Status\nC1,"value\x0bwith-control"\n', encoding="utf-8"
            )
            output = bundle / "workbook.xlsx"

            render_workbook.render(bundle, output)

            with zipfile.ZipFile(output) as workbook:
                self.assertIsNone(workbook.testzip())
                for name in workbook.namelist():
                    if name.endswith(".xml") or name.endswith(".rels"):
                        xml_bytes = workbook.read(name)
                        self.assertNotIn(b"\x0b", xml_bytes, name)
                        ET.fromstring(xml_bytes)

    def test_workbook_includes_header_styles_and_column_widths(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            bundle = Path(temp_dir)
            self.make_bundle(bundle)
            output = bundle / "workbook.xlsx"

            render_workbook.render(bundle, output)

            with zipfile.ZipFile(output) as workbook:
                self.assertIn("xl/styles.xml", workbook.namelist())
                styles = ET.fromstring(workbook.read("xl/styles.xml"))
                sheet = ET.fromstring(workbook.read("xl/worksheets/sheet2.xml"))

        namespace = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        self.assertIsNotNone(styles.find("main:cellXfs", namespace))
        self.assertIsNotNone(sheet.find("main:cols", namespace))
        first_row = sheet.find("main:sheetData/main:row", namespace)
        self.assertIsNotNone(first_row)
        self.assertTrue(all(cell.get("s") == "1" for cell in first_row))


if __name__ == "__main__":
    unittest.main()
