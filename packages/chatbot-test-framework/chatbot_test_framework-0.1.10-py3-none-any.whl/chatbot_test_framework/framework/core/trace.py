import time
import functools
from typing import Any, Callable, List, Dict, Optional

class Tracer:
    """
    A tracer that captures execution data and sends it to a configured recorder.
    """
    def __init__(self, recorder, run_id: str):
        if not hasattr(recorder, 'record'):
            raise TypeError("Recorder must have a 'record' method.")
        self._recorder = recorder
        self._run_id = run_id

    def trace(self, step_name: str) -> Callable:
        """A decorator to trace a function's execution."""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                """
                The wrapper that executes the function and records the trace.
                """
                extra_metadata_from_kwargs = kwargs.pop('_extra_metadata', None)
                
                start_time = time.time()
                try:
                    output = func(*args, **kwargs)
                    status = "success"
                    return output
                except Exception as e:
                    status = "error"
                    output = {"error": type(e).__name__, "message": str(e)}
                    raise
                finally:
                    end_time = time.time()
                    
                    # --- NEW: LANGGRAPH STATE INSPECTION ---
                    # Check if the first argument looks like a LangGraph state dictionary
                    # and if it contains our special metadata key.
                    extra_metadata_from_state = None
                    if args and isinstance(args[0], dict) and 'current_metadata' in args[0]:
                        extra_metadata_from_state = args[0].get('current_metadata')
                    
                    # --- Build the trace data ---
                    original_kwargs = kwargs.copy()
                    if extra_metadata_from_kwargs:
                        original_kwargs['_extra_metadata'] = extra_metadata_from_kwargs

                    trace_data = {
                        "run_id": self._run_id, "name": step_name,
                        "start_time": start_time, "end_time": end_time,
                        "status": status,
                        "inputs": {"args": args, "kwargs": original_kwargs},
                        "outputs": output
                    }
                    
                    # --- Merge metadata from either source ---
                    if extra_metadata_from_kwargs and isinstance(extra_metadata_from_kwargs, dict):
                        trace_data.update(extra_metadata_from_kwargs)
                    if extra_metadata_from_state and isinstance(extra_metadata_from_state, dict):
                        trace_data.update(extra_metadata_from_state)
                        # Optional: Clear the metadata from the state after recording
                        # to prevent it from accidentally being used by another node.
                        if isinstance(output, dict):
                            output.pop('current_metadata', None)

                    self._recorder.record(trace_data)
            return wrapper
        return decorator