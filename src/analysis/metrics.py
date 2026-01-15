def compute_basic_metrics(activities):
    """
    Compute aggregated metrics from a list of Strava activities.

    Parameters
    ----------
    activities : list[dict]
        Raw activity objects returned by the Strava API. https://developers.strava.com/docs/reference/#api-models-SummaryActivity

    Returns
    -------
    dict
        A dictionary containing aggregated metrics.
    """

    if not activities:
        return {
            "total_distance_km": 0,
            "total_moving_time_min": 0,
            "avg_pace_min_per_km": None,
            "total_elevation_gain_m": 0,
            "avg_speed_kmh": None,
            "avg_heart_rate": None,
            "avg_cadence": None,
            "avg_power": None,
        }

    # Filter out non-distance sessions (e.g. "Workout", "Strength") and activities with no distance
    excluded_types = {"Workout", "Strength"}
    relevant_activities = [
        a for a in activities
        if a.get("type") not in excluded_types and a.get("distance", 0) > 0
    ]

    if not relevant_activities:
        return {
            "total_distance_km": 0,
            "total_moving_time_min": 0,
            "avg_pace_min_per_km": None,
            "total_elevation_gain_m": 0,
            "avg_speed_kmh": None,
            "avg_heart_rate": None,
            "avg_cadence": None,
            "avg_power": None,
        }

    # Core metrics
    total_distance = sum(a.get("distance", 0) for a in relevant_activities)  # meters
    total_moving_time = sum(a.get("moving_time", 0) for a in relevant_activities)  # seconds
    total_elevation = sum(a.get("total_elevation_gain", 0) for a in relevant_activities)

    # Heart rate
    hr_values = [a.get("average_heartrate") for a in relevant_activities if a.get("average_heartrate")]
    avg_hr = sum(hr_values) / len(hr_values) if hr_values else None

    # Cadence (running or cycling)
    cadence_values = [a.get("average_cadence") for a in relevant_activities if a.get("average_cadence")]
    avg_cadence = sum(cadence_values) / len(cadence_values) if cadence_values else None

    # Power (cycling or running power meters)
    power_values = [a.get("average_watts") for a in relevant_activities if a.get("average_watts")]
    avg_power = sum(power_values) / len(power_values) if power_values else None

    # Derived metrics
    total_distance_km = total_distance / 1000
    total_moving_time_min = total_moving_time / 60

    if total_distance_km > 0:
        avg_pace_min_per_km = total_moving_time_min / total_distance_km
        avg_speed_kmh = (total_distance_km / total_moving_time) * 3600
    else:
        avg_pace_min_per_km = None
        avg_speed_kmh = None

    return {
        "total_distance_km": round(total_distance_km, 2),
        "total_moving_time_min": round(total_moving_time_min, 1),
        "avg_pace_min_per_km": round(avg_pace_min_per_km, 2) if avg_pace_min_per_km else None,
        "total_elevation_gain_m": round(total_elevation, 1),
        "avg_speed_kmh": round(avg_speed_kmh, 2) if avg_speed_kmh else None,
        "avg_heart_rate": round(avg_hr, 1) if avg_hr else None,
        "avg_cadence": round(avg_cadence, 1) if avg_cadence else None,
        "avg_power": round(avg_power, 1) if avg_power else None,
    }
