from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import ResearchState
from tools.fetch_data import fetch_summary
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o", temperature=0.2)

CODE_WRITER_SYSTEM_PROMPT = """
You are an expert quantitative analyst and Python programmer.
Your job is to write clean, correct Python backtesting code to test a financial hypothesis.

You will be given:
1. The hypothesis to test
2. Specific sub-questions to answer
3. A summary of available data (tickers, columns, date range)
4. Any previous error (if this is a retry)

You must write Python code that:
- Uses yfinance to download data directly (do NOT use pre-loaded variables)
- Tests the hypothesis rigorously
- Calculates these metrics where relevant:
    * Total return (%)
    * Annualized return (%)
    * Sharpe ratio (use risk-free rate of 0.04)
    * Maximum drawdown (%)
    * Win rate (% of profitable trades)
    * Number of trades
- Prints a clear results section at the end like this:
    print("=== RESULTS ===")
    print(f"Total Return: {total_return:.2f}%")
    print(f"Sharpe Ratio: {sharpe:.3f}")
    print(f"Max Drawdown: {max_dd:.2f}%")
    print(f"Win Rate: {win_rate:.2f}%")
    print(f"Number of Trades: {n_trades}")
    print(f"Annualized Return: {ann_return:.2f}%")
- Saves one matplotlib chart as 'outputs/backtest_chart.png'
- Has NO syntax errors
- Uses only these libraries: yfinance, pandas, numpy, matplotlib, scipy

CRITICAL RULES:
- Return ONLY the Python code, no explanation, no markdown backticks
- All data must be downloaded inside the code using yfinance
- Always handle edge cases (empty data, division by zero)
- The code must be fully self-contained and runnable as-is

NUMPY / SCIPY RULES — MANDATORY:
- ALWAYS wrap scipy stats results in float() immediately at assignment:
    CORRECT:   t_stat = float(scipy.stats.ttest_ind(a, b).statistic)
    CORRECT:   p_value = float(scipy.stats.ttest_ind(a, b).pvalue)
    WRONG:     t_stat = scipy.stats.ttest_ind(a, b).statistic
- NEVER use :.Xf formatting on a variable that might be a numpy array
- For ANY variable you plan to format with :.2f or :.3f, cast it to float() first
- When using .loc[] with dates, NEVER use exact timestamps — always use .iloc[] 
  or slice with .loc[start:end] to avoid KeyError on non-trading days
- Use df.index.asof(date) to find the nearest trading day to a given date
"""


def code_writer_node(state: ResearchState) -> ResearchState:
    print("\n[CODE WRITER] Writing backtesting code...")

    # Get data summary so LLM knows what's available
    data_summary = fetch_summary(
        state["assets"], state["timeframe"]["start"], state["timeframe"]["end"]
    )

    # Use refined hypothesis if we're in a retry loop
    hypothesis = state.get("refined_hypothesis") or state["hypothesis"]
    iteration = state.get("iteration", 0)

    # Build the prompt
    user_content = f"""
Hypothesis: {hypothesis}

Sub-questions to answer:
{chr(10).join(f"- {q}" for q in state["sub_questions"])}

Data available:
{data_summary}

Iteration: {iteration + 1}
"""

    # If this is a retry, include the previous error with explicit fix instructions
    if iteration > 0 and state.get("execution_result", {}).get("error"):
        user_content += f"""
PREVIOUS ATTEMPT FAILED. You must fix this specific error:

ERROR:
{state["execution_result"]["error"]}

ROOT CAUSE HINTS:
1. If the error is "unsupported format string passed to numpy.ndarray.__format__":
   - A numpy array is being formatted with :.Xf instead of a scalar
   - Fix: wrap ALL scipy/numpy results in float() at assignment time
   - Example: t_stat = float(scipy.stats.ttest_ind(a, b).statistic)

2. If the error is a KeyError with a Timestamp:
   - You used .loc[exact_date] but that date is not a trading day
   - Fix: use df.index.asof(pd.Timestamp(date)) to get nearest trading day
   - Or use .loc[start:end] slicing instead of exact date lookup

3. If the error is about MultiIndex columns from yfinance:
   - Fix: after downloading, flatten with df.columns = df.columns.get_level_values(0)

PREVIOUS BROKEN CODE:
{state["generated_code"]}

Write the COMPLETE fixed code from scratch. Do not repeat the same mistake.
"""

    messages = [
        SystemMessage(content=CODE_WRITER_SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]

    response = llm.invoke(messages)
    code = response.content.strip()

    # Strip markdown backticks if LLM added them anyway
    if code.startswith("```"):
        lines = code.split("\n")
        code = "\n".join(lines[1:-1])
        if code.startswith("python"):
            code = code[6:].strip()

    print(f"[CODE WRITER] Code generated ({len(code.splitlines())} lines)")

    return {**state, "generated_code": code, "status": "executing"}