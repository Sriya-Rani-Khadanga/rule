import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logic import Resolution, EventRequest

def validate_all(events: list[EventRequest]) -> dict:
    """Basic validation for event requests."""
    errors = []
    warnings = []
    
    for idx, e in enumerate(events):
        if not e.club_name.strip():
            errors.append(f"Event {idx+1}: Club name cannot be empty.")
        if not e.event_name.strip():
            errors.append(f"Event {idx+1}: Event name cannot be empty.")
        if e.budget_requested < 0:
            errors.append(f"Event {idx+1}: Budget cannot be negative.")
            
    return {"errors": errors, "warnings": warnings}


def explain_resolution(r: Resolution) -> str:
    """Converts a Resolution object into a human-readable explanation."""
    if r.resolution_type == "auto_swap":
        return f"{r.loser} moved to {r.new_time_slot} on {r.new_date} due to clear flexibility mismatch."
    elif r.resolution_type == "scored_decision":
        if r.new_venue and r.new_venue != r.conflict.parties[0]:
            return f"{r.winner} keeps the preferred setup. {r.loser} moved to {r.new_venue} at {r.new_time_slot}."
        return f"{r.winner} won the slot. {r.loser} moved to {r.new_time_slot}."
    elif r.resolution_type == "co_host_suggested":
        reason = r.explanation_data.get("resolution_reason", "Shared audience tags suggest co-hosting.")
        return f"{reason} ({', '.join(r.explanation_data.get('shared_tags', []))})"
    elif r.resolution_type == "budget_split":
        return "Total budget request exceeds daily cap. Proportional allocation applied."
    else:
        reason = r.explanation_data.get("resolution_reason", "No overlap; escalating to admin.")
        return f"Unable to automatically resolve - {reason}"
