#!/usr/bin/env python
import importlib
import importlib.util
import inspect
import os
import sys
import threading
import json
from socket import AF_UNIX, SOCK_STREAM, SocketIO, socket
from typing import Any, Callable, Optional
from uuid import uuid4

from .get_step_name_by_index import get_step_name_by_index
from .storage import (
    get_next_step,
    get_step_to_callable,
    get_step_branching,
)
from .validate_step_sequence import validate_step_sequence


def create_get_work_item_json(worker_id: int) -> str:
    return json.dumps({"type": "GET_WORK_ITEM", "worker_id": worker_id})


def create_get_execution_props_json(worker_id: int) -> str:
    return json.dumps({"type": "GET_STEP_EXECUTION_PROPS", "worker_id": worker_id})


def create_work_item_json(step_index: int, argument: Any, from_work_id: str) -> str:
    new_work_id = str(uuid4())
    return json.dumps(
        {
            "type": "WORK_ITEM",
            "work_id": new_work_id,
            "step_index": step_index,
            "argument": argument,
            "from_work_id": from_work_id,
        }
    )


def create_worker_publish_result_json(work_id_str: str, result: Any) -> str:
    return json.dumps(
        {"type": "PUBLISH_RESULT", "work_id": work_id_str, "result": result}
    )


def create_worker_error_json(
    work_id_str: Optional[str], error: str, traceback_str: str
) -> str:
    return json.dumps(
        {
            "type": "WORKER_ERROR",
            "error": error,
            "traceback": traceback_str,
            "work_id": work_id_str,
        }
    )


def create_worker_mark_as_idle_json(worker_id: int) -> str:
    return json.dumps({"type": "MARK_AS_IDLE", "worker_id": worker_id})


unix_socket = "/tmp/datallog_worker.sock"
my_id = int(sys.argv[1])

sock: Optional[socket] = None


def import_module_from_path(file_path: str):
    spec = importlib.util.spec_from_file_location("*", file_path)
    if spec is None:
        raise Exception(f"Failed to create spec for module: {file_path}")
    module = importlib.util.module_from_spec(spec)

    if spec.loader is None:
        raise Exception(f"Failed to get loader for module: {file_path}")

    spec.loader.exec_module(module)
    return module


def connect_to_conteiner_server():
    global sock
    sock = socket(AF_UNIX, SOCK_STREAM)
    sock.connect(unix_socket)
    return SocketIO(sock, "rwb")


sockio = connect_to_conteiner_server()


def send_message_to_conteiner_server(data: str):
    sockio.write(data.encode() + b"\n")
    sockio.flush()


def send_mark_as_idle_to_conteiner_server():
    json_payload = create_worker_mark_as_idle_json(worker_id=my_id)
    send_message_to_conteiner_server(json_payload)


def receive_message_from_conteiner_server():
    response_bytes = sockio.readline()
    if (
        not response_bytes
    ):  # Handle case where readline returns empty bytes (e.g. server closed connection)
        raise ConnectionAbortedError("Server closed connection or sent empty response.")
    response_str = response_bytes.decode().strip()
    if (
        not response_str
    ):  # Handle case where the line was just whitespace or empty after strip
        raise ValueError("Received an empty message from server.")
    return json.loads(response_str)


def get_work_item_from_conteiner_server():
    json_payload = create_get_work_item_json(worker_id=my_id)
    send_message_to_conteiner_server(json_payload)
    return receive_message_from_conteiner_server()


def get_execution_props_from_conteiner_server():
    json_payload = create_get_execution_props_json(worker_id=my_id)
    send_message_to_conteiner_server(json_payload)
    return receive_message_from_conteiner_server()


def send_worker_error_to_conteiner_server(
    work_id_str: Optional[str], error: str, traceback_str: str
):
    json_payload = create_worker_error_json(
        work_id_str=work_id_str, error=error, traceback_str=traceback_str
    )
    send_message_to_conteiner_server(json_payload)


def close_connection_to_conteiner_server():
    if sockio:
        sockio.close()
    if sock:
        sock.close()


def get_mandatory_argcount(f: Callable[..., Any]) -> int:
    sig = inspect.signature(f)

    def parameter_is_mandatory(p: inspect.Parameter) -> bool:
        return p.default is inspect.Parameter.empty and p.kind not in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        )

    return sum(parameter_is_mandatory(p) for p in sig.parameters.values())


def execute_steps():
    original_stderr = sys.stderr
    original_stdout = sys.stdout
    """
    Manages the execution lifecycle of steps for a single application instance
    within a dedicated worker process.

    This function runs continuously within a worker process, handling multiple
    steps sequentially as directed by the container server for a specific
    application execution. It loads the user's application code once and then
    enters a loop, processing work items received from the server. It supports
    optional arguments for steps and allows execution paths to branch based on
    step results, provided the step is explicitly marked for branching. The
    worker also notifies the server about its idle status to aid in efficient
    worker pool management.

    The execution flow is as follows:
    1.  **Initialization:**
        a. Fetches initial application execution properties (like code file path)
           from the container server (`get_execution_props_from_conteiner_server`).
        b. Records the initial number of active threads.
        c. Dynamically loads the user's application module. Decorator information
           (including branching flags) is gathered. (Decorator state persists).
        d. Performs an immediate check: If loading the module created lingering
           threads, reports an error (`send_thread_error_to_conteiner_server`)
           and terminates the worker.

    2.  **Step Execution Loop:**
        a. Enters a loop (with a safety break) to continuously poll for and
           execute steps.
        b. Fetches the next work item from the container server
           (`get_work_item_from_conteiner_server`).
        c. **Exit Condition:** If the received item indicates no more work
           (e.g., type is "NO_MORE_WORK_ITEMS"), closes the server connection
           and exits the loop/function.
        d. **Step Processing (within try...except block):**
            i.  If step index is 0, performs initial sequence validation.
            ii. Identifies the step function (callable) based on the index.
            iii. **Log Redirection:** Redirects stdout and stderr to a log file
                 specific to this step instance (`logs/{step_name}-{work_id}.log`)
                 for the duration of the step execution.
            iv. **Flexible Argument Handling:** Calls the step function correctly
                 based on whether an argument is provided and whether the step
                 requires mandatory arguments.
            v.  Executes the step function. Flushes stdout/stderr before restoring.
            vi. **Per-Step Thread Check:** Compares current thread count against the
                *initial* count. If new threads were created and not terminated,
                reports a thread error (`send_thread_error_to_conteiner_server`)
                and terminates the worker immediately.
            vii.**Idle Notification:** If the step completed successfully and a
                `next_step` exists (meaning this is not the final step), the
                worker immediately notifies the container server that it is
                momentarily idle (`send_mark_as_idle_to_conteiner_server`). This
                signal allows the server to optimize the allocation of pending
                tasks to available workers before this worker submits its
                follow-up task(s).
            viii.**Result Handling & Branching:** (Formerly 2.d.vi)
                - Checks if a `next_step` is defined for the current step.
                - If a `next_step` exists (idle notification was already sent):
                    - If the `step_result` is a list *and* the step is explicitly
                      marked for branching (`get_step_branching`):
                      Iterates through the list. For *each item*, sends a new
                      `WorkItem` payload to the server (`send_work_item_to_conteiner_server`)
                      for the `next_step`, using the item as the argument.
                    - Otherwise: Sends a single `WorkItem` payload for the
                      `next_step`, using the entire `step_result` as the argument.
                - If no `next_step` exists: Sends a final `WorkerPublishResult`
                  payload to the server (`send_result_to_conteiner_server`).
        e.  **Error Handling:** Catches other exceptions during step processing,
            reports them as a `WorkerPublishError` payload
            (`send_result_to_conteiner_server` handles both results and errors),
            and continues the loop to await the next work item or exit signal.
            (Note: Thread creation errors are fatal and exit the worker earlier).
    """
    # 1. Initialization
    try:
        execution_props = get_execution_props_from_conteiner_server()
    except (ConnectionAbortedError, ValueError, json.JSONDecodeError) as e:
        print(f"Failed to get execution properties: {e}", file=sys.stderr)
        # Optionally send a specific error type if the protocol supports it before exiting
        # For now, just close and exit.
        if sock:  # Ensure sock is defined before trying to close
            close_connection_to_conteiner_server()
        return

    num_of_threads = threading.active_count()

    try:
        import_module_from_path(execution_props["file_path"])
    except Exception as e:
        print(
            f"Failed to import module {execution_props.get('file_path', 'N/A')}: {e}",
            file=sys.stderr,
        )
        import traceback

        # Attempt to notify server about this critical initialization error
        # No work_id yet, so pass None.
        # This assumes the server can handle an error report this early.
        error_payload = create_worker_error_json(
            work_id_str=None,
            error=str(e),
            traceback_str=traceback.format_exc(),
        )
        try:
            send_message_to_conteiner_server(error_payload)
        except Exception as send_e:
            print(
                f"Additionally, failed to send import error to server: {send_e}",
                file=sys.stderr,
            )
        if sock:
            close_connection_to_conteiner_server()
        return

    if threading.active_count() > num_of_threads:
        send_worker_error_to_conteiner_server(
            work_id_str=None,
            error="New threads created during module import",
            traceback_str="Thread count increased during module import, indicating potential resource leak or mismanagement. Keep in mind that the code should be inside a step function, not at the module level.",
        )

        close_connection_to_conteiner_server()
        return

    # 2. Step Execution Loop
    for _ in range(1000):  # Safeguard
        try:
            work_item = get_work_item_from_conteiner_server()
        except (ConnectionAbortedError, ValueError, json.JSONDecodeError) as e:
            import traceback

            send_worker_error_to_conteiner_server(
                work_id_str=None,
                error=str(e),
                traceback_str=traceback.format_exc(),
            )
            close_connection_to_conteiner_server()
            return

        if (
            isinstance(work_item, dict)
            and work_item.get("type") == "NO_MORE_WORK_ITEMS"
        ):
            close_connection_to_conteiner_server()
            return

        if (
            not isinstance(work_item, dict)
            or work_item.get("type") != "WORK_ITEM"
            or "step_index" not in work_item
            or "work_id" not in work_item
        ):
            print(
                f"Received unexpected or malformed message: {work_item}",
                file=sys.stderr,
            )
            # Optionally, send an error to the server about the malformed message.
            # For now, we'll try to get another message.
            error_payload = create_worker_error_json(
                work_id_str=(
                    work_item.get("work_id") if isinstance(work_item, dict) else None
                ),
                error="Received malformed work item from server",
                traceback_str=f"Message: {work_item}",
            )
            send_message_to_conteiner_server(error_payload)
            continue

        current_work_id_str = work_item["work_id"]  # Assumed present for WORK_ITEM type
        original_stdout = sys.stdout  # Store original stdout/stderr for restoration
        original_stderr = sys.stderr

        try:
            step_index = work_item["step_index"]

            if step_index == 0:
                validate_step_sequence()

            step_name = get_step_name_by_index(step_index)
            step_callable = get_step_to_callable(step_name)
            log_file = None
            logging_to_files = execution_props.get("logging_to_files", False)
            try:
                if logging_to_files:
                    # Ensure logs directory exists
                    if not os.path.exists("logs"):
                        os.makedirs("logs")
                    log_file_path = (
                        f"logs/{step_name}-{current_work_id_str or 'unknown'}.log"
                    )

                    log_file = open(log_file_path, "a")
                    sys.stdout = log_file
                    sys.stderr = log_file

                step_argument = work_item.get("argument")
                if step_argument is None:
                    if get_mandatory_argcount(step_callable) > 0:
                        step_result = step_callable(None)
                    else:
                        step_result = step_callable()
                else:
                    step_result = step_callable(step_argument)
                    sys.stdout.flush()
                    sys.stderr.flush()
            finally:
                if logging_to_files:
                    sys.stdout = original_stdout
                    sys.stderr = original_stderr
                    if log_file:
                        log_file.close()

            if threading.active_count() > num_of_threads:
                create_worker_error_json(
                    work_id_str=current_work_id_str,
                    error="New threads created during step execution",
                    traceback_str="Thread count increased during step execution, indicating potential resource leak or mismanagement. Keep in mind that all threads should be properly managed and terminated within the step function.",
                )

                close_connection_to_conteiner_server()
                return

            next_step = get_next_step(step_name)

            if next_step is not None:
                send_mark_as_idle_to_conteiner_server()

                if isinstance(step_result, list) and get_step_branching(step_name):
                    # Process in reverse if original logic intended to preserve order after potential server-side reordering
                    # The original code did step_result.reverse(), assuming it's for specific processing order.
                    # If the order of submitting branched items doesn't matter or is handled by server, reverse might not be needed.
                    # For now, keeping it consistent with the original logic.
                    items_to_send = list(
                        step_result
                    )  # Create a copy if step_result could be modified elsewhere
                    items_to_send.reverse()
                    for item_arg in items_to_send:
                        next_work_item_json = create_work_item_json(
                            step_index=step_index
                            + 1,  # Assuming next_step maps to step_index + 1
                            argument=item_arg,
                            from_work_id=current_work_id_str,
                        )
                        send_message_to_conteiner_server(next_work_item_json)
                else:
                    next_work_item_json = create_work_item_json(
                        step_index=step_index
                        + 1,  # Assuming next_step maps to step_index + 1
                        argument=step_result,
                        from_work_id=current_work_id_str,
                    )
                    send_message_to_conteiner_server(next_work_item_json)
            else:
                result_payload_json = create_worker_publish_result_json(
                    work_id_str=current_work_id_str, result=step_result
                )
                send_message_to_conteiner_server(result_payload_json)

        except Exception as e:
            # Ensure stdout/stderr are restored if an error occurred mid-step processing
            if sys.stdout != original_stdout:
                sys.stdout = original_stdout
            if sys.stderr != original_stderr:
                sys.stderr = original_stderr

            import traceback

            error_payload_json = create_worker_error_json(
                work_id_str=current_work_id_str,
                error=str(e),
                traceback_str=traceback.format_exc(),
            )
            send_message_to_conteiner_server(error_payload_json)
            # Continue loop to await next work item or exit signal


if __name__ == "__main__":
    try:
        execute_steps()
    except Exception as e:
        # Catch-all for any unhandled exceptions during worker setup or main loop
        print(f"Unhandled exception in worker (worker_id: {my_id}): {e}", file=sys.stderr)
        import traceback

        # Attempt to notify the server about a critical failure if connection is still possible
        try:
            # work_id might not be available or relevant here, send None
            send_worker_error_to_conteiner_server(
                work_id_str=None, error=str(e), traceback_str=traceback.format_exc()
            )
        except Exception as final_e:
            traceback.print_exc(file=sys.stderr)
            print(
                f"Failed to send final thread error to server: {final_e}",
                file=sys.stderr,
            )
    finally:
        close_connection_to_conteiner_server()
