# Diversity Metrics System

A full-stack application to analyze and visualize diversity metrics for ideation solutions.

## Project Structure

```
diversity-demo/
├── backend/
│   ├── metrics/           # Core metric computations
│   │   ├── diversity_scorer.py    # Diversity = mean pairwise distance
│   │   ├── validator.py           # Quality checks
│   │   ├── io.py                  # Input/output schemas
│   │   └── compute_metrics.py     # Orchestration
│   ├── utils/
│   │   ├── embeddings.py          # Sentence-transformers wrapper
│   │   └── aideator_parser.py     # Extract solutions from Aideator JSON
│   ├── tests/                     # Unit tests
│   ├── api.py                     # FastAPI server
│   ├── requirements.txt
│   └── .env.example
├── frontend/              # React/TypeScript UI (Phase 2)
├── scripts/               # Utility scripts
└── README.md
```

## Quick Start

### 1. Setup Python Environment

```bash
# Install dependencies
bash scripts/setup.sh

# Or manually:
pip install -r backend/requirements.txt
```

### 2. Run Backend

```bash
bash scripts/start-backend.sh
```

Backend runs at `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Health check: `GET /health`

### 3. Run Tests

```bash
bash scripts/test-backend.sh
```

## API Endpoints

### POST `/api/analyze` - Manual Analysis

Analyze manually entered solutions.

**Request:**
```json
{
  "solutions": [
    {
      "title": "Solar Panel Installation",
      "description": "Install photovoltaic panels on building rooftops to generate renewable electricity"
    },
    {
      "title": "Wind Turbines",
      "description": "Deploy wind turbines in coastal areas to harness wind energy for power generation"
    }
  ],
  "mission": "Increase renewable energy capacity",
  "goal": "Reduce carbon emissions by 50%"
}
```

**Response:**
```json
{
  "diversity_score": 0.68,
  "solutions": [
    {
      "id": "uuid-1",
      "title": "Solar Panel Installation",
      "description": "...",
      "status": "valid"
    }
  ],
  "validation_report": {
    "valid": true,
    "warnings": [],
    "checks_passed": 4
  },
  "metadata": {
    "embeddings_model": "BAAI/bge-large-en-v1.5",
    "total_solutions": 2,
    "context_provided": {
      "mission": true,
      "goal": true
    }
  }
}
```

### POST `/api/analyze-experiment` - Aideator Experiment Analysis

Analyze solutions from an Aideator experiment folder (extracts from `results.json`).

**Request:**
```json
{
  "folder_path": "/path/to/experiment/20260414_010541_2_kyoto_tourism",
  "condition": 2,
  "domain": "kyoto_tourism"
}
```

**Response:** Same as `/api/analyze` but with experiment metadata

### GET `/health` - Health Check

```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

## Metrics Explained

### Diversity Score (0-1)

Measures semantic diversity via pairwise cosine distances.

**Formula:**
```
diversity = mean(cosine_distance(solution_i, solution_j) for all i < j)
```

- **0.0** = Solutions are identical
- **0.5** = Moderately different
- **1.0** = Maximally different (unrelated topics)

**Example:**
- "Solar panels" vs "Thermal heating" = ~0.25 (both energy)
- "Solar panels" vs "Underwater submarines" = ~0.95 (completely different)

## Implementation Details

### Embeddings

Uses `all-MiniLM-L6-v2` from sentence-transformers:
- Lightweight and fast
- 384-dimensional vectors
- Excellent semantic understanding

### Validation

All outputs are validated:
1. **Range check**: Score in [0, 1], is numeric, not NaN
2. **Spot-check**: Recompute and verify match (allows 1e-5 tolerance)
3. **Semantic check**: Identical solutions → ~0, different → ~1
4. **Formula check**: Verify embedding computation

## Testing

Run comprehensive unit tests:

```bash
bash scripts/test-backend.sh
```

**Test coverage:**
- ✅ Diversity scorer: 10+ test cases
- ✅ Aideator parser: 15+ test cases
- ✅ Validator: Integrated with metric tests
- ✅ API endpoints: Integration tests (Phase 2)

**Example test:**
```python
def test_two_identical_solutions(self):
    """Identical solutions should have diversity ~0."""
    solutions = ["same text", "same text"]
    diversity = compute_diversity(solutions)
    assert 0.0 <= diversity <= 0.15
```

## Real Data Integration

Works with Aideator experiment data:

**Example:** Kyoto Tourism Experiment
- **Folder**: `20260414_010541_2_kyoto_tourism`
- **Solutions**: 254 extracted from tree
- **Format**: Nested JSON with SOLUTION node types
- **Metadata**: Condition (0-3), Domain, Status

To analyze your experiments:

```bash
# Python script example
from backend.utils.aideator_parser import process_experiment_folder
from backend.metrics import compute_all_metrics
from backend.metrics.io import Solution

exp_data = process_experiment_folder(
    "/path/to/experiment/folder",
    condition=2,
    domain="kyoto_tourism"
)

solutions = [
    Solution(title=s["title"], description=s["description"])
    for s in exp_data["solutions"]
]

metrics = compute_all_metrics(solutions)
print(f"Diversity: {metrics.diversity_score:.3f}")
print(f"Diversity: {metrics.diversity_score:.3f}")
```

Or use the API:

```bash
curl -X POST http://localhost:8000/api/analyze-experiment \
  -H "Content-Type: application/json" \
  -d '{
    "folder_path": "/path/to/experiment/folder",
    "condition": 2,
    "domain": "kyoto_tourism"
  }'
```

## Frontend (Phase 2)

React/TypeScript frontend with:
- Manual solution entry form
- Aideator experiment file upload
- Diversity visualization
- Results table with metrics
- Design: Academic Logic palette (#4C7C9D primary, #B87987 secondary, #6F749E tertiary)

## Performance Notes

- **Embeddings**: First load ~30-60s (downloads BAAI model), subsequent calls ~100-500ms for 10 solutions
- **Diversity computation**: O(N²) for N solutions
- **Large experiments**: 254 solutions take ~2-3 seconds end-to-end

## Future Enhancements

- [ ] Batch processing (multiple experiments)
- [ ] LLM-based alignment scoring (GPT-4)
- [ ] CSV/JSON export
- [ ] Statistical comparison across conditions
- [ ] Dark mode UI
- [ ] Docker deployment
- [ ] Database persistence

## Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
BACKEND_URL=http://localhost:8000
EMBEDDINGS_MODEL=BAAI/bge-large-en-v1.5
DEBUG=True
```

## Dependencies

- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **sentence-transformers** - Embeddings
- **scikit-learn** - Cosine distance
- **pydantic** - Data validation
- **pytest** - Testing

See `backend/requirements.txt` for full list.

## License

Standalone project - no external dependencies on other folders.

## Quick Reference

| Metric | Range | Meaning | Formula |
|--------|-------|---------|---------|
| **Diversity** | [0, 1] | How different are solutions? | Mean pairwise cosine distance |


---

**Questions?** Check API docs at `/docs` when backend is running.
