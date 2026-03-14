import sqlite3
import json
import os
from datetime import datetime

DB_PATH = "outputs/graveyard.db"


def init_db():
    os.makedirs("outputs", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS hypothesis_graveyard (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            original_hypothesis TEXT NOT NULL,
            final_hypothesis TEXT NOT NULL,
            assets TEXT,
            timeframe_start TEXT,
            timeframe_end TEXT,
            verdict TEXT NOT NULL,
            sharpe_ratio REAL,
            total_return REAL,
            win_rate REAL,
            n_trades INTEGER,
            max_drawdown REAL,
            iterations INTEGER,
            issues TEXT,
            strengths TEXT,
            reasoning TEXT,
            suggested_refinement TEXT,
            report_path TEXT
        )
    """
    )
    conn.commit()
    conn.close()


def log_to_graveyard(state: dict, report_path: str = None) -> int:
    """Log a completed research session to graveyard.Returns the row id."""
    init_db()

    analysis = state.get("analysis", {})
    timeframe = state.get("timeframe", {})

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO hypothesis_graveyard (
            timestamp, original_hypothesis, final_hypothesis,
            assets, timeframe_start, timeframe_end,
            verdict, sharpe_ratio, total_return, win_rate,
            n_trades, max_drawdown, iterations,
            issues, strengths, reasoning,
            suggested_refinement, report_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   """,
        (
            datetime.now().isoformat(),
            state.get("hypothesis", ""),
            state.get("refined_hypothesis") or state.get("hypothesis", ""),
            json.dumps(state.get("assets", [])),
            timeframe.get("start", ""),
            timeframe.get("end", ""),
            analysis.get("verdict", "weak"),
            analysis.get("sharpe_ratio"),
            analysis.get("total_return"),
            analysis.get("win_rate"),
            analysis.get("n_trades"),
            analysis.get("max_drawdown"),
            state.get("iteration", 0),
            json.dumps(analysis.get("issues", [])),
            json.dumps(analysis.get("strengths", [])),
            analysis.get("reasoning", ""),
            analysis.get("suggested_refinement", ""),
            report_path or "",
        ),
    )

    row_id = cursor.lastrowid
    conn.commit()
    conn.close()

    print(
        f"[GRAVEYARD] Logged to graveyard (id={row_id}, verdict={analysis.get('verdict', 'weak').upper()})"
    )
    return row_id


def get_graveyard_summary() -> str:
    """Returns a plain text summary of all past research for the LLM to read."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT original_hypothesis, final_hypothesis, verdict,
               sharpe_ratio, total_return, n_trades, reasoning,
               suggested_refinement, timestamp
        FROM hypothesis_graveyard
        ORDER BY timestamp DESC
        LIMIT 20
    """
    )

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "No previous research found."

    lines = [f"=== HYPOTHESIS GRAVEYARD ({len(rows)} entries) ===\n"]
    for i, row in enumerate(rows, 1):
        orig, final, verdict, sharpe, ret, trades, reasoning, suggestion, ts = row
        lines.append(f"Entry {i} [{ts[:10]}]")
        lines.append(f"  Original: {orig[:100]}")
        lines.append(f"  Final:    {final[:100]}")
        lines.append(f"  Verdict:  {verdict.upper()}")
        lines.append(f"  Sharpe:   {sharpe} | Return: {ret}% | Trades: {trades}")
        lines.append(f"  Reason:   {reasoning[:150]}...")
        lines.append(
            f"  Next suggestion: {suggestion[:150] if suggestion else 'N/A'}..."
        )
        lines.append("")

    return "\n".join(lines)


def get_past_hypotheses() -> list[str]:
    """Returns list of all hypotheses ever tested — to avoid repeating them."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT original_hypothesis, final_hypothesis FROM hypothesis_graveyard"
    )
    rows = cursor.fetchall()
    conn.close()
    return [h for pair in rows for h in pair if h]


def print_graveyard():
    """Pretty-prints the full graveyard to terminal."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, timestamp, original_hypothesis, verdict,
               sharpe_ratio, total_return, iterations
        FROM hypothesis_graveyard
        ORDER BY timestamp DESC
    """
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("Graveyard is empty.")
        return

    print(f"\n{'='*70}")
    print(f"{'HYPOTHESIS GRAVEYARD':^70}")
    print(f"{'='*70}")
    print(
        f"{'ID':<4} {'Date':<12} {'Verdict':<8} {'Sharpe':<8} {'Return':<10} {'Iter':<6} Hypothesis"
    )
    print(f"{'-'*70}")

    for row in rows:
        id_, ts, hyp, verdict, sharpe, ret, iters = row
        sharpe_str = f"{sharpe:.3f}" if sharpe is not None else "N/A"
        ret_str = f"{ret:.1f}%" if ret is not None else "N/A"
        hyp_short = hyp[:40] + "..." if len(hyp) > 40 else hyp
        print(
            f"{id_:<4} {ts[:10]:<12} {verdict.upper():<8} {sharpe_str:<8} {ret_str:<10} {iters:<6} {hyp_short}"
        )

    print(f"{'='*70}\n")
