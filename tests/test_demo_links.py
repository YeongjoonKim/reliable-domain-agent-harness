"""브라우저 진입점이 누락된 자산·잘못된 상세 링크를 통과시키지 않는다."""
from pathlib import Path
import tempfile
import unittest

from scripts.check_repository import inspect_file


class DemoLinkTests(unittest.TestCase):
    def test_missing_script_and_escaped_local_link_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "index.html"
            path.write_text('<script src="missing.js"></script><a href="../outside.html">x</a>')
            self.assertEqual(inspect_file(root, path).count("broken-html-link"), 2)

    def test_cross_document_fragment_must_exist(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "detail.html").write_text('<section id="evidence">ok</section>')
            path = root / "index.html"
            path.write_text('<a href="detail.html#absent">missing</a>')
            self.assertIn("broken-html-fragment", inspect_file(root, path))
            path.write_text('<a href="detail.html#evidence">valid</a>')
            self.assertEqual(inspect_file(root, path), [])

    def test_encoded_asset_and_same_document_fragment(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data file.json").write_text("{}")
            path = root / "index.html"
            path.write_text('<a href="data%20file.json">JSON</a><a href="#trace">trace</a>'
                            '<section id="trace"></section><a href="https://example.com">source</a>')
            self.assertEqual(inspect_file(root, path), [])


if __name__ == "__main__":
    unittest.main()
