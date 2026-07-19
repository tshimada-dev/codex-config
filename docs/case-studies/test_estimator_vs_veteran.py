import hashlib
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[2]
CANONICAL = Path(__file__).with_name("estimator-vs-veteran.md")
JAPANESE = ROOT / "docs" / "ja" / "case-studies" / "estimator-vs-veteran.md"
ROOT_README = ROOT / "README.md"
ENGLISH_README = ROOT / "README.en.md"
SENSITIVE_PATTERNS = {
    "email": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "openai_key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "private_key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "windows_path": re.compile(r"\b[A-Za-z]:\\[^\s]+"),
}


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


class EstimatorVsVeteranCaseStudyTest(unittest.TestCase):
    def setUp(self):
        self.canonical = CANONICAL.read_text(encoding="utf-8")
        self.japanese = JAPANESE.read_text(encoding="utf-8")

    def test_published_observations_and_formulas_are_fixed(self):
        for value in (450, 170, 115, 175, 189):
            self.assertRegex(self.canonical, rf"\b{value}\b")
            self.assertRegex(self.japanese, rf"\b{value}\b")

        expected_formulas = [
            "450 / 170 = 2.647",
            "(450 - 170) / 170 = 164.7%",
            "450 / 115 = 3.913",
            "(175 - 170) / 170 = 2.9%",
            "(175 - 115) / 115 = 52.2%",
            "(175 - 115) / 175 = 34.3%",
            "((450 - 170) - (175 - 170)) / (450 - 170) = 98.2%",
        ]
        for formula in expected_formulas:
            self.assertIn(formula, self.canonical)
            self.assertIn(formula, self.japanese)

        self.assertAlmostEqual(450 / 170, 2.6470588235)
        self.assertAlmostEqual((175 - 170) / 170, 0.0294117647)
        self.assertAlmostEqual((175 - 115) / 115, 0.5217391304)
        self.assertAlmostEqual(((450 - 170) - (175 - 170)) / (450 - 170), 0.9821428571)

    def test_claims_are_bounded_and_reproducible(self):
        required_canonical = [
            "Reconstruction rules fixed before calculation",
            "source-reported attribution, not independently reproducible",
            "must not replace the reported 85%",
            "does not establish general estimator accuracy",
            "Reproduction checklist",
        ]
        for marker in required_canonical:
            self.assertIn(marker, self.canonical)

        required_japanese = [
            "計算前に固定する再構成ルール",
            "source報告の原因帰属。公開集計値からは独立再現不可",
            "98.2%を報告された85%の代わりに使ってはいけません",
            "一般的な見積精度",
            "再現チェックリスト",
        ]
        for marker in required_japanese:
            self.assertIn(marker, self.japanese)

        for issue in (3, 4, 10):
            url = f"https://github.com/tshimada-dev/codex-config/issues/{issue}"
            self.assertIn(url, self.canonical)
            self.assertIn(url, self.japanese)

    def test_japanese_reference_tracks_exact_canonical_blob(self):
        expected = git_blob_sha(CANONICAL.read_bytes())
        self.assertIn(f"source_blob: {expected}", self.japanese)
        self.assertIn("source: docs/case-studies/estimator-vs-veteran.md", self.japanese)
        self.assertIn("canonical: false", self.japanese)

    def test_readme_links_resolve(self):
        relative = "docs/case-studies/estimator-vs-veteran.md"
        self.assertIn(f"({relative})", ROOT_README.read_text(encoding="utf-8"))
        self.assertIn("(docs/case-studies/estimator-vs-veteran.md)", ENGLISH_README.read_text(encoding="utf-8"))
        self.assertTrue((ROOT / relative).is_file())

    def test_documents_are_sensitive_pattern_free(self):
        corpus = self.canonical + "\n" + self.japanese
        for name, pattern in SENSITIVE_PATTERNS.items():
            self.assertIsNone(pattern.search(corpus), f"sensitive pattern `{name}` found")


if __name__ == "__main__":
    unittest.main()
