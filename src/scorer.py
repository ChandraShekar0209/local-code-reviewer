# src/scorer.py
# Uses LLM to judge which model gave the best review

import ollama
import json
from prompts.review_prompt import build_score_prompt


def score_reviews(results: dict) -> dict:
    """
    Use llama3.2:3b to judge which model
    gave the best code review
    """

    # extract just the reviews
    reviews = {}
    for model_id, result in results.items():
        if result["success"]:
            reviews[model_id] = result["review"]

    # need at least 2 reviews to compare
    if len(reviews) < 2:
        model_id = list(reviews.keys())[0] if reviews else "none"
        return {
            "scores": {model_id: 10},
            "winner": model_id,
            "reasoning": "Only one model ran — no comparison possible"
        }

    # build scoring prompt
    prompt = build_score_prompt(reviews)

    try:
        # use fastest model to judge
        response = ollama.chat(
            model="llama3.2:3b",
            messages=[
                {
                    "role": "system",
                    "content": "You are evaluating AI code reviews. Return valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={"temperature": 0.1}
        )

        raw = response["message"]["content"].strip()

        # clean markdown if present
        if raw.startswith("```"):
            lines = raw.split("\n")
            raw = "\n".join(lines[1:-1])

        scores = json.loads(raw)
        return scores

    except Exception as e:
        # fallback — pick model with highest overall_score
        best_model = max(
            reviews.keys(),
            key=lambda m: reviews[m].get("overall_score", 0)
        )
        return {
            "scores": {m: 5 for m in reviews.keys()},
            "winner": best_model,
            "reasoning": f"Auto-selected based on overall score. Error: {str(e)}"
        }


def get_winner(scores: dict) -> str:
    """Return the winning model name"""
    return scores.get("winner", "unknown")


def get_winner_reasoning(scores: dict) -> str:
    """Return why the winner was chosen"""
    return scores.get("reasoning", "No reasoning provided")