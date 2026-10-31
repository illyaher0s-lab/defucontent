#!/usr/bin/env python3
"""
Gate 0 多维表格事件处理器 - 本地测试

测试事件解析和过滤逻辑，无需连接真实飞书服务。
"""
import logging
from typing import Any

# 模拟 logger
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def _on_bitable_record_changed(data: Any) -> Any:
    """Gate 0 多维表格记录变更事件处理器"""
    try:
        event = data.get("event", {})
        file_token = event.get("file_token")
        table_id = event.get("table_id")
        action = event.get("action")
        record_id = event.get("record_id")
        event_id = data.get("uuid") or data.get("event_id")
        
        # Gate 0 测试表过滤（替换为实际的 file_token 和 table_id）
        GATE0_FILE_TOKEN = "YOUR_FILE_TOKEN_HERE"
        GATE0_TABLE_ID = "YOUR_TABLE_ID_HERE"
        
        if file_token != GATE0_FILE_TOKEN or table_id != GATE0_TABLE_ID:
            logger.debug(f"[Feishu] Ignoring bitable event from non-Gate0 table: {file_token}/{table_id}")
            return
        
        # 只记录 record_edited
        if action != "record_edited":
            logger.debug(f"[Feishu] Ignoring bitable action: {action}")
            return
        
        # 记录事件（不包含敏感字段值）
        logger.info(
            f"[Feishu] Gate 0 bitable event: "
            f"event_id={event_id}, "
            f"file_token={file_token}, "
            f"table_id={table_id}, "
            f"action={action}, "
            f"record_id={record_id}"
        )
        
        return None
        
    except Exception as e:
        logger.warning(f"[Feishu] Failed to process bitable event: {e}", exc_info=True)
        return None


# ============================================
# 测试用例
# ============================================

def test_gate0_event():
    """测试 Gate 0 表的 record_edited 事件"""
    print("\n=== Test 1: Gate 0 表 record_edited 事件 ===")
    event = {
        "uuid": "test-event-001",
        "event": {
            "file_token": "YOUR_FILE_TOKEN_HERE",
            "table_id": "YOUR_TABLE_ID_HERE",
            "action": "record_edited",
            "record_id": "test_record_id"
        }
    }
    _on_bitable_record_changed(event)


def test_wrong_table():
    """测试非 Gate 0 表事件（应被忽略）"""
    print("\n=== Test 2: 非 Gate 0 表事件（应忽略）===")
    event = {
        "uuid": "test-event-002",
        "event": {
            "file_token": "OTHER_FILE_TOKEN",
            "table_id": "OTHER_TABLE_ID",
            "action": "record_edited",
            "record_id": "rec123"
        }
    }
    _on_bitable_record_changed(event)


def test_wrong_action():
    """测试 Gate 0 表但非 record_edited 事件（应被忽略）"""
    print("\n=== Test 3: Gate 0 表但非 record_edited 事件（应忽略）===")
    event = {
        "uuid": "test-event-003",
        "event": {
            "file_token": "YOUR_FILE_TOKEN_HERE",
            "table_id": "YOUR_TABLE_ID_HERE",
            "action": "record_created",
            "record_id": "rec456"
        }
    }
    _on_bitable_record_changed(event)


def test_malformed_event():
    """测试格式错误的事件（应优雅处理）"""
    print("\n=== Test 4: 格式错误的事件（应优雅处理）===")
    event = {
        "uuid": "test-event-004",
        "event": {}  # 缺少必要字段
    }
    _on_bitable_record_changed(event)


if __name__ == "__main__":
    print("开始测试 Gate 0 多维表格事件处理器...\n")
    print("=" * 60)
    print("\n注意: 使用前请替换 YOUR_FILE_TOKEN_HERE 和 YOUR_TABLE_ID_HERE")
    print("      为实际的飞书多维表格 file_token 和 table_id\n")
    print("=" * 60)
    
    test_gate0_event()
    test_wrong_table()
    test_wrong_action()
    test_malformed_event()
    
    print("\n" + "=" * 60)
    print("\n✓ 所有测试完成")
    print("\n预期结果:")
    print("  - Test 1: 应记录事件（INFO 级别）")
    print("  - Test 2-4: 应忽略或优雅处理（DEBUG/WARNING 级别）")
