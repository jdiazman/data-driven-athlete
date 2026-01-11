"""
Basic test script for the StravaClient.
Run manually to verify authentication and activity retrieval.
"""

from client import StravaClient
import datetime

def test_strava_client():
    print("🔍 Testing StravaClient...")

    client = StravaClient()

    # Optional: fetch only recent activities (last 7 days)
    seven_days_ago = int((datetime.datetime.utcnow() - datetime.timedelta(days=7)).timestamp())

    try:
        activities = client.get_activities(after_timestamp=seven_days_ago)
    except Exception as e:
        print("❌ Error while calling Strava API:")
        print(e)
        return

    if not activities:
        print("⚠️ No activities returned. This may be normal if nothing was recorded recently.")
    else:
        print(f"✅ Retrieved {len(activities)} activities.")
        print("📄 Example activity:")
        print({
            "name": activities[0].get("name"),
            "distance": activities[0].get("distance"),
            "moving_time": activities[0].get("moving_time"),
            "type": activities[0].get("type"),
            "start_date": activities[0].get("start_date"),
        })

    print("🎉 Test completed.")


if __name__ == "__main__":
    test_strava_client()
