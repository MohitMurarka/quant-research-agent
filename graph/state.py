from typing import TypedDict, Optional


class ResearchState(TypedDict):
    hypothesis: str  # original user input
    sub_questions: list[str]  # planner output
    assets: list[str]  # e.g. ["TSLA", "AAPL"]
    timeframe: dict  # {"start": "2020-01-01", "end": "2024-01-01"}
    generated_code: str  # code writer output
    execution_result: dict  # {"success": bool, "output": ..., "error": ...}
    analysis: dict  # {"sharpe": float, "verdict": "strong"/"weak"}
    iteration: int  # refinement loop counter
    refined_hypothesis: str  # updated hypothesis from refiner
    final_report: str  # final markdown report
    status: str  # "planning" | "coding" | "executing" | "analysing" | "refining" | "reporting" | "done"
