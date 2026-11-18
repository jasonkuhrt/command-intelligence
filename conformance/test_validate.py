"""Regression checks for portable fixture applicability."""
import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from validate import validate_core

ROOT = Path(__file__).resolve().parent / "core"


class CoreApplicabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads((ROOT / "cases.json").read_text())
        cls.schema = json.loads((ROOT / "schema.json").read_text())

    def case(self, document, case_id):
        return next(case for case in document["cases"] if case["id"] == case_id)

    def test_structured_typed_resource_needs_no_text_surface(self):
        case = self.case(self.document, "structured-typed-resource")
        self.assertIn("typed_resource_structured", case["requires"])
        self.assertNotIn("text_surface", case["requires"])
        self.assertEqual(case["expected"]["events"][0]["resource_selections"], {"Note/open/$note": "alpha-id"})
        validate_core(self.document)

    def test_typed_resource_expectations_follow_synthetic_matcher(self):
        expected_matches = {
            "typed-resource": ["alpha-id"],
            "typed-unresolved": [],
            "typed-ambiguous": ["one-shared", "two-shared"],
        }
        for prefix in ("", "structured-"):
            for name, matches in expected_matches.items():
                with self.subTest(case=prefix + name):
                    case = self.case(self.document, prefix + name)
                    action = next(item for item in case["actions"] if item["op"] == "type_resource")
                    self.assertEqual(action["matches"], matches)
                    events = case["expected"]["events"]
                    if len(matches) == 1:
                        self.assertEqual(len(events), 1)
                        self.assertEqual(events[0]["resource_selections"], {action["slot"]: matches[0]})
                    else:
                        self.assertEqual(events, [])
                        self.assertEqual(set(case["expected"]["status"]), {"open", "refused"})
        validate_core(self.document)

    def test_typed_ambiguity_requires_both_candidates_on_each_surface(self):
        for case_id in ("typed-ambiguous", "structured-typed-ambiguous"):
            for remaining in (0, 1):
                with self.subTest(case=case_id, remaining=remaining):
                    broken = copy.deepcopy(self.document)
                    broken["cases"] = [self.case(broken, case_id)]
                    candidates = broken["binding"]["resources"]["Note/open/$note"]
                    nonmatching = [candidate for candidate in candidates if candidate["label"] != "Shared"]
                    matching = [candidate for candidate in candidates if candidate["label"] == "Shared"]
                    candidates[:] = nonmatching + matching[:remaining]
                    with self.assertRaisesRegex(ValueError, f"{case_id}: 'Shared' matches"):
                        validate_core(broken)

    def test_universal_replay_cannot_require_resource_history(self):
        broken = copy.deepcopy(self.document)
        case = self.case(broken, "consistent-replay")
        item = case["input"]["history"][0]
        item.update(recorded_path=["Note", "Note/open", "Note/open/$note"],
                    arguments_present=True, resource_selections={"Note/open/$note": "alpha-id"})
        with self.assertRaisesRegex(ValueError, "resource history needs resource_slots"):
            validate_core(broken)

    def test_universal_replay_has_no_fixed_surface(self):
        broken = copy.deepcopy(self.document)
        case = self.case(broken, "consistent-replay")
        case["input"]["history"][0]["surface"] = "structured"
        with self.assertRaisesRegex(ValueError, "recorded event needs its surface capability"):
            validate_core(broken)

    def test_replay_can_require_a_structured_surface(self):
        supported = copy.deepcopy(self.document)
        case = self.case(supported, "consistent-replay")
        case["requires"].append("structured_surface")
        case["input"]["history"][0]["surface"] = "structured"
        Draft202012Validator(self.schema).validate(supported)
        validate_core(supported)

    def test_typed_resource_declares_its_surface_feature(self):
        broken = copy.deepcopy(self.document)
        case = self.case(broken, "structured-typed-resource")
        case["requires"].remove("typed_resource_structured")
        with self.assertRaisesRegex(ValueError, "typed_resource_structured"):
            validate_core(broken)

    def test_unfilled_resource_slot_still_requires_resource_support(self):
        broken = copy.deepcopy(self.document)
        case = self.case(broken, "promotion-abandoned")
        case["requires"].remove("resource_slots")
        with self.assertRaisesRegex(ValueError, "installed action slots need resource_slots"):
            validate_core(broken)


if __name__ == "__main__":
    unittest.main()
