# Gate 0 dependencies and evidence

Hermes upstream reference commit: 71d34bad1045610252eda02ee79549436896e784
Reference path: plugins/platforms/feishu/adapter.py
Actual live server checkout hash and adapter file hash: NOT independently verified.
Do not assume a local version label proves the running file matches.

Feishu event: drive.file.bitable_record_changed_v1
File-level subscription: user reports HTTP 200 and API code 0 on the isolated test base.
Application-level subscription publication: NOT yet verified by real delivery.
Event shape: header.event_id, event.action_list[].action/record_id,
event.file_token, event.table_id.
Reference: https://open.feishu.cn/document/server-docs/docs/drive-v1/event/list/bitable-record-changed

Python: stdlib-only feishu_bitable_gate0.py; no new dependencies.
Hermes existing adapter: Python Any, os, logger and lark_oapi EventDispatcherHandler.
Installed SDK version: NOT verified; inspect python -m pip show lark-oapi on the server before deployment.

Run isolated tests:
    python3 -m unittest -v test_bitable_handler.py

Patch test in the real adapter directory, but only after confirming the exact file:
    patch --dry-run --fuzz=0 -p1 < /path/to/adapter.patch

Safety: Keep secrets, application IDs, base/table IDs, raw event payloads and customer data out of this public repository.
Use service environment FEISHU_GATE0_FILE_TOKEN and FEISHU_GATE0_TABLE_ID. Unset values disable logging.
Do NOT print raw events. Do NOT use patch --fuzz=3 to force a patch.
Do NOT upgrade SDK or restart services as part of the offline tests.

Current verification scope: parser-only unit tests and upstream source review.
Pending: application event version activation, real WebSocket event delivery, controlled deploy and rollback, no-chat automatic Agent execution.
