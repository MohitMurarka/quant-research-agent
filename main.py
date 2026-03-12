from dotenv import load_dotenv
from agents.planner import planner_node
from agents.code_writer import code_writer_node
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

# Step 1: Planner
state = planner_node(initial_state)

# Step 2: Code Writer
state = code_writer_node(state)

print("\n--- GENERATED CODE ---")
print(state["generated_code"])
