"""Logging utilities for the prompt-to-bot service."""

import collections
import logging
import threading
from typing import Any, Deque, Dict

from rasa.builder import config

# Thread-safe deque for collecting recent logs
_recent_logs: Deque[str] = collections.deque(maxlen=config.MAX_LOG_ENTRIES)
_logs_lock = threading.RLock()


def collecting_logs_processor(
    logger: Any, log_level: str, event_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """Structlog processor that collects recent log entries.

    This processor is thread-safe and maintains a rolling buffer of recent logs.
    """
    if log_level != logging.getLevelName(logging.DEBUG).lower():
        event_message = event_dict.get("event_info") or event_dict.get("event", "")
        log_entry = f"[{log_level}] {event_message}"

        with _logs_lock:
            _recent_logs.append(log_entry)

    return event_dict


def get_recent_logs() -> str:
    """Get recent log entries as a formatted string.

    Returns:
        Formatted string of recent log entries, one per line.
    """
    with _logs_lock:
        return "\n".join(list(_recent_logs))


def clear_recent_logs() -> None:
    """Clear the recent logs buffer."""
    with _logs_lock:
        _recent_logs.clear()


def get_log_count() -> int:
    """Get the current number of log entries."""
    with _logs_lock:
        return len(_recent_logs)
