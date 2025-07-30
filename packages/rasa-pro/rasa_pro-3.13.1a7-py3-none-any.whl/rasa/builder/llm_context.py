import json
from typing import Optional

from rasa.shared.core.constants import DEFAULT_SLOT_NAMES
from rasa.shared.core.events import (
    ActionExecuted,
    BotUttered,
    FlowCompleted,
    FlowStarted,
    SlotSet,
    UserUttered,
)
from rasa.shared.core.trackers import DialogueStateTracker


def tracker_as_llm_context(tracker: Optional[DialogueStateTracker]) -> str:
    """Convert a tracker to a string that can be used as context for the LLM."""
    if not tracker or not tracker.events:
        return "No conversation history available."

    context_parts = []
    current_turn = []

    for event in tracker.events:
        if isinstance(event, UserUttered):
            if current_turn:
                context_parts.append(" | ".join(current_turn))
                current_turn = []
            current_turn.append(f"User: {event.text}")
            if event.intent:
                current_turn.append(f"Intent: {event.intent.get('name')}")
            if event.entities:
                current_turn.append(
                    f"Entities: {[e.get('entity') for e in event.entities]}"
                )
            if event.commands:
                current_turn.append(
                    f"Commands: {[cmd.get('name') for cmd in event.commands]}"
                )

        elif isinstance(event, BotUttered):
            if event.text:
                current_turn.append(f"Bot: {event.text}")

        elif isinstance(event, ActionExecuted):
            current_turn.append(f"Action: {event.action_name}")
            if event.confidence:
                current_turn.append(f"Confidence: {event.confidence:.2f}")

        elif isinstance(event, SlotSet) and event.key not in DEFAULT_SLOT_NAMES:
            current_turn.append(f"Slot Set: {event.key}={event.value}")

        elif isinstance(event, FlowStarted):
            current_turn.append(f"# Flow Started: {event.flow_id}")

        elif isinstance(event, FlowCompleted):
            current_turn.append(f"# Flow Completed: {event.flow_id}")

    if current_turn:
        context_parts.append(" | ".join(current_turn))

    # Add final state information
    context_parts.append("\nCurrent State:")
    context_parts.append(f"Latest Message: {tracker.latest_message.text or '-'}")

    # Add active flows from stack
    if tracker.active_flow:
        context_parts.append(f"Active Flow: {tracker.active_flow}")
    if tracker.stack:
        context_parts.append(f"Flow Stack: {json.dumps(tracker.stack.as_dict())}")

    # Add slot values that are not None
    non_empty_slots = {
        k: str(v.value)
        for k, v in tracker.slots.items()
        if v is not None and k not in DEFAULT_SLOT_NAMES
    }
    if non_empty_slots:
        context_parts.append(f"Slots: {json.dumps(non_empty_slots)}")

    return "\n".join(context_parts)
