"""Basic format and review-coverage checks; not a test of copywriting quality."""
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_copy_review.py"
spec = importlib.util.spec_from_file_location("validate_copy_review", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def sample():
    ids = [f"v{i}" for i in range(1, 6)]
    return {
        "candidates": [{"id": ident, "title": f"封面{ident}", "body": "真实细节，让空间更有感觉。"} for ident in ids],
        "reviews": [
            {"id": ident, "decision": "selected" if i < 3 else "rejected",
             "consumer_value": "表达明确的空间体验", "reason": "具体审查理由",
             "risk": "clear"} for i, ident in enumerate(ids)
        ],
        "selected_ids": ids[:3],
    }


class CopyReviewTest(unittest.TestCase):
    def test_valid_five_reviews_three_selected(self):
        self.assertEqual(mod.validate(sample()), [])

    def test_missing_review_fails(self):
        obj = sample()
        obj["reviews"].pop()
        self.assertTrue(mod.validate(obj))

    def test_unreviewed_five_draft_delivery_fails(self):
        obj = sample()
        obj["selected_ids"] = [f"v{i}" for i in range(1, 6)]
        self.assertTrue(mod.validate(obj))

    def test_mismatch_selection_fails(self):
        obj = sample()
        obj["selected_ids"] = ["v1", "v2", "v5"]
        self.assertTrue(mod.validate(obj))

    def test_long_selected_copy_fails(self):
        obj = sample()
        obj["candidates"][0]["body"] = "字" * 151
        self.assertTrue(mod.validate(obj))

    def test_unresolved_selected_risk_fails(self):
        obj = sample()
        obj["reviews"][0]["risk"] = "needs_check"
        self.assertTrue(mod.validate(obj))


if __name__ == "__main__":
    unittest.main()
