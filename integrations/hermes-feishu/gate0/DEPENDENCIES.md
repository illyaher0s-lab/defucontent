# 依赖信息

## Hermes Agent 版本

**来源**: Nous Research / Hermes Agent  
**Commit**: `71d34bad1045610252eda02ee79549436896e784`  
**日期**: 2026-10-11 20:08:03 -0700  
**最后修改**: fix(release): the builds-table render gets its R2 credentials and cannot block the release

**适配器文件路径**:
```
~/.hermes/hermes-agent/plugins/platforms/feishu/adapter.py
```

**适配器版本**: 基于上述 commit 的飞书平台适配器

---

## Python SDK

### lark_oapi (飞书开放平台 SDK)

**安装命令**:
```bash
pip install lark-oapi
```

**验证方法**:
```python
from lark_oapi.event.dispatcher_handler import EventDispatcherHandler
print("✓ SDK 已安装")
```

**必需模块**:
- `lark_oapi.event.dispatcher_handler.EventDispatcherHandler`
- `register_p2_customized_event` 方法

---

## 飞书 API 版本

**事件类型**: `drive.file.bitable_record_changed_v1`

**订阅 API**:
```
POST https://open.feishu.cn/open-apis/drive/v1/files/{file_token}/subscribe?file_type=bitable
```

**推送方式**: WebSocket 长连接（默认）

**事件结构** (基于飞书官方文档):
```json
{
  "uuid": "event-uuid",
  "event_id": "event-id",
  "event": {
    "file_token": "多维表格的 file_token",
    "table_id": "具体表的 table_id",
    "action": "record_edited | record_created | record_deleted",
    "record_id": "变更的记录 ID",
    "fields": {
      "字段名": "字段值"
    }
  }
}
```

**注意**: 本实现不读取 `fields` 内容，仅记录元数据。

---

## 兼容性测试

### 测试环境

- **操作系统**: Linux (Ubuntu)
- **Python**: 3.12+
- **Hermes**: 基于 commit `71d34bad`
- **lark_oapi**: 已安装（版本未知，SDK 未提供版本号）

### 测试结果

```bash
✓ lark_oapi 已安装
✓ EventDispatcherHandler 可用
✓ register_p2_customized_event 方法存在
✓ 事件注册语法正确
✓ 本地测试全部通过（4/4）
```

---

## 最小化要求

### Hermes 端

1. 飞书平台适配器已启用
2. WebSocket 连接正常
3. `EventDispatcherHandler` 可用
4. `_build_event_handler` 方法存在

### 飞书端

1. 应用已开通「多维表格」权限
2. 开放平台已订阅 `drive.file.bitable_record_changed_v1` 事件
3. 应用是目标表的「管理员」或「拥有者」
4. 已执行文件级订阅 API

### 系统端

1. Python 3.12+
2. pip 可用
3. 网络连通飞书 API

---

## 升级建议

### Hermes Agent 升级

如果 Hermes Agent 上游有重大更新，需要：

1. 检查 `adapter.py` 结构变化
2. 确认 `_build_event_handler` 方法签名
3. 验证 `EventDispatcherHandler` 兼容性
4. 重新测试补丁应用

### 飞书 SDK 升级

```bash
pip install --upgrade lark-oapi
```

升级后验证：
```python
from lark_oapi.event.dispatcher_handler import EventDispatcherHandler
handler = EventDispatcherHandler.builder('', '')
handler.register_p2_customized_event('test', lambda d: None)
print("✓ SDK 兼容")
```

---

## 已知问题

### 1. SDK 版本号缺失

`lark_oapi` 未提供 `__version__` 属性，无法通过代码查询版本。

**解决方案**: 通过 `pip show lark-oapi` 查看安装版本。

### 2. 事件结构文档不完整

飞书官方文档未完整披露 `drive.file.bitable_record_changed_v1` 的事件结构。

**解决方案**: 
1. 临时添加 `logger.info(f"Raw event: {data}")` 查看完整结构
2. 根据实际推送调整字段解析逻辑

### 3. 补丁行号依赖

补丁文件使用固定行号（1441, 2170），如果 `adapter.py` 有改动，行号可能偏移。

**解决方案**:
1. 手动定位插入位置
2. 或使用模糊匹配: `patch --fuzz=3`

---

## 更新历史

- **2024-10-31**: 初始版本，基于 Hermes commit `71d34bad`
