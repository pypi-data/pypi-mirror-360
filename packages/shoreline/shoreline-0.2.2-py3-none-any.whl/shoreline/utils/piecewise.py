"""
Calculating slopes between two isobaths is fairly straightforward.
However, if we assume that we'll have bathymetric data for spatial extents between
mean low water and mean high water isobaths, it makes sense to try to capture that in order to
characterise the slope of an input ray more accurately.
The simplest approach would seem to be a piecewise calculation, which can be used as input into
a length-weighted average slope.

Some refs from the literature:

Adams, E. W., & Schlager, W. (2000). Basic Types of Submarine Slope Curvature.
Journal of Sedimentary Research, 70(4), 814-828.
https://doi.org/10.1306/2DC4093A-0E47-11D7-8643000102C1865D

O'Grady, D. B., Syvitski, J. P. M., Pratson, L. F., & Sarg, J. F. (2000).
Categorizing the morphologic variability of siliciclastic passive continental margins.
Geology, 28(3), 207-210. Scopus. https://doi.org/10.1130/0091-7613(2000)28<207:ctmvos>2.0.co;2

"""

import warnings

import geopandas as gpd
import numpy as np
from scipy import stats
from shapely.geometry import LineString


def calculate_piecewise_slopes(
    ray: LineString, isobaths: gpd.GeoDataFrame
) -> tuple[list[float], list[float]]:
    """
    Calculate piecewise slopes along a ray intersecting isobaths
    Returns tuple of (slopes, segment_lengths)
    """
    # Enable spatial index if not already enabled
    if not isobaths.sindex:
        isobaths = isobaths.set_index(isobaths.index)

    # Query spatial index for potential intersections
    possible_matches_idx = list(isobaths.sindex.intersection(ray.bounds))
    possible_matches = isobaths.iloc[possible_matches_idx]

    # Find actual intersections
    intersections = []
    for _, row in possible_matches.iterrows():
        if ray.intersects(row.geometry):
            point = ray.intersection(row.geometry)
            if point.geom_type == "MultiPoint":
                points = [(p, row["depth"]) for p in point.geoms]
                intersections.extend(points)
            else:
                intersections.append((point, row["depth"]))

    # Sort intersections by distance along ray
    intersections.sort(key=lambda x: ray.project(x[0]))

    # Calculate slopes and lengths between consecutive points
    slopes = []
    lengths = []
    for i in range(len(intersections) - 1):
        p1, d1 = intersections[i]
        p2, d2 = intersections[i + 1]

        dx = p1.distance(p2)
        dz = d2 - d1

        slopes.append(dz / dx)
        lengths.append(dx)

    return slopes, lengths


def length_weighted_average_slope(
    slopes: list[float], segment_lengths: list[float]
) -> float:
    """
    Compute the length-weighted average slope
    This is probably the simplest way to calculate an average slope from piecewise data
    """
    warnings.warn(
        """A length-weighted average slope is the same as a simple slope. Consider using length_weighted_average_slope_distance_decay instead"""
    )
    return np.average(slopes, weights=segment_lengths)


def calculate_distance_weights(
    slopes: list[float], lengths: list[float], decay_factor: float = 0.5
) -> list[float]:
    """
    Calculate weights that decay with distance from end point.
    decay_factor controls how quickly importance diminishes with distance:

    Higher values mean near-shore segments dominate
    Lower values give a more even distribution of importance
    Setting it to 0 reduces to the original length-weighted approach (length_weighted_average_slope)
    """
    # Calculate cumulative distance from end point
    if decay_factor == 0:
        warnings.warn(
            "The decay factor of 0 will calculate a length-weighted average slope, which is the same as a simple slope."
        )
    cumulative_lengths = np.cumsum(lengths[::-1])[::-1]

    # Apply exponential decay
    weights = np.exp(-decay_factor * cumulative_lengths / np.sum(lengths))

    return weights


def length_weighted_average_slope_distance_decay(
    slopes: list[float], lengths: list[float], decay_factor: float = 0.5
) -> float:
    """Compute average slope with both length and distance weighting"""
    distance_weights = calculate_distance_weights(slopes, lengths, decay_factor)
    # Combine length and distance weights
    final_weights = lengths * distance_weights
    return np.average(slopes, weights=final_weights)


def analyze_slope_distribution(
    slopes: list[float], segment_lengths: list[float]
) -> dict:
    """
    Analyze slope frequency distribution weighted by segment length
    Returns statistical metrics and histogram data
    """
    # Convert to numpy arrays
    slopes = np.array(slopes)
    lengths = np.array(segment_lengths)

    # Calculate weighted statistics
    avg_slope = np.average(slopes, weights=lengths)
    variance = np.average((slopes - avg_slope) ** 2, weights=lengths)
    std_dev = np.sqrt(variance)

    # Create weighted histogram
    hist, bins = np.histogram(
        slopes,
        bins="auto",  # Or specify fixed bins
        weights=lengths,
    )

    # Calculate modality using KDE
    kde = stats.gaussian_kde(slopes, weights=lengths)
    x_eval = np.linspace(min(slopes), max(slopes), 100)
    y_eval = kde(x_eval)
    peaks = stats.find_peaks(y_eval)[0]

    return {
        "mean": avg_slope,
        "std": std_dev,
        "histogram": {"counts": hist, "bins": bins},
        "modality": len(peaks),
        "peaks": x_eval[peaks],
    }


def analyze_slope_distribution_weighted(
    slopes: list[float], lengths: list[float], decay_factor: float = 0.5
) -> dict:
    """
    Analyze slope frequency distribution with both length and distance weighting.
    This should  help identify dominant slope regimes near the shoreline. For example:

    Bimodal distributions might indicate a steeper upper beach face transitioning to a more gentle lower slope
    The variance will now better reflect the variability of slopes in the most relevant (near-shore) sections
    Peak detection will give more emphasis to slope changes near the end point
    """
    # Convert to numpy arrays
    slopes = np.array(slopes)
    lengths = np.array(lengths)

    # Calculate distance weights
    distance_weights = calculate_distance_weights(slopes, lengths, decay_factor)
    final_weights = lengths * distance_weights

    # Calculate weighted statistics
    avg_slope = np.average(slopes, weights=final_weights)
    variance = np.average((slopes - avg_slope) ** 2, weights=final_weights)
    std_dev = np.sqrt(variance)

    # Create weighted histogram
    hist, bins = np.histogram(
        slopes,
        bins="auto",
        weights=final_weights / np.sum(final_weights),  # Normalize weights
    )

    # Calculate modality using distance-weighted KDE
    kde = stats.gaussian_kde(slopes, weights=final_weights)
    x_eval = np.linspace(min(slopes), max(slopes), 100)
    y_eval = kde(x_eval)
    peaks = stats.find_peaks(y_eval)[0]

    return {
        "mean": avg_slope,
        "std": std_dev,
        "histogram": {"counts": hist, "bins": bins},
        "modality": len(peaks),
        "peaks": x_eval[peaks],
        "weights": final_weights,  # Include weights for reference
    }
