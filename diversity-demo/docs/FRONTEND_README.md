# Frontend Guide

## Run

Use project scripts from `diversity-demo/`:

```bash
./scripts/start.sh
```

Default frontend URL: `http://localhost:3008`

## Tabs

- `Manual Entry`: enter solution title + description directly
- `Experiment Folder`: upload one or more `results.json` files

## Experiment JSON behavior

The uploader supports both formats:
- top-level `solutions` array
- idea-tree outputs (extracts recursive nodes where `type="solution"`)

If a file has no solution nodes, the UI shows a validation error toast.

## API base URL behavior

Frontend reads:
- `VITE_API_BASE` if provided
- fallback: `http://localhost:8005/api`

## Build

```bash
cd frontend
npm run build
```
