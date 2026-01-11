"""
Basic test script for the StravaClient.
Run manually to verify authentication and activity retrieval and compare our
one-year aggregation against Strava /athletes/{id}/stats blocks.
"""

from client import StravaClient
import datetime
import json
import os

STRAVA_ATHLETE_ID = os.getenv("STRAVA_ATHLETE_ID")


def test_strava_client():
    print("🔍 Testing StravaClient...")

    client = StravaClient()

    # Fetch activities from the last year
    one_year_ago = int((datetime.datetime.utcnow() - datetime.timedelta(days=365)).timestamp())

    try:
        activities = client.get_activities(after_timestamp=one_year_ago)
    except Exception as e:
        print("❌ Error while calling Strava API:")
        print(e)
        return

    if not activities:
        print("⚠️ No activities returned for the last year.")
        return

    # Filter for runs / trail runs / hikes (be liberal in matching sport_type, type, or name)
    def is_run_or_hike(act):
        sport = (act.get("sport_type") or act.get("type") or "").lower().replace(" ", "")
        name = (act.get("name") or "").lower()

        if any(sport == tt for tt in ("run", "trailrun", "hike", "walk")):
            return True

        if any(k in sport for k in ("run", "trail", "hike")):
            return True

        keywords = ("run", "trail", "hike", "race", "long run", "tempo", "interval", "fartlek")
        if any(k in name for k in keywords):
            return True

        return False

    filtered = [a for a in activities if is_run_or_hike(a)]

    # Our approach: sum distances (meters -> km) and elevation gain (meters)
    total_km = sum((a.get("distance") or 0) / 1000.0 for a in filtered)
    total_elev_m = sum(a.get("total_elevation_gain") or 0 for a in filtered)

    print(f"✅ Found {len(filtered)} run/hike/trail activities in the last year.")
    print(f"Total distance (our one-year fetch): {total_km:.2f} km")
    print(f"Total elevation gain (our one-year fetch): {total_elev_m:.1f} m")

    # Show up to 10 most recent matching activities with key fields
    filtered_sorted = sorted(filtered, key=lambda a: a.get("start_date", ""), reverse=True)
    for act in filtered_sorted[:10]:
        start = act.get("start_date", "")
        name = act.get("name", "<no name>")
        sport = (act.get("sport_type") or act.get("type") or "")
        km = (act.get("distance") or 0) / 1000.0
        elev = act.get("total_elevation_gain") or 0
        print(f"- {start}: {name} [{sport}] — {km:.2f} km, {elev:.1f} m")

    # Determine athlete id (env var preferred, then activity payload, then client calls)
    athlete_id = None
    if STRAVA_ATHLETE_ID:
        try:
            athlete_id = int(STRAVA_ATHLETE_ID)
        except ValueError:
            athlete_id = STRAVA_ATHLETE_ID  # keep string if not numeric

    if not athlete_id and activities:
        first = activities[0]
        if isinstance(first, dict):
            athlete_id = (
                first.get("athlete", {}) and first.get("athlete", {}).get("id")
            ) or first.get("athlete_id") or first.get("user_id")

    for meth in ("get_athlete", "get_authenticated_athlete", "get_current_athlete"):
        if athlete_id:
            break
        if hasattr(client, meth):
            try:
                athlete = getattr(client, meth)()
                if isinstance(athlete, dict):
                    athlete_id = athlete.get("id")
                else:
                    athlete_id = getattr(athlete, "id", None)
            except Exception:
                pass

    if not athlete_id:
        print("⚠️ Could not determine athlete id; skipping /athletes/{id}/stats comparison.")
        if filtered_sorted:
            print("📄 Example activity (full details):")
            print(json.dumps(filtered_sorted[0], indent=2, default=str))
        print("🎉 Test completed.")
        return

    # Fetch stats (try common helpers first, then generic GET)
    stats = None
    for meth in ("get_athlete_stats", "get_stats", "athlete_stats"):
        if hasattr(client, meth):
            try:
                stats = getattr(client, meth)(athlete_id)
                break
            except Exception:
                stats = None

    if stats is None and hasattr(client, "get"):
        try:
            stats = client.get(f"/athletes/{athlete_id}/stats")
        except Exception:
            stats = None

    if not stats:
        print("❌ Unable to fetch /athletes/{id}/stats; skipping comparison.")
        if filtered_sorted:
            print("📄 Example activity (full details):")
            print(json.dumps(filtered_sorted[0], indent=2, default=str))
        print("🎉 Test completed.")
        return

    # Helper to safely pull run-stat blocks and compare units (Strava stats distances are meters)
    def cmp_block(label, block):
        dist_m = (block.get("distance") or 0)
        elev_m = (block.get("elevation_gain") or 0)
        dist_km = dist_m / 1000.0
        diff_km = dist_km - total_km
        diff_elev = elev_m - total_elev_m
        pct_km = (diff_km / total_km * 100.0) if total_km else float("nan")
        pct_elev = (diff_elev / total_elev_m * 100.0) if total_elev_m else float("nan")
        print(f"📊 {label}: {dist_km:.2f} km, {elev_m:.1f} m")
        print(f"   ↳ difference vs our one-year fetch: {diff_km:+.2f} km ({pct_km:+.1f}%), {diff_elev:+.1f} m ({pct_elev:+.1f}%)")

    # Compare to common run totals returned by Strava
    cmp_keys = [
        ("all_run_totals", "All-time run totals"),
        ("ytd_run_totals", "Year-to-date run totals"),
        ("recent_run_totals", "Recent run totals (typically last 4 weeks)")
    ]

    printed_any = False
    for key, label in cmp_keys:
        block = stats.get(key) or {}
        if any(block.values()):
            cmp_block(label, block)
            printed_any = True

    if not printed_any:
        # If none of the run totals are present, print raw stats for inspection
        print("ℹ️ /athletes/{id}/stats returned no run totals to compare. Dumping stats for inspection:")
        print(json.dumps(stats, indent=2, default=str))

    if filtered_sorted:
        print("📄 Example activity (full details):")
        print(json.dumps(filtered_sorted[0], indent=2, default=str))

    print("🎉 Test completed.")


if __name__ == "__main__":
    test_strava_client()
