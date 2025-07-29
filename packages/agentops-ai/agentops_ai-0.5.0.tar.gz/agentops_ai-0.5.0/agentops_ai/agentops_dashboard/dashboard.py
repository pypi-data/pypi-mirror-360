"""Dashboard utilities for AgentOps.

Provides functions for loading usage and coverage data.
"""

import streamlit as st
import os
import json

USAGE_FILE = os.path.expanduser("~/.agentops_usage.json")
COVERAGE_FILE = "coverage.txt"


def load_usage():
    """Load usage statistics for the dashboard."""
    if os.path.exists(USAGE_FILE):
        with open(USAGE_FILE) as f:
            return json.load(f)
    return {}


def load_coverage():
    """Load coverage data for the dashboard."""
    if os.path.exists(COVERAGE_FILE):
        with open(COVERAGE_FILE) as f:
            return f.read()
    return None


def main():
    """Run the dashboard main entry point."""
    st.set_page_config(page_title="AgentOps Dashboard", layout="wide")
    st.title("🧑‍💻 AgentOps Dashboard")
    usage = load_usage()
    col1, col2 = st.columns(2)
    # Test feedback
    feedback = usage.get("test_feedback", [])
    thumbs_up = sum(1 for f in feedback if f.get("useful"))
    thumbs_down = sum(1 for f in feedback if not f.get("useful"))
    with col1:
        st.header("Test Feedback")
        st.metric("👍 Thumbs Up", thumbs_up)
        st.metric("👎 Thumbs Down", thumbs_down)
        if feedback:
            st.subheader("Recent Feedback")
            for f in sorted(feedback, key=lambda x: x["timestamp"], reverse=True)[:5]:
                st.write(
                    f"{f['timestamp'][:19]} | {f['file']} → {f['output_file']} | {'👍' if f['useful'] else '👎'}"
                )
        else:
            st.info("No feedback yet.")
    # Run stats
    run_stats = usage.get("run_stats", [])
    with col2:
        st.header("Test Run Stats")
        total_runs = len(run_stats)
        successes = sum(1 for r in run_stats if r.get("success"))
        failures = total_runs - successes
        st.metric("Total Runs", total_runs)
        st.metric("Successes", successes)
        st.metric("Failures", failures)
        if run_stats:
            st.subheader("Recent Runs")
            for r in sorted(run_stats, key=lambda x: x["timestamp"], reverse=True)[:5]:
                st.write(
                    f"{r['timestamp'][:19]} | {r['target']} | {'✅' if r['success'] else '❌'}"
                )
        else:
            st.info("No run stats yet.")
    # Coverage summary
    st.header("Coverage Summary")
    coverage = load_coverage()
    if coverage:
        st.code(coverage, language="text")
    else:
        st.info("No coverage.txt found. Run tests with coverage to generate it.")


if __name__ == "__main__":
    main()
