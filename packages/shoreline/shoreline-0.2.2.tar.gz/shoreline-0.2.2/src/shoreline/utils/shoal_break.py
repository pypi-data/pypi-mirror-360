import warnings

import numpy as np
from geopandas import GeoDataFrame
from shapely import reverse
from shapely.affinity import scale
from shapely.geometry import LineString


def find_distance_for_depth(
    line: LineString,
    slope_angle: float,  # in radians, positive angle means seabed goes down
    target_depth: float,
) -> float:
    """
    Calculate the distance along a line needed to reach a target depth.

    This gives the horizontal distance along the sea surface from HAT
    In a right triangle: tan(θ) = opposite / adjacent = depth / horizontal_distance
    Solving for horizontal distance: x = depth / tan(θ)

    solving for sin(θ) would give us hypotenuse. We DO NOT want that: hypotenuse is seafloor distance.

    Args:
        line: LineString representing the incident ray, start -> end must be onshore to offshore
        slope_angle: Bathymetric angle in radians (positive means downward slope)
        target_depth: The depth we want to reach

    Returns:
        Distance along line from start point (HAT point) to reach target_depth

    Raises:
        ValueError: If the geometry is invalid or depth cannot be reached

    """
    # Basic validation
    if target_depth <= 0:
        raise ValueError("Target depth must be positive")

    if slope_angle <= 0:
        raise ValueError("Slope angle must be positive (downward slope)")

    distance = target_depth / np.tan(slope_angle)
    if distance > line.length:
        warnings.warn(
            f"Distance of {distance:.2f} to reach depth {target_depth:.2f} m given slope {slope_angle:.4f} rad exceeds HAT -> LAT ray distance of {line.length:.2f}"
        )

    return distance


def extend_linestring(line_ab, distance):
    """
    Extend a LineString with points A, B by creating a new point C
    such that BC has the same bearing as B→A (end to start) and a specified distance.

    Args:
        line_ab: Shapely LineString with points A, B
        distance: Desired length of new segment BC

    Returns:
        New LineString containing points B, C

    """
    # Extract points A and B
    point_a, point_b = list(line_ab.coords)

    # Create a LineString from B to A (reverse of original)
    reversed_line = reverse(line_ab)

    # Calculate the original length
    vec_x = point_a[0] - point_b[0]
    vec_y = point_a[1] - point_b[1]
    orig_length = (vec_x**2 + vec_y**2) ** 0.5

    # Scale factor to achieve the desired distance
    scale_factor = distance / orig_length

    # Scale the reversed line to the desired length
    scaled_line = scale(
        reversed_line, xfact=scale_factor, yfact=scale_factor, origin=point_b
    )
    return scaled_line


def line_of_breaking(wave_height: float, gdf: GeoDataFrame):
    """Create a new linestring where each vertex is a point on input lines at distance d from start/end.

    Args:
        wave_height: height in metres
        gdf: GeoDataFrame containing projected LineString geometries

    Returns:
        GeoDataFrame with new linestring connecting the interpolated points

    """
    height = wave_height * 0.78
    points = []
    for _, row in gdf.iterrows():
        # reverse needed because line "start" is offshore for these inputs
        distance = find_distance_for_depth(
            reverse(row.geometry), row["slope_radians"], height
        )
        along = row.geometry.interpolate(row.geometry.length - distance)
        points.append(along)

    ls = LineString(points)

    return GeoDataFrame(geometry=[ls], crs=gdf.crs)


def line_of_shoaling(
    wave_period: float, gdf: GeoDataFrame, start: bool = True
) -> GeoDataFrame:
    """Create a new linestring where each vertex is a point on input lines at distance d from start/end.

    Args:
        wave_period: Wave period in seconds
        gdf: GeoDataFrame containing projected LineString geometries
        start: If True, measure from start of line; if False, measure from end

    Returns:
        GeoDataFrame with new linestring connecting the interpolated points

    Citations:
    Short, A. D. (2012). Coastal Processes and Beaches. Nature Education Knowledge, 3(10).
    https://www.nature.com/scitable/knowledge/library/coastal-processes-and-beaches-26276621/

    """
    # wave length is period, velocity is period ^ 2
    wave_length = 1.56 * (wave_period)
    shoal_depth = wave_length / 2.0

    points = []
    for _, row in gdf.iterrows():
        # reverse needed because line "start" is offshore for these inputs
        rev = reverse(row.geometry)
        distance = find_distance_for_depth(rev, row["slope_radians"], shoal_depth)
        # create new ray containing onshore point + shoal distance
        shoal_distance_line = extend_linestring(row.geometry, distance)
        points.append(shoal_distance_line.coords[-1])

    ls = LineString(points)

    return GeoDataFrame(geometry=[ls], crs=gdf.crs)
