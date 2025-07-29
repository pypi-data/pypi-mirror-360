"""artist_skips.py

Show the total skip count for all tracks by each artist.
"""

from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis._utils_ import ensure_columns, save_plot


def run(tracks_df: pd.DataFrame, params: Dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    ensure_columns(tracks_df, ["Artist", "Skip Count"])

    df = tracks_df.dropna(subset=["Artist", "Skip Count"]).copy()

    # Convert Skip Count to numeric, fill missing values with 0
    df["Skip Count"] = (
        pd.to_numeric(df["Skip Count"], errors="coerce").fillna(0).astype(int)
    )

    # Sum skip count by artist and limit to top N
    window = (
        df.groupby("Artist")["Skip Count"]
        .sum()
        .sort_values(ascending=False)
        .head(params["top"])
        .sort_values(ascending=True)
    )

    # Set figure height dynamically based on number of rows
    plt.figure(figsize=(6, max(2, len(window) * 0.35)))

    # Plot the data
    window.plot(
        kind="barh",
        color=plt.get_cmap("tab10").colors,
        edgecolor="black",
    )
    plt.ylabel("Artist")
    plt.xlabel("Total Skip Count")
    title = f"Top {params['top']} Artists by Skip Count"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
