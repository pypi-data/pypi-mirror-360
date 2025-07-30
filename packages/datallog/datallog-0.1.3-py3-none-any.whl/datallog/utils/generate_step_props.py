from typing import Any, Dict


from .storage import get_core_step, get_next_step


def generate_step_props(app_name: str) -> Dict[str, Any]:
    """
    Generate step properties for each step in the workflow.

    Args:
        steps (list): List of steps in the workflow.
        context (list): List of context variables.

    Returns:
        dict: Dictionary containing step properties.
    """

    step_list = []
    old_step = None
    current_step = get_core_step()
    i = 0

    while current_step != None:
        i += 1
        next_step = get_next_step(current_step)
        tll = i if next_step is not None else i - 1

        if old_step is None:
            data_to_process = None
        else:
            data_to_process = "${{step.%s}}" % (i - 2)

        step_list.append(
            {
                "to_result": "exec_result" if next_step is None else None,
                "name_core_function": current_step,
                "data_to_process": data_to_process,
                "context_step_ttl": tll,
            }
        )
        old_step = current_step
        current_step = next_step
    return {"steps": step_list, "name": app_name, "context": []}
