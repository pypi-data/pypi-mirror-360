from ics import Calendar, Event
from datetime import timedelta
from typing import List, Dict, Any
from .schemas import Meeting


def generate_ics(meeting: Meeting, scheduled_slots: List[Dict[str, Any]]) -> str:
    """
    Generates an ICS calendar file for the scheduled meetings.

    Args:
        meeting: The Meeting object with original parameters.
        scheduled_slots: A list of solved meeting slots from the solver.

    Returns:
        A string containing the ICS calendar data.
    """
    c = Calendar()
    for slot in scheduled_slots:
        e = Event()
        e.name = f"Team Meeting (Occurrence {slot['occurrence'] + 1})"
        e.begin = slot["slot_utc"]
        e.end = slot["slot_utc"] + timedelta(minutes=meeting.duration_minutes)
        e.description = "Fairly scheduled team meeting."
        c.events.add(e)
    return str(c)
