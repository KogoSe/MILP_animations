"""Loads the real toy_solve_log.json (produced by hac_project/toy_solver.py)
and reconstructs the branch-and-bound tree structure from it. Every number
the scene displays comes from this file — nothing here is fabricated.
"""
import json
from pathlib import Path

TOY_LOG_PATH = Path(__file__).parent / "toy_solve_log.json"


def load_toy_log():
    with open(TOY_LOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def build_tree(data):
    """Rebuild parent/child links from the flat pre-order log using depth
    (= number of rows already assigned in that entry's assignment dict).
    Returns (nodes, children) where nodes[i] is a dict for log entry i and
    children[node_id] is the list of its direct child node ids."""
    log = data["log"]
    nodes = []
    stack = {}
    children = {}
    for i, entry in enumerate(log):
        depth = len(entry["assignment"])
        node = {
            "id": i,
            "step": entry["step"],
            "depth": depth,
            "assignment": entry["assignment"],
            "bound": entry["bound"],
            "action": entry["action"],
            "best_value_so_far": entry["best_value_so_far"],
            "parent_id": None,
        }
        if depth > 0:
            parent_id = stack[depth - 1]
            node["parent_id"] = parent_id
            children.setdefault(parent_id, []).append(i)
        stack[depth] = i
        nodes.append(node)
    return nodes, children


def last_pair(assignment: dict):
    """The pair chosen at the row decided most recently (the edge label
    into this node), given assignment is built by inserting keys in order."""
    if not assignment:
        return None
    return list(assignment.values())[-1]
