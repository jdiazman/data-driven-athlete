"""
charts.py
Improved charts for weekly training reports.
"""
import matplotlib.pyplot as plt
import numpy as np

def plot_distance_hr_elevation(dataset, output_path="combined_chart.png"):
    dates = [d["date"] for d in dataset]
    distance = np.array([d["distance_km"] for d in dataset])
    elevation = np.array([d["elevation_gain_m"] for d in dataset])
    hr = np.array([d["avg_heart_rate"] for d in dataset])

    plt.figure(figsize=(10, 4))

    # --- Primary axis: Distance ---
    ax1 = plt.gca()
    ax1.plot(dates, distance, marker="o", color="#0077cc", linewidth=2, label="Distance (km)")
    ax1.set_ylabel("Distance (km)", color="#0077cc")
    ax1.tick_params(axis="y", labelcolor="#0077cc")

    # --- Secondary axis: Elevation (normalized) ---
    ax2 = ax1.twinx()

    if elevation.max() > 0:
        # Normalize elevation to match distance visually
        elev_norm = elevation / elevation.max() * distance.max()
        ax2.bar(dates, elev_norm, color="#ffaa55", alpha=0.4, label="Elevation (scaled)")
        ax2.set_ylabel("Elevation (scaled)", color="#ffaa55")
        ax2.tick_params(axis="y", labelcolor="#ffaa55")

    # --- Heart rate (dots) ---
    if any(hr):
        ax3 = ax1.twinx()
        ax3.spines["right"].set_position(("outward", 50))  # offset third axis
        ax3.scatter(dates, hr, color="#cc0000", s=60, label="Heart Rate (bpm)")
        ax3.set_ylabel("Heart Rate (bpm)", color="#cc0000")
        ax3.tick_params(axis="y", labelcolor="#cc0000")

    # Styling
    plt.xticks(rotation=90)
    plt.title("Distance, Heart Rate & Elevation (Scaled)")
    ax1.grid(True, alpha=0.3)

    # Combined legend
    lines = []
    labels = []
    for ax in [ax1, ax2, ax3] if any(hr) else [ax1, ax2]:
        l, lab = ax.get_legend_handles_labels()
        lines.extend(l)
        labels.extend(lab)

    plt.legend(lines, labels, loc="upper left")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
