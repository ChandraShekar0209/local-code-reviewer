# app.py
# Streamlit UI for Local AI Code Reviewer

import streamlit as st
import tempfile
import os
import time
from src.models import MODELS, DEFAULT_MODELS
from src.parser import parse_code, get_summary
from src.reviewer import review_all_models
from src.benchmarker import compare_models, format_benchmark_table
from src.scorer import score_reviews, get_winner, get_winner_reasoning
from src.reporter import generate_pdf_report

st.set_page_config(
    page_title="Local AI Code Reviewer",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Local AI Code Reviewer")
st.markdown(
    "**Privacy-first** code analysis using local LLMs — "
    "no data leaves your machine, no API costs, works offline"
)
st.divider()

# sidebar — model selection
with st.sidebar:
    st.header("⚙️ Settings")
    st.markdown("**Select models to run:**")

    selected_models = []
    for model_id, info in MODELS.items():
        checked = st.checkbox(
            f"{info['name']} ({info['size']})",
            value=True,
            help=info["description"]
        )
        if checked:
            selected_models.append(model_id)

    st.divider()
    st.markdown("**Models info:**")
    for model_id, info in MODELS.items():
        st.markdown(f"**{info['name']}**")
        st.caption(f"Strengths: {info['strengths']}")

    st.divider()
    st.caption("All models run locally on your machine using Ollama")

# main area — tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📝 Code Input",
    "🔍 Reviews",
    "📊 Benchmarks",
    "📄 Download Report"
])

with tab1:
    st.subheader("Enter your Python code")

    input_method = st.radio(
        "Input method",
        ["Paste code", "Upload file"],
        horizontal=True
    )

    code = None

    if input_method == "Paste code":
        code = st.text_area(
            "Paste your Python code here",
            height=300,
            placeholder="def my_function():\n    pass"
        )

    else:
        uploaded = st.file_uploader(
            "Upload a Python file",
            type=["py"]
        )
        if uploaded:
            code = uploaded.read().decode("utf-8")
            st.code(code, language="python")

    st.divider()

    if not selected_models:
        st.warning("Please select at least one model in the sidebar")
    else:
        st.info(
            f"Will run: {', '.join(selected_models)} — "
            f"estimated time: {len(selected_models) * 30}-{len(selected_models) * 90} seconds"
        )

    run_btn = st.button(
        "🚀 Run Code Review",
        use_container_width=True,
        disabled=not code or not selected_models
    )

    if run_btn and code:
        # store results in session state
        with st.spinner("Analysing code structure..."):
            metadata = parse_code(code)

        st.success("Code parsed successfully")

        with st.expander("📋 Code analysis summary"):
            st.text(get_summary(metadata))

        # run models
        results = {}
        progress = st.progress(0)
        status = st.empty()

        for i, model_id in enumerate(selected_models):
            status.info(
                f"Running {MODELS[model_id]['name']}... "
                f"({i+1}/{len(selected_models)})"
            )
            from src.reviewer import review_with_model
            result = review_with_model(metadata, model_id)
            results[model_id] = result
            progress.progress((i + 1) / len(selected_models))

        status.success("All reviews complete!")

        # compare and score
        comparison = compare_models(results)
        scores = score_reviews(results)

        # store in session state
        st.session_state["metadata"]   = metadata
        st.session_state["results"]    = results
        st.session_state["comparison"] = comparison
        st.session_state["scores"]     = scores

        st.success(
            f"Done! Winner: **{get_winner(scores)}** — "
            f"{get_winner_reasoning(scores)}"
        )
        st.info("Check the Reviews and Benchmarks tabs for full results")

with tab2:
    st.subheader("Model Reviews")

    if "results" not in st.session_state:
        st.info("Run a code review first in the Code Input tab")
    else:
        results    = st.session_state["results"]
        scores     = st.session_state["scores"]
        winner     = get_winner(scores)

        cols = st.columns(len(results))

        for col, (model_id, result) in zip(cols, results.items()):
            with col:
                info   = MODELS[model_id]
                review = result["review"]
                is_winner = model_id == winner

                if is_winner:
                    st.markdown(f"### 🏆 {info['name']}")
                else:
                    st.markdown(f"### {info['name']}")

                score = review.get("overall_score", 0)
                st.metric("Score", f"{score}/10")

                if result["success"]:
                    # bugs
                    bugs = review.get("bugs", [])
                    with st.expander(f"🐛 Bugs ({len(bugs)})"):
                        if bugs:
                            for b in bugs:
                                st.markdown(f"• {b}")
                        else:
                            st.success("No bugs found")

                    # security
                    sec = review.get("security", [])
                    with st.expander(f"🔒 Security ({len(sec)})"):
                        if sec:
                            for s in sec:
                                st.markdown(f"• {s}")
                        else:
                            st.success("No security issues found")

                    # performance
                    perf = review.get("performance", [])
                    with st.expander(f"⚡ Performance ({len(perf)})"):
                        if perf:
                            for p in perf:
                                st.markdown(f"• {p}")
                        else:
                            st.success("No performance issues found")

                    # style
                    style = review.get("style", [])
                    with st.expander(f"💅 Style ({len(style)})"):
                        if style:
                            for s in style:
                                st.markdown(f"• {s}")
                        else:
                            st.success("No style issues found")

                    # summary
                    st.markdown("**Summary:**")
                    st.markdown(review.get("summary", "N/A"))

                    # priority fix
                    st.error(
                        f"🔧 Priority fix: {review.get('priority_fix', 'N/A')}"
                    )

                else:
                    st.error("Model failed to respond")

with tab3:
    st.subheader("Benchmark Comparison")

    if "comparison" not in st.session_state:
        st.info("Run a code review first in the Code Input tab")
    else:
        comparison = st.session_state["comparison"]
        scores     = st.session_state["scores"]

        # metrics table
        summary = comparison.get("summary", {})

        if summary:
            import pandas as pd

            df_data = []
            for model_id, m in summary.items():
                df_data.append({
                    "Model":     model_id,
                    "Time":      m["time_taken"],
                    "Tokens/s":  m["tokens_per_sec"],
                    "Score":     m["overall_score"]
                })

            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)

        # rankings
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**⚡ Speed ranking**")
            for i, m in enumerate(comparison.get("speed_ranking", []), 1):
                st.markdown(f"{i}. {m['model_id']} — {m['time_taken']}s")

        with col2:
            st.markdown("**🔤 Efficiency ranking**")
            for i, m in enumerate(comparison.get("efficiency_ranking", []), 1):
                st.markdown(f"{i}. {m['model_id']} — {m['tokens_per_sec']} t/s")

        with col3:
            st.markdown("**⭐ Quality ranking**")
            for i, m in enumerate(comparison.get("score_ranking", []), 1):
                st.markdown(f"{i}. {m['model_id']} — {m['overall_score']}/10")

        st.divider()
        st.markdown(f"**🏆 Overall winner: {get_winner(scores)}**")
        st.markdown(f"*{get_winner_reasoning(scores)}*")

with tab4:
    st.subheader("Download PDF Report")

    if "results" not in st.session_state:
        st.info("Run a code review first in the Code Input tab")
    else:
        st.markdown(
            "Download a complete PDF report including all reviews, "
            "benchmark comparisons, and recommendations."
        )

        if st.button("📄 Generate PDF Report", use_container_width=True):
            with st.spinner("Generating PDF..."):
                pdf_path = generate_pdf_report(
                    st.session_state["metadata"],
                    st.session_state["results"],
                    st.session_state["comparison"],
                    st.session_state["scores"]
                )

            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()

            st.download_button(
                label="⬇️ Download Report PDF",
                data=pdf_bytes,
                file_name="code_review_report.pdf",
                mime="application/pdf",
                use_container_width=True
            )

            os.unlink(pdf_path)
            st.success("Report ready — click above to download")