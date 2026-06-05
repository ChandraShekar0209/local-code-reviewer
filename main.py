# main.py
# FastAPI REST API for Local AI Code Reviewer

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import logging
import ollama

from src.parser import parse_code, get_summary
from src.reviewer import review_all_models
from src.benchmarker import compare_models, format_benchmark_table
from src.scorer import score_reviews, get_winner, get_winner_reasoning
from src.models import MODELS, DEFAULT_MODELS

# logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("api.log")
    ]
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Local AI Code Reviewer",
    description="Privacy-first code review using local LLMs — no data leaves your machine",
    version="1.0.0"
)


# request model
class ReviewRequest(BaseModel):
    code: str
    models: Optional[List[str]] = DEFAULT_MODELS


# health check
@app.get("/health")
async def health_check():
    logger.info("Health check called")

    # check if Ollama is running
    try:
        ollama.list()
        ollama_status = "running"
    except Exception:
        ollama_status = "not running"

    return {
        "status": "healthy",
        "service": "Local AI Code Reviewer",
        "version": "1.0.0",
        "ollama": ollama_status
    }


# available models endpoint
@app.get("/models")
async def get_models():
    logger.info("Models list requested")
    return {
        "available_models": MODELS,
        "default_models": DEFAULT_MODELS
    }


# main review endpoint
@app.post("/review")
async def review_code(request: ReviewRequest):
    logger.info(f"Review request — models: {request.models}")

    if not request.code.strip():
        raise HTTPException(
            status_code=400,
            detail="Code cannot be empty"
        )

    if not request.models:
        raise HTTPException(
            status_code=400,
            detail="At least one model must be selected"
        )

    # validate models
    invalid_models = [m for m in request.models if m not in MODELS]
    if invalid_models:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid models: {invalid_models}. Available: {list(MODELS.keys())}"
        )

    try:
        # step 1 — parse code
        logger.info("Parsing code with AST")
        metadata = parse_code(request.code)
        logger.info(f"Code parsed — {metadata.lines_of_code} lines, {len(metadata.functions)} functions")

        # step 2 — review with all models
        logger.info(f"Running review with models: {request.models}")
        results = review_all_models(metadata, request.models)

        # step 3 — benchmark
        logger.info("Comparing model benchmarks")
        comparison = compare_models(results)

        # step 4 — score
        logger.info("Scoring reviews")
        scores = score_reviews(results)

        winner = get_winner(scores)
        reasoning = get_winner_reasoning(scores)

        logger.info(f"Review complete — winner: {winner}")

        return JSONResponse(content={
            "status": "success",
            "code_analysis": {
                "lines_of_code": metadata.lines_of_code,
                "functions": metadata.functions,
                "classes": metadata.classes,
                "imports": metadata.imports,
                "complexity": metadata.complexity,
                "has_docstrings": metadata.has_docstrings,
                "has_type_hints": metadata.has_type_hints,
                "pre_detected_issues": metadata.potential_issues
            },
            "reviews": {
                model_id: {
                    "review": result["review"],
                    "metrics": result["metrics"],
                    "success": result["success"]
                }
                for model_id, result in results.items()
            },
            "benchmark": comparison.get("summary", {}),
            "winner": winner,
            "winner_reasoning": reasoning
        })

    except Exception as e:
        logger.error(f"Review failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Review failed: {str(e)}"
        )


# quick analysis endpoint — AST only, no LLM
@app.post("/analyse")
async def analyse_code(request: ReviewRequest):
    """
    Quick code analysis using AST only — no LLM needed.
    Returns code structure and pre-detected issues instantly.
    """
    logger.info("Quick analysis request")

    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")

    try:
        metadata = parse_code(request.code)
        logger.info(f"Analysis complete — {len(metadata.potential_issues)} issues found")

        return JSONResponse(content={
            "status": "success",
            "lines_of_code": metadata.lines_of_code,
            "functions": metadata.functions,
            "classes": metadata.classes,
            "imports": metadata.imports,
            "complexity": metadata.complexity,
            "has_docstrings": metadata.has_docstrings,
            "has_type_hints": metadata.has_type_hints,
            "pre_detected_issues": metadata.potential_issues,
            "summary": get_summary(metadata)
        })

    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))