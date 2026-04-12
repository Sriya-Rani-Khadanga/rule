"""
CLI runner: load a demo scenario, validate, detect conflicts, resolve, print metrics.

Run from repository root:
  python main.py       # default scenario A
  python main.py B
  python main.py C
"""
import os
import sys

_ROOT = os.path.dirname(os.path.abspath(__file__))
_FRONTEND = os.path.join(_ROOT, "frontend")
for _p in (_ROOT, _FRONTEND):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from logic import detect_conflicts, resolve, claim_score, reset_fairness, format_event_schedule
from explainer import validate_all, explain_resolution
from demo_data import SCENARIOS
from metrics import satisfaction_report

WIDTH = 68


def _line(char: str = "-"):
    print(char * WIDTH)


def _header(title: str):
    print()
    _line("=")
    pad = (WIDTH - len(title) - 2) // 2
    print(f"{'=' * pad} {title} {'=' * (WIDTH - pad - len(title) - 2)}")
    _line("=")


def _step(n: int, label: str):
    print()
    _line("-")
    print(f"  STEP {n}  |  {label}")
    _line("-")


def _sat_bar(score: int, width: int = 20) -> str:
    filled = round(score / 100 * width)
    filled = max(0, min(width, filled))
    mark = "#" if score >= 70 else ("+" if score >= 40 else ".")
    return "[" + mark * filled + "." * (width - filled) + "]"


def event_to_dict(e):
    return {
        "club_name": e.club_name,
        "event_name": e.event_name,
        "preferred_date": e.preferred_date,
        "preferred_start": e.preferred_start,
        "duration_minutes": e.duration_minutes,
        "preferred_venue": e.preferred_venue,
        "budget_requested": e.budget_requested,
        "expected_audience_size": e.expected_audience_size,
        "flexibility": e.flexibility,
        "noise_level": e.noise_level,
        "audience_tags": list(e.audience_tags),
    }


def run(scenario_name: str):
    if scenario_name not in SCENARIOS:
        keys = ", ".join(sorted(SCENARIOS.keys()))
        print(f"  [X] Unknown scenario '{scenario_name}'. Choose from: {keys}")
        sys.exit(1)

    events = SCENARIOS[scenario_name]
    reset_fairness()

    _header(f"CAMPUS EVENT CONFLICT RESOLVER  |  SCENARIO {scenario_name}")
    print(f"  {len(events)} club request(s) loaded.\n")

    _step(1, "INPUT EVENTS")
    for e in events:
        print(f"  >  {e.club_name}  -  {e.event_name}")
        print(f"       Venue    : {e.preferred_venue}")
        print(
            f"       Date     : {e.preferred_date}   Schedule: "
            f"{format_event_schedule(e.preferred_start, e.duration_minutes)}"
        )
        print(f"       Audience : {e.expected_audience_size}   Budget: Rs.{e.budget_requested:,}")
        print(f"       Noise    : {e.noise_level}   Flexibility: {e.flexibility}/5")
        print(
            f"       Weights  : venue={e.preference_weights.venue}  "
            f"time={e.preference_weights.time_slot}  "
            f"budget={e.preference_weights.budget}"
        )
        score = claim_score(e, events)
        print(f"       Claim    : {score['final_score']:.4f}")
        print()

    _step(2, "VALIDATION")
    raw_dicts = [event_to_dict(e) for e in events]
    report = validate_all(raw_dicts)
    errors = report.get("errors", [])
    warnings = report.get("warnings", [])

    if not errors and not warnings:
        print("  [OK] All inputs are valid - no issues found.")
    for msg in errors:
        print(f"  [ERR] {msg}")
    for msg in warnings:
        print(f"  [WARN] {msg}")

    if errors:
        print()
        print("  Halting: fix the above errors before proceeding.")
        sys.exit(1)

    _step(3, "CONFLICT DETECTION")
    conflicts = detect_conflicts(events)

    if not conflicts:
        print("  [OK] No conflicts detected. All requests can be granted as-is.")
    else:
        print(f"  {len(conflicts)} conflict(s) found:\n")
        for i, c in enumerate(conflicts, 1):
            sev_bar = _sat_bar(int(c.severity * 100))
            print(f"  [{i}] {c.type.upper().replace('_', ' ')}")
            print(f"       Parties  : {', '.join(c.parties)}")
            print(f"       Severity : {sev_bar}  {c.severity:.2f}")
            print(f"       Detail   : {c.description}")
            print()

    _step(4, "RESOLUTION")
    resolutions = resolve(conflicts, events) if conflicts else []

    if not resolutions:
        print("  [OK] Nothing to resolve.")
    else:
        for i, r in enumerate(resolutions, 1):
            outcome_icon = {
                "auto_swap": "[swap]",
                "scored_decision": "[score]",
                "co_host_suggested": "[cohost]",
                "escalate": "[escalate]",
                "budget_split": "[budget]",
            }.get(r.resolution_type, "[?]")

            print(f"  {outcome_icon}  Resolution {i}  [{r.resolution_type}]")
            print(f"     Winner : {r.winner}")
            print(f"     Loser  : {r.loser}")
            print(f"     -> {explain_resolution(r)}")
            print()

    _step(5, "SATISFACTION & FAIRNESS METRICS")
    metrics = satisfaction_report(events, resolutions)

    print("  PER-CLUB SATISFACTION SCORES")
    print()
    for club, score in metrics["individual_scores"].items():
        bar = _sat_bar(score)
        label = "Good" if score >= 70 else ("OK" if score >= 40 else "Poor")
        print(f"  {club:<22} {bar}  {score:>3}/100  {label}")

    print()
    _line()

    mean_sat = metrics["mean_satisfaction"]
    fairness = metrics["overall_fairness"]
    low_club, low_score = metrics["lowest_satisfied"]
    high_club, high_score = metrics["highest_satisfied"]

    print(f"  Mean satisfaction   : {mean_sat:.1f}/100")
    print(f"  Highest satisfied   : {high_club} ({high_score}/100)")
    print(f"  Lowest satisfied    : {low_club}  ({low_score}/100)")
    print()

    _line("=")
    fairness_bar = _sat_bar(fairness, width=30)
    label = (
        "EXCELLENT"
        if fairness >= 80
        else ("GOOD" if fairness >= 60 else ("FAIR" if fairness >= 40 else "POOR"))
    )
    print(f"  OVERALL FAIRNESS SCORE :  {fairness_bar}  {fairness}/100  [{label}]")
    _line("=")

    _line()
    escalated = sum(1 for r in resolutions if r.resolution_type == "escalate")
    resolved = len(resolutions) - escalated
    print(
        f"  Scenario {scenario_name} complete  |  "
        f"Conflicts: {len(conflicts)}  |  "
        f"Resolved: {resolved}  |  "
        f"Escalated: {escalated}  |  "
        f"Fairness: {fairness}/100"
    )
    _line("=")
    print()


if __name__ == "__main__":
    scenario_name = sys.argv[1].upper() if len(sys.argv) > 1 else "A"
    run(scenario_name)
