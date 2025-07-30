# ruff: noqa: S101

import geopandas as gpd
import numpy as np
import pytest
from numpy.testing import assert_almost_equal
from shapely.geometry import LineString

from shoreline import ShorelineAnalyzer
from shoreline.utils.piecewise import (
    calculate_piecewise_slopes,
    length_weighted_average_slope,
    length_weighted_average_slope_distance_decay,
)
from shoreline.utils.smoother import cast_smoothed_rays

SMALL_EPSILON = 1e-10


def test_init():
    sa = ShorelineAnalyzer(
        crs="EPSG:25829",
        shoreline="tests/test_data/dublin_coastline.geojson",
        tideline="tests/test_data/lat.geojson",
        hat=2.09,
        lat=-2.44,
        wave_period=3.0,
        wave_height=2.0,
        ray_resolution=250,
    )
    analysis = sa.evaluate()
    assert_almost_equal(analysis.metrics["mean_angle"], np.float64(0.17205233009279952))


def test_straight_line():
    """Test rays cast from a straight line are perpendicular."""
    line = LineString([(0, 0), (0, 10)])
    rays = cast_smoothed_rays(line, window=2, ray_length=1)

    # For a vertical line, rays should point left (negative x direction)
    for ray in rays:
        coords = ray.coords
        assert len(coords) == 2  # start and end point
        start, end = coords
        # Check ray direction is horizontal (y coordinates approximately equal)
        assert abs(end[1] - start[1]) < SMALL_EPSILON
        # Check ray points left
        assert end[0] < start[0]


def test_smoothing_effect():
    """Test that smoothing actually affects ray directions on a complex curve."""
    # Create an S-curve with a sharp turn to test smoothing
    t = np.linspace(0, 2 * np.pi, 20)
    x = t
    y = np.sin(t)  # creates an S-curve
    curve = LineString(zip(x, y))

    # Test with different window sizes
    small_window_rays = cast_smoothed_rays(curve, window=0.1, ray_length=1)
    large_window_rays = cast_smoothed_rays(curve, window=4.0, ray_length=1)

    # Compare ray directions at the inflection point (middle of S)
    mid_idx = len(t) // 2
    small_ray = small_window_rays[mid_idx]
    large_ray = large_window_rays[mid_idx]

    # Get ray vectors
    def get_ray_vector(ray):
        start, end = ray.coords
        vec = np.array([end[0] - start[0], end[1] - start[1]])
        return vec / np.linalg.norm(vec)

    small_vec = get_ray_vector(small_ray)
    large_vec = get_ray_vector(large_ray)

    # The rays should differ due to smoothing
    dot_product = np.dot(small_vec, large_vec)
    angle_diff = np.arccos(dot_product) * 180 / np.pi

    # If smoothing is working, rays should differ significantly
    assert angle_diff > 10, "Smoothing window size should affect ray direction"


def test_collinear_points():
    """Test that collinear points produce perpendicular rays."""
    # Create a straight line where smoothing_vec calculation would normally
    # involve collinear points
    line = LineString([(0, 0), (0, 5), (0, 10)])
    rays = cast_smoothed_rays(line, window=2, ray_length=1)

    # For a vertical line, rays should point exactly left (-1, 0)
    for ray in rays:
        start, end = ray.coords
        ray_vector = np.array([end[0] - start[0], end[1] - start[1]])
        ray_vector = ray_vector / np.linalg.norm(ray_vector)

        # Should be exactly [-1, 0] for left-pointing rays
        assert np.allclose(ray_vector, [-1, 0], atol=SMALL_EPSILON)

    # Test right-pointing rays too
    rays_right = cast_smoothed_rays(line, window=2, ray_length=1, right=True)
    for ray in rays_right:
        start, end = ray.coords
        ray_vector = np.array([end[0] - start[0], end[1] - start[1]])
        ray_vector = ray_vector / np.linalg.norm(ray_vector)

        # Should be exactly [1, 0] for right-pointing rays
        assert np.allclose(ray_vector, [1, 0], atol=SMALL_EPSILON)


def test_right_direction():
    """Test rays are cast rightward when right=True."""
    line = LineString([(0, 0), (0, 10)])
    rays = cast_smoothed_rays(line, window=2, ray_length=1, right=True)

    for ray in rays:
        start, end = ray.coords
        # Check rays point right
        assert end[0] > start[0]


def test_window_clamping():
    """Test window clamping at line endpoints."""
    line = LineString([(0, 0), (0, 10)])
    window = 4
    rays = cast_smoothed_rays(line, window=window, ray_length=1)

    # First and last rays should still be perpendicular
    # despite having asymmetric windows
    first_ray = rays[0]
    last_ray = rays[-1]

    for ray in [first_ray, last_ray]:
        start, end = ray.coords
        # Check ray is horizontal
        assert abs(end[1] - start[1]) < SMALL_EPSILON


def test_ray_length():
    """Test rays have correct length."""
    line = LineString([(0, 0), (0, 10)])
    length = 2.5
    rays = cast_smoothed_rays(line, window=2, ray_length=length)

    for ray in rays:
        assert abs(ray.length - length) < SMALL_EPSILON


def test_invalid_inputs():
    """Test handling of invalid inputs."""
    line = LineString([(0, 0), (0, 10)])

    # Negative window
    with pytest.raises(ValueError):
        cast_smoothed_rays(line, window=-1)

    # Negative ray length
    with pytest.raises(ValueError):
        cast_smoothed_rays(line, ray_length=-1)


def test_weighted_slope_calculations():
    # Create a simple LineString that will intersect our isobaths
    ray = LineString([(0, 0), (280, 0)])  # Length matches total of our segments

    # Create isobaths with depths that will give us our desired slopes
    depths = [0, 50, 114, 264, 312]  # These values will create our desired slopes
    isobaths = gpd.GeoDataFrame(
        {
            "depth": depths,
            "geometry": [
                LineString([(x, -10), (x, 10)]) for x in [0, 100, 180, 240, 280]
            ],
        }
    )

    # Calculate slopes and lengths
    slopes, lengths = calculate_piecewise_slopes(ray, isobaths)

    # Test each decay factor
    expected = {0.0: 1.1143, 0.2: 1.1481, 0.5: 1.1980, 0.75: 1.2384}

    for decay_factor, expected_slope in expected.items():
        weighted_slope = length_weighted_average_slope_distance_decay(
            slopes, lengths, decay_factor
        )
        assert np.isclose(weighted_slope, expected_slope, rtol=1e-4), (
            f"Decay factor {decay_factor}: expected {expected_slope}, got {weighted_slope}"
        )


def test_decay_zero_matches_simple_weighted():
    # Using our test values
    slopes = [0.5, 0.8, 2.5, 1.2]
    lengths = [100, 80, 60, 40]

    # Calculate using both methods
    simple_weighted = length_weighted_average_slope(slopes, lengths)
    distance_weighted = length_weighted_average_slope_distance_decay(
        slopes, lengths, decay_factor=0.0
    )
    assert np.isclose(simple_weighted, distance_weighted, rtol=1e-10)
