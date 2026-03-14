from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import ResearchState
import json
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-5-mini")

ANALYST_SYSTEM_PROMPT = """
You are a quantitative research analyst with deep expertise in statistics and financial markets.

Your job is to evaluate backtesting results and decide if they are statistically meaningful.

You will receive:
1. The hypothesis that was tested
2. The raw output from the backtest
3. The iteration number (how many times we've already tried)

You must return a JSON object with exactly these fields:
{
    "verdict": "strong" or "weak",
    "sharpe_ratio": float or null,
    "total_return": float or null,
    "win_rate": float or null,
    "n_trades": int or null,
    "max_drawdown": float or null,
    "issues": [list of specific problems found],
    "strengths": [list of specific strengths found],
    "reasoning": "detailed explanation of your verdict",
    "suggested_refinement": "if weak, suggest a specific modified hypothesis to test instead"
}

Verdict rules — mark as STRONG only if ALL of these are true:
- Sharpe ratio > 0.3 (or clearly trending positive)
- At least 10 trades/events analyzed
- Win rate > 50% (if applicable)
- Results are not obviously driven by a single outlier
- The output contains actual numeric results

Mark as WEAK if ANY of these are true:
- Fewer than 5 trades/events analyzed
- Sharpe ratio < 0 
- Results look like errors or placeholders
- Output is missing key metrics
- The hypothesis is too narrow to be testable

IMPORTANT: If iteration >= 2 and results are borderline, be more lenient.
Return ONLY the JSON, no extra text.
"""


def analyst_node(state: ResearchState) -> ResearchState:
    print("\n[ANALYST] Evaluating backtest results...")

    output = state["execution_result"].get("output", "")
    hypothesis = state.get("refined_hypothesis") or state["hypothesis"]
    iteration = state.get("iteration", 0)

    if not output:
        print("[ANALYST] No output to analyze - marking as weak")
        return {
            **state,
            "analysis": {
                "verdict": "weak",
                "issues": ["No output was produced by the backtest"],
                "strengths": [],
                "reasoning": "Empty output — code ran but produced no results",
                "suggested_refinement": "Simplify the hypothesis and ensure print statements exist",
                "sharpe_ratio": None,
                "total_return": None,
                "win_rate": None,
                "n_trades": None,
                "max_drawdown": None,
            },
            "status": "refining",
        }

    messages = [
        SystemMessage(content=ANALYST_SYSTEM_PROMPT),
        HumanMessage(
            content=f"""
        Hypothesis: {hypothesis}

Backtest Output:
{output}

Iteration: {iteration}
"""
        ),
    ]

    response = llm.invoke(messages)

    try:
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        analysis = json.loads(content.strip())
    except json.JSONDecodeError:
        analysis = {
            "verdict": "weak",
            "issues": ["Failed to parse analyst response"],
            "strengths": [],
            "reasoning": response.content,
            "suggested_refinement": "Retry with cleaner output format",
            "sharpe_ratio": None,
            "total_return": None,
            "win_rate": None,
            "n_trades": None,
            "max_drawdown": None,
        }

    verdict = analysis.get("verdict", "weak")

    print(f"[ANALYST] Verdict: {verdict.upper()}")
    print(f"[ANALYST] Sharpe Ratio: {analysis.get('sharpe_ratio')}")
    print(f"[ANALYST] Trades analyzed: {analysis.get('n_trades')}")
    print(f"[ANALYST] Issues: {analysis.get('issues')}")
    print(f"[ANALYST] Reasoning: {analysis.get('reasoning')}")

    if verdict == "strong":
        next_status = "reporting"
    else:
        next_status = "refining"
        print(f"[ANALYST] Suggested refinement: {analysis.get('suggested_refinement')}")

    return {**state, "analysis": analysis, "status": next_status}
