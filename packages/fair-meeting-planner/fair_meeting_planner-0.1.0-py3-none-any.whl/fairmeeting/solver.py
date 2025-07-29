import numpy as np
from typing import Dict, Any, Optional
from .schemas import Meeting
from .cost import calculate_cost_matrix, CostFunction
import pandas as pd
import pulp


def ilp_solver(
    meeting: Meeting, cost_function: Optional[CostFunction] = None
) -> Dict[str, Any]:
    """
    Solves the fair meeting scheduling problem for a recurring series using Integer Linear Programming.
    """
    # Generate candidate slots with optimization for performance
    start_date = pd.to_datetime("2025-07-07").tz_localize("UTC")
    candidate_slots_utc = []

    # OPTIMIZATION 1: Duration-aware slot intervals
    # Calculate appropriate interval based on meeting duration
    if meeting.duration_minutes <= 30:
        interval_minutes = 30  # 30-min slots for short meetings
    elif meeting.duration_minutes <= 60:
        interval_minutes = 60  # 1-hour slots for medium meetings
    elif meeting.duration_minutes <= 90:
        interval_minutes = 90  # 1.5-hour slots for longer meetings
    else:
        interval_minutes = 120  # 2-hour slots for very long meetings

    # OPTIMIZATION 4: For horizon 4+, be more aggressive with slot reduction
    if meeting.horizon >= 4:
        # For larger horizons, focus on prime meeting hours only
        start_hour = 8  # 8 AM UTC
        end_hour = 18  # 6 PM UTC
        # Also increase interval for better performance
        if interval_minutes < 120:
            interval_minutes = max(interval_minutes, 90)  # At least 90-min intervals
    else:
        # For smaller horizons, use wider range
        start_hour = 6
        end_hour = 22

    # OPTIMIZATION 3: Generate slots for each week in horizon
    for week in range(meeting.horizon):
        start_of_week = start_date + pd.Timedelta(weeks=week)
        for day in range(7):  # 7 days in a week
            current_day = start_of_week + pd.Timedelta(days=day)

            # Generate slots throughout the day with duration-aware intervals
            current_time = current_day.replace(hour=start_hour, minute=0, second=0)
            day_end_time = current_day.replace(hour=end_hour, minute=0, second=0)

            while current_time <= day_end_time:
                candidate_slots_utc.append(current_time)
                current_time += pd.Timedelta(minutes=interval_minutes)

    candidate_slots_utc = pd.DatetimeIndex(candidate_slots_utc)

    # Filter by allowed weekdays
    allowed_weekday_nums = [
        {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}[day]
        for day in meeting.allowed_weekdays
    ]
    candidate_slots_utc = candidate_slots_utc[
        candidate_slots_utc.weekday.isin(allowed_weekday_nums)
    ]

    if len(candidate_slots_utc) == 0:
        return {"error": "No candidate slots found for the given constraints."}

    # OPTIMIZATION 3: Pre-filter slots by cost to reduce problem size
    cost_matrix = (
        calculate_cost_matrix(
            meeting.participants, candidate_slots_utc, cost_function=cost_function
        )
        if cost_function
        else calculate_cost_matrix(meeting.participants, candidate_slots_utc)
    )

    # OPTIMIZATION 4: Remove extremely high-cost slots (outliers)
    # This reduces the search space significantly
    max_costs_per_slot = np.max(cost_matrix, axis=0)
    reasonable_cost_threshold = np.percentile(
        max_costs_per_slot, 75
    )  # Keep 75% of slots
    good_slot_indices = np.where(max_costs_per_slot <= reasonable_cost_threshold)[0]

    # Apply filtering
    candidate_slots_utc = candidate_slots_utc[good_slot_indices]
    cost_matrix = cost_matrix[:, good_slot_indices]

    num_participants, num_slots = cost_matrix.shape
    num_occurrences = meeting.horizon

    print(
        f"Debug: Optimized problem size - {num_slots} slots, {num_occurrences} meetings = {num_slots * num_occurrences} variables"
    )

    # Create the ILP problem
    prob = pulp.LpProblem("FairRecurringMeetingScheduling", pulp.LpMinimize)

    # Decision variables: x_o_s = 1 if occurrence o is scheduled in slot s
    slot_vars = pulp.LpVariable.dicts(
        "Slot", (range(num_occurrences), range(num_slots)), cat="Binary"
    )

    # Objective function: Minimize the maximum total cost for any participant over the horizon
    max_total_cost = pulp.LpVariable("MaxTotalCost", lowBound=0)
    prob += max_total_cost

    # Constraints
    # 1. Ensure the objective variable is indeed the maximum total cost
    for p in range(num_participants):
        prob += (
            pulp.lpSum(
                cost_matrix[p, s] * slot_vars[o][s]
                for o in range(num_occurrences)
                for s in range(num_slots)
            )
            <= max_total_cost
        )

    # 2. Exactly one slot must be chosen for each occurrence
    for o in range(num_occurrences):
        prob += pulp.lpSum(slot_vars[o][s] for s in range(num_slots)) == 1

    # 3. A slot can be used at most once across all occurrences
    for s in range(num_slots):
        prob += pulp.lpSum(slot_vars[o][s] for o in range(num_occurrences)) <= 1

    # OPTIMIZATION 5: Set solver time limit and use faster solver settings
    solver = pulp.PULP_CBC_CMD(
        msg=False, timeLimit=30, gapRel=0.05
    )  # 30 sec limit, 5% optimality gap
    prob.solve(solver)

    # Extract the solution
    if pulp.LpStatus[prob.status] == "Optimal":
        scheduled_slots = []
        for o in range(num_occurrences):
            for s in range(num_slots):
                if pulp.value(slot_vars[o][s]) == 1:
                    slot_info = {
                        "occurrence": o,
                        "slot_utc": candidate_slots_utc[s],
                        "participant_costs": cost_matrix[:, s],
                    }
                    scheduled_slots.append(slot_info)

        solution = {
            "scheduled_slots": sorted(scheduled_slots, key=lambda x: x["occurrence"]),
            "max_total_cost": pulp.value(max_total_cost),
        }
    elif pulp.LpStatus[prob.status] == "Not Solved":
        solution = {"error": "Solver timed out. Try reducing horizon or constraints."}
    else:
        solution = {
            "error": f"Could not find optimal solution. Status: {pulp.LpStatus[prob.status]}"
        }

    return solution
