from dotenv import load_dotenv
from agents.planner import planner_node
from agents.code_writer import code_writer_node
from agents.executor import executor_node
from agents.analyst import analyst_node
from agents.refiner import refiner_node
from graph.state import ResearchState

load_dotenv()

initial_state: ResearchState = {
    "hypothesis": "US equity momentum — buying SPY when it has positive returns over the prior 3 consecutive months generates better risk-adjusted returns than buy-and-hold SPY",
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
}

MAX_CODE_RETRIES = 4
MAX_REFINEMENTS = 2

# Step 1: Plan once
state = planner_node(initial_state)

# Step 2: Research loop
for refinement_round in range(MAX_REFINEMENTS + 1):
    print(f"\n{'='*50}")
    print(f"RESEARCH ROUND {refinement_round + 1}")
    print(f"Hypothesis: {state.get('refined_hypothesis') or state['hypothesis']}")
    print(f"{'='*50}")

    # Code → Execute loop
    state = code_writer_node(state)
    state = executor_node(state)

    # Retry on code errors
    retries = 0
    while not state["execution_result"]["success"] and retries < MAX_CODE_RETRIES:
        retries += 1
        print(f"\n[RETRY] Code attempt {retries + 1} of {MAX_CODE_RETRIES}")
        state = code_writer_node(state)
        state = executor_node(state)

    # Analyse results
    if state["execution_result"]["success"]:
        state = analyst_node(state)
    else:
        print("\n[PIPELINE] Code failed after max retries — stopping")
        break

    # Check verdict
    if state["analysis"].get("verdict") == "strong":
        print("\n[PIPELINE] Strong results — proceeding to report")
        break
    elif refinement_round < MAX_REFINEMENTS:
        print(
            f"\n[PIPELINE] Weak results — refining hypothesis (round {refinement_round + 1})"
        )
        state = refiner_node(state)
    else:
        print("\n[PIPELINE] Max refinements reached — reporting best results found")

print("\n--- PIPELINE COMPLETE ---")
print(f"Final hypothesis: {state.get('refined_hypothesis') or state['hypothesis']}")
print(f"Final verdict: {state['analysis'].get('verdict', 'N/A').upper()}")
print(f"Final status: {state['status']}")
