import argparse
import sys
import os
from dotenv import load_dotenv
from graph.graph import build_graph
from graph.state import ResearchState
from tools.graveyard import print_graveyard

load_dotenv()


# ── Terminal colors ───────────────────────────────────────────
class C:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def banner():
    print(
        f"""
{C.BOLD}{C.CYAN}╔══════════════════════════════════════════════════════════════╗
║          AUTONOMOUS QUANT RESEARCH AGENT                     ║
║          Powered by LangGraph + GPT-4o + E2B                 ║
╚══════════════════════════════════════════════════════════════╝{C.RESET}
"""
    )


def run_research(
    hypothesis: str,
    max_refinements: int = 2,
    verbose: bool = True,
    auto_approve: bool = False,
):
    if verbose:
        banner()
        print(f"{C.BOLD}Hypothesis:{C.RESET} {hypothesis}\n")

    os.environ["MAX_REFINEMENTS"] = str(max_refinements)
    os.environ["AUTO_APPROVE"] = "1" if auto_approve else "0"

    initial_state: ResearchState = {
        "hypothesis": hypothesis,
        "sub_questions": [],
        "assets": [],
        "timeframe": {},
        "generated_code": "",
        "execution_result": {},
        "analysis": {},
        "iteration": 0,
        "refined_hypothesis": "",
        "final_report": "",
        "status": "planning",
        "human_approved": False,
        "human_feedback": "",
    }

    graph = build_graph()
    print(f"{C.DIM}Starting research pipeline...{C.RESET}\n")

    # ── Stream node-by-node ───────────────────────────────────
    from tools.streaming import print_stream_event

    final_state = None
    for event in graph.stream(initial_state, stream_mode="updates"):
        for node_name, node_state in event.items():
            print_stream_event(node_name, node_state)
            final_state = node_state

    if final_state is None:
        print(f"{C.RED}Pipeline produced no output.{C.RESET}")
        return None

    # ── Summary ──────────────────────────────────────────────
    verdict = final_state.get("analysis", {}).get("verdict", "N/A").upper()
    verdict_color = C.GREEN if verdict == "STRONG" else C.YELLOW

    print(f"\n{C.BOLD}{'='*60}{C.RESET}")
    print(f"{C.BOLD}RESEARCH COMPLETE{C.RESET}")
    print(f"{C.BOLD}{'='*60}{C.RESET}")
    print(f"Verdict      : {verdict_color}{C.BOLD}{verdict}{C.RESET}")
    print(f"Status       : {final_state.get('status', 'N/A')}")
    print(f"Iterations   : {final_state.get('iteration', 0)}")

    analysis = final_state.get("analysis", {})
    if analysis.get("sharpe_ratio") is not None:
        sharpe = analysis["sharpe_ratio"]
        sharpe_color = C.GREEN if sharpe > 0.3 else C.RED
        print(f"Sharpe Ratio : {sharpe_color}{sharpe:.3f}{C.RESET}")
    if analysis.get("total_return") is not None:
        ret = analysis["total_return"]
        ret_color = C.GREEN if ret > 0 else C.RED
        print(f"Total Return : {ret_color}{ret:.2f}%{C.RESET}")
    if analysis.get("n_trades") is not None:
        print(f"Trades       : {analysis['n_trades']}")

    if final_state.get("final_report"):
        print(f"\n{C.DIM}--- Report Preview ---{C.RESET}")
        print(final_state["final_report"][:500])
        print(f"{C.DIM}...(full report saved to outputs/){C.RESET}")

    return final_state


def main():
    parser = argparse.ArgumentParser(
        description="Autonomous Quant Research Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "Bitcoin drops after Fed rate hikes"
  python main.py "Gold rises when dollar weakens" --max-refinements 3
  python main.py "SPY momentum strategy" --auto-approve
  python main.py "VIX spikes before crashes" --quiet --auto-approve
  python main.py --graveyard
        """,
    )

    parser.add_argument(
        "hypothesis", nargs="?", help="The financial hypothesis to research"
    )
    parser.add_argument(
        "--max-refinements",
        type=int,
        default=2,
        metavar="N",
        help="Maximum refinement rounds (default: 2)",
    )
    parser.add_argument(
        "--graveyard",
        action="store_true",
        help="Show the hypothesis graveyard and exit",
    )
    parser.add_argument(
        "--quiet", action="store_true", help="Suppress banner and extra output"
    )
    parser.add_argument(
        "--auto-approve",
        action="store_true",
        help="Skip human review and run fully autonomously",
    )

    args = parser.parse_args()

    # ── Show graveyard and exit ───────────────────────────────
    if args.graveyard:
        print_graveyard()
        sys.exit(0)

    # ── Require hypothesis ────────────────────────────────────
    if not args.hypothesis:
        print(f"{C.RED}Error: please provide a hypothesis.{C.RESET}")
        print(f'{C.DIM}Usage: python main.py "your hypothesis here"{C.RESET}')
        print(f"{C.DIM}       python main.py --graveyard{C.RESET}")
        sys.exit(1)

    run_research(
        hypothesis=args.hypothesis,
        max_refinements=args.max_refinements,
        verbose=not args.quiet,
        auto_approve=args.auto_approve,
    )

    print_graveyard()


if __name__ == "__main__":
    main()
