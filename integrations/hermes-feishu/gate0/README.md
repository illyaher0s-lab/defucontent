# Gate 0 | Feishu record-change listener

Status: isolated code only, NOT deployed or verified with a real WebSocket event.

Goal: log record_edited notifications for one test base/table. Do not run an AI Agent, query business records, or write back to Feishu.

## Files

- adapter.patch: one SDK custom event registration and a tiny adapter callback
- feishu_bitable_gate0.py: stdlib-only parser and safe metadata logger
- test_bitable_handler.py: unittest assertions using the real parser module
- DEPENDENCIES.md: pinned upstream baseline and remaining checks

Feishu official schema 2.0 (drive.file.bitable_record_changed_v1): header.event_id, event.file_token, event.table_id, event.action_list[].action and record_id. action is record_added, record_edited or record_deleted. Only edited actions are logged. The field_value payload is never read or logged.

Official event reference:
https://open.feishu.cn/document/server-docs/docs/drive-v1/event/list/bitable-record-changed

## Offline tests

From the gate0 directory:

    python3 -m unittest -v test_bitable_handler.py

No Feishu credentials, SDK or network are needed for parser tests. A passing local test does NOT prove the real event has been delivered to Hermes.

## Controlled deployment prerequisites (do NOT execute until reviewed)

1. Confirm the actual running Hermes adapter matches the pinned upstream commit shown in DEPENDENCIES.md and the Feishu application event configuration is published.
2. Save a persistent, protected backup of the original adapter.py (not just /tmp).
3. Copy feishu_bitable_gate0.py beside the running adapter.py in plugins/platforms/feishu/.
4. In the real Hermes service environment configure FEISHU_GATE0_FILE_TOKEN and FEISHU_GATE0_TABLE_ID to the isolated test base/table identifiers. Do not check actual IDs into GitHub. Empty values disable event logging.
5. Validate the patch in its target directory with patch --dry-run --fuzz=0 -p1 < adapter.patch and confirm only adapter.py is affected. Do not apply if context differs.
6. Confirm the ACTUAL service manager / restart command and rollback procedure; do not assume hermes restart is valid.
7. Apply the patch only after backup and deploy the module; verify syntax and module import, then perform a controlled service restart.
8. Confirm existing bot chat still works and the WebSocket connects; edit one isolated row and correlate logs to its record_id.
9. Save timestamps and logs as verification evidence, without raw event payload or any tokens.

Rollback: restore original adapter.py from the persistent backup, remove deployed feishu_bitable_gate0.py if introduced by this deployment, restore service settings, and restart with the previously verified service command. Do not change the main branch or production data.

## Important limitations

- Logs only: does NOT yet invoke Hermes Agent or perform the final Gate 0 automatic writeback.
- No event_id deduplication is needed for this log-only probe. Add durable idempotency and current-request checks BEFORE enabling real task execution.
- The SDK callback is expected to pass a CustomizedEvent-like object with event and header; this is tested with SimpleNamespace but has not been verified against an actual delivered event.
- Real event delivery and application-version activation remain to be tested.
- Never print the raw event: it can contain customer field_value data.
