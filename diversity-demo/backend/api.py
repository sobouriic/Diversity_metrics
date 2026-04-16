from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Dict
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from metrics.io import AnalyzeRequest, MetricsResponse, ExperimentAnalyzeRequest
from metrics.compute_metrics import compute_all_metrics
from utils.aideator_parser import process_experiment_folder, validate_solution_format


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Diversity Metrics API")
    
    from utils.embeddings import get_embedder
    try:
        embedder = get_embedder()
        logger.info(f"Embeddings model loaded: {embedder.model_name}")
    except Exception as e:
        logger.error(f"Failed to load embeddings model: {e}")
    
    yield
    
    logger.info("Shutting down API")


app = FastAPI(
    title="Diversity Metrics API",
    description="Analyze diversity of ideation solutions using embeddings and cosine distance",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "ok", "version": "1.0.0"}


@app.post("/api/analyze", response_model=MetricsResponse)
async def analyze_manual(request: AnalyzeRequest) -> MetricsResponse:
    """
    Analyze manually entered solutions for diversity.
    
    This endpoint:
    1. Accepts user-entered solutions with optional mission/goal context
    2. Computes embeddings for each solution
    3. Calculates diversity score (0-1 scale)
    4. Validates results and provides warnings
    5. Returns comprehensive metrics response
    
    Request Schema (AnalyzeRequest):
    {
        "solutions": [
            {"title": "str", "description": "str"},
            {"title": "str", "description": "str"}
        ],
        "mission": "str (optional)",
        "goal": "str (optional)"
    }
    
    Response Schema (MetricsResponse):
    {
        "diversity_score": 0.0-1.0,
        "solutions": [...],
        "validation_report": {...},
        "metadata": {...}
    }
    
    Errors:
    - 400 Bad Request: Invalid solution format or validation error
    - 500 Internal Server Error: Computation failed (embedding/metric error)
    
    Args:
        request: AnalyzeRequest with solutions and optional context
        
    Returns:
        MetricsResponse with diversity score and detailed metrics
        
    Raises:
        HTTPException: 400 for validation errors, 500 for computation errors
    """
    try:
        logger.info(f"Analyzing {len(request.solutions)} manual solutions")
        
        # Compute diversity and other metrics
        response = compute_all_metrics(
            solutions=request.solutions,
            mission=request.mission,
            goal=request.goal
        )
        
        logger.info(
            f"Analysis complete: diversity={response.diversity_score:.3f}"
        )
        
        return response
        
    except ValueError as e:
        # Client error - invalid request data
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Server error - computation failed
        logger.error(f"Computation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compute metrics: {str(e)}"
        )


@app.post("/api/analyze-experiment", response_model=MetricsResponse)
async def analyze_experiment(request: ExperimentAnalyzeRequest) -> MetricsResponse:
    
    try:
        logger.info(
            f"Processing experiment: condition={request.condition}, "
            f"domain={request.domain}"
        )
        
        # Load and parse experiment folder structure
        experiment_data = process_experiment_folder(
            request.folder_path,
            request.condition,
            request.domain
        )
        
        solutions = experiment_data["solutions"]
        metadata = experiment_data["metadata"]
        
        if not solutions:
            raise ValueError("No solutions found in experiment folder")
        
        invalid_solutions = [
            s for s in solutions if not validate_solution_format(s)
        ]
        if invalid_solutions:
            raise ValueError(
                f"Invalid solution format in {len(invalid_solutions)} solutions"
            )
        
        logger.info(f"Extracted {len(solutions)} solutions from experiment")
        
        from metrics.io import Solution
        solution_objects = [
            Solution(title=s["title"], description=s["description"])
            for s in solutions
        ]
        
        response = compute_all_metrics(
            solutions=solution_objects,
            mission=None,
            goal=None
        )
        
        # Add experiment-specific metadata to response
        response.metadata.update({
            "source": "experiment",
            "condition": metadata.get("condition"),
            "domain": metadata.get("domain"),
            "total_solutions_extracted": len(solutions),
            "experiment_status": metadata.get("status"),
        })
        
        logger.info(
            f"Experiment analysis complete: diversity={response.diversity_score:.3f}"
        )
        
        return response
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Computation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process experiment: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )
