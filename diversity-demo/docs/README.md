# Documentation Index

## Run Modes

- Local development: `./scripts/start.sh`
- Server background mode: `./scripts/start-server.sh [PUBLIC_HOST]`

Defaults:
- Frontend: `http://localhost:3008`
- Backend: `http://localhost:8005`

## Core Docs

- [`SYSTEM_OVERVIEW.md`](./SYSTEM_OVERVIEW.md): architecture and module map
- [`METRICS_EXPLAINED.md`](./METRICS_EXPLAINED.md): quick interpretation guide
- [`METRICS_CALCULATION_AND_EMBEDDINGS.md`](./METRICS_CALCULATION_AND_EMBEDDINGS.md): detailed math and embedding pipeline
- [`INTEGRATION_GUIDE.md`](./INTEGRATION_GUIDE.md): API payload examples and integration patterns
- [`FRONTEND_README.md`](./FRONTEND_README.md): frontend behavior and upload workflow

## Security Notes

- No server IP is committed in scripts.
- API request validation returns standardized JSON errors with request IDs.
- Experiment folder analysis is path-restricted by default to the project `experiments/` directory.

## Performance Tuning

For faster runtime on larger batches:

- `EMBEDDING_BATCH_SIZE=96` (or `128`) to increase embedding throughput
- `VALIDATION_SPOTCHECK_SIZE=12` to keep validation light on large inputs

For faster server restarts:

- `SKIP_FRONTEND_BUILD=1 ./scripts/start-server.sh` to skip frontend rebuild
- `UVICORN_WORKERS=2 ./scripts/start-server.sh` for higher API throughput on multi-core machines
