# SCENARIO CONFLICT COVERAGE
# ---------------------------------------------------------------------------
# Scenario A — "Simple venue clash"
#   - venue_clash: CodeCraft and DebSoc both request Auditorium, same date,
#     same evening slot. CodeCraft submitted first (flexibility=2) vs DebSoc
#     (flexibility=4). Different audience tags — no audience overlap.
#
# Scenario B — "Budget overrun + audience overlap"
#   - budget_exceeded: LitSoc (₹25,000) + Photography Club (₹20,000) +
#     Robotics Club (₹18,000) = ₹63,000 > ₹50,000 daily cap on date+10.
#   - audience_overlap: LitSoc and Photography Club share ["arts","cultural",
#     "general"] out of 4-tag union → ratio 0.75 > 0.70. Different venues,
#     same afternoon slot.
#
# Scenario C — "All conflict types"
#   - venue_clash:        CodeCraft + DebSoc → Auditorium, evening (same slot)
#   - audience_overlap:   CodeCraft + LitSoc → both ["tech","final_year"],
#                         ratio = 1.0 > 0.6
#   - budget_exceeded:    5 clubs total ₹55,000 > ₹50,000 daily cap
#   - noise_proximity:    CodeCraft (Auditorium, noise=high, evening)
#                         ↔ LitSoc (Seminar Hall, noise=low, evening)
#                         — adjacent venues per campus map
#   - fairness_imbalance: CodeCraft priority_score=0.8 vs DebSoc 0.3 at same
#                         Auditorium+evening slot → ratio ≈ 2.67 ≥ 2.0
# ---------------------------------------------------------------------------

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic import EventRequest, PreferenceWeights
from datetime import date, time, timedelta

# ---------------------------------------------------------------------------
# Shared dates (relative to today so data never goes stale)
# ---------------------------------------------------------------------------
_DATE_A = date.today() + timedelta(days=7)
_DATE_B = date.today() + timedelta(days=10)
_DATE_C = date.today() + timedelta(days=14)

# ---------------------------------------------------------------------------
# Scenario A — Simple venue clash
# ---------------------------------------------------------------------------
_scenario_a: list[EventRequest] = [
    EventRequest(
        club_name="CodeCraft",
        event_name="Code Blitz Hackathon",
        preferred_date=_DATE_A,
        preferred_start=time(18, 0),
        duration_minutes=120,
        preferred_venue="Auditorium",
        expected_audience_size=200,
        audience_tags=["tech", "final_year"],
        budget_requested=15000,
        flexibility=2,
        noise_level="medium",
        priority_score=0.75,
        preference_weights=PreferenceWeights(venue=0.9, time_slot=0.7, budget=0.5),
    ),
    EventRequest(
        club_name="DebSoc",
        event_name="Spring Debate Championship",
        preferred_date=_DATE_A,
        preferred_start=time(18, 45),
        duration_minutes=90,
        preferred_venue="Auditorium",
        expected_audience_size=150,
        audience_tags=["arts", "general"],
        budget_requested=12000,
        flexibility=4,
        noise_level="low",
        priority_score=0.55,
        preference_weights=PreferenceWeights(venue=0.5, time_slot=0.5, budget=0.5),
    ),
]

# ---------------------------------------------------------------------------
# Scenario B — Budget overrun + audience overlap
# Total: 25000 + 20000 + 18000 = 63000 > 50000
# LitSoc ∩ Photography Club tags = {arts, cultural, general} / union = 4 → 0.75
# ---------------------------------------------------------------------------
_scenario_b: list[EventRequest] = [
    EventRequest(
        club_name="LitSoc",
        event_name="Literary Fest Afternoon",
        preferred_date=_DATE_B,
        preferred_start=time(14, 0),
        duration_minutes=120,
        preferred_venue="Seminar Hall",
        expected_audience_size=300,
        audience_tags=["arts", "cultural", "general", "first_year"],
        budget_requested=25000,
        flexibility=3,
        noise_level="low",
        priority_score=0.65,
        preference_weights=PreferenceWeights(venue=0.6, time_slot=0.5, budget=0.4),
    ),
    EventRequest(
        club_name="Photography Club",
        event_name="Shutter Stories Exhibition",
        preferred_date=_DATE_B,
        preferred_start=time(13, 30),
        duration_minutes=90,
        preferred_venue="Open Ground",
        expected_audience_size=250,
        audience_tags=["arts", "cultural", "general"],
        budget_requested=20000,
        flexibility=2,
        noise_level="low",
        priority_score=0.60,
        preference_weights=PreferenceWeights(venue=0.7, time_slot=0.4, budget=0.5),
    ),
    EventRequest(
        club_name="Robotics Club",
        event_name="RoboWars Qualifier",
        preferred_date=_DATE_B,
        preferred_start=time(9, 0),
        duration_minutes=120,
        preferred_venue="Lab Block A",
        expected_audience_size=180,
        audience_tags=["tech", "final_year", "sports"],
        budget_requested=18000,
        flexibility=4,
        noise_level="high",
        priority_score=0.70,
        preference_weights=PreferenceWeights(venue=0.5, time_slot=0.6, budget=0.4),
    ),
]

# ---------------------------------------------------------------------------
# Scenario C — All conflict types (5 clubs, same date)
# Total budget: 15000+12000+10000+10000+8000 = 55000 > 50000
# ---------------------------------------------------------------------------
_scenario_c: list[EventRequest] = [
    EventRequest(
        club_name="CodeCraft",
        event_name="All-Night Hackathon",
        preferred_date=_DATE_C,
        preferred_start=time(18, 0),
        duration_minutes=360,
        preferred_venue="Auditorium",
        expected_audience_size=400,
        audience_tags=["tech", "final_year"],
        budget_requested=15000,
        flexibility=1,
        noise_level="high",
        priority_score=0.8,
        preference_weights=PreferenceWeights(venue=0.9, time_slot=0.8, budget=0.3),
    ),
    EventRequest(
        club_name="DebSoc",
        event_name="Grand Finale Debate",
        preferred_date=_DATE_C,
        preferred_start=time(18, 30),
        duration_minutes=180,
        preferred_venue="Auditorium",
        expected_audience_size=200,
        audience_tags=["arts", "general"],
        budget_requested=12000,
        flexibility=3,
        noise_level="medium",
        priority_score=0.3,
        preference_weights=PreferenceWeights(venue=0.5, time_slot=0.5, budget=0.5),
    ),
    EventRequest(
        club_name="LitSoc",
        event_name="Tech & Lit Symposium",
        preferred_date=_DATE_C,
        preferred_start=time(18, 0),
        duration_minutes=180,
        preferred_venue="Seminar Hall",
        expected_audience_size=120,
        audience_tags=["tech", "final_year"],
        budget_requested=10000,
        flexibility=4,
        noise_level="low",
        priority_score=0.55,
        preference_weights=PreferenceWeights(venue=0.4, time_slot=0.6, budget=0.5),
    ),
    EventRequest(
        club_name="Drama Society",
        event_name="Monsoon Play Festival",
        preferred_date=_DATE_C,
        preferred_start=time(13, 0),
        duration_minutes=180,
        preferred_venue="Open Ground",
        expected_audience_size=350,
        audience_tags=["arts", "cultural"],
        budget_requested=10000,
        flexibility=2,
        noise_level="high",
        priority_score=0.65,
        preference_weights=PreferenceWeights(venue=0.6, time_slot=0.5, budget=0.4),
    ),
    EventRequest(
        club_name="Music Society",
        event_name="Unplugged Sessions",
        preferred_date=_DATE_C,
        preferred_start=time(13, 45),
        duration_minutes=90,
        preferred_venue="Cafeteria Court",
        expected_audience_size=180,
        audience_tags=["arts", "cultural"],
        budget_requested=8000,
        flexibility=5,
        noise_level="medium",
        priority_score=0.45,
        preference_weights=PreferenceWeights(venue=0.3, time_slot=0.4, budget=0.6),
    ),
]

# ---------------------------------------------------------------------------
# Public export
# ---------------------------------------------------------------------------
SCENARIOS: dict[str, list[EventRequest]] = {
    "A": _scenario_a,
    "B": _scenario_b,
    "C": _scenario_c,
}
