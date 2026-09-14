import json
import tempfile
import unittest
from pathlib import Path

from triple_model_session.build_precomputed_challenger_package import build
from triple_model_session.validate_precomputed_challengers import validate_package


class PrecomputedChallengerTests(unittest.TestCase):
    def review(self, job, reviewer):
        return {
            "schema_version": 1,
            "reviewer": reviewer,
            "document_key": job["document_key"],
            "source": {key: job[key] for key in ("relative_path", "sha256", "size_bytes")},
            "route_recommendation": "network",
            "purpose": "Understand the documented equipment scheme",
            "supported_questions": ["What explicitly connects to BC-04?"],
            "coverage": {"status": "complete", "reviewed_units": [{"unit": "page 1"}], "gaps": []},
            "candidate_findings": [{
                "finding_id": "f1",
                "kind": "connection",
                "subject_as_written": "BC-04",
                "statement": "BC-04 feeds CH-04",
                "predicate": "feeds",
                "object_as_written": "CH-04",
                "value": None,
                "unit": None,
                "network": "material",
                "origin": "explicit",
                "confidence": 0.95,
                "evidence": [{
                    "source_relative_path": job["relative_path"],
                    "page_or_sheet": 1,
                    "locator": None,
                    "quote": "BC-04 feeds CH-04",
                    "region": None,
                    "visual_description": None,
                }],
                "qualifiers": {},
                "risk_flags": [],
            }],
            "unresolved_questions": [],
        }

    def test_build_is_state_independent_and_validation_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sources = root / "sources"
            sources.mkdir()
            (sources / "scheme.txt").write_text("BC-04 feeds CH-04", encoding="utf-8")
            package = root / "package"
            result = build(sources, package)
            self.assertEqual(result["documents"], 1)
            manifest = json.loads((package / "source_manifest.json").read_text(encoding="utf-8"))
            self.assertTrue(manifest["state_independent"])
            job = json.loads((package / "review_jobs.json").read_text(encoding="utf-8"))["jobs"][0]
            for reviewer in ("gemini", "muse"):
                path = root / reviewer / job["expected_output"]
                path.parent.mkdir(parents=True)
                path.write_text(json.dumps(self.review(job, reviewer)), encoding="utf-8")
            report = validate_package(package, sources, {"gemini": root / "gemini", "muse": root / "muse"})
            self.assertEqual(report["status"], "PASS")

    def test_changed_source_and_incomplete_review_block(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sources = root / "sources"
            sources.mkdir()
            source = sources / "scheme.txt"
            source.write_text("BC-04 feeds CH-04", encoding="utf-8")
            package = root / "package"
            build(sources, package)
            job = json.loads((package / "review_jobs.json").read_text(encoding="utf-8"))["jobs"][0]
            for reviewer in ("gemini", "muse"):
                review = self.review(job, reviewer)
                if reviewer == "muse":
                    review["coverage"]["status"] = "incomplete"
                path = root / reviewer / job["expected_output"]
                path.parent.mkdir(parents=True)
                path.write_text(json.dumps(review), encoding="utf-8")
            source.write_text("changed source", encoding="utf-8")
            report = validate_package(package, sources, {"gemini": root / "gemini", "muse": root / "muse"})
            self.assertEqual(report["status"], "BLOCK")
            self.assertTrue(any("SHA-256 mismatch" in error for error in report["errors"]))
            self.assertTrue(any("coverage.status" in error for error in report["errors"]))

    def test_package_cannot_be_written_inside_source_folder(self):
        with tempfile.TemporaryDirectory() as temp:
            sources = Path(temp) / "sources"
            sources.mkdir()
            (sources / "scheme.txt").write_text("BC-04", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "outside the source directory"):
                build(sources, sources / "challenger-package")


if __name__ == "__main__":
    unittest.main()
