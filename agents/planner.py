from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import ResearchState
from tools.graveyard import get_graveyard_summary, get_past_hypotheses
import json
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-5-mini")

PLANNER_SYSTEM_PROMPT = """
You are a quantitative research planner. Your job is to take a financial hypothesis
and break it down into a structured research plan.

Given a hypothesis, you must return a JSON object with exactly these fields:
{
    "sub_questions": [list of 2-4 specific testable questions],
    "assets": [list of ticker symbols to analyze, e.g. "TSLA", "BTC-USD", "SPY"],
    "timeframe": {
        "start": "YYYY-MM-DD",
        "end": "YYYY-MM-DD"
    },
    "reasoning": "brief explanation of your plan"
}

Rules:
- Assets must be valid yfinance ticker symbols
- Timeframe MUST span at least 10 years to ensure enough events for statistical significance
- Start date must be no later than 2010-01-01
- End date should be 2024-01-01
- Sub-questions must be specific and testable with price/volume data
- If past research is provided, do NOT repeat the same assets and timeframe combinations
- Return ONLY the JSON, no extra text
"""


def planner_node(state: ResearchState) -> ResearchState:
    print("\n[PLANNER] Breaking down hypothesis...")

    # Load graveyard context so planner avoids repeating past work
    past_summary = get_graveyard_summary()
    past_hypotheses = get_past_hypotheses()

    hypothesis = state["hypothesis"]

    user_content = f"""Hypothesis: {hypothesis}

PAST RESEARCH HISTORY (avoid repeating these exact approaches):
{past_summary}
"""

    if past_hypotheses:
        user_content += f"""
Previously tested hypotheses (do not repeat):
{chr(10).join(f'- {h[:120]}' for h in past_hypotheses[:10])}
"""

    messages = [
        SystemMessage(content=PLANNER_SYSTEM_PROMPT),
        HumanMessage(content=user_content)
    ]

    response = llm.invoke(messages)

    try:
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        plan = json.loads(content.strip())
    except json.JSONDecodeError:
        import re
        match = re.search(r'\{.*\}', response.content, re.DOTALL)
        if match:
            plan = json.loads(match.group())
        else:
            raise ValueError(f"Planner failed to return valid JSON: {response.content}")

    print(f"[PLANNER] Assets identified: {plan['assets']}")
    print(f"[PLANNER] Timeframe: {plan['timeframe']['start']} to {plan['timeframe']['end']}")
    print(f"[PLANNER] Sub-questions: {len(plan['sub_questions'])} questions")
    print(f"[PLANNER] Reasoning: {plan['reasoning']}")

    return {
        **state,
        "sub_questions": plan["sub_questions"],
        "assets":        plan["assets"],
        "timeframe":     plan["timeframe"],
        "status":        "coding"
    }