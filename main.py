from dotenv import load_dotenv
from graph.graph import build_graph
from graph.state import ResearchState
from tools.graveyard import print_graveyard

load_dotenv()

def run_research(hypothesis: str):
    print(f"\n{'='*60}")
    print(f"AUTONOMOUS QUANT RESEARCH AGENT")
    print(f"{'='*60}")
    print(f"Hypothesis: {hypothesis}\n")

    initial_state: ResearchState = {
        "hypothesis":         hypothesis,
        "sub_questions":      [],
        "assets":             [],
        "timeframe":          {},
        "generated_code":     "",
        "execution_result":   {},
        "analysis":           {},
        "iteration":          0,
        "refined_hypothesis": "",
        "final_report":       "",
        "status":             "planning"
    }

    graph = build_graph()
    final_state = graph.invoke(initial_state)

    print(f"\n{'='*60}")
    print(f"RESEARCH COMPLETE")
    print(f"{'='*60}")
    print(f"Final verdict   : {final_state['analysis'].get('verdict', 'N/A').upper()}")
    print(f"Final status    : {final_state['status']}")
    print(f"Total iterations: {final_state['iteration']}")

    if final_state.get("final_report"):
        print("\n--- REPORT PREVIEW ---")
        print(final_state["final_report"][:600])
        print("...\n(Full report saved to outputs/)")

    return final_state


if __name__ == "__main__":
    # Run a hypothesis
    run_research(
        "Bitcoin drops in the 7 days following a US Federal Reserve "
        "interest rate hike announcement"
    )

    # Show the full graveyard after run
    print_graveyard()