import os
from langgraph.graph import StateGraph, END
from graph.state import ResearchState
from agents.planner import planner_node
from agents.code_writer import code_writer_node
from agents.executor import executor_node
from agents.analyst import analyst_node
from agents.refiner import refiner_node
from agents.report_writer import report_writer_node
from agents.human_review import human_review_node

MAX_CODE_RETRIES = 4
MAX_REFINEMENTS = int(os.environ.get("MAX_REFINEMENTS", 2))


def route_after_human(state: ResearchState) -> str:
    """After human review: approved → code, skipped → end."""
    if state.get("human_approved"):
        return "code_writer"
    return "report_writer"


def route_after_executor(state: ResearchState) -> str:
    success = state["execution_result"].get("success", False)
    iteration = state.get("iteration", 0)
    if success:
        return "analyst"
    elif iteration < MAX_CODE_RETRIES:
        print(f"\n[GRAPH] Code failed — retrying (attempt {iteration + 1})")
        return "code_writer"
    else:
        print("\n[GRAPH] Max code retries reached — writing report on best effort")
        return "report_writer"


def route_after_analyst(state: ResearchState) -> str:
    verdict = state["analysis"].get("verdict", "weak")
    iteration = state.get("iteration", 0)
    if verdict == "strong":
        print("\n[GRAPH] Strong verdict — writing report")
        return "report_writer"
    elif iteration <= MAX_REFINEMENTS * MAX_CODE_RETRIES:
        print(f"\n[GRAPH] Weak verdict — refining hypothesis")
        return "refiner"
    else:
        print("\n[GRAPH] Max refinements reached — writing report on best results")
        return "report_writer"


def route_after_refiner(state: ResearchState) -> str:
    return "code_writer"


def build_graph() -> StateGraph:
    graph = StateGraph(ResearchState)

    graph.add_node("planner", planner_node)
    graph.add_node("human_review", human_review_node)
    graph.add_node("code_writer", code_writer_node)
    graph.add_node("executor", executor_node)
    graph.add_node("analyst", analyst_node)
    graph.add_node("refiner", refiner_node)
    graph.add_node("report_writer", report_writer_node)

    graph.set_entry_point("planner")

    # Planner → human review (new)
    graph.add_edge("planner", "human_review")

    # Human review → conditional
    graph.add_conditional_edges(
        "human_review",
        route_after_human,
        {
            "code_writer": "code_writer",
            "report_writer": "report_writer",
        },
    )

    graph.add_edge("code_writer", "executor")
    graph.add_edge("report_writer", END)

    graph.add_conditional_edges(
        "executor",
        route_after_executor,
        {
            "analyst": "analyst",
            "code_writer": "code_writer",
            "report_writer": "report_writer",
        },
    )

    graph.add_conditional_edges(
        "analyst",
        route_after_analyst,
        {
            "report_writer": "report_writer",
            "refiner": "refiner",
        },
    )

    graph.add_conditional_edges(
        "refiner", route_after_refiner, {"code_writer": "code_writer"}
    )

    return graph.compile()
