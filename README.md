# Diversity Metrics System

A full-stack tool to compute semantic diversity across ideation solutions.

## Quick Start (Local)

```bash
cd diversity-demo
./scripts/start.sh
```

Default local endpoints:
- Frontend: `http://localhost:3008`
- Backend: `http://localhost:8005`
- API docs: `http://localhost:8005/docs`

## Server Mode (Background)

```bash
cd diversity-demo
./scripts/start-server.sh [PUBLIC_HOST]
```

No server IP is hardcoded in the repository. Set host/ports at runtime using
arguments or environment variables (`PUBLIC_HOST`, `BACKEND_PORT`, `FRONTEND_PORT`).

Stop commands:
- Local: `./scripts/stop.sh`
- Server: `./scripts/stop-server.sh`

## Main Features

- Diversity score (0 to 1) using semantic embeddings
- Manual solution analysis via `/api/analyze`
- Experiment-tree extraction of `type="solution"` nodes
- Robust JSON validation with standardized error responses

## Documentation

- Project docs index: [`diversity-demo/docs/README.md`](diversity-demo/docs/README.md)
- Metrics and embedding internals: [`diversity-demo/docs/METRICS_CALCULATION_AND_EMBEDDINGS.md`](diversity-demo/docs/METRICS_CALCULATION_AND_EMBEDDINGS.md)

## License

MIT (see `LICENSE`)
