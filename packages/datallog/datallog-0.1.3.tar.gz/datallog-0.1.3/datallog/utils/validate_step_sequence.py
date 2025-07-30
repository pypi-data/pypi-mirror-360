from typing import Set
from .storage import get_core_step, get_next_step, get_step_to_callable
from .errors import (
    CoreStepNotSetError,
    StepNotDefinedError,
    CircularStepDefinitionError,
)


def validate_step_sequence() -> None:
    core_step = get_core_step()
    if core_step is None:
        raise CoreStepNotSetError(
            "Core step not set - please set it using @core_step decorator"
        )

    current_step = core_step
    name_used: Set[str] = set()
    name_used.add(core_step)
    old_step = None
    while current_step is not None:
        if get_step_to_callable(current_step) is None:
            raise StepNotDefinedError(
                f"Step {current_step} is not defined but is set as next step for {old_step} - please define it using @step decorator"
            )
        next_step = get_next_step(current_step)

        if next_step is None:
            break

        if next_step in name_used:
            raise CircularStepDefinitionError(
                f"Circular step definition detected: {current_step} -> {next_step}"
            )
        name_used.add(next_step)
        old_step = current_step
        current_step = next_step
