import pytest
from fairmeeting.schemas import Participant, Meeting
from fairmeeting.solver import ilp_solver
from fairmeeting.export import generate_ics
import subprocess
import yaml
import sys
from ics import Calendar


@pytest.fixture
def sample_participants():
    return [
        Participant(
            name="Alice", tz="America/Los_Angeles", work_start="09:00", work_end="17:00"
        ),
        Participant(
            name="Bob", tz="Europe/Berlin", work_start="09:00", work_end="17:00"
        ),
        Participant(
            name="Charlie", tz="Asia/Kolkata", work_start="09:00", work_end="17:00"
        ),
    ]


@pytest.fixture
def sample_meeting(sample_participants):
    return Meeting(
        participants=sample_participants,
        duration_minutes=60,
        allowed_weekdays=["Mon", "Tue", "Wed", "Thu", "Fri"],
        horizon=2,  # Test with 2 occurrences
        min_gap_between_meetings=0,
    )


def test_ilp_solver_recurring(sample_meeting):
    solution = ilp_solver(sample_meeting)
    assert "scheduled_slots" in solution
    assert len(solution["scheduled_slots"]) == sample_meeting.horizon
    assert "max_total_cost" in solution
    assert solution["max_total_cost"] >= 0


def test_ics_generation(sample_meeting):
    solution = ilp_solver(sample_meeting)
    if "scheduled_slots" in solution:
        ics_content = generate_ics(sample_meeting, solution["scheduled_slots"])
        c = Calendar(ics_content)
        assert len(list(c.events)) == sample_meeting.horizon


def test_cli_recurring_and_ics(tmp_path, sample_participants):
    p_file = tmp_path / "participants.yaml"
    ics_file = tmp_path / "meetings.ics"
    participants_dict = {"participants": [p.model_dump() for p in sample_participants]}
    with open(p_file, "w") as f:
        yaml.dump(participants_dict, f)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "fairmeeting.cli",
            str(p_file),
            "--horizon",
            "2",
            "--ics",
            str(ics_file),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Fair Meeting Plan (2 Occurrences)" in result.stdout
    assert "Success" in result.stdout
    assert ics_file.exists()
    with open(ics_file, "r") as f:
        ics_content = f.read()
        c = Calendar(ics_content)
        assert len(list(c.events)) == 2
