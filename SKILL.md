---
name: defu-content-planning
description: Use for 德夫国际石材 content planning, batch topic generation, copywriting, scripts, review, three-stage scoring, performance records and retrospectives. Not for unrelated-brand copy or raw meeting-note cleanup.
---

# 德夫内容工作流

先执行用户实际要求，不把简单文案任务扩大为完整营销报告。围绕真实客户判断、素材与可证实的德夫价值创作；兼顾观看理由与后续经营价值。

## 1. 精准路由

| 用户要做什么 | 读取 | 默认交付 |
| --- | --- | --- |
| 单条/批量选题、素材找选题 | [Planning](modules/planning.md) | 选题或优先级清单 |
| 文案、改稿、脚本、分镜 | [Writing](modules/writing.md) | 直接可用的指定成稿 |
| 批量初筛/质量检查 | [Review](modules/review.md) | 通过/修改/补证/放弃 |
| 不打分的审稿/审片 | Review + [content-system](references/content-system.md) | 最关键问题与最小修改 |
| 正式评分：选题/脚本/成片 | Review + [scoring](references/scoring.md) | 按阶段唯一标准及可见证据评分 |
| 发布数据、复盘、反馈学习 | [Learning](modules/learning.md) + [asset-rules](references/asset-rules.md) | 数据/结论，授权时才写入 |
| 一次完成多条内容 | [batch](workflows/batch.md) + 所需模块 | 批量成品及阻塞清单 |
| 精细打磨单条 | [single](workflows/single.md) + 所需模块 | 用户要求的当前阶段成品 |
| 同步内容工作台/飞书 | [workspace 接口](integrations/workspace.md) | 由 Agent 按实际表结构适配 |

用户要求多操作就按顺序执行，不遗漏也不自动增加。用户只要字幕/标题，直接给字幕/标题。普通创作不自动正式评分、记录或发布。批量轻检不等于完整六维评分。没有可用图像/视频生成工具时，不声称能自动生成成片。

## 2. 操作边界

- **模块**负责各自的业务能力；**工作流**只组合模块；**references**承载既有事实/评分/数据约束；外部工作区存放真实素材、台账与现行标准。不要在模块间复制同一规则。
- 创作按已给方向执行，素材不足时给可用部分及最小补证清单。内容不必每次展示过程；优先交付成品。
- 选题可以来自素材，也可以先于素材。批量优先去重、可执行性和观看价值，不能为了数量凑不成立的题目。
- 重要主张区分**已确认／工作假设／待核验**。未经核验，不得公开宣称价格、参数推导的性能、认证、排名、客户案例、独家性、合作关系、服务承诺及素材授权。多项目素材不得伪装为单一案例。
- 标记**可制作／待补证／不做**；涉及发布红线不因分数高而放行。单条自动修稿不无限循环。

## 3. 业务真源、评分与写入

`SKILL_DIR` 为本文件目录；`WORKSPACE` 为业务工作区；`ASSET_ROOT = WORKSPACE/content-ops/defu-content-system/`。这些路径不得混为一谈。

- 企业背景、老板反馈、执行规范、历史模板、内容战略地图、记录和复盘的唯一真源及检索规则：见 [asset-rules](references/asset-rules.md)。背景资料不自动成为可公开承诺。
- task/script/video 正式评分分别读取工作区现行标准，按照 [scoring](references/scoring.md) 操作；缺标准不得发明正式分数。只给逐字稿不能猜成片画质声音。
- `scripts/route.py` 仅在需要解析工作区评分/记录路径时使用，例如 `python scripts/route.py score --stage script --workspace "<WORKSPACE>"`；它只报告依赖、不评分不写入。缺业务工作区时仍可完成不依赖工作区的低风险创作；不猜测缺失事实。
- 用户明确要求保存/回填，或有仍适用的持续记录授权，才按 asset-rules 写入；当前“不记录”优先。先匹配唯一作品/事件、再追加、写后核验；不能覆盖历史或重复写入。
- 内容工作台/飞书只保留 [适配契约](integrations/workspace.md)：由运行 Agent 探查真实字段和权限，未经确认不新建列、不迁移旧表，不预设固定 ID 结构。

## 4. 交付与异常

优先完成可做的部分，不以少量缺失资料阻断全任务。选题没有实际价值、主张无法证实或素材不适配时明确指出，并给最小替代方案。外部视频缺失不猜画面；播放数据不等于内容质量或因果结论。AI 图片生成、自动剪辑、自动发布目前均**不在本 Skill 范围**。

相关质量回归场景见 [architecture-cases](tests/architecture-cases.md) 与既有 [acceptance-cases](tests/acceptance-cases.md)。未实测不得声称已通过 Agent 行为测试。
