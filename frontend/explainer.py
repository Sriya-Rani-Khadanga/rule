import sys
import os
from dataclasses import asdict
from datetime import date, time
from typing import Any, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logic import (
    Resolution,
    EventRequest,
    VENUES,
    MIN_EVENT_DURATION,
    MAX_EVENT_DURATION,
    format_event_schedule,
)

_ALLOWED_NOISE = frozenset({"low", "medium", "high"})
# Tags used in forms + demo scenarios; unknown tags get a warning only.
_KNOWN_AUDIENCE_TAGS = frozenset({
    "tech", "arts", "sports", "general", "first_year", "final_year",
    "cultural", "literature", "competitive",
})


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _safe(data: dict, key: str, default=None):
    val = data.get(key)
    return default if val is None else val


def _to_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _event_to_dict(event: Any) -> dict:
    if isinstance(event, EventRequest):
        return asdict(event)
    return event


def _parse_time_value(val: Any) -> Optional[time]:
    if val is None:
        return None
    if isinstance(val, time):
        return val
    if isinstance(val, dict) and "hour" in val:
        return time(
            int(val["hour"]),
            int(val.get("minute", 0)),
            int(val.get("second", 0)),
        )
    if isinstance(val, str):
        s = val.strip()
        if not s:
            return None
        parts = s.replace(".", ":").split(":")
        h = int(parts[0])
        m = int(parts[1]) if len(parts) > 1 else 0
        sec = int(parts[2]) if len(parts) > 2 else 0
        return time(h, m, sec)
    return None


# ---------------------------------------------------------------------------
# validate_all
# ---------------------------------------------------------------------------

def validate_all(events: list[EventRequest] | list[dict]) -> dict:
    """
    Validate event requests (EventRequest instances or raw dicts).
    Returns {"errors": [...], "warnings": [...]}.
    """
    errors: list[str] = []
    warnings: list[str] = []
    seen_clubs: set[str] = set()
    today = date.today()

    raw_list = [_event_to_dict(e) for e in events]

    for idx, event in enumerate(raw_list, start=1):
        prefix = f"Event {idx}: "
        club_name = (event.get("club_name") or "").strip()
        event_name = (event.get("event_name") or "").strip()

        if not club_name or not event_name:
            errors.append(prefix + "Club name and event name are required.")

        preferred_date = event.get("preferred_date")
        if preferred_date is not None:
            if isinstance(preferred_date, str):
                try:
                    preferred_date = date.fromisoformat(preferred_date)
                except ValueError:
                    errors.append(prefix + "Preferred date is not a valid ISO date.")
                    preferred_date = None
            if isinstance(preferred_date, date) and preferred_date < today:
                errors.append(prefix + "Event date cannot be in the past.")

        budget = event.get("budget_requested")
        if budget is None or budget <= 0:
            errors.append(prefix + "Budget must be a positive number.")

        venue = event.get("preferred_venue")
        if venue is not None and str(venue).strip() not in VENUES:
            errors.append(
                prefix + "Venue must be one of: " + ", ".join(VENUES) + "."
            )

        pst = _parse_time_value(event.get("preferred_start"))
        if pst is None:
            errors.append(prefix + "Start time is required (HH:MM or time picker).")

        dur_raw = event.get("duration_minutes", 90)
        try:
            dur = int(dur_raw)
        except (TypeError, ValueError):
            dur = -1
        if dur < MIN_EVENT_DURATION or dur > MAX_EVENT_DURATION:
            errors.append(
                prefix + f"Duration must be between {MIN_EVENT_DURATION} and "
                f"{MAX_EVENT_DURATION} minutes."
            )
        elif pst is not None:
            start_m = pst.hour * 60 + pst.minute
            if start_m + dur > 24 * 60:
                warnings.append(
                    prefix + "Event extends past midnight; overlap checks use the full interval."
                )

        flex = event.get("flexibility")
        if flex is not None and flex != "":
            try:
                fi = int(flex)
                if not 1 <= fi <= 5:
                    errors.append(prefix + "Flexibility must be an integer from 1 to 5.")
            except (TypeError, ValueError):
                errors.append(prefix + "Flexibility must be an integer from 1 to 5.")

        noise = event.get("noise_level")
        if noise is not None and str(noise).strip() not in _ALLOWED_NOISE:
            errors.append(prefix + "Noise level must be low, medium, or high.")

        tags = event.get("audience_tags") or []
        if isinstance(tags, list):
            if len(tags) == 0:
                warnings.append(
                    prefix + "No audience tags — overlap detection between events will be limited."
                )
            unknown = [t for t in tags if str(t).strip() not in _KNOWN_AUDIENCE_TAGS]
            if unknown:
                warnings.append(
                    prefix + "Unknown audience tag(s): "
                    + ", ".join(str(t) for t in unknown)
                    + " — engine still runs; consider using standard tags."
                )

        audience_size = event.get("expected_audience_size", 0) or 0
        if audience_size <= 0 or audience_size > 5000:
            warnings.append(prefix + "Audience size seems unrealistic.")

        if club_name:
            if club_name in seen_clubs:
                warnings.append(f"{club_name} has already submitted a request.")
            else:
                seen_clubs.add(club_name)

    if len(raw_list) >= 2 and all(e.get("flexibility") == 5 for e in raw_list):
        warnings.append(
            "All organizers marked preferences as non-negotiable. "
            "Resolution quality may be limited."
        )

    return {"errors": errors, "warnings": warnings}


# ---------------------------------------------------------------------------
# explain_resolution
# ---------------------------------------------------------------------------

def explain_resolution(resolution: Resolution) -> str:
    """Return a human-readable explanation string for a Resolution."""
    data: dict = resolution.explanation_data or {}
    rt: str = resolution.resolution_type
    ct: str = resolution.conflict.type
    winner: str = resolution.winner
    loser: str = resolution.loser

    if rt == "budget_split":
        reason = (resolution.explanation_data or {}).get("resolution_reason", "")
        base = (
            "Total budget request exceeds the daily cap. "
            "Proportional allocation was applied across clubs on that date."
        )
        return f"{base} {reason}".strip()

    winner_score: float = _to_float(_safe(data, "winner_score", None))
    loser_score: float = _to_float(_safe(data, "loser_score", None))
    if winner_score == 0.0 and loser_score == 0.0:
        wb = data.get("winner_breakdown") or {}
        lb = data.get("loser_breakdown") or {}
        winner_score = _to_float(wb.get("final_score", 0.0))
        loser_score = _to_float(lb.get("final_score", 0.0))

    alternative_venue: str = (
        _safe(data, "alternative_venue", None)
        or resolution.new_venue
        or "TBD"
    )
    moved_start = resolution.new_start or _parse_time_value(_safe(data, "moved_to_start", None))
    moved_dur = int(_safe(data, "moved_duration_minutes", 0) or 0)
    moved_to_date = (
        _safe(data, "moved_to_date", None)
        or resolution.new_date
        or "TBD"
    )
    if moved_start is None:
        slot_disp = "TBD"
    elif moved_dur > 0:
        slot_disp = format_event_schedule(moved_start, moved_dur)
    else:
        slot_disp = moved_start.strftime("%H:%M")
    shared_tags = _safe(data, "shared_tags", []) or []
    resolution_reason: str = _safe(data, "resolution_reason", "") or ""

    if rt == "co_host_suggested":
        tags_str = ", ".join(str(t) for t in shared_tags) if shared_tags else "none"
        return (
            f"Both {winner} and {loser} have strong claims with overlapping audiences "
            f"(shared tags: {tags_str}). Recommendation: co-host as a joint event. "
            f"{resolution_reason}"
        )

    if rt == "escalate":
        return (
            f"Conflict between {winner} and {loser} cannot be auto-resolved. "
            f"Both have rigid preferences with no overlap. {resolution_reason} "
            f"Manual review by student council required. "
            f"Claim scores: {winner_score:.2f} vs {loser_score:.2f}."
        )

    if ct == "venue_clash" and rt == "scored_decision":
        return (
            f"{winner} keeps the venue. {loser}'s event reassigned to "
            f"{alternative_venue} ({slot_disp}, {moved_to_date}). "
            f"Decision based on claim scores: {winner_score:.2f} vs {loser_score:.2f}."
        )

    if ct == "venue_clash" and rt == "auto_swap":
        return (
            f"{loser}'s event automatically rescheduled to {slot_disp} on "
            f"{moved_to_date}. Low-severity conflict - {winner} retains the original "
            f"slot. Claim scores: {winner_score:.2f} vs {loser_score:.2f}."
        )

    if ct == "audience_overlap":
        return (
            f"{loser}'s event shifted to a different slot to reduce audience "
            f"competition with {winner}. Reassigned to {slot_disp} on "
            f"{moved_to_date}. Claim scores: {winner_score:.2f} vs {loser_score:.2f}."
        )

    if ct == "budget_exceeded":
        return (
            f"Budget conflict resolved: {winner} retains full budget allocation. "
            f"{loser} needs to revise their budget request. "
            f"Claim scores favored {winner} ({winner_score:.2f} vs {loser_score:.2f})."
        )

    if ct == "noise_proximity":
        return (
            f"Noise mismatch resolved: {loser}'s event relocated to "
            f"{alternative_venue} to avoid disrupting {winner}'s session in the "
            f"adjacent space. Claim scores: {winner_score:.2f} vs {loser_score:.2f}."
        )

    if ct == "fairness_imbalance":
        return (
            f"Fairness adjustment: {winner} has been deprioritized in past rounds "
            f"and gets the slot this time. {loser} reassigned to {slot_disp} on "
            f"{moved_to_date}. Claim scores: {winner_score:.2f} vs {loser_score:.2f}."
        )

    return (
        f"Conflict '{ct}' resolved via {rt}. "
        f"Winner: {winner}, affected: {loser}."
    )
