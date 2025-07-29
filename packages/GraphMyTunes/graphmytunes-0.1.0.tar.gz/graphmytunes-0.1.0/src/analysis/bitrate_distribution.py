"""bitrate_distribution.py

Produce a histogram showing the frequency of song bitrates (using the
'Bit Rate' field).
"""

from typing import Any, Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.analysis._utils_ import ensure_columns, save_plot


def run(tracks_df: pd.DataFrame, params: Dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    ensure_columns(tracks_df, ["Bit Rate"])

    # Convert Bit Rate to numeric, drop NaNs
    bitrates = pd.to_numeric(tracks_df["Bit Rate"], errors="coerce").dropna()
    # Omit outliers beyond the 99th percentile
    upper_limit = bitrates.quantile(0.99)
    filtered_bitrates = bitrates[bitrates <= upper_limit]
    max_bitrate = filtered_bitrates.max()
    min_bitrate = filtered_bitrates.min()
    # Define bins (e.g., 16 kbps steps)
    bins = np.arange(min_bitrate, max_bitrate + 16, 16)
    plt.figure(figsize=(10, 6))
    plt.hist(
        filtered_bitrates,
        bins=bins,
        color=plt.get_cmap("tab10")(0),  # Use a single color for the dataset
        edgecolor="black",
    )
    plt.xlabel("Bit Rate (kbps)")
    plt.ylabel("Number of Tracks")
    plt.xlim(0, 2000)
    plt.xticks(np.arange(0, 2001, 64), rotation=45)
    title = "Distribution of Song Bit Rates (≤99th percentile)"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
