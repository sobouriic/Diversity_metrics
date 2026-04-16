# Diversity Metrics System

A comprehensive system for measuring and analyzing solution diversity across various domains. This project provides both a React frontend and a FastAPI backend for analyzing how different solutions are from each other using semantic embeddings and cosine distance metrics.

## Project Structure

```
Diversity_metrics/
├── diversity-demo/          # Main project directory
│   ├── frontend/            # React + TypeScript frontend
│   ├── backend/             # FastAPI backend
│   ├── docs/                # System documentation
│   ├── experiments/         # Sample experiment data
│   ├── scripts/             # Utility scripts (start.sh, stop.sh)
│   └── venv/                # Python virtual environment
├── LICENSE                  # MIT License
└── README.md               # This file
```

## Quick Start

Navigate to the main project and start the system:

```bash
cd diversity-demo
./scripts/start.sh
```

This will:
- Start the FastAPI backend on **http://localhost:8004**
- Start the React frontend on **http://localhost:3005**

## Features

- **Diversity Scoring**: Calculates how different solutions are from each other (0-1 scale)
- **Semantic Analysis**: Uses sentence-transformers for intelligent solution comparison
- **Web Interface**: User-friendly React frontend for manual analysis
- **REST API**: FastAPI endpoints for programmatic access
- **Experiment Support**: Analyze solutions from Aideator experiment files
- **Results Export**: Download metrics in JSON or CSV format

## Usage

### Web Interface
Open http://localhost:3005 in your browser to:
- Enter solutions manually
- Upload experiment files
- View diversity scores and analysis

### API
Send POST requests to `/api/analyze`:
```bash
curl -X POST http://localhost:8004/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "solutions": [
      {
        "title": "Solution 1",
        "description": "Description of solution 1"
      },
      {
        "title": "Solution 2", 
        "description": "Description of solution 2"
      }
    ],
    "mission": "Optional mission context"
  }'
```

## Documentation

For detailed information, see [diversity-demo/docs/README.md](diversity-demo/docs/README.md)

Key documentation files:
- [SYSTEM_OVERVIEW.md](diversity-demo/docs/SYSTEM_OVERVIEW.md) - Architecture and components
- [METRICS_EXPLAINED.md](diversity-demo/docs/METRICS_EXPLAINED.md) - How diversity is calculated
- [FRONTEND_README.md](diversity-demo/docs/FRONTEND_README.md) - Frontend setup and features
- [INTEGRATION_GUIDE.md](diversity-demo/docs/INTEGRATION_GUIDE.md) - Integration with Aideator

## Technology Stack

- **Frontend**: React 18.2 + TypeScript + Vite
- **Backend**: FastAPI + Python 3.11
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **Distance Metric**: Cosine distance
- **Database**: JSON-based (no external DB required)

## Requirements

- Python 3.11+
- Node.js 16+
- npm or yarn

## License

MIT License - See [LICENSE](LICENSE) file for details

## Author

Soukaina

---
