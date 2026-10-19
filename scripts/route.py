"""Resolve explicit operations and workspace paths; never write business data."""
import argparse
import json
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
ASSETS = Path('content-ops/defu-content-system')
STAGES = {
    'task': ('德夫视频任务与价值点评分标准_V1.md', '08_视频任务评分与迭代记录.md'),
    'script': ('德夫脚本分镜文案评分标准_V1.md', '09_脚本分镜文案评分与迭代记录.md'),
    'video': ('德夫短视频评分标准_V1.md', '07_视频评分与校准记录.md'),
}
LEARN_TARGETS = {
    'template': '02_内容结构模板库.md',
    'rule': '06_内容复盘与规则更新.md',
}


def resolve(action, stage, start, record=False, target=None):
    if action not in ('create', 'review', 'score', 'data', 'retro', 'learn'):
        raise ValueError('Unknown action')
    if (action == 'score' and stage not in STAGES) or (action != 'score' and stage):
        raise ValueError('Only score requires --stage task|script|video')
    if action == 'learn':
        target = target or 'template'
        if target not in LEARN_TARGETS:
            raise ValueError('learn --target must be template or rule')
    elif target:
        raise ValueError('--target applies only to learn')
    if record and action not in ('score', 'retro', 'learn'):
        raise ValueError('--record applies to score, retro, or learn; data writes by action')
    start = Path(start).resolve()
    if start == SKILL or SKILL in start.parents:
        raise ValueError('Skill directory is not a business workspace; pass --workspace')
    root = next((p for p in (start, *start.parents) if (p / ASSETS).is_dir()), None)
    if root is None:
        raise ValueError('No content-ops/defu-content-system found; pass an existing business workspace')
    asset_root = (root / ASSETS).resolve()
    if asset_root == SKILL or SKILL in asset_root.parents or root not in asset_root.parents:
        raise ValueError('Business assets must stay inside workspace and outside skill directory')
    required, refs, ledger = [], [], None
    if action == 'score':
        standard, name = STAGES[stage]
        required.append(root / 'docs' / standard)
        refs.append('scoring.md')
        if stage == 'task':
            required.append(asset_root / '00_德夫内容战略地图.md')
        ledger = asset_root / name
    elif action == 'data':
        refs.append('asset-rules.md')
        ledger = asset_root / STAGES['video'][1]
    elif action == 'retro':
        refs.append('asset-rules.md')
        ledger = asset_root / '06_内容复盘与规则更新.md'
    elif action == 'learn':
        refs.append('asset-rules.md')
        ledger = asset_root / LEARN_TARGETS[target]
    elif action == 'review':
        refs.append('content-system.md')
    if record:
        if 'asset-rules.md' not in refs:
            refs.append('asset-rules.md')
    if ledger is not None and ledger.resolve().parent != asset_root:
        raise ValueError('Ledger redirects outside business asset directory')
    required.extend(SKILL / 'references' / ref for ref in refs)
    return dict(action=action, stage=stage, workspace=str(root), asset_root=str(asset_root),
                required=[str(p) for p in required],
                missing_required=[str(p) for p in required if not p.is_file()],
                ledger=str(ledger) if ledger else None,
                write_requested=record or action == 'data',
                note='Path resolution only. retro/learn writes require evidence; ledger creation is on demand.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['create', 'review', 'score', 'data', 'retro', 'learn'])
    parser.add_argument('--stage', choices=list(STAGES))
    parser.add_argument('--target', choices=list(LEARN_TARGETS))
    parser.add_argument('--workspace', default=str(Path.cwd()))
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()
    try:
        print(json.dumps(resolve(args.action, args.stage, args.workspace, args.record, args.target), ensure_ascii=False, indent=2))
    except ValueError as exc:
        parser.exit(2, str(exc) + '\n')
