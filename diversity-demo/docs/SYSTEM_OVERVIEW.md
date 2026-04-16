# Diversity Metrics System - Complete Overview

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React/Vite)                    │
│                    http://localhost:3005                      │
│  - Manual solution entry form                                │
│  - Experiment folder upload                                  │
│  - Results popup modal with metrics display                  │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP POST (JSON)
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   BACKEND API (FastAPI)                      │
│                    http://localhost:8004                      │
│                                                                │
│  POST /api/analyze                                           │
│  └─ Input: solutions list + mission/goal                    │
  └─ Output: diversity score                                 │
                                                                │
  POST /api/analyze-experiment                               │
  └─ Input: experiment folder path                           │
  └─ Output: diversity score                                 │
│                                                                │
│  GET /health                                                 │
│  └─ Status check                                             │
└────────────────────────┬────────────────────────────────────┘
                         │
            ┌────────────┴────────────┐
            │                         │
    ┌───────▼────────┐      ┌────────▼──────────┐
    │  EMBEDDINGS    │      │  METRICS COMPUTE  │
    │  all-MiniLM    │      │                   │
    │  (384-dim)     │      │  - Diversity      │
    │                │      │                   │
    │  Fast, light   │      │  - Validation     │
    └────────────────┘      └───────────────────┘
```

---

## 2. Frontend (React + TypeScript)

### Path: `/diversity-demo/frontend/`

### Components:

**App.tsx** - Main orchestrator
- Manages tabs (Manual Entry / Experiment Folder)
- Handles form submissions
- Shows results modal on analysis complete
- Manages loading state and errors

**ManualForm.tsx** - Solution input form
- Accept mission and goal (optional context)
- Add/remove solutions dynamically
- Validates: minimum 2 solutions, title ≥2 chars, description ≥10 chars
- Submit to `/api/analyze`

**ExperimentForm.tsx** - Experiment folder upload
- Select folder from Aideator experiments
- Choose domain (renewable_energy, kyoto_tourism, um6p_university)
- Choose condition (0-3)
- Submit to `/api/analyze-experiment`

**ResultsModal.tsx** - Popup display (appears after analysis)
- Shows diversity score with progress bar
- Validation status
- Solutions analyzed list
- Download buttons (JSON, CSV)

### How It Works:
1. User enters solutions
2. Clicks "Analyze"
3. Frontend makes POST request to backend API
4. Backend computes metrics (0.5-1 second)
5. Results popup appears with metrics
6. User can download or close

---

## 3. Backend (FastAPI + Python)

### Path: `/diversity-demo/backend/`

### Core Modules:

#### **metrics/diversity_scorer.py**
```python
def compute_diversity(solutions, context="") -> float:
    """
    Calculate how different solutions are from each other.
    
    Process:
    1. Embed each solution (convert text → 384-dim vector)
    2. Compute pairwise cosine distances
    3. Return mean distance (0=identical, 1=completely different)
    
    Returns: float 0-1
    """
```

**Key Logic:**
- Uses sentence-transformer embeddings (all-MiniLM-L6-v2)
- Treats embedding space as semantic similarity
- Distance = 1 - cosine_similarity
- Mean of all pairwise distances

**Examples:**
- "Solar panels on roofs" + "Wind turbines offshore" = ~0.25 (similar domain)
- "Solar energy" + "Smart consumption reduction" = ~0.55 (different domains)

#### **metrics/validator.py**
- Checks all scores are 0-1
- No NaN/infinity values
- Valid solution counts
- Consistency checks
- Returns 8-point validation report

#### **utils/embeddings.py**
```python
class EmbedderEngine:
    """Lazy-loads sentence-transformer model."""
    - Model: all-MiniLM-L6-v2 (22MB, fast)
    - Loads once, reused for all requests
    - Returns 384-dimensional vectors
```

#### **utils/aideator_parser.py**
- Reads Aideator experiment JSON
- Extracts solution nodes
- Handles both raw tree format and pre-extracted solutions
- Parses domain/condition from folder names

---

## 4. API Endpoints

### Endpoint 1: Manual Analysis

```
POST http://localhost:8004/api/analyze

Input (JSON):
{
  "solutions": [
    {
      "title": "Solar Panels on Roofs",
      "description": "Install photovoltaic panels to generate..."
    },
    {
      "title": "Wind Turbines",
      "description": "Build coastal wind farms..."
    }
  ],
  "mission": "renewable energy",      // optional
  "goal": "reduce carbon emissions"   // optional
}

Output (JSON):
{
  "diversity_score": 0.249,
  "solutions": [
    {
      "id": "sol_1",
      "title": "Solar Panels on Roofs",
      "description": "...",
      "status": "valid"
    },
    {
      "id": "sol_2",
      "title": "Wind Turbines",
      "status": "valid"
    }
  ],
  "validation_report": {
    "valid": true,
    "checks_passed": 8,
    "warnings": [],
    "details": {...}
  },
  "metadata": {
    "solutions_count": 2,
    "mission": "renewable energy",
    "goal": "reduce carbon emissions"
  }
}
```

### Endpoint 2: Experiment Analysis

```
POST http://localhost:8004/api/analyze-experiment

Input (JSON):
{
  "folder_path": "/home/sobouric/Desktop/Diversity_metrics/aideator-python-minimal-main/experiments/all_domains_0/",
  "condition": 0,
  "domain": "renewable_energy"
}

Returns: Same MetricsResponse as Endpoint 1
```

### Endpoint 3: Health Check

```
GET http://localhost:8004/health

Output:
{
  "status": "ok",
  "version": "1.0.0"
}
```

---

## 5. Data Flow

### Manual Entry Flow:

```
USER INPUT
    ↓
Frontend Form (mission, goal, solutions)
    ↓
POST /api/analyze
    ↓
Backend: compute_all_metrics()
    ├─ Load embeddings model
    ├─ Embed all solutions (with context)
    ├─ Compute diversity (pairwise distances)
    ├─ Validate results
    └─ Return MetricsResponse
    ↓
Results Modal Popup
    ├─ Display scores
    ├─ Show validation status
    ├─ Table with per-solution metrics
    └─ Download buttons
```

### Experiment Folder Flow:

```
USER UPLOADS EXPERIMENT FOLDER
    ↓
aideator_parser.process_experiment_folder()
    ├─ Read results.json
    ├─ Extract solutions
    ├─ Parse domain/condition from path
    └─ Return cleaned solution list
    ↓
compute_all_metrics()
    └─ Same as manual flow
    ↓
Results Modal
```

---

## 6. Future Integration with Aideator

### How Aarya's Team Will Use It:

#### Option A: API Calls (Recommended)

```python
# In experiment_runner.py, after solutions are generated:

import requests

tree, solutions = run_creative_pipeline(mission, desc)

# Prepare solutions for API
solutions_for_api = [
    {"title": sol.name, "description": sol.description}
    for sol in solutions
]

# Call metrics API
response = requests.post(
    'http://localhost:8004/api/analyze',
    json={
        "solutions": solutions_for_api,
        "mission": mission,
        "goal": desc
    }
)

metrics = response.json()

# Store in results
results['diversity_score'] = metrics['diversity_score']

# Display in web_app.py metrics tab
```

📖 **See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) for complete integration examples.**

#### Option B: Direct Import

```python
# Copy diversity_scorer.py to Aideator codebase
from diversity_metrics import compute_diversity

score = compute_diversity(solutions)
# No network calls, instant
```

---

## 7. Technical Details

### Models & Libraries:

| Component | Library | Size | Speed | Purpose |
|-----------|---------|------|-------|---------|
| Embeddings | sentence-transformers | 22MB | Fast | Convert text to vectors |
| Model | all-MiniLM-L6-v2 | 384-dim | 0.3s for 10 sols | Semantic understanding |
| API | FastAPI | Lightweight | <1ms | HTTP server |
| Frontend | React + Vite | Minimal | Instant | UI |
| Similarity | scikit-learn | cosine_distances | <10ms | Pairwise distances |

### Performance:

- **First request**: ~8-10 seconds (model download + analysis)
- **Subsequent requests**: ~0.5-1 second (model cached)
- **Bottleneck**: Model loading (one-time cost)
- **Optimization**: Model loads on backend startup, stays loaded

### Diversity Score Ranges:

```
Diversity Score: 0-1
  0.0-0.2 = Nearly identical solutions
  0.2-0.4 = Similar core ideas, different context
  0.4-0.6 = Mixed similarities and differences
  0.6-0.8 = Quite different approaches
  0.8-1.0 = Completely different domains
```

---

## 8. Validation System

Every analysis runs 8 checks:

1. **Score range validation** - All scores are 0-1
2. **NaN/Infinity checks** - No invalid numbers
3. **Solution count check** - Minimum 2 solutions
4. **Solution completeness** - All fields present
5. **Data type validation** - Correct types
6. **Reasonableness check** - Scores make sense
7. **Consistency check** - Per-solution metrics reasonable
8. **Metadata completeness** - All metadata present

---

## 9. File Structure

```
diversity-demo/
├── backend/
│   ├── metrics/
│   │   ├── diversity_scorer.py     # Core diversity calculation
│   │   ├── validator.py            # Validation logic
│   │   ├── compute_metrics.py      # Orchestration
│   │   └── io.py                   # Pydantic models
│   ├── utils/
│   │   ├── embeddings.py           # Sentence-transformer wrapper
│   │   ├── aideator_parser.py      # Aideator data parsing
│   │   └── __init__.py
│   ├── tests/
│   │   └── test_aideator_parser.py # 14 passing tests
│   ├── api.py                      # FastAPI server
│   ├── requirements.txt            # Dependencies
│   └── __init__.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ManualForm.tsx      # Solution input
│   │   │   ├── ExperimentForm.tsx  # Folder upload
│   │   │   ├── ResultsModal.tsx    # Results popup
│   │   │   ├── Form.css
│   │   │   └── ResultsModal.css
│   │   ├── App.tsx                 # Main app
│   │   ├── App.css
│   │   ├── api.ts                  # API client
│   │   └── main.tsx
│   ├── vite.config.ts              # Proxy to backend
│   ├── package.json
│   ├── tsconfig.json
│   └── index.html
│
├── start.sh                        # Start both servers
├── stop.sh                         # Stop both servers
├── METRICS_EXPLAINED.md            # Documentation
├── README.md
└── requirements.txt
```

---

## 10. How to Brief an AI Agent

**Summary for handoff:**

> "We built a metrics system that measures solution diversity. It has a React frontend where users enter solutions, and a FastAPI backend that embeds solutions using sentence-transformers, computes pairwise distances for diversity analysis. The system runs locally (ports 3005 frontend, 8004 backend), takes 0.5-1 second per analysis, and outputs diversity scores. It can be integrated into Aideator via API calls or direct imports. Aarya's team can either call the `/api/analyze` endpoint with solutions after running their experiment pipeline, or copy the diversity_scorer directly into their code. The system is fully standalone (100% self-contained), production-ready, and documented."

---

## 11. Setup & Running

```bash
# Start everything
cd /home/sobouric/Desktop/Diversity_metrics/diversity-demo
./start.sh

# Frontend: http://localhost:3005
# Backend: http://localhost:8004
# API docs: http://localhost:8004/docs

# Stop everything
./stop.sh
```

---

## 12. Next Steps for Aarya's Team

**👉 Read [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) first** — it has:
- ✅ Step-by-step integration instructions
- ✅ Copy-paste code examples
- ✅ All three integration options (API, experiments, direct import)
- ✅ Exactly what data format to use

Then:
1. **Review the API** at `http://localhost:8004/docs` (Swagger)
2. **Test the metrics** with sample solutions at frontend
3. **Choose integration** from INTEGRATION_GUIDE.md
4. **Call `/api/analyze`** with solutions
5. **Extract `diversity_score`** from response

---

## Summary Table

| Aspect | Details |
|--------|---------|
| **What it does** | Measures semantic diversity of solutions |
| **Input** | List of solutions (title + description) |
| **Output** | Diversity score (0-1) + validation report |
| **Speed** | 0.5-1 second (after first load) |
| **Model** | all-MiniLM-L6-v2 (384-dimensional embeddings) |
| **Deployment** | Standalone, local, no external APIs required |
| **Integration** | REST API or direct Python imports |
| **Interface** | React web UI + API swagger docs |
| **Status** | Production-ready, diversity-only (accurate) |
