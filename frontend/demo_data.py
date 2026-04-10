import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logic import EventRequest, PreferenceWeights

_today = datetime.date.today()

SCENARIOS = {
    "A": [
        EventRequest("CodeCraft", "Hackathon 2026", _today + datetime.timedelta(days=1), "morning", "Auditorium", 300, ["tech", "competitive", "first_year"], 25000, 4, "high", 1.2, PreferenceWeights()),
        EventRequest("LitSoc", "Poetry Slam", _today + datetime.timedelta(days=1), "morning", "Auditorium", 80, ["literature", "general"], 8000, 2, "low", 0.5, PreferenceWeights())
    ],
    "B": [
        EventRequest("CodeCraft", "Hackathon 2026", _today + datetime.timedelta(days=1), "morning", "Auditorium", 300, ["tech", "competitive", "first_year"], 30000, 4, "high", 1.2, PreferenceWeights()),
        EventRequest("Robotics", "Bot Wars", _today + datetime.timedelta(days=1), "morning", "Seminar Hall", 200, ["tech", "competitive", "first_year"], 30000, 5, "high", 2.8, PreferenceWeights())
    ],
    "C": [
        EventRequest("CodeCraft", "Hackathon 2026", _today + datetime.timedelta(days=1), "morning", "Auditorium", 300, ["tech", "competitive", "first_year"], 25000, 4, "high", 1.2, PreferenceWeights()),
        EventRequest("LitSoc", "Poetry Slam", _today + datetime.timedelta(days=1), "morning", "Auditorium", 80, ["literature", "general"], 8000, 2, "low", 0.5, PreferenceWeights()),
        EventRequest("Robotics", "Bot Wars", _today + datetime.timedelta(days=1), "morning", "Seminar Hall", 200, ["tech", "competitive", "first_year"], 30000, 5, "high", 2.8, PreferenceWeights()),
        EventRequest("DebSoc", "Inter-College Debate", _today + datetime.timedelta(days=1), "afternoon", "Seminar Hall", 120, ["general", "literature"], 5000, 1, "low", 0.3, PreferenceWeights())
    ]
}
