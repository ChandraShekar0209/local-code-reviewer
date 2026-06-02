# prompts/review_prompt.py
# Builds structured prompts for code review

from src.parser import CodeMetadata


def build_review_prompt(metadata: CodeMetadata) -> str:
    """
    Build a structured prompt that asks the model
    to return a JSON code review
    """

    # format pre-detected issues for context
    if metadata.potential_issues:
        issues_context = "\n".join(
            f"- {issue}" for issue in metadata.potential_issues
        )
    else:
        issues_context = "- None pre-detected"

    prompt = f"""You are an expert Python code reviewer.
Analyse the following Python code and return a JSON review.

CODE METADATA:
- Lines: {metadata.lines_of_code}
- Functions: {', '.join(metadata.functions) if metadata.functions else 'None'}
- Classes: {', '.join(metadata.classes) if metadata.classes else 'None'}
- Imports: {', '.join(metadata.imports) if metadata.imports else 'None'}
- Complexity: {metadata.complexity}
- Has docstrings: {metadata.has_docstrings}
- Has type hints: {metadata.has_type_hints}
- Pre-detected issues:
{issues_context}

CODE TO REVIEW:
```python
{metadata.raw_code}
```

Return ONLY valid JSON — no explanation, no markdown, no extra text.
Use exactly this format:

{{
    "bugs": ["specific bug with line number if possible"],
    "security": ["specific security issue with line number if possible"],
    "performance": ["specific performance issue with line number if possible"],
    "style": ["specific style issue with line number if possible"],
    "overall_score": <number between 1 and 10>,
    "summary": "one paragraph summary of the code quality",
    "priority_fix": "the single most important thing to fix first"
}}

Rules:
- Each list should have 1-5 specific actionable items
- If no issues found in a category return an empty list []
- overall_score: 1=terrible, 5=average, 10=perfect
- Be specific — include line numbers where possible
- Focus on Python best practices
"""

    return prompt


def build_score_prompt(reviews: dict) -> str:
    """
    Build a prompt that asks LLM to judge
    which model gave the best review
    """

    reviews_text = ""
    for model_id, review in reviews.items():
        reviews_text += f"""
Model: {model_id}
Review: {review}
---"""

    prompt = f"""You are evaluating the quality of AI code reviews.

Here are three code reviews from different AI models:
{reviews_text}

Rate each review on these criteria:
1. Specificity — does it give specific line numbers and details?
2. Accuracy — are the issues real and correctly identified?
3. Actionability — does it give clear fixes?
4. Completeness — does it cover all categories?

Return ONLY valid JSON:
{{
    "scores": {{
        "model_id_1": <score 1-10>,
        "model_id_2": <score 1-10>,
        "model_id_3": <score 1-10>
    }},
    "winner": "model_id_of_best_review",
    "reasoning": "one sentence why the winner is best"
}}
"""

    return prompt