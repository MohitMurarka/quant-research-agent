from dotenv import load_dotenv
from agents.planner import planner_node
from graph.state import ResearchState

load_dotenv()

# Create a minimal state with just a hypothesis
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
    "status": "planning"
}

# Run the planner
result = planner_node(initial_state)

print("\n--- PLANNER OUTPUT ---")
print("Sub-questions:")
for q in result["sub_questions"]:
    print(f"  - {q}")
print(f"Assets: {result['assets']}")
print(f"Timeframe: {result['timeframe']}")
print(f"Status: {result['status']}")