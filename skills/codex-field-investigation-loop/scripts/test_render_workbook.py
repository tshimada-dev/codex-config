import json
import tempfile
import unittest
from pathlib import Path

import render_workbook


class RenderWorkbookTest(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
