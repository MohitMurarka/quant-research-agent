from langgraph.graph import StateGraph, END
from graph.state import ResearchState
from agents.planner import planner_node
from agents.code_writer import code_writer_node
from agents.executor import executor_node
from agents.analyst import analyst_node
from agents.refiner import refiner_node
from agents.report_writer import report_writer_node

# ── Constants ────────────────────────────────────────────────
MAX_CODE_RETRIES = 4
MAX_REFINEMENTS = 2

# ── Routing functions (pure logic, no LLM) ───────────────────


def route_after_executor(state: ResearchState) -> str:
    """After executor: did the code succeed?"""
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
    """After analyst: strong → report, weak → refine or report."""
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
    """After refiner: always go back to code writer with new hypothesis."""
    return "code_writer"


# ── Build the graph ───────────────────────────────────────────


def build_graph() -> StateGraph:
    graph = StateGraph(ResearchState)

    # Add all nodes
    graph.add_node("planner", planner_node)
    graph.add_node("code_writer", code_writer_node)
    graph.add_node("executor", executor_node)
    graph.add_node("analyst", analyst_node)
    graph.add_node("refiner", refiner_node)
    graph.add_node("report_writer", report_writer_node)

    # Entry point
    graph.set_entry_point("planner")

    # Fixed edges
    graph.add_edge("planner", "code_writer")
    graph.add_edge("code_writer", "executor")
    graph.add_edge("report_writer", END)

    # Conditional edges
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
        "refiner",
        route_after_refiner,
        {
            "code_writer": "code_writer",
        },
    )

    return graph.compile()
