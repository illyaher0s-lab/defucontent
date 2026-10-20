# 内容工作台接入接口

## 飞书多维表格写入

已提供 `scripts/feishu_write.py`，从 `~/.hermes/.env` 读取凭证（FEISHU_APP_ID/FEISHU_APP_SECRET），使用 `lark_oapi` SDK。

**用法**：
```python
import lark_oapi as lark
from lark_oapi.api.bitable.v1 import *
import os

# 读凭证
env_file = os.path.expanduser("~/.hermes/.env")
app_id = app_secret = None
with open(env_file, 'r') as f:
    for line in f:
        if '=' in line:
            key, val = line.strip().split('=', 1)
            val = val.strip('"').strip("'")
            if 'APP_ID' in key: app_id = val
            elif 'APP_SECRET' in key: app_secret = val

# 创建客户端
client = lark.Client.builder().app_id(app_id).app_secret(app_secret).build()

# 写入记录
request = CreateAppTableRecordRequest.builder() \
    .app_token("<app_token>") \
    .table_id("<table_id>") \
    .request_body(AppTableRecord.builder().fields({
        "文本": "选题标题",
        "核心价值点": "价值描述",
        # ... 其他字段
    }).build()) \
    .build()

response = client.bitable.v1.app_table_record.create(request)
```

**字段格式**：字段名直接用中文名（如 `"文本"`），值类型按表格定义。选择字段用列表 `["选项1"]`，优先级等特殊字段用 `[{"text": "A", "type": "text"}]`。

**写入前必查**：用 `ListAppTableFieldRequest` 获取字段定义，检查选择类字段的 `property.options`，只能填已有选项，不得自造新值。写入前用 `ListAppTableRecordRequest` 读3条现有记录查看实际格式。

## 通用接口约定

**不在 Skill 内绑定飞书 API、表格字段、数据库或连接器。** 具体接入由使用该 Skill 的 Agent 根据用户授权、可用工具与当前飞书工作台结构实现。

模块交接时使用可映射的通用对象，而非预设飞书列名：
- `content_id`：可选；优先使用工作台已有唯一 ID。不存在时本轮用临时编号，不擅自创建持久 ID。
- `topic`、`audience`、`goal`、`status`（候选/待素材/待文案/待审核/可制作/待补证/已发布等）、`asset_refs`、`draft_ref`、`review_ref`、`source`、`version`：均按可用字段映射，非强制建列。
- 与已有 VT/SS/VC 评分记录关联时保留其原 ID，不做破坏性迁移。

Agent 接入步骤：
1. 先读取现有飞书表结构、字段含义、状态规则、唯一键及权限。
2. 映射现有字段，识别缺项和冲突；不得未经确认新增列/表、改字段、迁移旧记录。
3. 写入前确认用户授权、目标表、唯一内容记录和更新字段；仅提交必要变化，写后读回核对。
4. 没有飞书工具、权限或映射不明确时，仅输出结构化待写数据，不谎称已同步。
5. 飞书字段改变时修改 Agent 的适配层，不修改 Planning/Writing/Review 的业务逻辑。

此文件是集成契约，不是已完成的飞书集成。
