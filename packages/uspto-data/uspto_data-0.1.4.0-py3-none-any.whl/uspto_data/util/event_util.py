from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Any, Optional


def get_last_event(eventHistoryBag: List[Any]) -> Optional[Dict[str, Any]]:
    """Retrieve the last recorded event from the patent term adjustment history data."""
    if not eventHistoryBag:
        return None

    last_event = max(eventHistoryBag, key=lambda event: event.eventDate)
    return last_event

def get_events_by_code(event_history: List[Any], event_code: str) -> List[Dict[str, Any]]:
    """Retrieve all events matching a given event code."""
    return [
        {
            "event_code": event.eventCode,
            "event_description": event.eventDescriptionText,
            "event_date": event.eventDate
        }
        for event in event_history if event.eventCode == event_code
    ]


def office_actions(event_history: List[Any]) -> List[Dict[str, Any]]:
    """Retrieve all Office Action events from the event history."""
    office_action_codes = {
        "CTNF", "MCTNF", "CTFR", "MCTFR", "CTRT", "CTRC", "CTPI", "CTAI",
        "NOREJ", "AFCP", "CTCR", "CTSP", "AIAOA", "CTAV", "MCTAV", "CTRS", "MCTRS"
    }

    return [event for event in event_history if event.eventCode in office_action_codes]


def group_and_merge_events(event_history: List[Any], time_threshold_days=7) -> List[Dict[str, Any]]:
    """Groups events by their base code (ignoring "M" mail prefix) and merges them."""
    if not event_history:
        return []

    event_list = []
    for event in event_history:
        try:
            event_list.append({
                "event_code": event.eventCode,
                "event_description": event.eventDescriptionText,
                "event_date": datetime.strptime(event.eventDate, "%Y-%m-%d"),
                "raw_event": event
            })
        except AttributeError:
            continue

    event_list.sort(key=lambda x: x["event_date"])  # Sort by date
    grouped_events = defaultdict(list)

    for event in event_list:
        base_code = event["event_code"][1:] if event["event_code"].startswith("M") else event["event_code"]
        grouped_events[base_code].append(event)

    merged_events = []
    for base_code, event_group in grouped_events.items():
        event_group.sort(key=lambda x: x["event_date"])

        temp_group = []
        for event in event_group:
            if temp_group and (event["event_date"] - temp_group[-1]["event_date"]).days <= time_threshold_days:
                temp_group.append(event)
            else:
                if temp_group:
                    merged_events.append(merge_event_group(temp_group))
                temp_group = [event]

        if temp_group:
            merged_events.append(merge_event_group(temp_group))

    return merged_events


def merge_event_group(event_group: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merges related events into one, prioritizing the 'M' prefixed event.

    Args:
        event_group (List[Dict[str, Any]]): Grouped events to be merged.

    Returns:
        Dict[str, Any]: A single merged event dictionary.
    """
    # Start with the first event as the base
    merged_event = event_group[0].copy()

    for event in event_group:
        # If there's a mailed event, use its data as the primary source
        if event["event_code"].startswith("M"):
            merged_event.update(event)

    # Store all event codes, descriptions, and dates within the merged event
    merged_event["event_codes"] = [e["event_code"] for e in event_group]
    merged_event["event_descriptions"] = [e["event_description"] for e in event_group]
    merged_event["event_dates"] = [e["event_date"].strftime("%Y-%m-%d") for e in event_group]

    return merged_event



def parse_prosecution_history(event_history: List[Any]) -> Dict[str, List[Dict[str, Any]]]:
    """Parses and organizes the prosecution history of a patent, ensuring events are first grouped and merged."""

    if not event_history:
        return {}

    # **Make sure grouping is done first before parsing**
    grouped_events = group_and_merge_events(event_history)

    event_list = []
    for event in grouped_events:
        try:
            event_list.append({
                "event_code": event["event_code"],  # Use dictionary keys
                "event_description": event["event_description"],
                "event_date": event["event_date"],
                "raw_event": event
            })
        except AttributeError:
            continue

    event_list.sort(key=lambda x: x["event_date"])  # Sort events by date
    prosecution_history = defaultdict(list)

    event_categories = {
        "Office Actions": {"CTNF", "MCTNF", "CTFR", "MCTFR", "CTAV", "MCTAV", "CTRS", "MCTRS"},
        "Applicant Responses": {"A...", "A.LA", "A.NE", "A.NA", "A.PE", "RCEX", "ELC."},
        "Interviews": {"EXIN", "MEXIN"},
        "Appeals": {"N/AP", "AP.B", "APEA", "APDA", "APDP", "APDR", "APDS", "APWH"},
        "Final Decisions": {"MN/=", "N/=", "PILS", "PGM/", "WPIR", "ABN2", "MABN2"},
        "Miscellaneous": {"IDSC", "WIDS", "DIST", "PET.", "DOCK"}
    }

    for event in event_list:
        categorized = False
        for category, codes in event_categories.items():
            if event["event_code"] in codes:
                prosecution_history[category].append(event)
                categorized = True
                break

        if not categorized:
            prosecution_history["Other"].append(event)

    return prosecution_history
