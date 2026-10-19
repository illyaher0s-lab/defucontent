"""Run with python -B tests/test_route.py. Uses temporary workspaces only."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'route.py'


class RouteTest(unittest.TestCase):
    def test_routing_and_storage_boundaries(self):
        self.assertTrue(SCRIPT.exists(), 'Missing deterministic route/path resolver')
        spec = importlib.util.spec_from_file_location('route', SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'content-ops/defu-content-system').mkdir(parents=True)
            nested = root / 'docs/nested'
            nested.mkdir(parents=True)
            for stage, prefix in [('task', '08_'), ('script', '09_'), ('video', '07_')]:
                result = mod.resolve('score', stage, nested)
                self.assertEqual(Path(result['workspace']), root.resolve())
                self.assertTrue(Path(result['ledger']).name.startswith(prefix))
                self.assertTrue(result['missing_required'])
                self.assertFalse(result['write_requested'])
                recorded = mod.resolve('score', stage, root, record=True)
                self.assertTrue(recorded['write_requested'])
            self.assertFalse(mod.resolve('create', None, root)['write_requested'])
            self.assertFalse(mod.resolve('review', None, root)['write_requested'])
            self.assertTrue(mod.resolve('data', None, root)['write_requested'])
            retro_recorded = mod.resolve('retro', None, root, record=True)
            learn_recorded = mod.resolve('learn', None, root, record=True)
            learn_rule_recorded = mod.resolve('learn', None, root, record=True, target='rule')
            self.assertTrue(retro_recorded['write_requested'])
            self.assertTrue(learn_recorded['write_requested'])
            self.assertEqual(Path(learn_recorded['ledger']).name, '02_内容结构模板库.md')
            self.assertEqual(Path(learn_rule_recorded['ledger']).name, '06_内容复盘与规则更新.md')
            self.assertEqual(len(retro_recorded['required']), len(set(retro_recorded['required'])))
            self.assertEqual(len(learn_recorded['required']), len(set(learn_recorded['required'])))
            with self.assertRaises(ValueError):
                mod.resolve('data', None, root, record=True)
            self.assertTrue(Path(mod.resolve('retro', None, root)['ledger']).name.startswith('06_'))
            with self.assertRaises(ValueError):
                mod.resolve('score', None, root)
            with self.assertRaises(ValueError):
                mod.resolve('unknown', None, root)
            with self.assertRaises(ValueError):
                mod.resolve('create', 'video', root)
            with self.assertRaises(ValueError):
                mod.resolve('create', None, root, record=True)
            with self.assertRaises(ValueError):
                mod.resolve('retro', None, root, target='rule')
            with self.assertRaises(ValueError):
                mod.resolve('create', None, SCRIPT.parent.parent)
            self.assertFalse(list(root.rglob('*.md')), 'Resolver must not create ledgers')


if __name__ == '__main__':
    unittest.main()
