# ⚡ Autonomous Quant Research Agent

An end-to-end agentic AI system that autonomously researches financial hypotheses — writing backtesting code, executing it in a secure sandbox, evaluating results statistically, refining weak hypotheses, and generating professional research reports.

Built with **LangGraph**, **GPT-4o**, **E2B**, and **React**.

---

## Demo

> _"Gold prices rise when the US dollar weakens"_

The system autonomously:

1. Plans the research approach and identifies relevant assets
2. Writes Python backtesting code from scratch
3. Executes it securely in an isolated cloud sandbox
4. Evaluates statistical significance (Sharpe ratio, p-values, bootstrap CIs)
5. Refines the hypothesis if results are weak
6. Generates a professional markdown research report
7. Logs everything to a persistent Hypothesis Graveyard

![Research Tab](docs/screenshot_research.png)
![Graveyard Tab](docs/screenshot_graveyard.png)

---

## Architecture

```
User Hypothesis
      │
      ▼
┌─────────────┐     ┌──────────────┐
│   Planner   │────▶│ Human Review │  (approve / edit / skip)
└─────────────┘     └──────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │ Code Writer  │◀──────────────┐
                    └──────────────┘               │
                            │                      │ fix error
                            ▼                      │
                    ┌──────────────┐               │
                    │   Executor   │───── fail ────┘
                    │  (E2B Sand.) │
                    └──────────────┘
                            │ success
                            ▼
                    ┌──────────────┐
                    │   Analyst    │────── strong ──▶ Report Writer ──▶ END
                    └──────────────┘
                            │ weak
                            ▼
                    ┌──────────────┐
                    │   Refiner    │──▶ Code Writer (new hypothesis)
                    └──────────────┘
```

### Agent Roles

| Agent             | Responsibility                                                                                                                      |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| **Planner**       | Breaks hypothesis into sub-questions, selects assets and timeframe. Reads past research from the Graveyard to avoid repeating work. |
| **Human Review**  | Pauses execution so the user can approve, edit, or reject the research plan before any code is written.                             |
| **Code Writer**   | Writes self-contained Python backtesting code. Receives error messages on failure and auto-fixes.                                   |
| **Executor**      | Runs code in an E2B cloud sandbox. LLM-generated code never touches the host filesystem.                                            |
| **Analyst**       | Evaluates results statistically — Sharpe ratio, win rate, p-values, drawdown. Returns `strong` or `weak` verdict.                   |
| **Refiner**       | If results are weak, produces a meaningfully different hypothesis and sends the system back to Code Writer.                         |
| **Report Writer** | Generates a professional markdown research report and logs the session to the Hypothesis Graveyard.                                 |

---

## Key Design Decisions

**Why LangGraph?**
LangGraph allows defining the agent workflow as a stateful graph with conditional edges. The retry loop (Executor → Code Writer on failure) and the refinement loop (Analyst → Refiner → Code Writer on weak results) are first-class graph constructs — not hardcoded Python loops.

**Why E2B for code execution?**
LLM-generated code is untrusted by definition. Running it with `exec()` or `subprocess` on the host machine is a security risk. E2B executes each backtest in an isolated cloud VM that cannot access the host filesystem or network. This is the production-grade approach used by systems like Cognition/Devin.

**Why a Hypothesis Graveyard?**
Most financial hypotheses don't hold in data — that's real finance, not a bug. The Graveyard gives the system persistent memory across sessions. The Planner reads past research before starting, avoiding repeated approaches. Over time the system builds an institutional knowledge base of what has and hasn't worked.

**Why human-in-the-loop?**
Fully autonomous agents make mistakes at the planning stage that propagate through the entire pipeline. Pausing after the Planner to show the user the research plan (assets, timeframe, sub-questions) before writing any code catches these mistakes cheaply. The user can edit or reject the plan without wasting API calls on a bad backtest.

---

## Tech Stack

| Layer               | Technology                    |
| ------------------- | ----------------------------- |
| Agent Orchestration | LangGraph                     |
| LLM                 | GPT-4o (OpenAI)               |
| Code Execution      | E2B Cloud Sandbox             |
| Financial Data      | yfinance                      |
| Backend API         | FastAPI                       |
| Frontend            | React                         |
| Persistent Memory   | SQLite (Hypothesis Graveyard) |
| Backtesting         | pandas, numpy, scipy          |
| Charts              | matplotlib                    |

---

## Project Structure

```
quant-research-agent/
│
├── agents/                  # One file per agent
│   ├── planner.py
│   ├── code_writer.py
│   ├── executor.py
│   ├── analyst.py
│   ├── refiner.py
│   ├── report_writer.py
│   └── human_review.py
│
├── graph/
│   ├── state.py             # LangGraph state schema
│   └── graph.py             # Graph definition + routing functions
│
├── tools/
│   ├── fetch_data.py        # yfinance data fetcher
│   ├── graveyard.py         # SQLite persistence layer
│   └── streaming.py         # Terminal streaming output
│
├── api/
│   └── main.py              # FastAPI backend
│
├── outputs/                 # Generated reports + charts
├── main.py                  # CLI entry point
└── quant-frontend/          # React frontend
```

---

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API key
- E2B API key (free tier at [e2b.dev](https://e2b.dev))

### Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/quant-research-agent
cd quant-research-agent

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Add your OPENAI_API_KEY and E2B_API_KEY to .env
```

### Running

```bash
# Terminal 1 — Start the API
uvicorn api.main:app --reload --port 8000

# Terminal 2 — Start the frontend
cd quant-frontend
npm install
npm start

# Or use the CLI directly
python main.py "Gold rises when the dollar weakens"
python main.py "SPY momentum strategy" --auto-approve --max-refinements 3
python main.py --graveyard
```

---

## CLI Usage

```bash
# Run a hypothesis interactively (shows plan, waits for approval)
python main.py "your hypothesis here"

# Skip human review
python main.py "your hypothesis here" --auto-approve

# More refinement rounds
python main.py "your hypothesis here" --max-refinements 3

# View all past research
python main.py --graveyard

# Quiet mode
python main.py "your hypothesis here" --auto-approve --quiet
```

---

## Example Hypotheses to Try

```
"Gold rises when the US dollar weakens"
"Bitcoin drops in the 7 days after a Fed rate hike"
"SPY outperforms in January every year"
"Tesla stock drops in the week after Elon Musk tweets"
"VIX spikes above 30 predict market recoveries"
"Apple outperforms the S&P500 after iPhone launches"
```

---

## What I Learned

Building this taught me several things that tutorials don't cover:

**Agentic loops are hard to debug.** When an agent fails 3 iterations in, the error might have originated in the Planner's choice of assets. Understanding how state propagates through a LangGraph is essential.

**LLM-generated code fails in consistent, fixable ways.** The same numpy/pandas errors appeared repeatedly. The solution was making error messages more explicit and adding domain-specific fix hints to the Code Writer's retry prompt.

**Most financial hypotheses don't hold in data.** This isn't a bug — it's the point. A system that rigorously tests and rejects hypotheses is more valuable than one that confirms them. The Hypothesis Graveyard turned this insight into a feature.

**Human-in-the-loop is a design pattern, not a fallback.** Inserting a human approval step after planning and before execution is architecturally significant. It separates reasoning from action, which is the right boundary for agentic systems.

---

## License

MIT
