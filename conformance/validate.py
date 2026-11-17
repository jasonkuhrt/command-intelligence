#!/usr/bin/env python3
"""Validate both portable suites and the invariants JSON Schema cannot express."""
import json
import sys
from datetime import datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parent


def walk(nodes):
    for node in nodes:
        yield node
        yield from walk(node.get("children", []))


def fail(message):
    raise ValueError(message)


def validate_reference(document):
    for case in document["cases"]:
        if case.get("type") != "ranking":
            continue
        query = case["query"]
        if "match_quality" not in query:
            fail(f"{case['id']}: ranking query is missing match_quality")
        nodes = {node["id"]: node for node in walk(case["tree"])}
        parent = nodes.get(query.get("parent"), {})
        if parent.get("slot_kind") == "resource":
            candidates = {candidate["id"] for candidate in parent["candidates"]}
            supplied = set(query["match_quality"])
            if candidates != supplied:
                fail(f"{case['id']}: match_quality must cover every candidate; "
                     f"missing={sorted(candidates - supplied)}, extra={sorted(supplied - candidates)}")


def validate_core(document):
    binding = document["binding"]
    nodes = binding["nodes"]
    by_id = {node["id"]: node for node in nodes}
    if len(by_id) != len(nodes):
        fail("core binding: duplicate node IDs")
    for node in nodes:
        if node["parent"] is not None and node["parent"] not in by_id:
            fail(f"core binding: unknown parent for {node['id']}")
        for step in node.get("steps", []):
            if step not in by_id:
                fail(f"core binding: unknown flow step {step}")
    for slot, candidates in binding["resources"].items():
        if by_id.get(slot, {}).get("kind") != "resource_slot":
            fail(f"core binding: {slot} is not a resource slot")
        if len({candidate['id'] for candidate in candidates}) != len(candidates):
            fail(f"core binding: duplicate resources in {slot}")

    def event(case_id, item):
        path = item["recorded_path"]
        if not path or any(node not in by_id for node in path):
            fail(f"{case_id}: empty or unknown recorded path")
        for slot, identity in item["resource_selections"].items():
            ids = {candidate['id'] for candidate in binding['resources'].get(slot, [])}
            if slot not in path or identity not in ids:
                fail(f"{case_id}: invalid resource selection {slot}={identity}")

    for case in document["cases"]:
        case_id, required = case["id"], set(case["requires"])
        if case["type"] == "interaction":
            for action in case["actions"]:
                op = action["op"]
                if op == "commit" and action["surface"] + "_surface" not in required:
                    fail(f"{case_id}: missing surface capability")
                if op == "type_resource" and not {"text_surface", "resource_slots"} <= required:
                    fail(f"{case_id}: typed resources need text_surface and resource_slots")
                if op == "pick_resource" and "resource_slots" not in required:
                    fail(f"{case_id}: resource selection needs resource_slots")
            for item in case["expected"]["events"]:
                event(case_id, item)
            for text in case["expected"].get("forbidden_text", []):
                if text in json.dumps(case["expected"]["events"], ensure_ascii=False):
                    fail(f"{case_id}: forbidden input appears in expected events")
        elif case["type"] == "consistency":
            for item in case["input"]["history"]:
                event(case_id, item)
            actual, expected = case["input"]["candidates"], case["expected"]["candidates"]
            if len(actual) != len(set(actual)) or set(actual) != set(expected):
                fail(f"{case_id}: inconsistent candidate sets")
        elif case["type"] == "edit":
            for value in (case["input"], case["expected"]):
                data, cursor = value["line"].encode(), value["cursor"]
                if cursor > len(data):
                    fail(f"{case_id}: cursor outside line")
                try:
                    data[:cursor].decode()
                except UnicodeDecodeError:
                    fail(f"{case_id}: cursor splits a UTF-8 character")
        elif case["type"] == "cutoff":
            parse = lambda value: datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parse(case["input"]["earlier"]) >= parse(case["input"]["now"]):
                fail(f"{case_id}: earlier time must precede now")


def main():
    for name, check in (("core", validate_core), ("reference", validate_reference)):
        directory = ROOT / name
        schema = json.loads((directory / "schema.json").read_text())
        document = json.loads((directory / "cases.json").read_text())
        Draft202012Validator.check_schema(schema)
        # Check this invariant first, so incomplete resource queries name the case
        # and missing IDs instead of reporting a generic oneOf schema failure.
        if name == "reference":
            check(document)
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(document)
        if name == "core":
            check(document)
        ids = [case["id"] for case in document["cases"]]
        if len(ids) != len(set(ids)):
            fail(f"{name}: duplicate case IDs")
        print(f"{name}: {len(ids)} cases valid")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError) as error:
        print(f"Conformance validation failed: {error}", file=sys.stderr)
        sys.exit(1)
