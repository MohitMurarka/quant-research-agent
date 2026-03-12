# Quant Research Agent

An AI-powered agent that converts financial hypotheses into structured quantitative research.

The system uses Large Language Models (LLMs) to transform a hypothesis into a research plan, identify relevant financial assets, retrieve historical market data, and prepare datasets for quantitative analysis.

---

## Overview

Traditional quantitative research involves manually designing experiments, selecting assets, collecting historical data, and testing hypotheses. This project automates that workflow using an agent-based architecture.

Given a financial hypothesis, the agent:

1. Breaks it into **testable research questions**
2. Identifies **relevant financial assets**
3. Selects a **statistically meaningful timeframe**
4. Retrieves **historical price and volume data**
5. Prepares the data for further analysis

---

## Example Hypothesis

Input:

```
Bitcoin tends to rise after halving events
```

Generated research plan:

* Assets: `BTC-USD`, `SPY`
* Timeframe: `2016-01-01 → 2025-01-01`
* Research Questions:

  * Does BTC show positive returns within 90 days after halving?
  * Is trading volume higher after halving events?
  * Does BTC outperform SPY after halving periods?

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
Data Collection
    ↓
Market Dataset
    ↓
Quantitative Analysis
```

Each stage operates as an independent node, enabling flexible and scalable research workflows.

---

## Tech Stack

* Python
* LangGraph
* LangChain
* OpenAI API
* yfinance
* pandas
* numpy

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
│   └── planner_node.py
│
├── main.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## Status

🚧 Work in progress — additional agents for data analysis, visualization, and automated research reporting are planned.
