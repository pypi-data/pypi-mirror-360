"""album_playtime.py

Show the total play time (duration x play count) for all tracks in each
album. Duration is assumed to be in milliseconds (iTunes 'Total Time').
"""

from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis._utils_ import ensure_columns, save_plot, trim_label


def run(tracks_df: pd.DataFrame, params: Dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    ensure_columns(tracks_df, ["Album", "Play Count", "Total Time"])

    df = tracks_df.dropna(subset=["Album", "Play Count", "Total Time"]).copy()

    # Convert Play Count and Total Time to numeric, fill missing values with 0
    df["Play Count"] = (
        pd.to_numeric(df["Play Count"], errors="coerce").fillna(0).astype(int)
    )
    df["Total Time"] = (
        pd.to_numeric(df["Total Time"], errors="coerce").fillna(0).astype(int)
    )

    # Calculate total play time per track in hours
    df["Total Play Time (Hours)"] = (df["Play Count"] * df["Total Time"]) / (
        1000 * 60 * 60
    )

    # Trim long names
    df["Album (Trimmed)"] = df["Album"].apply(trim_label)

    # Sum play time by trimmed album
    window = (
        df.groupby("Album (Trimmed)")["Total Play Time (Hours)"]
        .sum()
        .sort_values(ascending=True)
    )

    # TODO: Adjust title and result limit based on parameters
    # head_n = params.get("head")
    # tail_n = params.get("tail")
    # if head_n is not None:
    #     window = window.head(int(head_n))
    #     title = f"Top {head_n} Albums by Total Play Time (Hours)"
    # elif tail_n is not None:
    #     window = window.tail(int(tail_n))
    #     title = f"Bottom {head_n} Albums by Total Play Time (Hours)"
    # else:
    window = window.tail(params["top"])

    # Set figure height dynamically based on number of rows
    plt.figure(figsize=(6, max(2, len(window) * 0.35)))

    # Plot the data
    window.plot(
        kind="barh",
        color=plt.get_cmap("tab10").colors,
        edgecolor="black",
    )
    plt.ylabel("Album")
    plt.xlabel("Total Play Time (Hours)")
    title = f"Top {params['top']} Albums by Total Play Time"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
