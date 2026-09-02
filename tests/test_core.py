import json
import tempfile
import unittest
from pathlib import Path

from backend.duplicates.finder import find_duplicates
from backend.rules.engine import matches
from backend.scanner.scanner import scan
from backend.sorter.engine import execute, preview


class SortixCoreTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_scan_is_metadata_first_and_recursive(self):
        (self.root / "nested").mkdir()
        (self.root / "nested" / "notes.txt").write_text("hello", encoding="utf-8")
        result = scan(str(self.root))
        self.assertEqual(result["file_count"], 1)
        self.assertEqual(result["files"][0]["category"], "Documents")
        self.assertEqual(result["files"][0]["relative_path"], "nested/notes.txt")

    def test_preview_and_execute_move_without_overwrite(self):
        source = self.root / "photo.jpg"
        source.write_bytes(b"image")
        existing = self.root / "Images"
        existing.mkdir()
        (existing / "photo.jpg").write_bytes(b"other")
        records = scan(str(self.root))["files"]
        plan = preview(str(self.root), records)
        self.assertEqual(plan["count"], 1)
        self.assertTrue(plan["moves"][0]["destination"].endswith("photo (1).jpg"))
        result = execute(plan)
        self.assertEqual(result["count"], 1)
        self.assertTrue((existing / "photo (1).jpg").exists())
        self.assertTrue((existing / "photo.jpg").exists())

    def test_duplicates_group_by_content(self):
        first = self.root / "one.txt"
        second = self.root / "two.txt"
        first.write_text("same", encoding="utf-8")
        second.write_text("same", encoding="utf-8")
        result = find_duplicates(scan(str(self.root))["files"])
        self.assertEqual(result["group_count"], 1)
        self.assertEqual(result["duplicate_count"], 2)

    def test_rule_matching_is_explicit(self):
        record = {"name": "invoice_august.pdf", "extension": "pdf", "category": "PDFs"}
        self.assertTrue(matches(record, {"field": "filename", "operator": "contains", "value": "invoice"}))
        self.assertFalse(matches(record, {"field": "extension", "operator": "is", "value": "jpg"}))


if __name__ == "__main__":
    unittest.main()