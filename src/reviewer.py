# src/reviewer.py
# Calls Ollama models and gets structured JSON reviews

import ollama
import json
import time
import psutil
import os
from src.parser import CodeMetadata
from prompts.review_prompt import build_review_prompt


def get_memory_usage() -> float:
    """Get current memory usage in MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024


def review_with_model(
    metadata: CodeMetadata,
    model_id: str
) -> dict:
    """
    Send code to a specific Ollama model
    and get a structured JSON review back
    """

    # build the prompt
    prompt = build_review_prompt(metadata)

    # measure memory before
    mem_before = get_memory_usage()

    # measure time
    start_time = time.time()

    try:
        # call Ollama
        response = ollama.chat(
            model=model_id,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert Python code reviewer. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0.1,  # low temp = consistent structured output
                "num_predict": 1000  # max tokens
            }
        )

        # measure time taken
        time_taken = time.time() - start_time

        # measure memory after
        mem_after = get_memory_usage()

        # get raw response
        raw_content = response["message"]["content"]

        # clean response — remove markdown if model added it
        clean_content = raw_content.strip()
        if clean_content.startswith("```"):
            lines = clean_content.split("\n")
            clean_content = "\n".join(lines[1:-1])

        # parse JSON
        try:
            review = json.loads(clean_content)
        except json.JSONDecodeError:
            # if JSON parsing fails return structured error
            review = {
                "bugs": ["Could not parse model response as JSON"],
                "security": [],
                "performance": [],
                "style": [],
                "overall_score": 0,
                "summary": raw_content[:500],
                "priority_fix": "N/A"
            }

        # calculate tokens per second
        total_tokens = response.get("eval_count", 0)
        tokens_per_sec = total_tokens / time_taken if time_taken > 0 else 0

        return {
            "model_id": model_id,
            "review": review,
            "metrics": {
                "time_taken": round(time_taken, 2),
                "tokens_per_sec": round(tokens_per_sec, 1),
                "memory_used_mb": round(mem_after - mem_before, 1),
                "total_tokens": total_tokens
            },
            "success": True
        }

    except Exception as e:
        time_taken = time.time() - start_time
        return {
            "model_id": model_id,
            "review": {
                "bugs": [],
                "security": [],
                "performance": [],
                "style": [],
                "overall_score": 0,
                "summary": f"Error: {str(e)}",
                "priority_fix": "N/A"
            },
            "metrics": {
                "time_taken": round(time_taken, 2),
                "tokens_per_sec": 0,
                "memory_used_mb": 0,
                "total_tokens": 0
            },
            "success": False
        }


def review_all_models(
    metadata: CodeMetadata,
    model_ids: list
) -> dict:
    """
    Run code review across all selected models
    sequentially — one at a time to respect 8GB RAM
    """

    results = {}

    for model_id in model_ids:
        print(f"Running {model_id}...")
        result = review_with_model(metadata, model_id)
        results[model_id] = result
        print(f"Done — {result['metrics']['time_taken']}s")

    return results