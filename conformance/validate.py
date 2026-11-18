#!/usr/bin/env python3
"""Validate both portable suites and the invariants JSON Schema cannot express."""
import json
import sys
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
    capabilities = {item["id"]: item for item in binding["capabilities"]}
    if len(capabilities) != len(binding["capabilities"]):
        fail("core binding: duplicate capability IDs")
    resource_actions = set()
    for node in nodes:
        if node["parent"] is not None and node["parent"] not in by_id:
            fail(f"core binding: unknown parent for {node['id']}")
        if "valid_values" in node and node["kind"] != "ordinary_slot":
            fail(f"core binding: {node['id']} is not an ordinary slot")
        if "capability" in node:
            capability = capabilities.get(node["capability"])
            if not capability or node.get("safety") != capability["safety"]:
                fail(f"core binding: invalid capability or safety for {node['id']}")
        if node["kind"] == "resource_slot":
            if node["id"] not in binding["resources"]:
                fail(f"core binding: missing candidate list for {node['id']}")
            resource_actions.add(node["parent"])
    for slot, candidates in binding["resources"].items():
        if by_id.get(slot, {}).get("kind") != "resource_slot":
            fail(f"core binding: {slot} is not a resource slot")
        if len({candidate['id'] for candidate in candidates}) != len(candidates):
            fail(f"core binding: duplicate resources in {slot}")

    def event(case_id, item, required):
        path = item["recorded_path"]
        if not path or any(node not in by_id for node in path):
            fail(f"{case_id}: empty or unknown recorded path")
        if item.get("surface") and item["surface"] + "_surface" not in required:
            fail(f"{case_id}: recorded event needs its surface capability")
        if item["resource_selections"] and "resource_slots" not in required:
            fail(f"{case_id}: resource history needs resource_slots")
        feature_paths(case_id, path, required)
        for slot, identity in item["resource_selections"].items():
            ids = {candidate['id'] for candidate in binding['resources'].get(slot, [])}
            if slot not in path or identity not in ids:
                fail(f"{case_id}: invalid resource selection {slot}={identity}")

    def feature_paths(case_id, path, required):
        installed = set()
        for node_id in path:
            while node_id is not None and node_id not in installed:
                node = by_id.get(node_id)
                if not node:
                    fail(f"{case_id}: unknown node {node_id}")
                installed.add(node_id)
                node_id = node["parent"]
        if installed & resource_actions and "resource_slots" not in required:
            fail(f"{case_id}: installed action slots need resource_slots")

    for case in document["cases"]:
        case_id, required = case["id"], set(case["requires"])
        for surface in ("text", "structured"):
            if f"typed_resource_{surface}" in required and not {f"{surface}_surface", "resource_slots"} <= required:
                fail(f"{case_id}: typed_resource_{surface} needs its surface and resource_slots")
        if case["type"] == "interaction":
            index = {
                slot: {candidate["id"]: candidate["label"] for candidate in candidates}
                for slot, candidates in binding["resources"].items()
            }
            context = binding["context"]
            for action in case["actions"]:
                op = action["op"]
                if "path" in action:
                    feature_paths(case_id, action["path"], required)
                if op == "choose" and action["via"] == "promotion" and any(
                    by_id[node]["kind"] == "native" for node in action["path"]
                ) and "native_promotions" not in required:
                    fail(f"{case_id}: native promotion needs native_promotions")
                if op == "commit" and action["surface"] + "_surface" not in required:
                    fail(f"{case_id}: missing surface capability")
                if "context_after_start" in action:
                    if action["context_after_start"] == context:
                        fail(f"{case_id}: execution must change the context")
                    context = action["context_after_start"]
                if op in ("advance", "back") and "structured_surface" not in required:
                    fail(f"{case_id}: navigation needs structured_surface")
                if op in ("pick_resource", "type_resource", "remove_resource"):
                    feature_paths(case_id, [action["slot"]], required)
                    if action["slot"] not in index:
                        fail(f"{case_id}: operation requires a resource slot")
                    candidates = index[action["slot"]]
                    if op in ("pick_resource", "remove_resource") and action["id"] not in candidates:
                        fail(f"{case_id}: {action['id']} is not in the current fixture index")
                    if op == "remove_resource":
                        del candidates[action["id"]]
                if op == "type_resource":
                    surface = action["surface"]
                    if f"typed_resource_{surface}" not in required:
                        fail(f"{case_id}: typed resource needs typed_resource_{surface}")
                    if not any(a["op"] == "commit" and a["surface"] == surface for a in case["actions"]):
                        fail(f"{case_id}: typed resource has no commit on its surface")
                    matches = sorted(identity for identity, label in candidates.items() if label == action["text"])
                    if matches != sorted(action["matches"]):
                        fail(f"{case_id}: {action['text']!r} matches {matches}, expected {action['matches']}")
                if op == "ordinary_value":
                    feature_paths(case_id, [action["slot"]], required)
                    if by_id[action["slot"]]["kind"] != "ordinary_slot":
                        fail(f"{case_id}: ordinary value needs an ordinary slot")
            for item in case["expected"]["events"]:
                event(case_id, item, required)
            feature_paths(case_id, case["expected"]["executions"], required)
            for item in case["expected"].get("navigation", []):
                feature_paths(case_id, [item["current"], *item["choices"]], required)
            if len(case["expected"].get("navigation", [])) != sum(
                action["op"] in ("advance", "back") for action in case["actions"]
            ):
                fail(f"{case_id}: each navigation operation needs an observation")
            for item in case["expected"].get("resolutions", []):
                feature_paths(case_id, [item["target"]], required)
            if len(case["expected"].get("resolutions", [])) != sum(
                action["op"] == "resolve" for action in case["actions"]
            ):
                fail(f"{case_id}: each resolve operation needs an observation")
            for item in case["expected"].get("capabilities", []):
                if item != capabilities.get(item["id"]):
                    fail(f"{case_id}: unknown instrumented capability")
            for text in case["expected"].get("forbidden_text", []):
                if text in json.dumps(case["expected"]["events"], ensure_ascii=False):
                    fail(f"{case_id}: forbidden input appears in expected events")
        elif case["type"] == "consistency":
            for item in case["input"]["history"]:
                event(case_id, item, required)
            actual, expected = case["input"]["candidates"], case["expected"]["candidates"]
            feature_paths(case_id, actual, required)
            if case["input"]["mode"] == "surfaces" and not {"text_surface", "structured_surface"} <= required:
                fail(f"{case_id}: surface consistency needs both surface capabilities")
            if len(actual) != len(set(actual)) or set(actual) != set(expected):
                fail(f"{case_id}: inconsistent candidate sets")
        elif case["type"] == "edit":
            if "text_surface" not in required:
                fail(f"{case_id}: text edit needs text_surface")
            for value in (case["input"], case["expected"]):
                if "cursor" not in value:
                    continue
                data, cursor = value["line"].encode(), value["cursor"]
                if cursor > len(data):
                    fail(f"{case_id}: cursor outside line")
                try:
                    data[:cursor].decode()
                except UnicodeDecodeError:
                    fail(f"{case_id}: cursor splits a UTF-8 character")


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
