"""
serializer.py
Transforms raw Strava activities into a structured dataset
with timestamps and computed metrics.
"""

from datetime import datetime
from analysis.metrics import compute_basic_metrics


def serialize_activities(activities):
    """
    Convert raw Strava activities into a structured dataset.

    Parameters
    ----------
    activities : list[dict]
        Raw Strava activity objects.

    Returns
    -------
    list[dict]
        A list of structured activity entries.

    Example
    -------
    [
    {
        "date": "2025-01-10",
        "timestamp": 1736486400,
        "type": "Run",
        "distance_km": 10.2,
        "moving_time_min": 52.3,
        "pace_min_per_km": 5.13,
        "elevation_gain_m": 120,
        "avg_hr": 148,
        "avg_cadence": 168,
        "avg_power": 245
    },
    ...
    ]

    """

    dataset = []

    for a in activities:
        entry = {
            "id": a.get("id"),
            "name": a.get("name"),
            "type": a.get("type"),
            "timestamp": int(datetime.fromisoformat(a["start_date"].replace("Z", "+00:00")).timestamp()),
            "date": a["start_date"][:10],  # YYYY-MM-DD
            "distance_km": round(a.get("distance", 0) / 1000, 2),
            "moving_time_min": round(a.get("moving_time", 0) / 60, 2),
            "elevation_gain_m": a.get("total_elevation_gain", 0),
            "avg_heart_rate": a.get("average_heartrate"),
            "avg_cadence": a.get("average_cadence"),
            "avg_power": a.get("average_watts"),
        }

        # Derived metrics
        if entry["distance_km"] > 0:
            entry["pace_min_per_km"] = round(
                entry["moving_time_min"] / entry["distance_km"], 2
            )
            entry["avg_speed_kmh"] = round(
                (entry["distance_km"] / (entry["moving_time_min"] / 60)), 2
            )
        else:
            entry["pace_min_per_km"] = None
            entry["avg_speed_kmh"] = None

        dataset.append(entry)

    return dataset
