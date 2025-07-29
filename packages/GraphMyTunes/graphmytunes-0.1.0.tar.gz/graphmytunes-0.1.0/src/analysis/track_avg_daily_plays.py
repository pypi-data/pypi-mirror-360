"""track_avg_daily_plays.py

Graph the top N tracks based on average daily plays:
Play Count divided by number of days the track has been in the library (today minus 'Date Added').
"""

from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis._utils_ import (
    ensure_columns,
    get_today_matching_tz,
    save_plot,
    trim_label,
)


def run(tracks_df: pd.DataFrame, params: Dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    ensure_columns(tracks_df, ["Play Count", "Date Added", "Name"])

    df = tracks_df.dropna(subset=["Play Count", "Date Added", "Name"]).copy()

    # Convert Play Count to numeric, fill missing values with 0
    df["Play Count"] = (
        pd.to_numeric(df["Play Count"], errors="coerce").fillna(0).astype(int)
    )

    # Convert Date Added to datetime, skip missing values
    df["Date Added"] = pd.to_datetime(df["Date Added"], errors="coerce")
    df = df.dropna(subset=["Date Added"])

    today = get_today_matching_tz(df["Date Added"])

    df["Days In Library"] = (today - df["Date Added"].dt.floor("D")).dt.days.clip(
        lower=1
    )
    df["Avg Daily Plays"] = df["Play Count"] / df["Days In Library"]

    # Get top 50 tracks by average daily plays
    window = df.sort_values("Avg Daily Plays", ascending=False).head(params["top"])

    # Trim long names
    window["Name (Trimmed)"] = window["Name"].apply(trim_label)

    # Set figure height dynamically based on number of rows
    plt.figure(figsize=(6, max(2, len(window) * 0.35)))

    # Plot the data
    window[::-1].plot(
        kind="barh",
        x="Name (Trimmed)",
        y="Avg Daily Plays",
        color=plt.get_cmap("tab10").colors,
        edgecolor="black",
        legend=False,
        ax=plt.gca(),
    )
    plt.xlabel("Average Daily Plays")
    title = f"Top {params['top']} Tracks by Average Daily Plays"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
