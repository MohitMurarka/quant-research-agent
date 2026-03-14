from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import ResearchState
import json
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-5-mini")

REFINER_SYSTEM_PROMPT = """
You are a quantitative research strategist. Your job is to take a failed or weak 
financial hypothesis and refine it into a stronger, more testable one.

You will receive:
1. The original hypothesis
2. The analyst's verdict and issues
3. The analyst's suggested refinement
4. The iteration number

Your job is to produce a refined hypothesis that:
- Is specific and testable with price/volume data from yfinance
- Addresses the exact weaknesses the analyst identified
- Uses the same or related assets where possible
- Is meaningfully different from the original (not just rephrased)
- Has a realistic chance of showing a signal

Return a JSON object with exactly these fields:
{
    "refined_hypothesis": "the new hypothesis as a clear one-sentence statement",
    "assets": ["list", "of", "tickers"],
    "reasoning": "why this refinement is likely to perform better",
    "changes_made": ["list of specific changes from original hypothesis"]
}

Rules:
- refined_hypothesis must be a single, clear, testable sentence
- Assets must be valid yfinance tickers
- Do not just restate the original hypothesis with minor wording changes
- Return ONLY the JSON, no extra text
"""


def refiner_node(state: ResearchState) -> ResearchState:
    print("\n[REFINER] Generating refined hypothesis...")

    analysis = state.get("analysis", {})
    original_hypothesis = state["hypothesis"]
    current_hypothesis = state.get("refined_hypothesis") or original_hypothesis
    iteration = state.get("iteration", 0)

    messages = [
        SystemMessage(content=REFINER_SYSTEM_PROMPT),
        HumanMessage(
            content=f"""
Original hypothesis: {original_hypothesis}
Current hypothesis being tested: {current_hypothesis}

Analyst verdict: {analysis.get("verdict")}
Issues found: {analysis.get("issues")}
Strengths found: {analysis.get("strengths")}
Analyst suggestion: {analysis.get("suggested_refinement")}
Analyst reasoning: {analysis.get("reasoning")}

Iteration: {iteration}

Produce a refined hypothesis that fixes these issues.
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
        result = json.loads(content.strip())
    except json.JSONDecodeError:
        # Fallback if parsing fails
        result = {
            "refined_hypothesis": analysis.get(
                "suggested_refinement", current_hypothesis
            ),
            "assets": state["assets"],
            "reasoning": "Fallback refinement due to parse error",
            "changes_made": ["Used analyst suggestion directly"],
        }

    print(f"[REFINER] New hypothesis: {result['refined_hypothesis']}")
    print(f"[REFINER] Assets: {result['assets']}")
    print(f"[REFINER] Changes: {result['changes_made']}")

    return {
        **state,
        "refined_hypothesis": result["refined_hypothesis"],
        "assets": result["assets"],
        "status": "coding",
    }
