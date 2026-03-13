# Quant Research Agent

An AI-powered agent that converts financial hypotheses into structured quantitative research and automated strategy testing.

The system uses Large Language Models (LLMs) to transform a hypothesis into a research plan, identify relevant financial assets, retrieve historical market data, generate backtesting strategies, and safely execute them in a sandbox environment.

---

## Overview

Traditional quantitative research involves manually designing experiments, selecting assets, collecting historical data, and testing hypotheses.

This project automates that workflow using an **agent-based architecture**.

Given a financial hypothesis, the agent:

1. Breaks it into **testable research questions**
2. Identifies **relevant financial assets**
3. Selects a **statistically meaningful timeframe**
4. Retrieves **historical price and volume data**
5. Generates **quantitative strategy code**
6. Executes strategies in a **secure sandbox**
7. Analyzes the results for further research

---

## Example Hypothesis

Input:

```
Bitcoin tends to rise after halving events
```

Generated research plan:

Assets:

```
BTC-USD, SPY
```

Timeframe:

```
2016-01-01 → 2025-01-01
```

Research Questions:

- Does BTC show positive returns within 90 days after halving?
- Is trading volume higher after halving events?
- Does BTC outperform SPY after halving periods?

The agent then generates **Python backtesting code**, executes it, and analyzes the results.

---

## Architecture

The system is built using a **modular agent pipeline**.

```
Hypothesis
    ↓
Planner Agent
    ↓
Research Plan
    ↓
Market Data Fetcher
    ↓
Dataset Summary
    ↓
Strategy Code Generator
    ↓
Sandbox Executor (E2B)
    ↓
Result Analysis
```

Each stage operates as an independent node, enabling flexible and scalable research workflows.

---

## Tech Stack

- Python
- LangGraph
- LangChain
- OpenAI API
- yfinance
- pandas
- numpy
- E2B sandbox for secure code execution

---

## Setup

Clone the repository

```
git clone https://github.com/yourusername/quant-research-agent.git
cd quant-research-agent
```

Create a virtual environment

```
python -m venv venv
```

Activate it

Windows

```
venv\Scripts\activate
```

Mac/Linux

```
source venv/bin/activate
```

Install dependencies

```
pip install -r requirements.txt
```

Create a `.env` file

```
OPENAI_API_KEY=your_api_key
E2B_API_KEY=your_e2b_key
```

Run the project

```
python main.py
```

---

## Project Structure

```
quant-research-agent
│
├── graph
│   └── state.py
│
├── nodes
│   ├── planner_node.py
│   ├── code_writer_node.py
│   ├── executor_node.py
│   └── analysis_node.py
│
├── tools
│   └── fetch_data.py
│
├── main.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## Status

🚧 Work in progress — upcoming improvements include:

- portfolio-level strategy testing
- performance visualization
- automated strategy improvement (reflection agents)
- risk and factor analysis
