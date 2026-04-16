# How to Use the Diversity Metrics API


The API is **fully portable** with no hardcoded paths or assumptions. Here's exactly what someone needs to do:

---

## 🚀 OPTION 1: Use the REST API (Recommended for Aideator Integration)

### Step 1: Start the API Server

```bash
cd /Diversity_metrics/diversity-demo
./start.sh
```

- Backend runs on: `http://localhost:8004`
- Frontend runs on: `http://localhost:3005`
- Takes ~8-10 seconds first time (model download), then ~0.5-1 second per analysis

### Step 2: Make HTTP POST Request

**From anywhere in  code** (experiment runner, web app, etc.):

```python
import requests

solutions = [
    {
        "title": "Solution Name 1",
        "description": "Full description of how this solves the problem..."
    },
    {
        "title": "Solution Name 2",
        "description": "Another solution approach..."
    }
]

response = requests.post(
    'http://localhost:8004/api/analyze',
    json={
        "solutions": solutions,
        "mission": "your mission context (optional)",  # Can be None
        "goal": "your goal context (optional)"          # Can be None
    }
)

# Get the results
metrics = response.json()
diversity_score = metrics['diversity_score']

print(f"Diversity Score: {diversity_score}")
```

---

## 🎯 OPTION 2: Use with Aideator Experiments (For Experiment Folders)

If you have an **Aideator experiment folder** with `results.json`:

```python
import requests

# Load your own experiment or use Aideator's path
response = requests.post(
    'http://localhost:8004/api/analyze-experiment',
    json={
        "folder_path": "/path/to/your/aideator/experiment/folder",
        "condition": 0,  # 0-3
        "domain": "renewable_energy"  # or "kyoto_tourism" or "um6p_university"
    }
)

metrics = response.json()
diversity_score = metrics['diversity_score']
```

**The parser automatically extracts solutions** from:
- ✅ `results.json` (any Aideator format)
- ✅ Nested tree structures
- ✅ Pre-extracted solution lists
- ✅ Any folder structure with `results.json`

---

## OPTION 3: Direct Python Import (No Network Call)

Copy `diversity_scorer.py` to your Aideator codebase:

```python
from diversity_metrics import compute_diversity

solutions = [
    "Solar panels on roofs",
    "Wind turbines offshore",
    "Geothermal energy systems"
]

# Instant computation (no API call)
diversity_score = compute_diversity(solutions)

print(f"Diversity: {diversity_score}")
```

**Pros:**
- ✅ No network call (instant)
- ✅ No server needed
- ✅ Direct import

**Cons:**
- ✗ Need sentence-transformers installed
- ✗ First call downloads model (~22MB)

---

## ❓ WILL IT WORK WITH EXPERIMENT RUNNER?


```python

from aideator.pipeline import run_creative_pipeline
import requests

# Run your Aideator pipeline
mission = "Reduce carbon emissions"
description = "How can we achieve renewable energy adoption?"

tree, solutions = run_creative_pipeline(mission, description)

# Prepare solutions for API
solutions_payload = [
    {
        "title": sol.name,
        "description": sol.description
    }
    for sol in solutions
]

# Call diversity metrics API
response = requests.post(
    'http://localhost:8004/api/analyze',
    json={
        "solutions": solutions_payload,
        "mission": mission,
        "goal": description
    }
)

metrics = response.json()

# Store in your results
results['diversity_score'] = metrics['diversity_score']
results['validation'] = metrics['validation_report']

```

---

## ❓ WILL IT WORK WITH IDEA TREE?

**YES** — The parser handles tree structures automatically:

```python

tree_data = {
    "type": "problem",
    "name": "Main Problem",
    "children": [
        {
            "type": "solution",
            "name": "Solution 1",
            "description": "..."
        },
        {
            "type": "solution",
            "name": "Solution 2",
            "description": "..."
        }
    ]
}

# Send to API with custom payload
solutions = extract_solutions_from_tree(tree_data)  # Helper function in parser

response = requests.post(
    'http://localhost:8004/api/analyze',
    json={
        "solutions": [
            {
                "title": sol["name"],
                "description": sol["description"]
            }
            for sol in solutions
        ]
    }
)
```

---

## ✅ CHECKLIST: What You Need to Do

- [ ] **Start the server**: `./start.sh`
- [ ] **Have solutions** (as title + description strings)
- [ ] **Make POST request** to `/api/analyze` with JSON payload
- [ ] **Parse the response** and extract `diversity_score`


---

---

---

## 📊 Response Format (What You Get Back)

```json
{
  "diversity_score": 0.675,
  "solutions": [
    {
      "id": "sol_1",
      "title": "Solar panels on rooftops",
      "description": "...",
      "status": "valid"
    },
    {
      "id": "sol_2",
      "title": "Wind turbines offshore",
      "description": "...",
      "status": "valid"
    }
  ],
  "validation_report": {
    "valid": true,
    "checks_passed": 4,
    "warnings": [],
    "details": {...}
  },
  "metadata": {
    "embeddings_model": "all-MiniLM-L6-v2",
    "total_solutions": 2,
    "context_provided": {
      "mission": true,
      "goal": true
    }
  }
}
```

Extract just the `diversity_score` and you're done.

---

## 🎯 Quick Start (Copy-Paste)

```python
import requests

# Your solutions
solutions = [
    {"title": "Idea 1", "description": "Details about idea 1"},
    {"title": "Idea 2", "description": "Details about idea 2"},
    {"title": "Idea 3", "description": "Details about idea 3"},
]

# Call API
r = requests.post('http://localhost:8004/api/analyze', json={"solutions": solutions})

# Get score
diversity = r.json()['diversity_score']
print(f"Diversity: {diversity:.2f}")
```

---

---

## Summary

**To use the API as Aarya's team:**

1. ✅ **Option A (Easiest)**: Start server, POST to `/api/analyze` with solutions
2. ✅ **Option B (For experiments)**: POST to `/api/analyze-experiment` with folder path
3. ✅ **Option C (Offline)**: Import `compute_diversity` directly


