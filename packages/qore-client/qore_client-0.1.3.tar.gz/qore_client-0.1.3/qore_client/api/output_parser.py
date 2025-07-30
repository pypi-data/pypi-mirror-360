import base64
import json
import pickle
from typing import Any, Dict, Literal


def parse_workflow_output(
    response_data: Dict[str, Any], format: Literal["logs", "raw", "output"]
) -> Dict[str, Any]:
    if response_data is None:
        raise ValueError("Failed to execute workflow, received None response.")

    if format == "logs":
        return format_execution_result(response_data)
    elif format == "raw":
        return response_data
    elif format == "output":
        return extract_workflow_output(response_data)
    else:
        raise ValueError(f"Invalid format: {format}")


def extract_workflow_output(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts the top-level output data from workflow execution result.
    Automatically unpickles data if it's pickled.
    Raises an error if output is empty.

    :param result: The raw execution result from the API.
    :return: The output data (unpickled if necessary).
    :raises ValueError: If output is empty or not found.
    """
    if not isinstance(result, dict):
        raise ValueError("Invalid result format: not a dictionary.")

    # Get the top-level output field
    if "output" in result:
        output_data = result["output"]
    else:
        raise ValueError("No 'output' field found in workflow execution result.")

    # Check if output is empty
    if not output_data:
        # Check for errors in stdout data and print error logs
        error_messages = []
        if "stdout" in result:
            stdout_data = result["stdout"]
            for node_id, node_data in stdout_data.items():
                if isinstance(node_data, dict):
                    status = node_data.get("status")
                    if status == "failed":
                        execute_result = node_data.get("execute_result", {})
                        stderr = execute_result.get("stderr")
                        if stderr:
                            error_messages.append(f"Node {node_id} failed:\n{stderr}")

        if error_messages:
            error_log = "\n\n".join(error_messages)
            raise ValueError(f"Workflow execution failed with errors:\n\n{error_log}")
        else:
            return {
                "message": "Success without output. If you want to see the result, Please pass the variable to End node."
            }

    # Get the inner output

    for k, v in output_data.items():
        if isinstance(v, dict) and v.get("_pickled") is True:
            try:
                # Decode the base64 pickled data
                pickled_bytes = base64.b64decode(v["pickled_data"])
                # Unpickle the data
                unpickled_data = pickle.loads(pickled_bytes)
                output_data[k] = unpickled_data
            except Exception as e:
                raise ValueError(f"Failed to unpickle data: {e}") from e
        elif isinstance(v, str):
            try:
                parsed_data = json.loads(v)
                output_data[k] = parsed_data
            except json.JSONDecodeError:
                # If it's not valid JSON, return the string as-is
                output_data[k] = v

    return output_data


def format_execution_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Formats the workflow execution result into a dictionary.
    Sorts nodes by start time and includes duration, status, and stdout for each.

    :param result: The raw execution result from the API.
    :return: A dictionary with formatted execution details for each node, sorted by start time.
    """
    import datetime

    if not isinstance(result, dict):
        return {"error": "Invalid result format: not a dictionary."}

    # Check if the new API structure with 'stdout' key exists
    if "stdout" in result:
        execution_data = result["stdout"]
    else:
        # Fallback to old structure
        execution_data = result

    node_executions = []
    for node_id, data in execution_data.items():
        if isinstance(data, dict) and "start_time" in data and "end_time" in data:
            node_executions.append((node_id, data))

    try:
        # Sort by start_time
        node_executions.sort(key=lambda x: x[1]["start_time"])
    except (KeyError, TypeError):
        # Fallback to original order if sorting fails
        pass

    output_data = {}
    for node_id, data in node_executions:
        start_time = data.get("start_time")
        end_time = data.get("end_time")

        duration_seconds = None
        if start_time is not None and end_time is not None:
            try:
                # Handle both string timestamps and numeric timestamps (milliseconds)
                if isinstance(start_time, str):
                    start_dt = datetime.datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                    end_dt = datetime.datetime.fromisoformat(end_time.replace("Z", "+00:00"))
                else:
                    # Numeric timestamp in milliseconds
                    start_dt = datetime.datetime.fromtimestamp(start_time / 1000)
                    end_dt = datetime.datetime.fromtimestamp(end_time / 1000)

                duration = end_dt - start_dt
                duration_seconds = duration.total_seconds()
            except (ValueError, TypeError):
                pass

        status = data.get("status", "N/A")

        execute_result = data.get("execute_result", {})
        # Changed from 'logs' to 'stdout' to match new API structure
        stdout = execute_result.get("stdout") or ""

        output_data[node_id] = {
            "duration_seconds": duration_seconds,
            "status": status,
            "stdout": stdout,
        }

    if not output_data:
        return result

    return output_data
