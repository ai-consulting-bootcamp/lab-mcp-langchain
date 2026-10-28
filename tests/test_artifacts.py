"""Regression checks for stale traces, snapshots, and dependency records."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import sys

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))
from lab_artifacts import fence, validate_run


class ArtifactValidationTests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)
        self.project = Path(self.workspace.name)
        latest = json.loads((PROJECT / "evidence/latest.json").read_text(encoding="utf-8"))
        self.evidence = self.project / "evidence" / "run"
        shutil.copytree(PROJECT / latest["directory"], self.evidence)
        shutil.copytree(PROJECT / "sample_docs", self.project / "sample_docs")
        shutil.copyfile(PROJECT / "requirements.txt", self.project / "requirements.txt")

    def test_current_run_is_consistent(self):
        self.assertEqual(validate_run(self.project, self.evidence)["status"], "passed")

    def test_missing_call_is_rejected(self):
        path = self.evidence / "agent_runs.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["combined"]["call_ids"].append("call-999999")
        path.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaisesRegex(AssertionError, "combined"):
            validate_run(self.project, self.evidence)

    def test_changed_resource_snapshot_is_rejected(self):
        with (self.evidence / "langchain_guide.md").open("a", encoding="utf-8") as stream:
            stream.write("\nChanged snapshot\n")
        with self.assertRaises(AssertionError):
            validate_run(self.project, self.evidence)

    def test_dependency_drift_is_rejected(self):
        path = self.project / "requirements.txt"
        path.write_text(path.read_text().replace("langchain==", "unexpected-package=="), encoding="utf-8")
        with self.assertRaisesRegex(AssertionError, "Requirements differ"):
            validate_run(self.project, self.evidence)

    def test_nested_code_fences_remain_inside_the_excerpt(self):
        rendered = fence("A source example:\n```python\nprint('example')\n```")
        self.assertTrue(rendered.startswith("````text\n"))
        self.assertTrue(rendered.endswith("\n````\n"))


if __name__ == "__main__":
    unittest.main()
