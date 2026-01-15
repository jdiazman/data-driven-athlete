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
        activities = []
        page = 1
        per_page = 200  # fetch the largest page size supported by Strava
        page_supported = True
        while True:
            try:
                # try the common signature that accepts a 'page' kwarg
                batch = client.get_activities(after=one_year_ago, page=page, per_page=per_page)
            except TypeError:
                # fallback: client may expect different param names or not support page-based pagination
                page_supported = False
                try:
                    batch = client.get_activities(after=one_year_ago, per_page=per_page)
                except TypeError:
                    # final fallback to older/alternate param name used elsewhere
                    batch = client.get_activities(after_timestamp=one_year_ago, per_page=per_page)
            if not batch:
                break
            activities.extend(batch)
            if len(batch) < per_page:
                break
            if not page_supported:
                # cannot paginate by page on this client interface; stop after first page
                break
            page += 1
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



    if filtered_sorted:
        print("📄 Example activity (full details):")
        print(json.dumps(filtered_sorted[0], indent=2, default=str))

    print("🎉 Test completed.")


if __name__ == "__main__":
    test_strava_client()
