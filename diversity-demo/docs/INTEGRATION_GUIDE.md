# Integration Guide

## Base URL

Local default:

`http://localhost:8005`

## Endpoint 1: Manual solutions

`POST /api/analyze`

```json
{
  "solutions": [
    {
      "title": "Solution A",
      "description": "Detailed description for solution A."
    },
    {
      "title": "Solution B",
      "description": "Detailed description for solution B."
    }
  ],
  "mission": "optional",
  "goal": "optional"
}
```

## Endpoint 2: Idea-tree payload directly

`POST /api/analyze`

```json
{
  "tree": {
    "type": "mission",
    "achievers": [
      {
        "type": "solution",
        "name": "Lifecycle Co-optimization Design",
        "description": "Integrate recyclability in early design."
      }
    ]
  }
}
```

Alternative keys supported for tree mode:
- `idea_tree`
- `posts`

## Endpoint 3: Experiment folder analysis

`POST /api/analyze-experiment`

```json
{
  "folder_path": "experiments",
  "condition": 2,
  "domain": "kyoto_tourism"
}
```

By default, folder access is restricted to the configured experiments base directory.

## Python example

```python
import requests

payload = {
    "tree": idea_tree,  # experiment runner output
    "mission": mission,
    "goal": goal,
}

r = requests.post("http://localhost:8005/api/analyze", json=payload, timeout=120)
r.raise_for_status()
print(r.json()["diversity_score"])
```

## Error format

All API errors are normalized to:

```json
{
  "detail": "human-readable message",
  "error_code": "machine_code",
  "request_id": "trace_id"
}
```
