from functools import wraps
from .step import step

from typing import Callable, Optional


def core_step(*, next_step: Optional[str] = None) -> Callable:
    return step(next_step=next_step, core_step=True)