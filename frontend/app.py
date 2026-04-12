import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import datetime

from logic import (
    EventRequest, PreferenceWeights, VENUES, format_event_schedule,
    detect_conflicts, resolve, reset_fairness,
    compute_system_fairness, satisfaction_results_for_session,
)
from explainer import validate_all, explain_resolution
from demo_data import SCENARIOS

st.set_page_config(
    page_title="Taalमेल — Campus Event Peace Engine",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "events" not in st.session_state: st.session_state["events"] = []
if "conflicts" not in st.session_state: st.session_state["conflicts"] = []
if "resolutions" not in st.session_state: st.session_state["resolutions"] = []
if "satisfaction" not in st.session_state: st.session_state["satisfaction"] = []
if "fairness" not in st.session_state: st.session_state["fairness"] = {}

st.title("Taalमेल")
st.caption("Campus Event Peace Engine — Mediate smarter. Schedule better.")
st.divider()

left_col, right_col = st.columns([4, 6], gap="large")

with left_col:
  st.subheader("Load a Demo Scenario")
  scenario_choice = st.selectbox(
      "Choose a pre-built scenario",
      options=[
          "— select —",
          "A: Simple venue clash (Auditorium, overlapping times)",
          "B: Budget overrun + audience overlap",
          "C: All conflict types (stress test, 5 clubs)",
      ],
      key="scenario_select",
  )
  if scenario_choice != "— select —":
      scenario_key = scenario_choice[0]  # "A", "B", or "C"
      if st.button(f"Load Scenario {scenario_key}", type="secondary"):
          st.session_state["events"] = SCENARIOS[scenario_key]
          reset_fairness()
          st.session_state["conflicts"] = []
          st.session_state["resolutions"] = []
          st.session_state["satisfaction"] = []
          st.session_state["fairness"] = {}
          st.success(f"Scenario {scenario_key} loaded — {len(SCENARIOS[scenario_key])} events added.")

  st.divider()

  st.subheader("Add Event Request")

  with st.form("event_form", clear_on_submit=True):
      col1, col2 = st.columns(2)
      with col1:
          club_name   = st.text_input("Club Name *")
          event_name  = st.text_input("Event Name *")
          pref_date   = st.date_input("Event Date *", min_value=datetime.date.today())
          start_time  = st.time_input(
              "Start time *",
              value=datetime.time(12, 0),
              step=300,
              help="Granularity 5 minutes. End time is start + duration.",
          )
      with col2:
          venue       = st.selectbox("Venue", VENUES, help="Must match campus venues used by the engine.")
          duration_m  = st.number_input(
              "Duration (minutes) *",
              min_value=15,
              max_value=720,
              value=90,
              step=15,
              help="Used for overlap detection (venue, audience, adjacent noise).",
          )
          audience    = st.number_input("Expected Audience", min_value=1, max_value=5000, value=100)
          budget      = st.number_input("Budget Requested (₹)", min_value=1, value=5000)
          noise       = st.radio("Noise Level", ["low", "medium", "high"], horizontal=True)

      audience_tags = st.multiselect(
          "Audience Tags",
          sorted(
              {
                  "tech", "arts", "sports", "general", "first_year", "final_year",
                  "cultural", "literature", "competitive",
              }
          ),
          help="Pick at least one for meaningful audience-overlap detection.",
      )
      flexibility = st.slider("Overall Flexibility (1=very flexible, 5=rigid)", 1, 5, 3)
      priority    = st.slider("Priority Score (0=always gets slots, 1=long deprived)", 0.0, 1.0, 0.0, step=0.1)

      st.markdown("**How important are these to you?** (0 = flexible, 1.0 = non-negotiable)")
      wcol1, wcol2, wcol3 = st.columns(3)
      with wcol1:
          w_venue = st.slider("Venue", 0.0, 1.0, 0.5, step=0.1, key="w_venue")
      with wcol2:
          w_slot  = st.slider("Schedule / time importance", 0.0, 1.0, 0.5, step=0.1, key="w_slot")
      with wcol3:
          w_budget = st.slider("Budget", 0.0, 1.0, 0.5, step=0.1, key="w_budget")

      submitted = st.form_submit_button("Add Event Request", type="primary", use_container_width=True)

      if submitted:
          raw = {
              "club_name": club_name, "event_name": event_name,
              "preferred_date": pref_date,
              "preferred_start": start_time,
              "duration_minutes": int(duration_m),
              "preferred_venue": venue, "expected_audience_size": audience,
              "audience_tags": audience_tags, "budget_requested": budget,
              "flexibility": flexibility, "noise_level": noise,
              "priority_score": priority,
          }
          validation = validate_all(st.session_state["events"] + [EventRequest(
                  **{k: v for k, v in raw.items()},
                  preference_weights=PreferenceWeights(
                      venue=w_venue, time_slot=w_slot, budget=w_budget
                  )
              )])
          if validation["errors"]:
              for err in validation["errors"]:
                  st.error(err)
          else:
              for warn in validation["warnings"]:
                  st.warning(warn)
              event = EventRequest(
                  **{k: v for k, v in raw.items()},
                  preference_weights=PreferenceWeights(
                      venue=w_venue, time_slot=w_slot, budget=w_budget
                  )
              )
              st.session_state["events"].append(event)
              st.success(f"Added: {club_name} — {event_name}")

  if st.session_state["events"]:
      st.markdown(f"**{len(st.session_state['events'])} event(s) submitted**")
      table_data = [{
          "Club": e.club_name, "Event": e.event_name,
          "Date": str(e.preferred_date),
          "Schedule": format_event_schedule(e.preferred_start, e.duration_minutes),
          "Venue": e.preferred_venue, "Audience": e.expected_audience_size,
          "Budget (₹)": f"₹{e.budget_requested:,}", "Flexibility": e.flexibility
      } for e in st.session_state["events"]]
      st.dataframe(table_data, use_container_width=True, hide_index=True)

      col_r, col_c = st.columns(2)
      with col_r:
          if st.button("🔍 Detect Conflicts & Resolve", type="primary",
                       use_container_width=True,
                       disabled=len(st.session_state["events"]) < 2):
              with st.spinner("Detecting conflicts..."):
                  time.sleep(0.8)
                  st.session_state["conflicts"] = detect_conflicts(st.session_state["events"])
              with st.spinner("Running resolution engine..."):
                  time.sleep(0.8)
                  st.session_state["resolutions"] = resolve(
                      st.session_state["conflicts"], st.session_state["events"]
                  )
              with st.spinner("Computing satisfaction scores..."):
                  time.sleep(0.5)
                  sat_results = satisfaction_results_for_session(
                      st.session_state["events"],
                      st.session_state["resolutions"],
                  )
                  st.session_state["satisfaction"] = sat_results
                  st.session_state["fairness"] = compute_system_fairness(sat_results)
              st.rerun()
      with col_c:
          if st.button("🗑 Clear All", use_container_width=True):
              for key in ["events","conflicts","resolutions","satisfaction","fairness"]:
                  st.session_state[key] = [] if key != "fairness" else {}
              reset_fairness()
              st.rerun()

with right_col:
  if not st.session_state["conflicts"] and not st.session_state["resolutions"]:
      st.info("Submit 2 or more event requests and click 'Detect Conflicts & Resolve' to see results here.")

  else:
      conflicts   = st.session_state["conflicts"]
      resolutions = st.session_state["resolutions"]
      fairness    = st.session_state["fairness"]
      satisfaction = st.session_state["satisfaction"]

      st.subheader("Summary")
      m1, m2, m3, m4, m5 = st.columns(5)
      high_sev   = sum(1 for c in conflicts if c.severity > 0.7)
      auto_res   = sum(1 for r in resolutions if r.resolution_type == "auto_swap")
      avg_sat    = fairness.get("average_satisfaction", 0)
      fair_score = fairness.get("fairness_score", 0)

      m1.metric("Total Conflicts",   len(conflicts))
      m2.metric("High Severity",     high_sev,  delta=f"{high_sev} escalated" if high_sev else "none")
      m3.metric("Auto-Resolved",     auto_res)
      m4.metric("Avg Satisfaction",  f"{avg_sat}/100")
      m5.metric("System Fairness",   f"{fair_score}/100",
                delta=fairness.get("interpretation", "")[:30] if fairness else None)

      st.divider()

      st.subheader(f"Conflicts Detected ({len(conflicts)})")
      if not conflicts:
          st.success("No conflicts detected.")
      else:
          for c in conflicts:
              if c.severity > 0.7:
                  badge = "🔴 Severe"
                  expander_fn = st.error
              elif c.severity > 0.3:
                  badge = "🟡 Moderate"
                  expander_fn = st.warning
              else:
                  badge = "🟢 Minor"
                  expander_fn = st.success

              with st.expander(f"{badge} — {c.type.replace('_',' ').title()} | {' vs '.join(c.parties[:2])} | severity {c.severity}"):
                  st.progress(c.severity, text=f"Severity: {c.severity}")
                  st.write(c.description)
                  if c.severity > 0.7:
                      st.error("Severe conflict — manual mediation may be required.")
                  elif c.severity > 0.3:
                      st.warning("Moderate — resolved via scored decision.")
                  else:
                      st.success("Minor — auto-resolved.")

      st.divider()

      st.subheader(f"Resolutions ({len(resolutions)})")
      if not resolutions:
          st.info("No resolutions generated.")
      else:
          for r in resolutions:
              explanation = explain_resolution(r)

              if r.resolution_type == "auto_swap":
                  st.success(f"✅ Auto-resolved: {explanation}")
              elif r.resolution_type == "scored_decision":
                  st.success(f"⚖️ Scored decision: {explanation}")
              elif r.resolution_type == "co_host_suggested":
                  st.info(f"🤝 Co-hosting suggested: {explanation}")
              elif r.resolution_type == "budget_split":
                  st.warning(f"💰 Budget cap: {explanation}")
              else:
                  st.error(f"⚠️ Escalated: {explanation}")

              with st.expander("Why this decision? (full score breakdown)"):
                  data = r.explanation_data
                  if "winner_breakdown" in data and "loser_breakdown" in data:
                      wb = data["winner_breakdown"]
                      lb = data["loser_breakdown"]
                      bcol1, bcol2 = st.columns(2)
                      with bcol1:
                          st.markdown(f"**{r.winner}** (winner) — score: `{wb.get('final_score', 'N/A')}`")
                          st.write({
                              "Priority":    wb.get("priority_component"),
                              "Audience":    wb.get("audience_component"),
                              "Flexibility": wb.get("flexibility_component"),
                              "Budget eff.": wb.get("budget_component"),
                              "Pref weight": wb.get("preference_weight_applied"),
                              "Fairness adj": wb.get("deprivation_bonus", 0) + wb.get("fairness_penalty", 0),
                          })
                      with bcol2:
                          st.markdown(f"**{r.loser}** (adjusted) — score: `{lb.get('final_score', 'N/A')}`")
                          st.write({
                              "Priority":    lb.get("priority_component"),
                              "Audience":    lb.get("audience_component"),
                              "Flexibility": lb.get("flexibility_component"),
                              "Budget eff.": lb.get("budget_component"),
                              "Pref weight": lb.get("preference_weight_applied"),
                              "Fairness adj": lb.get("deprivation_bonus", 0) + lb.get("fairness_penalty", 0),
                          })
                  elif "allocations" in data:
                      st.write(data.get("resolution_reason", ""))
                      st.write("Budget allocation breakdown (Rs.):")
                      st.json(data.get("allocations", {}))
                  else:
                      st.json(data)

          st.divider()

      if satisfaction:
          st.subheader("Satisfaction Scores")
          for s in satisfaction:
              bar_color = "normal" if s.satisfaction_score >= 60 else "inverse"
              col_a, col_b = st.columns([3, 1])
              with col_a:
                  st.progress(
                      int(s.satisfaction_score) / 100,
                      text=f"{s.club_name}: {s.satisfaction_score}/100 — "
                           f"venue {'✓' if s.got_preferred_venue else '✗'} | "
                           f"slot {'✓' if s.got_preferred_slot else '✗'} | "
                           f"budget ₹{s.budget_allocated:,} of ₹{s.budget_requested:,}"
                  )
              with col_b:
                  with st.expander("details"):
                      ev = next(
                          (e for e in st.session_state["events"] if e.club_name == s.club_name),
                          None,
                      )
                      if ev:
                          st.caption(
                              "Preferred: "
                              f"{format_event_schedule(ev.preferred_start, ev.duration_minutes)}"
                          )
                      st.json(s.breakdown)

          st.divider()
          st.markdown(f"**Overall System Fairness: {fairness.get('fairness_score', 0)}/100**")
          st.caption(fairness.get("interpretation", ""))
          fc1, fc2, fc3 = st.columns(3)
          fc1.metric("Avg Satisfaction", f"{fairness.get('average_satisfaction',0)}/100")
          fc2.metric("Std Deviation",    fairness.get("std_deviation", 0))
          fc3.metric("Min / Max",        f"{fairness.get('min_satisfaction',0)} / {fairness.get('max_satisfaction',0)}")

st.divider()
st.caption("Taalमेल · Campus Event Peace Engine · All decisions are deterministic — no AI used in resolution logic.")
