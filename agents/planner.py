from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import ResearchState
import json
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o", temperature=0)

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
- Timeframe should be at least 2 years for statistical significance
- Sub-questions must be specific and testable with price/volume data
- Return ONLY the JSON, no extra text
"""


def planner_node(state: ResearchState) -> ResearchState:
    print("\n[PLANNER] Breaking down hypothesis...")

    hypothesis = state["hypothesis"]

    messages = [
        SystemMessage(content=PLANNER_SYSTEM_PROMPT),
        HumanMessage(content=f"Hypothesis: {hypothesis}"),
    ]

    response = llm.invoke(messages)

    try:
        plan = json.loads(response.content) #This converts text → Python dictionary.
    except json.JSONDecodeError:
        # Sometimes LLM wraps in ```json ... ``` so we clean it up
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        plan = json.loads(content.strip())

    print(f"[PLANNER] Assets identified: {plan['assets']}")
    print(
        f"[PLANNER] Timeframe: {plan['timeframe']['start']} to {plan['timeframe']['end']}"
    )
    print(f"[PLANNER] Sub-questions: {len(plan['sub_questions'])} questions")
    print(f"[PLANNER] Reasoning: {plan['reasoning']}")

    return {
        **state, #This merges the new plan into the state.So basically updayes the changes in the original state
        "sub_questions": plan["sub_questions"],
        "assets": plan["assets"],
        "timeframe": plan["timeframe"],
        "status": "coding",
    }
