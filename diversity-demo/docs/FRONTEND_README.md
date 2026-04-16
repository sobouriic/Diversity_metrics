# Diversity Metrics

A complete system for analyzing diversity of ideation solutions using AI embeddings.

## Features

- **Two Analysis Modes**:
  - Manual entry: Submit solutions directly in the UI
  - Experiment folder: Analyze Aideator experiment results
  
- **Metrics**:
  - **Diversity Score** (0-1): Semantic difference between solutions

- **Professional UI**: Clean, minimal interface with real-time metrics display

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 16+ (for frontend)

### Option 1: Run Both Servers (Recommended)

**Linux/Mac:**
```bash
cd diversity-demo
chmod +x start.sh
./start.sh
```

**Windows:**
```bash
cd diversity-demo
start.bat
```

This will automatically:
- Create Python virtual environment
- Install backend dependencies
- Install frontend dependencies
- Start backend on **port 8004**
- Start frontend on **port 3005**

Then open: **http://localhost:3005**

### Option 2: Run Manually

**Backend:**
```bash
cd diversity-demo
python -m venv venv
source venv/bin/activate  
pip install -r backend/requirements.txt
python -m uvicorn backend.api:app --host 0.0.0.0 --port 8004
```

**Frontend (in new terminal):**
```bash
cd diversity-demo/frontend
npm install
npm run dev  # Runs on port 3005
```

## API Reference

### Analyze Manual Solutions
```
POST http://localhost:8004/api/analyze

{
  "solutions": [
    {"title": "Solution 1", "description": "Description..."},
    {"title": "Solution 2", "description": "Description..."}
  ],
  "mission": "Optional mission context",
  "goal": "Optional goal context"
}
```

### Analyze Experiment Folder
```
POST http://localhost:8004/api/analyze-experiment

{
  "folder_path": "/path/to/experiment",
  "condition": 0,
  "domain": "kyoto_tourism"
}
```

## Architecture

```
diversity-demo/
├── backend/
│   ├── metrics/          # Scoring logic
│   ├── utils/            # Parsers & embeddings
│   ├── tests/            # Unit tests
│   ├── api.py            # FastAPI server
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── App.tsx       # Main app
│   │   └── api.ts        # Backend client
│   ├── package.json
│   └── vite.config.ts
├── start.sh              # Linux/Mac startup
└── start.bat             # Windows startup
```

## Ports

- **Frontend**: http://localhost:3005
- **Backend API**: http://localhost:8004
- **API Docs**: http://localhost:8004/docs (Swagger UI)

## Metrics Explanation

### Diversity Score
Measures semantic difference between solutions using cosine distance:
- 0.0 = All solutions identical
- 0.5 = Medium diversity
- 1.0 = Completely different

## Validation

All results include validation checks:
- Scores in valid range [0, 1]
- No NaN or infinity values
- Spot-check calculations
- Formula consistency

## Troubleshooting

**Port already in use?**
```bash
# Kill process on specific port
lsof -ti:8004 | xargs kill -9   # Port 8004
lsof -ti:3005 | xargs kill -9   # Port 3005
```

**Dependencies issues?**
```bash
cd diversity-demo
rm -rf venv frontend/node_modules
./start.sh  # Will reinstall everything
```

**Backend not responding?**
Check http://localhost:8004/health for API status

## Performance

- 5 solutions: ~10-15 seconds
- 50 solutions: ~30-45 seconds
- 254 solutions: ~2-3 minutes

Process time depends on solution text length and hardware.

## License

See LICENSE file
