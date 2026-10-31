#!/usr/bin/env python3
"""Regression tests for the actual Gate 0 parser module (no duplicate mock handler)."""
import logging
import unittest
from types import SimpleNamespace

from feishu_bitable_gate0 import parse_gate0_record_edits, log_gate0_record_edits

FILE, TABLE = "test-base", "test-table"


def sample(actions=None, *, file_token=FILE, table_id=TABLE, event_id="evt_1"):
    if actions is None:
        actions = [{"action": "record_edited", "record_id": "rec_1"}]
    return {
        "schema": "2.0",
        "header": {"event_id": event_id, "event_type": "drive.file.bitable_record_changed_v1"},
        "event": {
            "file_token": file_token,
            "table_id": table_id,
            "action_list": actions,
        },
    }


class TestGate0Parser(unittest.TestCase):
    def parse(self, payload, **overrides):
        return parse_gate0_record_edits(
            payload, file_token=overrides.get("file_token", FILE),
            table_id=overrides.get("table_id", TABLE),
        )

    def test_official_event_shape(self):
        self.assertEqual(self.parse(sample()), [("evt_1", "rec_1")])

    def test_sdk_object_and_object_header(self):
        event = sample()
        sdk_event = SimpleNamespace(
            header=SimpleNamespace(event_id="evt_sdk"),
            event=event["event"],
        )
        self.assertEqual(self.parse(sdk_event), [("evt_sdk", "rec_1")])

    def test_json_string_event(self):
        import json
        payload = sample()
        payload["event"] = json.dumps(payload["event"])
        self.assertEqual(self.parse(payload), [("evt_1", "rec_1")])

    def test_multiple_actions_ignores_added_deleted(self):
        actions = [
            {"action": "record_added", "record_id": "rec_added"},
            {"action": "record_edited", "record_id": "rec_a"},
            {"action": "record_deleted", "record_id": "rec_deleted"},
            {"action": "record_edited", "record_id": "rec_b"},
        ]
        self.assertEqual(
            self.parse(sample(actions)), [("evt_1", "rec_a"), ("evt_1", "rec_b")]
        )

    def test_other_table_is_ignored(self):
        self.assertEqual(self.parse(sample(table_id="not-gate0")), [])
        self.assertEqual(self.parse(sample(file_token="not-gate0")), [])

    def test_missing_configuration_disables_handler(self):
        self.assertEqual(self.parse(sample(), file_token=""), [])
        self.assertEqual(self.parse(sample(), table_id=""), [])

    def test_malformed_and_legacy_payloads_are_ignored(self):
        self.assertEqual(self.parse({}), [])
        self.assertEqual(self.parse(None), [])
        self.assertEqual(self.parse({"event": {"action": "record_edited"}}), [])
        self.assertEqual(self.parse(sample(actions="not-an-array")), [])
        self.assertEqual(self.parse(sample(actions=[None, 1, {}])), [])

    def test_invalid_identifiers_are_not_logged(self):
        self.assertEqual(
            self.parse(sample(actions=[{"action": "record_edited", "record_id": "rec\ninjected"}])),
            [],
        )
        self.assertEqual(
            self.parse(sample(event_id="id\ninjected")), [("unknown", "rec_1")]
        )

    def test_log_reports_only_safe_metadata(self):
        logger = logging.getLogger("gate0-test")
        payload = sample()
        payload["event"]["action_list"][0]["after_value"] = [
            {"field_id": "secret_field", "field_value": "DO_NOT_LOG"}
        ]
        with self.assertLogs(logger, level="INFO") as logs:
            count = log_gate0_record_edits(
                payload, logger, file_token=FILE, table_id=TABLE
            )
        self.assertEqual(count, 1)
        joined = "\n".join(logs.output)
        self.assertIn("record_id=rec_1", joined)
        self.assertIn("event_id=evt_1", joined)
        self.assertNotIn("DO_NOT_LOG", joined)
        self.assertNotIn(FILE, joined)

    def test_no_log_on_unmatched_event(self):
        logger = logging.getLogger("gate0-test")
        with self.assertNoLogs(logger, level="INFO"):
            count = log_gate0_record_edits(
                sample(table_id="other"), logger, file_token=FILE, table_id=TABLE
            )
        self.assertEqual(count, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
