"""plays_by_month.py

Graph the number of plays grouped by month. Uses the 'Play Date UTC'
field and converts to the specified time zone.
"""

from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd
import pytz

from src.analysis._utils_ import ensure_columns, save_plot


def run(tracks_df: pd.DataFrame, params: Dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    ensure_columns(tracks_df, ["Play Date UTC"])

    # Get time zone from params or use default
    default_tz = "America/Los_Angeles"
    time_zone = params.get("time_zone", default_tz)
    try:
        tz = pytz.timezone(time_zone)
    except Exception:
        tz = pytz.timezone(default_tz)

    # Drop missing play dates and convert to datetime
    df = tracks_df.dropna(subset=["Play Date UTC"]).copy()
    df["Play Date UTC"] = pd.to_datetime(df["Play Date UTC"], errors="coerce", utc=True)
    df = df.dropna(subset=["Play Date UTC"])

    # Convert to local time zone
    df["Local Play Time"] = df["Play Date UTC"].dt.tz_convert(tz)

    # Extract month (1-12)
    df["Month"] = df["Local Play Time"].dt.month

    # Count plays by month across all years
    window = df.groupby("Month").size().reindex(range(1, 13), fill_value=0)

    # Prepare labels for x-axis (month names)
    month_labels = [
        pd.Timestamp(month=m, day=1, year=2000).strftime("%B") for m in window.index
    ]

    # Set figure width dynamically based on number of columns
    plt.figure(figsize=(max(6, len(window) * 0.35), 6))

    # Plot the results
    window.plot(
        kind="bar",
        color=plt.get_cmap("tab10").colors,
        edgecolor="black",
    )
    plt.xlabel("Month")
    plt.ylabel("Tracks")
    plt.xticks(ticks=range(12), labels=month_labels, rotation=45)
    title = "Plays by Month"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
