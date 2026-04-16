# System Overview

## Architecture

`frontend (React + Vite)` → `backend (FastAPI)` → `embeddings + diversity computation`

### Frontend

- Manual entry mode for direct solution input
- Experiment upload mode for `results.json`
- Recursive extraction of `type="solution"` nodes in upload flow

### Backend

- `/api/analyze`: manual solutions or idea-tree payload
- `/api/analyze-experiment`: folder-based experiment processing
- `metrics/`: scoring + validation logic
- `utils/aideator_parser.py`: extraction and normalization for experiment trees

## Data Flow

1. Input arrives as manual `solutions` or tree payload
2. Solutions are normalized to `{title, description}`
3. Embeddings are computed (`all-MiniLM-L6-v2`)
4. Pairwise cosine distances are aggregated into one diversity score
5. Validation and metadata are attached to response

## Security/Robustness Controls

- Request schema validation with explicit error responses
- Standardized API error payload with request IDs
- Input size and solution-count limits
- CORS restricted by configurable origins
- Experiment folder access restricted by default to the configured base directory

## Defaults

- Frontend: `http://localhost:3008`
- Backend: `http://localhost:8005`
