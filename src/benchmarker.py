# src/benchmarker.py
# Compares performance metrics across all models

def compare_models(results: dict) -> dict:
    """
    Compare benchmark metrics across all models
    and determine rankings
    """

    comparison = {
        "speed_ranking": [],
        "efficiency_ranking": [],
        "score_ranking": [],
        "summary": {}
    }

    # collect metrics for each model
    model_metrics = []
    for model_id, result in results.items():
        if result["success"]:
            model_metrics.append({
                "model_id": model_id,
                "time_taken": result["metrics"]["time_taken"],
                "tokens_per_sec": result["metrics"]["tokens_per_sec"],
                "memory_used_mb": result["metrics"]["memory_used_mb"],
                "overall_score": result["review"]["overall_score"]
            })

    # rank by speed — fastest first
    comparison["speed_ranking"] = sorted(
        model_metrics,
        key=lambda x: x["time_taken"]
    )

    # rank by efficiency — most tokens per second first
    comparison["efficiency_ranking"] = sorted(
        model_metrics,
        key=lambda x: x["tokens_per_sec"],
        reverse=True
    )

    # rank by review quality score — highest first
    comparison["score_ranking"] = sorted(
        model_metrics,
        key=lambda x: x["overall_score"],
        reverse=True
    )

    # build summary for each model
    for metric in model_metrics:
        model_id = metric["model_id"]
        comparison["summary"][model_id] = {
            "time_taken":     f"{metric['time_taken']}s",
            "tokens_per_sec": f"{metric['tokens_per_sec']} t/s",
            "memory_used_mb": f"{metric['memory_used_mb']} MB",
            "overall_score":  f"{metric['overall_score']}/10"
        }

    return comparison


def get_fastest_model(comparison: dict) -> str:
    """Return the model id of the fastest model"""
    if comparison["speed_ranking"]:
        return comparison["speed_ranking"][0]["model_id"]
    return "N/A"


def get_best_quality_model(comparison: dict) -> str:
    """Return the model id with highest review quality"""
    if comparison["score_ranking"]:
        return comparison["score_ranking"][0]["model_id"]
    return "N/A"


def format_benchmark_table(comparison: dict) -> str:
    """Format benchmark results as a readable table"""

    table = "\nBENCHMARK RESULTS\n"
    table += "=" * 60 + "\n"
    table += f"{'Model':<20} {'Time':>8} {'Tokens/s':>10} {'Score':>8}\n"
    table += "-" * 60 + "\n"

    for model_id, summary in comparison["summary"].items():
        short_name = model_id.split(":")[0][:18]
        table += (
            f"{short_name:<20} "
            f"{summary['time_taken']:>8} "
            f"{summary['tokens_per_sec']:>10} "
            f"{summary['overall_score']:>8}\n"
        )

    table += "=" * 60 + "\n"
    table += f"Fastest: {get_fastest_model(comparison)}\n"
    table += f"Best quality: {get_best_quality_model(comparison)}\n"

    return table