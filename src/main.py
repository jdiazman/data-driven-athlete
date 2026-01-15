"""
main.py
Basic end-to-end pipeline for DataDrivenAthlete.

Steps:
1. Fetch raw activities from Strava
2. Serialize them into a structured dataset
3. Compute aggregated metrics
4. Return everything for further analysis or insights
"""

from strava.client import StravaClient
from analysis.serializer import serialize_activities
from analysis.metrics import compute_basic_metrics
from report.generator import generate_weekly_report


def run_basic_pipeline(days_back=7):
    print("🏃 Running basic DataDrivenAthlete pipeline...")

    # 1. Fetch activities
    client = StravaClient()
    print(f"📡 Fetching activities from the last {days_back} days...")

    from datetime import datetime, timedelta
    after_ts = int((datetime.utcnow() - timedelta(days=days_back)).timestamp())

    try:
        raw_activities = client.get_activities(after_timestamp=after_ts)
    except Exception as e:
        print("❌ Error fetching activities:", e)
        return None

    if not raw_activities:
        print("⚠️ No activities found.")
        return None

    print(f"📥 Retrieved {len(raw_activities)} activities.")

    # 2. Serialize activities
    print("🔧 Serializing activities...")
    dataset = serialize_activities(raw_activities)

    # 3. Compute aggregated metrics
    print("📊 Computing metrics...")
    metrics = compute_basic_metrics(raw_activities)

    print("✨ Basic pipeline completed.")
    return {
        "dataset": dataset,
        "metrics": metrics,
    }

if __name__ == "__main__":
    result = run_basic_pipeline(days_back=7)
    if result: 
        print("\n📄 Dataset sample:") 
        print(result["dataset"][0]) 
        print("\n📊 Aggregated metrics:") 
        for k, v in result["metrics"].items(): 
            print(f"- {k}: {v}")
        generate_weekly_report(
            dataset=result["dataset"],
            metrics=result["metrics"],
            output_path="weekly_report.pdf"
        )