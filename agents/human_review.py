import os
import sys
from graph.state import ResearchState


def human_review_node(state: ResearchState) -> ResearchState:
    """
    Pauses execution and asks the human to approve the research plan.
    The human can: approve, edit assets/timeframe, or cancel.
    Skipped entirely if AUTO_APPROVE env var is set to 1.
    """

    # ── Auto-approve mode ─────────────────────────────────────
    if os.environ.get("AUTO_APPROVE") == "1":
        print("\n[HUMAN] Auto-approved (--auto-approve flag set)")
        return {
            **state,
            "human_approved": True,
            "human_feedback": "auto",
            "status": "coding",
        }

    print(f"\n{'='*60}")
    print("HUMAN REVIEW — Research Plan")
    print(f"{'='*60}")
    print(f"\nHypothesis : {state.get('refined_hypothesis') or state['hypothesis']}")
    print(f"Assets     : {state['assets']}")
    print(
        f"Timeframe  : {state['timeframe'].get('start')} to {state['timeframe'].get('end')}"
    )
    print(f"\nSub-questions:")
    for i, q in enumerate(state["sub_questions"], 1):
        print(f"  {i}. {q}")

    print(f"\n{'─'*60}")
    print("Options:")
    print("  [Enter]  Approve and continue")
    print("  [e]      Edit assets or timeframe")
    print("  [s]      Skip this hypothesis")
    print("  [q]      Quit")
    print(f"{'─'*60}")

    while True:
        choice = input("\nYour choice: ").strip().lower()

        # ── Approve ──────────────────────────────────────────
        if choice == "":
            print("\n[HUMAN] Plan approved — starting research...")
            return {
                **state,
                "human_approved": True,
                "human_feedback": "approved",
                "status": "coding",
            }

        # ── Edit ─────────────────────────────────────────────
        elif choice == "e":
            print("\nEdit mode. Press Enter to keep current value.\n")

            current_assets = ", ".join(state["assets"])
            new_assets_str = input(f"Assets [{current_assets}]: ").strip()
            new_assets = (
                [a.strip().upper() for a in new_assets_str.split(",")]
                if new_assets_str
                else state["assets"]
            )

            current_start = state["timeframe"].get("start", "")
            new_start = (
                input(f"Start date [{current_start}]: ").strip() or current_start
            )

            current_end = state["timeframe"].get("end", "")
            new_end = input(f"End date [{current_end}]: ").strip() or current_end

            print(f"\nSub-questions (press Enter to keep all current):")
            edit_q = input("Edit sub-questions? [y/N]: ").strip().lower()
            new_questions = state["sub_questions"]
            if edit_q == "y":
                new_questions = []
                print("Enter sub-questions one by one. Empty line to finish:")
                while True:
                    q = input(f"  Q{len(new_questions)+1}: ").strip()
                    if not q:
                        break
                    new_questions.append(q)
                if not new_questions:
                    new_questions = state["sub_questions"]

            print(f"\n[HUMAN] Updated plan:")
            print(f"  Assets    : {new_assets}")
            print(f"  Timeframe : {new_start} to {new_end}")
            print(f"  Questions : {len(new_questions)} sub-questions")

            confirm = input("\nConfirm and continue? [Y/n]: ").strip().lower()
            if confirm != "n":
                print("\n[HUMAN] Edited plan approved — starting research...")
                return {
                    **state,
                    "assets": new_assets,
                    "timeframe": {"start": new_start, "end": new_end},
                    "sub_questions": new_questions,
                    "human_approved": True,
                    "human_feedback": "edited",
                    "status": "coding",
                }

        # ── Skip ─────────────────────────────────────────────
        elif choice == "s":
            print("\n[HUMAN] Hypothesis skipped.")
            return {
                **state,
                "human_approved": False,
                "human_feedback": "skipped",
                "status": "done",
            }

        # ── Quit ─────────────────────────────────────────────
        elif choice == "q":
            print("\n[HUMAN] Quitting.")
            sys.exit(0)

        else:
            print(
                "Invalid choice. Press Enter to approve, 'e' to edit, 's' to skip, 'q' to quit."
            )
