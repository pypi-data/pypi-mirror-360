import pandas as pd
import numpy as np
from datetime import time
from typing import List, Protocol, runtime_checkable
from .schemas import Participant


@runtime_checkable
class CostFunction(Protocol):
    """A protocol for cost functions."""

    def __call__(self, local_t: pd.Timestamp, p: Participant) -> float: ...


class DefaultCostFunction:
    """The default cost function based on working hours."""

    def __call__(self, local_t: pd.Timestamp, p: Participant) -> float:
        work_start = time.fromisoformat(p.work_start)
        work_end = time.fromisoformat(p.work_end)
        slot_time = local_t.time()

        if work_start <= slot_time < work_end:
            cost = 0.0
        else:
            if slot_time < work_start:
                diff = pd.Timestamp.combine(
                    local_t.date(), work_start
                ) - pd.Timestamp.combine(local_t.date(), slot_time)
            else:
                diff = pd.Timestamp.combine(
                    local_t.date(), slot_time
                ) - pd.Timestamp.combine(local_t.date(), work_end)

            hours_outside = diff.total_seconds() / 3600
            cost = 1 + 0.1 * hours_outside

        return cost * p.weight


def calculate_cost_matrix(
    participants: List[Participant],
    candidate_slots_utc: pd.DatetimeIndex,
    cost_function: CostFunction = DefaultCostFunction(),
) -> np.ndarray:
    """
    Calculates the cost matrix C[p, s] for each participant and each candidate slot.

    Args:
        participants: A list of Participant objects.
        candidate_slots_utc: A pandas DatetimeIndex of candidate meeting slots in UTC.
        cost_function: A function that calculates the cost for a given time and participant.

    Returns:
        A numpy array representing the cost matrix.
    """
    num_participants = len(participants)
    num_slots = len(candidate_slots_utc)
    cost_matrix = np.zeros((num_participants, num_slots))

    for i, p in enumerate(participants):
        local_times = candidate_slots_utc.tz_convert(p.tz)
        for j, local_t in enumerate(local_times):
            cost_matrix[i, j] = cost_function(local_t, p)

    return cost_matrix
