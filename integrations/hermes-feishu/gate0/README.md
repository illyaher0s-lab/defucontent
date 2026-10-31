# Gate 0 飞书多维表格事件监听器

## 概述

为 Hermes Agent 的飞书平台适配器添加最小化的多维表格记录变更事件监听器。

**目标事件**: `drive.file.bitable_record_changed_v1`

**特性**:
- ✅ 轻量级，不阻塞 WebSocket 事件循环
- ✅ 仅监听指定测试表，不影响其他表
- ✅ 只记录 `record_edited` 事件，忽略其他操作
- ✅ 不调用 AI，不修改记录，不触发业务流程
- ✅ 安全过滤，不记录敏感字段值或凭证

---

## 文件清单

```
integrations/hermes-feishu/gate0/
├── adapter.patch              # Hermes 飞书适配器补丁
├── test_bitable_handler.py    # 本地测试脚本
└── README.md                  # 本文档
```

---

## 前置条件

### 1. Hermes Agent 版本

**已测试版本**: 
- Hermes Agent (基于 Nous Research 开源版本)
- 飞书平台适配器路径: `plugins/platforms/feishu/adapter.py`

**依赖**:
- `lark_oapi` SDK (飞书开放平台 Python SDK)
- `EventDispatcherHandler` (lark_oapi.event.dispatcher_handler)

**检查方法**:
```bash
python3 -c "
from lark_oapi.event.dispatcher_handler import EventDispatcherHandler
print('✓ SDK 可用')
"
```

### 2. 飞书配置

**必需**:
1. 飞书应用已开通「多维表格」权限
2. 飞书开放平台已订阅 `drive.file.bitable_record_changed_v1` 事件
3. 应用是目标多维表格的「管理员」或「拥有者」
4. 已执行文件级事件订阅:
   ```bash
   POST /drive/v1/files/{file_token}/subscribe?file_type=bitable
   ```

### 3. Hermes 配置

**当前连接方式**: WebSocket 长连接（默认）

**配置位置**: `~/.hermes/config.yaml`

**飞书配置示例**:
```yaml
feishu:
  app_id: "YOUR_APP_ID"
  app_secret: "YOUR_APP_SECRET"
```

---

## 使用说明

### 步骤 1: 配置测试表 ID

**在补丁文件和测试脚本中替换占位符**:

```python
# 替换为实际值
GATE0_FILE_TOKEN = "YOUR_FILE_TOKEN_HERE"  # 多维表格的 file_token
GATE0_TABLE_ID = "YOUR_TABLE_ID_HERE"      # 具体表的 table_id
```

**获取方法**:
- file_token: 从飞书多维表格 URL 中提取 (`/base/{file_token}`)
- table_id: 从 URL 参数中提取 (`?table={table_id}`)

### 步骤 2: 本地测试

```bash
python3 test_bitable_handler.py
```

**预期输出**:
```
开始测试 Gate 0 多维表格事件处理器...

=== Test 1: Gate 0 表 record_edited 事件 ===
INFO: [Feishu] Gate 0 bitable event: event_id=test-event-001, 
      file_token=YOUR_FILE_TOKEN_HERE, 
      table_id=YOUR_TABLE_ID_HERE, 
      action=record_edited, 
      record_id=test_record_id

=== Test 2-4: 其他测试（应被过滤或优雅处理）===

✓ 所有测试完成
```

### 步骤 3: 应用补丁

**备份原文件**:
```bash
cp ~/.hermes/hermes-agent/plugins/platforms/feishu/adapter.py \
   ~/.hermes/hermes-agent/plugins/platforms/feishu/adapter.py.backup
```

**应用补丁**:
```bash
cd ~/.hermes/hermes-agent/plugins/platforms/feishu
patch -p1 < /path/to/adapter.patch
```

**验证修改**:
```bash
grep -A 5 "_on_bitable_record_changed" adapter.py
```

### 步骤 4: 重启 Hermes

```bash
hermes restart
```

**验证启动**:
```bash
hermes status
hermes logs | tail -50
```

### 步骤 5: 触发测试事件

1. 在飞书多维表格中打开 Gate 0 测试表
2. 修改任意记录的任意字段
3. 观察 Hermes 日志

**预期日志**:
```
INFO: [Feishu] Gate 0 bitable event: 
      event_id=<实际事件ID>, 
      file_token=<实际file_token>, 
      table_id=<实际table_id>, 
      action=record_edited, 
      record_id=<实际record_id>
```

---

## 回退方案

### 方案 1: 恢复备份

```bash
cp ~/.hermes/hermes-agent/plugins/platforms/feishu/adapter.py.backup \
   ~/.hermes/hermes-agent/plugins/platforms/feishu/adapter.py
hermes restart
```

### 方案 2: 反向应用补丁

```bash
cd ~/.hermes/hermes-agent/plugins/platforms/feishu
patch -p1 -R < /path/to/adapter.patch
hermes restart
```

### 验证回退

```bash
grep "_on_bitable_record_changed" ~/.hermes/hermes-agent/plugins/platforms/feishu/adapter.py
# 预期: 无输出

hermes status
# 预期: ✓ running
```

---

## 代码说明

### 修改范围

**文件**: `plugins/platforms/feishu/adapter.py`  
**修改**: 2 处，共 48 行

#### 修改 1: 注册事件（1 行）

在 `_build_event_handler` 方法中添加:

```python
.register_p2_customized_event("drive.file.bitable_record_changed_v1", self._on_bitable_record_changed)
```

#### 修改 2: 添加事件处理器（43 行）

在 `_on_meeting_invited_event` 方法之后添加 `_on_bitable_record_changed` 方法。

### 事件处理流程

```
飞书推送事件
    ↓
WebSocket 接收
    ↓
EventDispatcherHandler 分发
    ↓
_on_bitable_record_changed
    ↓
过滤 file_token 和 table_id
    ↓
过滤 action（仅 record_edited）
    ↓
记录日志（INFO 级别）
    ↓
返回（不执行业务逻辑）
```

### 安全特性

1. **表级隔离**: 仅处理指定 file_token 和 table_id 的事件
2. **操作过滤**: 仅记录 `record_edited`，忽略 `record_created` 和 `record_deleted`
3. **无副作用**: 不调用外部 API，不修改数据，不触发 Agent
4. **错误隔离**: 异常被捕获并记录，不影响其他事件处理

---

## 故障排查

### 问题 1: 日志中无事件记录

**可能原因**:
1. 文件级订阅未成功
2. file_token 或 table_id 配置错误
3. 应用权限不足
4. 飞书开放平台未订阅事件

**排查步骤**:
```bash
# 检查 WebSocket 连接
hermes status

# 检查日志是否有其他飞书事件
hermes logs | grep -i feishu

# 手动触发其他事件（如发送消息给机器人）验证连接正常
```

### 问题 2: 重启失败

**可能原因**:
1. 补丁应用失败，语法错误
2. 依赖缺失

**排查步骤**:
```bash
# 检查语法
python3 -m py_compile ~/.hermes/hermes-agent/plugins/platforms/feishu/adapter.py

# 查看启动日志
hermes logs

# 回退到备份
cp adapter.py.backup adapter.py
hermes restart
```

### 问题 3: 收到非 Gate 0 表的事件

**原因**: file_token 或 table_id 配置错误

**解决**:
1. 从飞书多维表格 URL 重新提取正确的 token 和 ID
2. 更新补丁文件中的常量
3. 重新应用补丁

---

## 限制与扩展

### 当前限制

1. **单表监听**: 仅支持一个测试表，不支持多表
2. **单操作**: 仅记录 `record_edited`，不处理创建/删除
3. **无业务逻辑**: 仅记录日志，不触发 AI 或其他操作
4. **硬编码 ID**: file_token 和 table_id 硬编码在代码中

### 扩展方向

#### 1. 支持多表监听

```python
MONITORED_TABLES = {
    "file_token_1": ["table_id_1", "table_id_2"],
    "file_token_2": ["table_id_3"],
}

if file_token not in MONITORED_TABLES:
    return
if table_id not in MONITORED_TABLES[file_token]:
    return
```

#### 2. 支持所有操作类型

```python
MONITORED_ACTIONS = ["record_created", "record_edited", "record_deleted"]

if action not in MONITORED_ACTIONS:
    return
```

#### 3. 触发业务逻辑

```python
# 读取变更内容
record = self._fetch_record(file_token, table_id, record_id)

# 调用 AI 处理
if record.get("某字段") == "触发条件":
    self._trigger_ai_workflow(record)

# 写回结果
self._update_record(file_token, table_id, record_id, {"状态": "已处理"})
```

#### 4. 配置化管理

```yaml
# ~/.hermes/config.yaml
feishu:
  bitable_monitors:
    - file_token: "xxx"
      table_id: "yyy"
      actions: ["record_edited"]
      handler: "custom_handler_function"
```

---

## 依赖信息

### Hermes Agent

**项目**: [Nous Research / Hermes Agent](https://github.com/NousResearch/hermes-agent)  
**版本**: 基于开源版本（具体 commit 见部署时的 Hermes 安装）

### 飞书 SDK

**包名**: `lark_oapi`  
**安装**: `pip install lark-oapi`  
**文档**: [飞书开放平台 Python SDK](https://open.feishu.cn/document/ukTMukTMukTM/uQjN0YjL0YDN24CN2QjN)

---

## 许可证

本补丁代码遵循 Hermes Agent 的许可证（MIT License）。

---

## 贡献者

- 初版实现: 2024-10-31
- 测试验证: 本地测试通过

---

## 更新日志

### v1.0.0 (2024-10-31)

- ✅ 初始实现
- ✅ 支持 Gate 0 单表监听
- ✅ 仅记录 record_edited 事件
- ✅ 本地测试通过
- ✅ SDK 兼容性验证通过

---

## 注意事项

⚠️ **安全提醒**:
1. 不要将真实的 file_token、table_id、app_id、app_secret 提交到公开仓库
2. 不要上传包含企业数据或敏感信息的日志文件
3. 生产环境部署前请在测试环境充分验证
4. 定期检查飞书开放平台的事件订阅配额和限流

⚠️ **性能考虑**:
1. 事件处理器在 WebSocket 线程中执行，应保持轻量
2. 避免在处理器中执行耗时操作（如复杂计算、外部 API 调用）
3. 如需执行重操作，应使用 `self._submit_if_ready` 异步提交

⚠️ **维护建议**:
1. 监控事件处理的成功率和延迟
2. 定期检查飞书 SDK 更新
3. 关注 Hermes Agent 上游更新，及时同步适配器改动
