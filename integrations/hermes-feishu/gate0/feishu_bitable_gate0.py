"""Gate 0: parse Feishu bitable record changes without launching an Agent.

This module uses only the Python standard library. It never reads field values
and does not perform API calls. The adapter calls it from its existing handler.
"""
from __future__ import annotations

import json
import re
from typing import Any


_SAFE_ID = re.compile(r"[A-Za-z0-9_-]{1,128}\Z")


def _as_dict(value: Any) -> dict:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            decoded = json.loads(value)
        except (TypeError, ValueError):
            return {}
        return decoded if isinstance(decoded, dict) else {}
    if value is not None and hasattr(value, "__dict__"):
        return vars(value)
    return {}


def parse_gate0_record_edits(
    data: Any, *, file_token: str, table_id: str,
) -> list[tuple[str, str]]:
    """Return safe (event_id, record_id) pairs for edited Gate 0 rows.

    Accepts a dict or an SDK CustomizedEvent-like object, including a header
    object and an event object/dict. Invalid or unmatched payloads are ignored.
    """
    if not file_token or not table_id:
        return []

    root = _as_dict(data)
    event = _as_dict(root.get("event", getattr(data, "event", None)))
    header = _as_dict(root.get("header", getattr(data, "header", None)))
    if event.get("file_token") != file_token or event.get("table_id") != table_id:
        return []

    raw_id = header.get("event_id")
    event_id = raw_id if isinstance(raw_id, str) and _SAFE_ID.fullmatch(raw_id) else "unknown"
    actions = event.get("action_list")
    if not isinstance(actions, list):
        return []

    edits: list[tuple[str, str]] = []
    for raw_action in actions:
        action = _as_dict(raw_action)
        record_id = action.get("record_id")
        if (
            action.get("action") == "record_edited"
            and isinstance(record_id, str)
            and _SAFE_ID.fullmatch(record_id)
        ):
            edits.append((event_id, record_id))
    return edits


def log_gate0_record_edits(
    data: Any, logger: Any, *, file_token: str, table_id: str,
) -> int:
    """Log safe identifiers only; return the number of matching edits."""
    try:
        edits = parse_gate0_record_edits(
            data, file_token=file_token, table_id=table_id
        )
        for event_id, record_id in edits:
            logger.info(
                "[Feishu] Gate 0 bitable event: event_id=%s "
                "table=gate0 action=record_edited record_id=%s",
                event_id, record_id,
            )
        return len(edits)
    except Exception:
        # Do not leak raw event bodies or exceptions that may include values.
        logger.warning("[Feishu] Gate 0 event parser failed")
        return 0
