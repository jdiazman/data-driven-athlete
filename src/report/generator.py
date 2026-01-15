"""
generator.py
Enhanced weekly PDF report with charts and styling.
"""

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from datetime import datetime

from report.charts import (
    plot_distance_hr_elevation
)
def draw_header(c, width, height, start_date, end_date):
    # Orange bar
    c.setFillColorRGB(1, 0.55, 0.1)  # soft orange
    c.rect(0, height - 2*cm, width, 2*cm, fill=True, stroke=False)

    # Title
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(1.5*cm, height - 1.2*cm, "Weekly Training Report")

    # Period
    c.setFont("Helvetica", 11)
    c.drawString(1.5*cm, height - 1.8*cm, f"Period: {start_date} → {end_date}")


def generate_weekly_report(dataset, metrics, output_path="weekly_report.pdf"):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    start_date = dataset[0]["date"]
    end_date = dataset[-1]["date"]

    # Header
    draw_header(c, width, height, start_date, end_date)

    # Summary section
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, height - 3.5*cm, "Weekly Summary")

    y = height - 4.8*cm
    c.setFont("Helvetica", 12)

    for key, value in metrics.items():
        label = key.replace("_", " ").title()
        c.drawString(2*cm, y, f"- {label}: {value}")
        y -= 0.6*cm

    # Generate chart
    plot_distance_hr_elevation(dataset)

    # Insert chart
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, y - 1*cm, "Weekly Chart")
    y -= 2*cm

    img = ImageReader("combined_chart.png")
    c.drawImage(img, 2*cm, y - 10*cm, width=16*cm, height=10*cm)

    c.save()
    print(f"📄 Weekly report saved to {output_path}")

def insert_chart(c, title, path, x=2*cm, y_offset=12*cm):
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y_offset + 0.5*cm, title)
    img = ImageReader(path)
    c.drawImage(img, x, y_offset - 8*cm, width=16*cm, height=8*cm)

