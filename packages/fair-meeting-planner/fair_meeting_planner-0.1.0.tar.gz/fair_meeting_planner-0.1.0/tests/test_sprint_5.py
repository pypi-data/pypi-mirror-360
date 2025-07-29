import pytest
from fairmeeting.schemas import Participant, Meeting
from fairmeeting.solver import ilp_solver
from fairmeeting.cost import DefaultCostFunction
import pandas as pd


class FridayPenaltyCost(DefaultCostFunction):
    def __call__(self, local_t: pd.Timestamp, p: Participant) -> float:
        base_cost = super().__call__(local_t, p)
        if local_t.weekday() == 4:  # Friday
            return base_cost + 100
        return base_cost


@pytest.fixture
def sample_meeting():
    return Meeting(
        participants=[
            Participant(
                name="Alice",
                tz="America/New_York",
                work_start="09:00",
                work_end="17:00",
            ),
            Participant(
                name="Bob", tz="Europe/London", work_start="09:00", work_end="17:00"
            ),
        ],
        duration_minutes=60,
        allowed_weekdays=["Mon", "Tue", "Wed", "Thu", "Fri"],
        horizon=1,
        min_gap_between_meetings=0,
    )


def test_custom_cost_function_avoids_fridays(sample_meeting):
    # With high penalty, no meeting should be on a Friday
    solution_penalty = ilp_solver(sample_meeting, cost_function=FridayPenaltyCost())

    assert "scheduled_slots" in solution_penalty
    for slot in solution_penalty["scheduled_slots"]:
        # Check that the solution with the penalty does not schedule on a Friday
        # Note: We check the weekday in the participants' timezones
        for p in sample_meeting.participants:
            local_time = slot["slot_utc"].tz_convert(p.tz)
            assert local_time.weekday() != 4
