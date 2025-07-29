"""_utils_.py

Utility functions for GraphMyTunes analysis modules.
"""

import matplotlib

# Use the 'Agg' backend for non-GUI rendering
matplotlib.use("Agg")
import os

# flake8: noqa: E402
import matplotlib.pyplot as plt
import pandas as pd

from src import __version__


def ensure_columns(df: pd.DataFrame, columns: list[str]) -> None:
    """Ensure the DataFrame contains the specified columns."""
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")


def rating_to_stars(rating: pd.Series) -> pd.Series:
    """Convert iTunes ratings (0-100 scale) to 0-5 stars."""
    rating = (rating.fillna(0) / 20).round().astype(int)
    return rating.clip(lower=0, upper=5)


def trim_label(label: str, max_len: int = 32) -> str:
    """Trim a label to a maximum length, appending an ellipsis if it exceeds
    the limit."""
    return label if len(label) <= max_len else label[:max_len] + "…"


def get_numeric_axes(ax: plt.Axes) -> str:
    """Return "x" if x-axis is numeric, "y" otherwise."""

    def is_numeric(tick_labels: list[plt.Text]) -> bool:
        """Check if the first tick label of a given axis is numeric."""
        if not tick_labels:
            return False
        try:
            float(tick_labels[0].get_text())
            return True
        except ValueError:
            return False

    if ax.get_yticklabels() and is_numeric(ax.get_yticklabels()):
        if ax.get_xticklabels() and is_numeric(ax.get_xticklabels()):
            # Both axes are numeric, prefer x-axis
            return "y"
    if ax.get_xticklabels() and is_numeric(ax.get_xticklabels()):
        # Only x-axis is numeric
        return "x"

    # Neither axis is numeric, default to y-axis
    return "y"


def save_plot(title: str, output_path: str, ext: str = "png", dpi: int = 300) -> None:
    """Save the current plot to a file with the specified extension and dpi,
    with a footer."""

    # Set the font properties for plots
    plt.rcParams["font.family"] = "Lato, Helvetica, Arial, sans-serif"
    plt.rcParams["font.size"] = 10
    plt.rcParams["axes.labelsize"] = 10
    plt.rcParams["axes.titlesize"] = 14
    plt.rcParams["axes.titleweight"] = "bold"

    # Set the plot title and style
    plt.suptitle(
        title,
        fontsize=16,
        fontweight="bold",
        fontstyle="italic",
        color="black",
        ha="center",
    )

    # Keep layout tight, but leave extra space at the bottom for the footer
    plt.subplots_adjust(bottom=0.11)
    plt.tight_layout(rect=(0, 0.03, 1, 1))

    # Ensure grid lines are below the plot elements
    ax = plt.gca()
    ax.set_axisbelow(True)

    # Remove spines for a cleaner look
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)

    # Print text of first tick label of x axis
    ax.grid(axis=get_numeric_axes(ax), linestyle="--", linewidth=0.5, alpha=0.5)

    # Add a footer with version info and GitHub link
    plt.gcf().text(
        0.99,
        0.01,
        f"GraphMyTunes v{__version__} ● https://github.com/homebysix/GraphMyTunes",
        fontsize=6,
        color="gray",
        ha="right",
        va="bottom",
        alpha=0.7,
    )

    # Save and close the plot
    plt.savefig(f"{output_path}.{ext}", dpi=dpi)
    plt.close()


def get_today_matching_tz(date_series: pd.Series) -> pd.Timestamp:
    """Return 'today' as a pd.Timestamp, tz-aware if date_series is tz-aware,
    else naive."""
    if isinstance(date_series.dtype, pd.DatetimeTZDtype):
        tz = date_series.dt.tz
        return pd.Timestamp.now(tz=tz).normalize()
    else:
        return pd.Timestamp.now().normalize()


def sec_to_human_readable(secs: int) -> str:
    """Convert seconds to a human-readable format.
    Format: {YEAR}y {WEEK}w {DAY}d {HOUR}h {MINUTE}m {SECOND}s
    """
    if secs < 0:
        return "0s"

    years, remainder = divmod(secs, 31536000)  # 60 * 60 * 24 * 365
    days, remainder = divmod(remainder, 86400)  # 60 * 60 * 24
    hours, remainder = divmod(remainder, 3600)  # 60 * 60
    minutes, seconds = divmod(remainder, 60)

    parts = []
    units = [
        ("y", years),
        ("d", days),
        ("h", hours),
        ("m", minutes),
        ("s", seconds),
    ]
    parts = [f"{int(value)}{unit}" for unit, value in units if value]
    if not parts:
        parts.append("0s")

    return " ".join(parts)
