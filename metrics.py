"""
Satisfaction and fairness metrics aligned with the Streamlit UI (logic.compute_satisfaction
+ logic.compute_system_fairness).
"""
from typing import Dict, List, Tuple

from logic import (
    EventRequest,
    Resolution,
    compute_system_fairness,
    satisfaction_results_for_session,
)


def calculate_satisfaction(event: EventRequest, resolutions: List[Resolution]) -> int:
    """Per-club score 0-100; same definition as the UI session aggregation."""
    results = satisfaction_results_for_session(
        [event],
        resolutions,
    )
    if not results:
        return 100
    return int(round(results[0].satisfaction_score))


def calculate_fairness_score(events: List[EventRequest], resolutions: List[Resolution]) -> int:
    """System fairness 0-100; same formula as compute_system_fairness."""
    if len(events) <= 1:
        return 100
    sat = satisfaction_results_for_session(events, resolutions)
    return int(round(compute_system_fairness(sat)["fairness_score"]))


def satisfaction_report(
    events: List[EventRequest], resolutions: List[Resolution]
) -> Dict:
    """
    Keys:
        individual_scores  : {club_name: int score}
        overall_fairness   : int
        mean_satisfaction  : float
        lowest_satisfied   : (club_name, score)
        highest_satisfied  : (club_name, score)
        fairness_detail    : dict from compute_system_fairness
    """
    sat = satisfaction_results_for_session(events, resolutions)
    fair = compute_system_fairness(sat)

    individual: Dict[str, int] = {
        r.club_name: int(round(r.satisfaction_score)) for r in sat
    }

    scores = list(individual.values())
    mean_sat = sum(scores) / len(scores) if scores else 0.0

    lowest: Tuple[str, int] = min(individual.items(), key=lambda x: x[1], default=("", 0))
    highest: Tuple[str, int] = max(individual.items(), key=lambda x: x[1], default=("", 0))

    return {
        "individual_scores": individual,
        "overall_fairness": int(round(fair["fairness_score"])),
        "mean_satisfaction": round(mean_sat, 2),
        "lowest_satisfied": lowest,
        "highest_satisfied": highest,
        "fairness_detail": fair,
    }
