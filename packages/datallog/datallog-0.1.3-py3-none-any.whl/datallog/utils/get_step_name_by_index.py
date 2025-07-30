from .storage import get_core_step, get_next_step, get_step_to_callable
from typing import Optional


def get_step_name_by_index(step_index: int) -> Optional[str]:
    if step_index == 0:
        return get_core_step()
    else:
        current_step = get_core_step()
        for _ in range(step_index):
            if current_step is None:
                return None
            current_step = get_next_step(current_step)
        return current_step
