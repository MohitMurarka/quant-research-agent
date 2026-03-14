import os
from e2b_code_interpreter import Sandbox
from graph.state import ResearchState
from dotenv import load_dotenv

load_dotenv()


def executor_node(state: ResearchState) -> ResearchState:
    print("\n[EXECUTOR] Launching E2B sandbox...")

    code = state["generated_code"]
    iteration = state.get("iteration", 0)

    try:
        with Sandbox.create() as sandbox:
            print("[EXECUTOR] Sandbox started. Installing dependencies...")

            sandbox.commands.run(
                "pip install yfinance pandas numpy matplotlib scipy --quiet"
            )
            print("[EXECUTOR] Dependencies installed. Running backtest...")

            sandbox.commands.run("mkdir -p outputs")

            execution = sandbox.run_code(code)

            stdout_lines = []
            has_error = False
            error_text = ""

            for log in execution.logs.stdout:
                stdout_lines.append(log)

            for log in execution.logs.stderr:
                # Skip warnings — only catch real errors
                if "warning" in log.lower() or "deprecat" in log.lower():
                    continue
                if any(
                    keyword in log.lower()
                    for keyword in [
                        "error",
                        "traceback",
                        "exception",
                        "syntaxerror",
                        "nameerror",
                        "typeerror",
                        "valueerror",
                        "indexerror",
                    ]
                ):
                    has_error = True
                    error_text += log + "\n"

            stdout = "\n".join(stdout_lines).strip()

            if execution.error:
                has_error = True
                error_text = f"{execution.error.name}: {execution.error.value}\n{execution.error.traceback}"

            if not has_error:
                print("[EXECUTOR] Code ran successfully")
                print(f"[EXECUTOR] Output:\n{stdout}")

                # Try to download the chart from sandbox
                chart_saved = False
                try:
                    chart_data = sandbox.files.read("outputs/backtest_chart.png")
                    os.makedirs("outputs", exist_ok=True)
                    with open("outputs/backtest_chart.png", "wb") as f:
                        f.write(chart_data)
                    chart_saved = True
                    print("[EXECUTOR] Chart saved to outputs/backtest_chart.png")
                except Exception:
                    print(
                        "[EXECUTOR] No chart from sandbox — generating fallback chart..."
                    )
                    from tools.fetch_data import generate_fallback_chart

                    hypothesis = state.get("refined_hypothesis") or state["hypothesis"]
                    chart_saved = generate_fallback_chart(stdout, hypothesis)
                    if chart_saved:
                        print(
                            "[EXECUTOR] Fallback chart saved to outputs/backtest_chart.png"
                        )
                    else:
                        print(
                            "[EXECUTOR] Could not generate chart — no parseable metrics"
                        )

                return {
                    **state,
                    "execution_result": {
                        "success": True,
                        "output": stdout,
                        "error": None,
                        "chart_saved": chart_saved,
                    },
                    "iteration": iteration + 1,
                    "status": "analysing",
                }

            else:
                print(f"[EXECUTOR] Code failed:")
                print(error_text)

                return {
                    **state,
                    "execution_result": {
                        "success": False,
                        "output": stdout,
                        "error": error_text,
                        "chart_saved": False,
                    },
                    "iteration": iteration + 1,
                    "status": "coding",
                }

    except Exception as e:
        print(f"[EXECUTOR] Sandbox error: {e}")
        return {
            **state,
            "execution_result": {
                "success": False,
                "output": "",
                "error": str(e),
                "chart_saved": False,
            },
            "iteration": iteration + 1,
            "status": "coding",
        }
