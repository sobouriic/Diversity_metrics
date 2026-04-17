import logging
import os
import sys
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).parent))

from metrics.compute_metrics import compute_all_metrics
from metrics.io import AnalyzeRequest, ExperimentAnalyzeRequest, MetricsResponse, Solution
from utils.aideator_parser import (
    extract_solutions_from_experiment_payload,
    process_experiment_folder,
    validate_solution_format,
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_EXPERIMENTS_BASE_DIR = (PROJECT_ROOT / "experiments").resolve()

MAX_SOLUTIONS = 3000
MAX_TOTAL_CHARACTERS = 750_000


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_cors_origins() -> list[str]:
    raw = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:3005,http://localhost:3008")
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    return origins or ["http://localhost:3005", "http://localhost:3008"]


def _create_request_id() -> str:
    return uuid.uuid4().hex[:12]


def _error_payload(detail: str, error_code: str, request_id: str) -> Dict[str, str]:
    return {
        "detail": detail,
        "error_code": error_code,
        "request_id": request_id,
    }


def _validate_solution_count(count: int) -> None:
    if count < 2:
        raise ValueError("At least 2 solutions are required for analysis.")
    if count > MAX_SOLUTIONS:
        raise ValueError(f"Maximum supported solutions per request is {MAX_SOLUTIONS}.")


def _validate_payload_size(solutions: list[Solution]) -> None:
    total_chars = sum(len(solution.title) + len(solution.description) for solution in solutions)
    if total_chars > MAX_TOTAL_CHARACTERS:
        raise ValueError("Payload is too large. Reduce solution text size and try again.")


def _resolve_experiment_folder_path(folder_path: str) -> Path:
    allow_external = _parse_bool(os.getenv("ALLOW_EXTERNAL_EXPERIMENT_PATHS", "false"))
    base_dir = Path(
        os.getenv("EXPERIMENTS_BASE_DIR", str(DEFAULT_EXPERIMENTS_BASE_DIR))
    ).expanduser().resolve()

    try:
        resolved = Path(folder_path).expanduser().resolve()
    except Exception:
        raise ValueError("Invalid experiment folder path.")

    if not resolved.exists() or not resolved.is_dir():
        raise ValueError("Experiment folder does not exist or is not a directory.")

    if not allow_external and not resolved.is_relative_to(base_dir):
        raise ValueError(
            "Experiment folder is outside allowed directory. "
            f"Allowed base: {base_dir}"
        )

    return resolved


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Diversity Metrics API")
    from utils.embeddings import get_embedder

    try:
        embedder = get_embedder()
        logger.info("Embeddings model loaded: %s", embedder.model_name)
    except Exception:
        logger.exception("Failed to load embeddings model during startup")

    yield
    logger.info("Shutting down API")


app = FastAPI(
    title="Diversity Metrics API",
    description="Analyze diversity of ideation solutions using embeddings and cosine distance",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_cors_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    request_id = _create_request_id()
    logger.warning(
        "Request validation failed | id=%s path=%s errors=%s",
        request_id,
        request.url.path,
        exc.errors(),
    )
    return JSONResponse(
        status_code=400,
        content=_error_payload(
            "Invalid JSON payload. Check field names, types, and required values.",
            "INVALID_REQUEST",
            request_id,
        ),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    request_id = _create_request_id()
    detail = exc.detail if isinstance(exc.detail, str) else "Request failed."
    logger.warning(
        "HTTP error | id=%s path=%s status=%s detail=%s",
        request_id,
        request.url.path,
        exc.status_code,
        detail,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_payload(detail, "REQUEST_ERROR", request_id),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = _create_request_id()
    logger.exception("Unhandled server error | id=%s path=%s", request_id, request.url.path)
    return JSONResponse(
        status_code=500,
        content=_error_payload("Internal server error.", "INTERNAL_ERROR", request_id),
    )


@app.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "ok", "version": "1.0.0"}


@app.post("/api/analyze", response_model=MetricsResponse)
async def analyze_manual(request: AnalyzeRequest) -> MetricsResponse:
    try:
        source = "manual"
        solution_objects = request.solutions or []

        if not solution_objects:
            payload = {}
            if request.tree is not None:
                payload["tree"] = request.tree
            if request.idea_tree is not None:
                payload["tree"] = request.idea_tree
            if request.posts is not None:
                payload["posts"] = request.posts

            extracted_solutions = extract_solutions_from_experiment_payload(payload)
            if not extracted_solutions:
                raise ValueError(
                    "No solution posts were found. Expected nodes with type='solution'."
                )

            invalid_solutions = [
                solution
                for solution in extracted_solutions
                if not validate_solution_format(solution)
            ]
            if invalid_solutions:
                raise ValueError(
                    f"Found {len(invalid_solutions)} invalid extracted solutions."
                )

            _validate_solution_count(len(extracted_solutions))

            solution_objects = [
                Solution(title=solution["title"], description=solution["description"])
                for solution in extracted_solutions
            ]
            source = "idea_tree"

        _validate_solution_count(len(solution_objects))
        _validate_payload_size(solution_objects)

        logger.info("Analyzing %s solutions (source=%s)", len(solution_objects), source)

        response = compute_all_metrics(
            solutions=solution_objects,
            mission=request.mission,
            goal=request.goal,
        )
        response.metadata.update(
            {
                "source": source,
                "input_format": "solutions" if source == "manual" else "idea_tree",
                "total_solutions_extracted": len(solution_objects),
            }
        )
        return response

    except (ValueError, ValidationError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/analyze-experiment", response_model=MetricsResponse)
async def analyze_experiment(request: ExperimentAnalyzeRequest) -> MetricsResponse:
    try:
        safe_folder = _resolve_experiment_folder_path(request.folder_path)
        logger.info(
            "Processing experiment from %s (condition=%s, domain=%s)",
            safe_folder,
            request.condition,
            request.domain,
        )

        experiment_data = process_experiment_folder(
            str(safe_folder),
            request.condition,
            request.domain,
        )
        solutions = experiment_data["solutions"]
        metadata = experiment_data["metadata"]

        if not solutions:
            raise ValueError("No solutions found in experiment folder.")

        invalid_solutions = [solution for solution in solutions if not validate_solution_format(solution)]
        if invalid_solutions:
            raise ValueError(f"Found {len(invalid_solutions)} invalid solutions in experiment data.")

        solution_objects = [
            Solution(title=solution["title"], description=solution["description"])
            for solution in solutions
        ]

        _validate_solution_count(len(solution_objects))
        _validate_payload_size(solution_objects)

        response = compute_all_metrics(solutions=solution_objects, mission=None, goal=None)
        response.metadata.update(
            {
                "source": "experiment",
                "condition": metadata.get("condition"),
                "domain": metadata.get("domain"),
                "total_solutions_extracted": len(solutions),
                "experiment_status": metadata.get("status"),
            }
        )
        return response

    except (FileNotFoundError, ValueError, ValidationError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
