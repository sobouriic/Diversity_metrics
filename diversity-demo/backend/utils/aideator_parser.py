
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


def _normalize_text(value: Any) -> str:
    """Convert arbitrary values to clean display text."""
    if value is None:
        return ""

    if isinstance(value, str):
        return value.strip()

    if isinstance(value, (dict, list)):
        try:
            return json.dumps(value, ensure_ascii=False).strip()
        except TypeError:
            return str(value).strip()

    return str(value).strip()


def _dedupe_solutions(solutions: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Remove duplicate solutions while preserving order."""
    seen: Set[Tuple[str, str, str]] = set()
    deduped: List[Dict[str, str]] = []

    for solution in solutions:
        key = (
            solution.get("id", "").strip(),
            solution.get("title", "").strip().lower(),
            solution.get("description", "").strip().lower(),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(solution)

    return deduped


def _extract_preparsed_solutions(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Parse top-level `solutions` list when already present.

    Supports entries with either `title` or `name`.
    """
    parsed: List[Dict[str, str]] = []
    for index, item in enumerate(payload.get("solutions", [])):
        if not isinstance(item, dict):
            continue

        title = _normalize_text(item.get("title") or item.get("name"))
        description = _normalize_text(item.get("description"))
        solution_id = _normalize_text(item.get("id")) or f"solution_{index + 1}"

        if not title:
            title = f"Solution {index + 1}"
        if not description:
            description = "No description"

        parsed.append(
            {
                "id": solution_id,
                "title": title,
                "description": description,
            }
        )

    return parsed


def extract_solutions_from_tree(tree_root: Any) -> List[Dict[str, str]]:
    """
    Recursively extract nodes where `type == "solution"` from any tree-like payload.
    """
    solutions: List[Dict[str, str]] = []

    def traverse(node: Any) -> None:
        if isinstance(node, list):
            for item in node:
                traverse(item)
            return

        if not isinstance(node, dict):
            return

        node_type = _normalize_text(node.get("type")).lower()
        if node_type == "solution":
            title = _normalize_text(node.get("name") or node.get("title"))
            description = _normalize_text(node.get("description"))
            solution_id = _normalize_text(node.get("id")) or f"solution_{len(solutions) + 1}"

            if not title:
                title = f"Solution {len(solutions) + 1}"

            if not description:
                achievers = node.get("achievers")
                if isinstance(achievers, list) and achievers:
                    description = _normalize_text(achievers)
            if not description:
                description = "No description"

            solutions.append(
                {
                    "id": solution_id,
                    "title": title,
                    "description": description,
                }
            )

        # Traverse all nested dict/list values to support multiple shapes.
        for value in node.values():
            if isinstance(value, (dict, list)):
                traverse(value)

    traverse(tree_root)
    return _dedupe_solutions(solutions)


def extract_solutions_from_experiment_payload(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Extract solutions from experiment-runner style payloads.

    This supports:
    - `{ "solutions": [...] }`
    - `{ "tree": {...} }`
    - `{ "posts": [...] }`
    - direct tree payloads
    """
    if not isinstance(payload, dict):
        return []

    solutions: List[Dict[str, str]] = []

    if isinstance(payload.get("solutions"), list):
        solutions.extend(_extract_preparsed_solutions(payload))

    for key in ("tree", "idea_tree", "posts"):
        if key in payload:
            solutions.extend(extract_solutions_from_tree(payload[key]))

    if not solutions:
        solutions.extend(extract_solutions_from_tree(payload))

    return _dedupe_solutions(solutions)


def load_experiment_results(folder_path: str) -> Dict[str, Any]:
    """Load `results.json` (and optional `status.json`) from experiment folder."""
    folder = Path(folder_path)
    results_file = folder / "results.json"
    status_file = folder / "status.json"

    if not results_file.exists():
        raise FileNotFoundError(f"results.json not found in {folder_path}")

    with open(results_file, "r", encoding="utf-8") as f:
        results = json.load(f)

    if not isinstance(results, dict):
        raise ValueError("results.json must be a JSON object")

    solutions = extract_solutions_from_experiment_payload(results)

    metadata: Dict[str, Any] = {}
    if status_file.exists():
        with open(status_file, "r", encoding="utf-8") as f:
            status = json.load(f)
            metadata = {
                "status": status.get("state", "unknown"),
                "nodes_generated": status.get("nodes_generated", 0),
                "total_solutions": status.get("total_solutions", len(solutions)),
                "timestamp": status.get("timestamp"),
            }

    metadata["solution_count"] = len(solutions)

    return {
        "solutions": solutions,
        "metadata": metadata,
    }


def process_experiment_folder(
    folder_path: str,
    condition: Optional[int] = None,
    domain: Optional[str] = None,
) -> Dict[str, Any]:
    """Process experiment folder and enrich metadata with condition/domain."""
    result = load_experiment_results(folder_path)

    if condition is not None:
        result["metadata"]["condition"] = condition
    if domain is not None:
        result["metadata"]["domain"] = domain

    folder_name = Path(folder_path).name
    try:
        parts = folder_name.split("_")
        for i, part in enumerate(parts):
            if part.isdigit() and 0 <= int(part) <= 3 and i > 1:
                parsed_condition = int(part)
                parsed_domain = "_".join(parts[i + 1 :]) if i + 1 < len(parts) else None

                if condition is None:
                    result["metadata"]["condition"] = parsed_condition
                if domain is None and parsed_domain:
                    result["metadata"]["domain"] = parsed_domain
                break
    except (ValueError, IndexError):
        # Folder name parsing is optional.
        pass

    return result


def validate_solution_format(solution: Dict[str, str]) -> bool:
    """Validate required structure for a normalized solution record."""
    title = solution.get("title")
    description = solution.get("description")
    return (
        isinstance(title, str)
        and isinstance(description, str)
        and bool(title.strip())
        and bool(description.strip())
    )
