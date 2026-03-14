from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import ResearchState
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-5-mini")

REPORT_WRITER_SYSTEM_PROMPT = """
You are a professional quantitative research analyst writing a formal research report.

You will receive the full research session data: original hypothesis, all refined 
hypotheses tried, backtest results, and the analyst's verdict.

Write a professional markdown research report with these exact sections:

# Quantitative Research Report
## Executive Summary
## Research Hypothesis
## Methodology
## Results
## Statistical Analysis
## Risk Analysis
## Conclusion
## Appendix: Hypothesis Evolution

Guidelines:
- Be precise and honest — do not oversell weak results
- Use exact numbers from the backtest output
- The Hypothesis Evolution section should list every hypothesis tried and why it was refined
- Conclusion should clearly state whether the hypothesis is supported or not
- Write like a professional quant researcher, not a student
- If results are weak, say so clearly but explain what was learned
- If results are strong, explain the caveats clearly
- Length: 600-900 words
- Return ONLY the markdown, no extra text

"""


def report_writer_node(state: ResearchState) -> ResearchState:
    print("\n[REPORT WRITER] Generating research report...")

    # Build full research history
    original_hypothesis = state["hypothesis"]
    final_hypothesis = state.get("refined_hypothesis") or original_hypothesis
    analysis = state.get("analysis", {})
    execution_output = state.get("execution_result", {}).get("output", "")
    assets = state.get("assets", [])
    timeframe = state.get("timeframe", {})
    sub_questions = state.get("sub_questions", [])
    iteration = state.get("iteration", 0)
    verdict = analysis.get("verdict", "weak").upper()
    chart_saved = state.get("execution_result", {}).get("chart_saved", False)

    messages = [
        SystemMessage(content=REPORT_WRITER_SYSTEM_PROMPT),
        HumanMessage(
            content=f"""RESEARCH SESSION DATA:

Original Hypothesis: {original_hypothesis}
Final Hypothesis Tested: {final_hypothesis}
Assets Analyzed: {assets}
Timeframe: {timeframe.get('start')} to {timeframe.get('end')}
Total Iterations: {iteration}
Final Verdict: {verdict}

Sub-questions investigated:
{chr(10).join(f"- {q}" for q in sub_questions)}

Backtest Output:
{execution_output}

Analyst Assessment:
- Verdict: {verdict}
- Sharpe Ratio: {analysis.get('sharpe_ratio')}
- Trades Analyzed: {analysis.get('n_trades')}
- Win Rate: {analysis.get('win_rate')}
- Total Return: {analysis.get('total_return')}
- Max Drawdown: {analysis.get('max_drawdown')}
- Strengths: {analysis.get('strengths')}
- Issues: {analysis.get('issues')}
- Reasoning: {analysis.get('reasoning')}

Hypothesis Evolution (all versions tried):
1. Original: {original_hypothesis}
2. Final: {final_hypothesis}"""
        ),
    ]

    response = llm.invoke(messages)
    report = response.content.strip()

    # Save report to file
    os.makedirs("outputs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"outputs/research_report_{timestamp}.md"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
        if chart_saved:
            f.write("\n\n---\n*Chart: See backtest_chart.png in outputs directory*\n")
      
    print(f"[REPORT WRITER] Report saved to {report_path}")
    print(f"[REPORT WRITER] Verdict in report: {verdict}")

    return {
        **state,
        "final_report": report,
        "status": "done"
    }
      
