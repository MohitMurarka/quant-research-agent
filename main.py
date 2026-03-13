from dotenv import load_dotenv
from agents.planner import planner_node
from agents.code_writer import code_writer_node
from agents.executor import executor_node
from agents.analyst import analyst_node
from graph.state import ResearchState

load_dotenv()

initial_state: ResearchState = {
    "hypothesis": "Apple stock outperforms the S&P500 in the month after an iPhone launch",
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

# Linear pipeline for now
state = planner_node(initial_state)
state = code_writer_node(state)
state = executor_node(state)

# Retry loop
MAX_CODE_RETRIES = 3
while (
    not state["execution_result"]["success"] and state["iteration"] < MAX_CODE_RETRIES
):
    print(f"\n[RETRY] Code attempt {state['iteration'] + 1} of {MAX_CODE_RETRIES}")
    state = code_writer_node(state)
    state = executor_node(state)

# Analyst
if state["execution_result"]["success"]:
    state = analyst_node(state)

print("\n--- ANALYST RESULT ---")
print(f"Verdict: {state['analysis'].get('verdict', 'N/A').upper()}")
print(f"Status: {state['status']}")
print(f"Strengths: {state['analysis'].get('strengths')}")
print(f"Issues: {state['analysis'].get('issues')}")
print(f"Suggested refinement: {state['analysis'].get('suggested_refinement')}")
