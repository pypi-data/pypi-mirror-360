from functools import wraps
from typing import Optional, Callable
from datallog.utils.storage import set_next_step, set_step_to_callable, set_core_step, set_step_not_branching




def step(*, next_step: Optional[str] = None, core_step: bool = False, branching: bool = True) -> Callable:
    """
    Decorator to mark a function as a step in a sequence.
    
    Args:
        next_step (Optional[str]): The name of the next step in the sequence.
        core_step (bool): Whether the step is the core step of the application. (first step)
        branching (bool): Whether the step is a branching step. If False, the step will spawn a only new step.
    """

    def decorator(func):
        set_step_to_callable(func.__name__, func)
        set_next_step(func.__name__, next_step)
        if core_step:
            set_core_step(func.__name__)
        if not branching:
            set_step_not_branching(func.__name__)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator
