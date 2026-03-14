from graph.state import ResearchState


# Maps node names to display labels and colors
NODE_LABELS = {
    "planner": ("🔍 PLANNER", "\033[94m"),  # blue
    "human_review": ("👤 HUMAN REVIEW", "\033[95m"),  # purple
    "code_writer": ("✍️  CODE WRITER", "\033[96m"),  # cyan
    "executor": ("⚙️  EXECUTOR", "\033[93m"),  # yellow
    "analyst": ("📊 ANALYST", "\033[92m"),  # green
    "refiner": ("🔄 REFINER", "\033[91m"),  # red
    "report_writer": ("📝 REPORT WRITER", "\033[95m"),  # purple
}

BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def print_stream_event(node_name: str, state: ResearchState):
    """Print a clean summary when a node finishes."""
    label, color = NODE_LABELS.get(node_name, (node_name.upper(), "\033[0m"))

    print(f"\n{color}{BOLD}▶ {label}{RESET}")

    # Print relevant state changes per node
    if node_name == "planner":
        print(f"  Assets    : {state.get('assets', [])}")
        tf = state.get("timeframe", {})
        print(f"  Timeframe : {tf.get('start')} → {tf.get('end')}")
        print(f"  Questions : {len(state.get('sub_questions', []))}")

    elif node_name == "human_review":
        feedback = state.get("human_feedback", "")
        approved = state.get("human_approved", False)
        status = "✓ Approved" if approved else "✗ Skipped"
        print(f"  Decision  : {status} ({feedback})")

    elif node_name == "code_writer":
        code = state.get("generated_code", "")
        lines = len(code.splitlines()) if code else 0
        hyp = state.get("refined_hypothesis") or state.get("hypothesis", "")
        print(f"  Lines     : {lines}")
        print(f"  Hypothesis: {hyp[:80]}{'...' if len(hyp) > 80 else ''}")

    elif node_name == "executor":
        result = state.get("execution_result", {})
        success = result.get("success", False)
        icon = "✓" if success else "✗"
        status = "Success" if success else "Failed"
        print(f"  Result    : {icon} {status}")
        print(f"  Iteration : {state.get('iteration', 0)}")
        if success:
            output = result.get("output", "")
            # Print just the RESULTS section if present
            if "=== RESULTS ===" in output:
                lines = output.split("\n")
                in_results = False
                for line in lines:
                    if "=== RESULTS ===" in line:
                        in_results = True
                    if in_results:
                        print(f"  {DIM}{line}{RESET}")
                    if (
                        in_results
                        and line.strip() == ""
                        and "=== RESULTS ===" not in line
                    ):
                        break
        else:
            error = result.get("error", "")
            first_line = error.split("\n")[0] if error else "Unknown error"
            print(f"  {DIM}Error: {first_line[:100]}{RESET}")

    elif node_name == "analyst":
        analysis = state.get("analysis", {})
        verdict = analysis.get("verdict", "N/A").upper()
        color_v = "\033[92m" if verdict == "STRONG" else "\033[93m"
        print(f"  Verdict   : {color_v}{BOLD}{verdict}{RESET}")
        if analysis.get("sharpe_ratio") is not None:
            print(f"  Sharpe    : {analysis['sharpe_ratio']}")
        if analysis.get("n_trades") is not None:
            print(f"  Trades    : {analysis['n_trades']}")
        issues = analysis.get("issues", [])
        if issues:
            print(f"  Top issue : {DIM}{issues[0][:80]}{RESET}")

    elif node_name == "refiner":
        new_hyp = state.get("refined_hypothesis", "")
        print(f"  New hyp   : {new_hyp[:80]}{'...' if len(new_hyp) > 80 else ''}")

    elif node_name == "report_writer":
        print(f"  Status    : Report generated")
        verdict = state.get("analysis", {}).get("verdict", "N/A").upper()
        color_v = "\033[92m" if verdict == "STRONG" else "\033[93m"
        print(f"  Verdict   : {color_v}{BOLD}{verdict}{RESET}")
