"""
Event Scheduling Conflict Detection & Resolution Engine
========================================================
Pure Python (stdlib + dataclasses only). No external dependencies.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import Optional


# ── Dataclasses ──────────────────────────────────────────────────────────────

VENUES = ["Auditorium", "Seminar Hall", "Open Ground", "Lab Block A", "Cafeteria Court"]

MIN_EVENT_DURATION = 15
MAX_EVENT_DURATION = 720  # minutes; must fit typical same-day campus use


def format_event_schedule(start: time, duration_minutes: int) -> str:
    """Clock span for UI and conflict descriptions (same calendar day display)."""
    s0 = datetime(2000, 1, 1, start.hour, start.minute, start.second)
    e0 = s0 + timedelta(minutes=int(duration_minutes))
    return f"{start.strftime('%H:%M')}-{e0.strftime('%H:%M')} ({int(duration_minutes)} min)"


def _event_window(ev: "EventRequest") -> tuple[datetime, datetime]:
    start = datetime.combine(ev.preferred_date, ev.preferred_start)
    end = start + timedelta(minutes=int(ev.duration_minutes))
    return start, end


def intervals_overlap_on_calendar(a: "EventRequest", b: "EventRequest") -> bool:
    """True if the two events' [start, end) intervals intersect in absolute time."""
    sa, ea = _event_window(a)
    sb, eb = _event_window(b)
    return sa < eb and sb < ea


def _bump_start(day: date, start: time, delta_minutes: int) -> tuple[time, date]:
    dt = datetime.combine(day, start) + timedelta(minutes=int(delta_minutes))
    return dt.time(), dt.date()


# Adjacent venue pairs (bidirectional) – noise can bleed between these
ADJACENT_VENUES: set[frozenset[str]] = {
    frozenset({"Auditorium", "Seminar Hall"}),
    frozenset({"Seminar Hall", "Lab Block A"}),
    frozenset({"Open Ground", "Cafeteria Court"}),
    frozenset({"Auditorium", "Cafeteria Court"}),
}

DAILY_BUDGET_CAP = 50_000  # rupees


@dataclass
class PreferenceWeights:
    venue: float = 0.5
    time_slot: float = 0.5
    budget: float = 0.5


@dataclass
class EventRequest:
    club_name: str
    event_name: str
    preferred_date: date
    preferred_start: time             # e.g. 13:45 — user-selectable
    duration_minutes: int = 90        # event length for overlap detection
    preferred_venue: str = ""         # one of VENUES
    expected_audience_size: int = 0
    audience_tags: list[str] = field(default_factory=list)
    budget_requested: int = 0
    flexibility: int = 3
    noise_level: str = "medium"
    priority_score: float = 0.0
    preference_weights: PreferenceWeights = field(default_factory=PreferenceWeights)



class FairnessTracker:
    def __init__(self):
        self.wins: dict[str, int] = {}
        self.prime_slots: dict[str, int] = {}

    def record_win(self, club: str, venue: str, event_start: time):
        self.wins[club] = self.wins.get(club, 0) + 1
        start_m = event_start.hour * 60 + event_start.minute
        if venue == "Auditorium" or start_m >= 17 * 60:
            self.prime_slots[club] = self.prime_slots.get(club, 0) + 1

    def fairness_penalty(self, club: str) -> float:
        return -0.15 if self.wins.get(club, 0) >= 2 else 0.0

    def deprivation_bonus(self, club: str, priority_score: float) -> float:
        if self.wins.get(club, 0) == 0 and priority_score >= 0.7:
            return 0.1
        return 0.0


_fairness = FairnessTracker()


def reset_fairness():
    global _fairness
    _fairness = FairnessTracker()


@dataclass
class Conflict:
    type: str         # venue_clash | audience_overlap | budget_exceeded | noise_proximity | fairness_imbalance
    severity: float   # 0.0 – 1.0
    parties: list[str]
    description: str


@dataclass
class Resolution:
    conflict: Conflict
    winner: str
    loser: str
    resolution_type: str              # auto_swap | scored_decision | escalate | co_host_suggested
    new_venue: Optional[str]
    new_start: Optional[time]         # new start time for loser when rescheduled
    new_date: Optional[date]
    explanation_data: dict


@dataclass
class SatisfactionResult:
    club_name: str
    satisfaction_score: float      # 0-100
    got_preferred_venue: bool
    got_preferred_slot: bool
    got_preferred_date: bool
    budget_allocated: int
    budget_requested: int
    breakdown: dict                # all components for transparency


# ── Conflict Detection ───────────────────────────────────────────────────────

def _tag_overlap_ratio(tags_a: list[str], tags_b: list[str]) -> float:
    if not tags_a or not tags_b:
        return 0.0
    set_a, set_b = set(tags_a), set(tags_b)
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union) if union else 0.0


def detect_conflicts(events: list[EventRequest]) -> list[Conflict]:
    """Scan all event pairs (and the full list) for the five conflict types."""
    if len(events) < 2:
        return []
    conflicts: list[Conflict] = []

    for a, b in itertools.combinations(events, 2):
        # ── venue_clash ──────────────────────────────────────────────
        if (
            a.preferred_venue == b.preferred_venue
            and intervals_overlap_on_calendar(a, b)
        ):
            if a.flexibility == 5 and b.flexibility == 5:
                severity = 0.9
            elif a.flexibility == 5 or b.flexibility == 5:
                severity = 0.4
            else:
                severity = 0.2
            conflicts.append(Conflict(
                type="venue_clash",
                severity=severity,
                parties=[a.club_name, b.club_name],
                description=(
                    f"Both '{a.event_name}' ({a.club_name}) and '{b.event_name}' ({b.club_name}) "
                    f"want {a.preferred_venue} on {a.preferred_date}; schedules overlap "
                    f"({format_event_schedule(a.preferred_start, a.duration_minutes)} vs "
                    f"{format_event_schedule(b.preferred_start, b.duration_minutes)})."
                ),
            ))

        # ── audience_overlap ─────────────────────────────────────────
        ratio = _tag_overlap_ratio(a.audience_tags, b.audience_tags)
        if ratio > 0.6 and intervals_overlap_on_calendar(a, b):
            conflicts.append(Conflict(
                type="audience_overlap",
                severity=round(ratio, 3),
                parties=[a.club_name, b.club_name],
                description=(
                    f"'{a.event_name}' and '{b.event_name}' share {ratio:.0%} audience tags "
                    f"with overlapping times on {a.preferred_date} "
                    f"({format_event_schedule(a.preferred_start, a.duration_minutes)} vs "
                    f"{format_event_schedule(b.preferred_start, b.duration_minutes)}); "
                    f"attendees will be split."
                ),
            ))

        # ── noise_proximity ──────────────────────────────────────────
        if (
            intervals_overlap_on_calendar(a, b)
            and frozenset({a.preferred_venue, b.preferred_venue}) in ADJACENT_VENUES
        ):
            noise_pair = {a.noise_level, b.noise_level}
            if "high" in noise_pair and "low" in noise_pair:
                conflicts.append(Conflict(
                    type="noise_proximity",
                    severity=0.7,
                    parties=[a.club_name, b.club_name],
                    description=(
                        f"High-noise event '{a.event_name if a.noise_level == 'high' else b.event_name}' "
                        f"is adjacent to low-noise event "
                        f"'{b.event_name if a.noise_level == 'high' else a.event_name}' "
                        f"during {format_event_schedule(a.preferred_start, a.duration_minutes)} "
                        f"on {a.preferred_date}."
                    ),
                ))

        # ── fairness_imbalance ───────────────────────────────────────
        if (
            a.preferred_venue == b.preferred_venue
            and intervals_overlap_on_calendar(a, b)
        ):
            if a.priority_score > 0 and b.priority_score > 0:
                higher = max(a.priority_score, b.priority_score)
                lower = min(a.priority_score, b.priority_score)
                if higher > 2 * lower:
                    conflicts.append(Conflict(
                        type="fairness_imbalance",
                        severity=0.5,
                        parties=[a.club_name, b.club_name],
                        description=(
                            f"Priority-score gap ({higher:.2f} vs {lower:.2f}) suggests "
                            f"one club has been deprioritised too often."
                        ),
                    ))

    # ── budget_exceeded (global, per-date) ───────────────────────────
    by_date: dict[date, list[EventRequest]] = {}
    for e in events:
        by_date.setdefault(e.preferred_date, []).append(e)

    for d, day_events in by_date.items():
        total = sum(e.budget_requested for e in day_events)
        if total > DAILY_BUDGET_CAP:
            severity = min(1.0, (total - DAILY_BUDGET_CAP) / total)
            conflicts.append(Conflict(
                type="budget_exceeded",
                severity=round(severity, 3),
                parties=[e.club_name for e in day_events],
                description=(
                    f"Total budget on {d} is Rs.{total:,} which exceeds the Rs.{DAILY_BUDGET_CAP:,} cap "
                    f"(over by Rs.{total - DAILY_BUDGET_CAP:,})."
                ),
            ))

    return conflicts


# ── Claim Scoring ────────────────────────────────────────────────────────────

def claim_score(event: EventRequest, all_events: list[EventRequest]) -> dict:
    """
    Returns a dict with component breakdown and final_score.
    Score = (priority_score * 0.3)
          + (norm_audience  * 0.2)
          + ((6 - flexibility) / 5 * 0.2)
          + (budget_efficiency * 0.15)
          + 0.15  (base)
          + fairness_penalty + deprivation_bonus
    Preference weights are averaged and applied as a multiplier.
    """
    sizes = [e.expected_audience_size for e in all_events]
    max_size = max(sizes) if max(sizes) > 0 else 1
    norm_audience = event.expected_audience_size / max_size

    denom = event.expected_audience_size * 100 if event.expected_audience_size else 1
    budget_efficiency = 1 - min(1.0, event.budget_requested / denom)

    priority_component = event.priority_score * 0.3
    audience_component = norm_audience * 0.2
    flexibility_component = (6 - event.flexibility) / 5 * 0.2
    budget_component = budget_efficiency * 0.15
    base = 0.15

    pw = event.preference_weights
    preference_weight_applied = (pw.venue + pw.time_slot + pw.budget) / 3.0

    fp = _fairness.fairness_penalty(event.club_name)
    db = _fairness.deprivation_bonus(event.club_name, event.priority_score)

    raw = (
        priority_component
        + audience_component
        + flexibility_component
        + budget_component
        + base
        + fp
        + db
    )
    final = round(raw * preference_weight_applied, 4)

    return {
        "final_score": final,
        "priority_component": round(priority_component, 4),
        "audience_component": round(audience_component, 4),
        "flexibility_component": round(flexibility_component, 4),
        "budget_component": round(budget_component, 4),
        "preference_weight_applied": round(preference_weight_applied, 4),
        "fairness_penalty": round(fp, 4),
        "deprivation_bonus": round(db, 4),
    }


# ── Resolution Engine ────────────────────────────────────────────────────────

def _bump_minutes_for_loser(loser: EventRequest) -> int:
    """Push the loser's start forward enough to usually clear a same-venue overlap."""
    return max(30, int(loser.duration_minutes))


def _find_event(name: str, events: list[EventRequest]) -> EventRequest | None:
    for e in events:
        if e.club_name == name:
            return e
    return None


def _best_alternative_venue(exclude: str) -> str:
    for v in VENUES:
        if v != exclude:
            return v
    return exclude  # fallback


def resolve(conflicts: list[Conflict], events: list[EventRequest]) -> list[Resolution]:
    """Apply resolution strategy based on severity thresholds."""
    reset_fairness()
    resolutions: list[Resolution] = []

    for c in conflicts:
        if c.type == "budget_exceeded":
            day_events = [e for e in events if e.club_name in c.parties]
            if not day_events:
                continue
            scores = {e.club_name: claim_score(e, events) for e in day_events}
            total_score = sum(s["final_score"] for s in scores.values())
            allocations = {}
            for e in day_events:
                portion = scores[e.club_name]["final_score"] / total_score if total_score else 1/len(day_events)
                allocations[e.club_name] = int(DAILY_BUDGET_CAP * portion)
            resolutions.append(Resolution(
                conflict=c,
                winner="System",
                loser="All",
                resolution_type="budget_split",
                new_venue=None,
                new_start=None,
                new_date=None,
                explanation_data={
                    "allocations": allocations,
                    "resolution_reason": (
                        "Each club's share of the daily cap is proportional to their "
                        "claim score relative to other clubs on that date."
                    ),
                },
            ))
            continue

        if len(c.parties) < 2:
            continue

        ev_a = _find_event(c.parties[0], events)
        ev_b = _find_event(c.parties[1], events)
        if ev_a is None or ev_b is None:
            continue

        result_a = claim_score(ev_a, events)
        result_b = claim_score(ev_b, events)
        score_a = result_a["final_score"]
        score_b = result_b["final_score"]

        # Determine tentative winner / loser by score
        if score_a > score_b:
            winner, loser = ev_a, ev_b
            w_score, l_score = score_a, score_b
            w_breakdown, l_breakdown = result_a, result_b
        elif score_b > score_a:
            winner, loser = ev_b, ev_a
            w_score, l_score = score_b, score_a
            w_breakdown, l_breakdown = result_b, result_a
        else:
            # tie-break: higher priority_score wins
            if ev_a.priority_score >= ev_b.priority_score:
                winner, loser = ev_a, ev_b
                w_score, l_score = score_a, score_b
                w_breakdown, l_breakdown = result_a, result_b
            else:
                winner, loser = ev_b, ev_a
                w_score, l_score = score_b, score_a
                w_breakdown, l_breakdown = result_b, result_a

        # ── severity < 0.3 → auto_swap ──────────────────────────────
        if c.severity < 0.3:
            bump = _bump_minutes_for_loser(loser)
            new_start, new_date = _bump_start(
                loser.preferred_date, loser.preferred_start, bump,
            )
            resolutions.append(Resolution(
                conflict=c,
                winner=winner.club_name,
                loser=loser.club_name,
                resolution_type="auto_swap",
                new_venue=None,
                new_start=new_start,
                new_date=new_date,
                explanation_data={
                    "winner_breakdown": w_breakdown,
                    "loser_breakdown": l_breakdown,
                    "moved_to_start": new_start.strftime("%H:%M"),
                    "moved_duration_minutes": loser.duration_minutes,
                    "moved_to_date": str(new_date),
                },
            ))
            _register_fairness_win(winner)

        # ── 0.3 ≤ severity ≤ 0.7 → scored_decision ─────────────────
        elif c.severity <= 0.7:
            alt_venue = _best_alternative_venue(winner.preferred_venue)
            bump = _bump_minutes_for_loser(loser)
            new_start, new_date = _bump_start(
                loser.preferred_date, loser.preferred_start, bump,
            )
            resolutions.append(Resolution(
                conflict=c,
                winner=winner.club_name,
                loser=loser.club_name,
                resolution_type="scored_decision",
                new_venue=alt_venue,
                new_start=new_start,
                new_date=new_date,
                explanation_data={
                    "winner_breakdown": w_breakdown,
                    "loser_breakdown": l_breakdown,
                    "alternative_venue": alt_venue,
                    "moved_to_start": new_start.strftime("%H:%M"),
                    "moved_duration_minutes": loser.duration_minutes,
                    "moved_to_date": str(new_date),
                },
            ))
            _register_fairness_win(winner)

        # ── severity > 0.7 → escalate or co_host_suggested ──────────
        else:
            shared_tags = set(ev_a.audience_tags) & set(ev_b.audience_tags)
            if shared_tags:
                res_type = "co_host_suggested"
            else:
                res_type = "escalate"

            resolutions.append(Resolution(
                conflict=c,
                winner=winner.club_name,
                loser=loser.club_name,
                resolution_type=res_type,
                new_venue=None,
                new_start=None,
                new_date=None,
                explanation_data={
                    "winner_breakdown": w_breakdown,
                    "loser_breakdown": l_breakdown,
                    "shared_tags": list(shared_tags),
                    "resolution_reason": (
                        "Shared audience tags suggest co-hosting."
                        if shared_tags
                        else "No overlap; escalating to admin."
                    ),
                },
            ))
            _register_fairness_win(winner)

    return resolutions


def _register_fairness_win(winner: EventRequest) -> None:
    """Track wins so repeat winners get a claim-score penalty on later conflicts."""
    _fairness.record_win(
        winner.club_name,
        winner.preferred_venue,
        winner.preferred_start,
    )


def satisfaction_results_for_session(
    events: list[EventRequest],
    resolutions: list[Resolution],
) -> list[SatisfactionResult]:
    """
    Per-club satisfaction using the same aggregation as the Streamlit UI:
    first resolution where the club is winner or loser, plus budget allocation
    when a budget cap resolution exists.
    """
    results: list[SatisfactionResult] = []
    budget_res = next(
        (r for r in resolutions if r.conflict.type == "budget_exceeded"),
        None,
    )
    for event in events:
        rel_res = next(
            (r for r in resolutions if event.club_name in (r.winner, r.loser)),
            None,
        )
        budget_alloc = None
        if budget_res:
            budget_alloc = (budget_res.explanation_data or {}).get("allocations", {}).get(
                event.club_name
            )
        results.append(compute_satisfaction(event, rel_res, budget_alloc))
    return results


# ── Satisfaction & Fairness ──────────────────────────────────────────────────

def compute_satisfaction(
    event: EventRequest,
    resolution: Optional[Resolution],
    budget_allocated: Optional[int] = None
) -> SatisfactionResult:
    """
    Computes 0-100 satisfaction score for a single club after resolution.
    Higher = club got more of what it wanted, weighted by their preference_weights.
    """
    # If this club was the winner or not involved in any conflict, they keep everything
    if resolution is None or event.club_name == resolution.winner:
        venue_score = 100.0
        slot_score  = 100.0
        date_score  = 100.0
    else:
        # Loser: check what actually changed
        final_venue = resolution.new_venue or event.preferred_venue
        final_start = (
            resolution.new_start
            if resolution.new_start is not None
            else event.preferred_start
        )
        final_date = resolution.new_date or event.preferred_date

        venue_score = 100.0 if final_venue == event.preferred_venue else 30.0
        slot_score = (
            100.0
            if (
                final_date == event.preferred_date
                and final_start == event.preferred_start
            )
            else 50.0
        )
        date_score = 100.0 if final_date == event.preferred_date else 40.0

    # Budget satisfaction
    alloc = budget_allocated if budget_allocated is not None else event.budget_requested
    budget_score = min(100.0, round((alloc / event.budget_requested) * 100)) if event.budget_requested > 0 else 100.0

    # Weighted final score using the club's own preference_weights
    w = event.preference_weights
    total_weight = w.venue + w.time_slot + w.budget + 0.5  # 0.5 = fixed date weight
    if total_weight == 0:
        total_weight = 1

    weighted_score = (
        venue_score  * w.venue +
        slot_score   * w.time_slot +
        date_score   * 0.5 +
        budget_score * w.budget
    ) / total_weight

    final = round(weighted_score, 1)

    return SatisfactionResult(
        club_name=event.club_name,
        satisfaction_score=final,
        got_preferred_venue=(venue_score == 100.0),
        got_preferred_slot=(slot_score == 100.0),
        got_preferred_date=(date_score == 100.0),
        budget_allocated=alloc,
        budget_requested=event.budget_requested,
        breakdown={
            "venue_score": venue_score,
            "slot_score": slot_score,
            "date_score": date_score,
            "budget_score": budget_score,
            "preference_weights": {
                "venue": w.venue,
                "time_slot": w.time_slot,
                "budget": w.budget,
            }
        }
    )


def compute_system_fairness(satisfaction_results: list[SatisfactionResult]) -> dict:
    """
    Computes an overall 0-100 system fairness score.
    High score = satisfaction is evenly distributed. Low score = one club dominates.
    Uses two components:
      - Average satisfaction (did everyone do reasonably well?)
      - Equality (are scores close together, or is there a big gap?)
    """
    if not satisfaction_results:
        return {"fairness_score": 100.0, "average_satisfaction": 100.0,
                "std_deviation": 0.0, "min_satisfaction": 100.0,
                "max_satisfaction": 100.0, "interpretation": "No conflicts to evaluate."}

    scores = [r.satisfaction_score for r in satisfaction_results]
    n = len(scores)
    avg = sum(scores) / n
    variance = sum((s - avg) ** 2 for s in scores) / n
    std = variance ** 0.5

    # Equality score: 100 = all clubs equally satisfied, 0 = max disparity
    # Normalize std against the worst-case (0 vs 100 spread = std ~50)
    equality_score = max(0.0, 100.0 - (std * 2))

    # Final fairness = 60% average satisfaction + 40% equality
    fairness = round(avg * 0.6 + equality_score * 0.4, 1)

    # Human-readable interpretation
    if fairness >= 80:
        interpretation = "Excellent - all clubs received outcomes close to their preferences."
    elif fairness >= 60:
        interpretation = "Good - most clubs are reasonably satisfied with minor compromises."
    elif fairness >= 40:
        interpretation = "Fair - some clubs made significant compromises; review escalated conflicts."
    else:
        interpretation = "Poor - high disparity in outcomes. Manual review strongly recommended."

    return {
        "fairness_score": fairness,
        "average_satisfaction": round(avg, 1),
        "std_deviation": round(std, 1),
        "min_satisfaction": round(min(scores), 1),
        "max_satisfaction": round(max(scores), 1),
        "scores_by_club": {r.club_name: r.satisfaction_score for r in satisfaction_results},
        "interpretation": interpretation,
    }


# ── Demo / Self-test ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    test_events = [
        EventRequest(
            club_name="CodeCraft",
            event_name="Hackathon 2026",
            preferred_date=date(2026, 4, 20),
            preferred_start=time(9, 0),
            duration_minutes=120,
            preferred_venue="Auditorium",
            expected_audience_size=300,
            audience_tags=["tech", "competitive", "first_year"],
            budget_requested=25000,
            flexibility=4,
            noise_level="high",
            priority_score=1.2,
        ),
        EventRequest(
            club_name="LitSoc",
            event_name="Poetry Slam",
            preferred_date=date(2026, 4, 20),
            preferred_start=time(9, 30),
            duration_minutes=90,
            preferred_venue="Auditorium",           # ← venue clash with CodeCraft
            expected_audience_size=80,
            audience_tags=["literature", "general"],
            budget_requested=8000,
            flexibility=2,
            noise_level="low",
            priority_score=0.5,
        ),
        EventRequest(
            club_name="Robotics",
            event_name="Bot Wars",
            preferred_date=date(2026, 4, 20),
            preferred_start=time(10, 0),
            duration_minutes=180,
            preferred_venue="Seminar Hall",
            expected_audience_size=200,
            audience_tags=["tech", "competitive", "first_year"],  # heavy overlap with CodeCraft
            budget_requested=30000,                               # ← pushes total budget over 50k
            flexibility=5,
            noise_level="high",
            priority_score=2.8,
        ),
        EventRequest(
            club_name="DebSoc",
            event_name="Inter-College Debate",
            preferred_date=date(2026, 4, 20),
            preferred_start=time(14, 0),
            duration_minutes=120,
            preferred_venue="Seminar Hall",
            expected_audience_size=120,
            audience_tags=["general", "literature"],
            budget_requested=5000,
            flexibility=1,
            noise_level="low",
            priority_score=0.3,
        ),
    ]

    print("=" * 72)
    print("  EVENT SCHEDULING - CONFLICT DETECTION & RESOLUTION")
    print("=" * 72)

    # -- Detect -------------------------------------------------------
    conflicts = detect_conflicts(test_events)
    print(f"\n>> Detected {len(conflicts)} conflict(s):\n")
    for i, c in enumerate(conflicts, 1):
        print(f"  {i}. [{c.type}]  severity={c.severity:.2f}")
        print(f"     parties : {c.parties}")
        print(f"     details : {c.description}\n")

    # -- Scores -------------------------------------------------------
    print(">> Claim scores:")
    for e in test_events:
        result = claim_score(e, test_events)
        print(f"  - {e.club_name:12s}  score = {result['final_score']:.4f}  {result}")

    # -- Resolve ------------------------------------------------------
    resolutions = resolve(conflicts, test_events)
    print(f"\n>> {len(resolutions)} resolution(s):\n")
    for i, r in enumerate(resolutions, 1):
        print(f"  {i}. conflict  : {r.conflict.type} ({r.conflict.severity:.2f})")
        print(f"     strategy  : {r.resolution_type}")
        print(f"     winner    : {r.winner}")
        print(f"     loser     : {r.loser}")
        if r.new_venue:
            print(f"     new venue : {r.new_venue}")
        if r.new_start:
            dur = (r.explanation_data or {}).get("moved_duration_minutes", 90)
            print(f"     new start : {format_event_schedule(r.new_start, int(dur))}")
        if r.new_date:
            print(f"     new date  : {r.new_date}")
        print(f"     data      : {r.explanation_data}\n")

    # -- Satisfaction --------------------------------------------------
    print(">> Club Satisfaction:")
    satisfaction_results = []
    for event in test_events:
        # Find the resolution that involved this club, if any
        rel_resolution = next(
            (r for r in resolutions if event.club_name in [r.winner, r.loser]), None
        )
        # For budget splits, pull allocated amount from explanation_data
        budget_alloc = None
        budget_res = next((r for r in resolutions if r.conflict.type == "budget_exceeded"), None)
        if budget_res:
            budget_alloc = budget_res.explanation_data.get("allocations", {}).get(event.club_name)
        sat = compute_satisfaction(event, rel_resolution, budget_alloc)
        satisfaction_results.append(sat)
        print(f"  {sat.club_name}: satisfaction = {sat.satisfaction_score}/100")

    # -- System Fairness -----------------------------------------------
    fairness = compute_system_fairness(satisfaction_results)
    print(f"\nSystem Fairness Score: {fairness['fairness_score']}/100")
    print(f"Interpretation: {fairness['interpretation']}")

    print("=" * 72)
