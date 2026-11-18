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
        for prefix in ("", "structured-"):
            for name in ("typed-resource", "typed-unresolved", "typed-ambiguous"):
                with self.subTest(case=prefix + name):
                    case = self.case(self.document, prefix + name)
                    action = next(item for item in case["actions"] if item["op"] == "type_resource")
                    candidates = self.document["binding"]["resources"][action["slot"]]
                    matches = [item["id"] for item in candidates if item["label"] == action["text"]]
                    events = case["expected"]["events"]
                    if len(matches) == 1:
                        self.assertEqual(events[0]["resource_selections"], {action["slot"]: matches[0]})
                    else:
                        self.assertEqual(events, [])
                        self.assertEqual(set(case["expected"]["status"]), {"open", "refused"})

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

    def test_flow_case_cannot_claim_to_be_universal(self):
        broken = copy.deepcopy(self.document)
        case = self.case(broken, "capability-flow-structured")
        case["requires"].remove("flows")
        with self.assertRaisesRegex(ValueError, "flow needs flows"):
            validate_core(broken)


if __name__ == "__main__":
    unittest.main()
