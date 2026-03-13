from dotenv import load_dotenv
from agents.planner import planner_node
from agents.code_writer import code_writer_node
from agents.executor import executor_node
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

state = planner_node(initial_state)
state = code_writer_node(state)
state = executor_node(state)

# --- RETRY LOOP (max 3 attempts) ---
MAX_RETRIES = 3
while not state["execution_result"]["success"] and state["iteration"] < MAX_RETRIES:
    print(f"\n[RETRY] Attempt {state['iteration'] + 1} of {MAX_RETRIES}")
    state = code_writer_node(state)  # Code Writer sees the error and fixes it
    state = executor_node(state)

print("\n--- FINAL RESULT ---")
print(f"Success: {state['execution_result']['success']}")
print(f"Attempts: {state['iteration']}")

if state["execution_result"]["success"]:
    print("\nOutput:")
    print(state["execution_result"]["output"])
    print(f"Chart saved: {state['execution_result']['chart_saved']}")
else:
    print("Failed after max retries.")
    print(state["execution_result"]["error"])
