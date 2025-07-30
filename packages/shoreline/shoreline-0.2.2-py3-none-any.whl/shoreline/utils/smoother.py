import numpy as np
from shapely.affinity import rotate, scale, translate
from shapely.geometry import LineString, MultiLineString, Point

SMALL_EPSILON = 1e-10


def determine_ray_direction(gdf_a, gdf_b):
    """
    Determine the direction to cast perpendicular rays from A towards B.

    Args:
    gdf_a (GeoDataFrame): Contains LineString or MultiLineString geometries
    gdf_b (GeoDataFrame): Contains target geometries (Polygon, MultiPolygon, or other types)

    Returns:
    str: 'left' or 'right' indicating the "side" of A on which B is located

    """
    # Compute centroids
    centroid_a = gdf_a.geometry.centroid.iloc[0]
    centroid_b = gdf_b.geometry.centroid.iloc[0]

    # Get the LineString from gdf_a
    geom_a = gdf_a.geometry.iloc[0]

    # Extract direction vector for LineString A
    if isinstance(geom_a, LineString):
        coords = list(geom_a.coords)
        start_point = coords[0]
        end_point = coords[-1]
        dir_a = (end_point[0] - start_point[0], end_point[1] - start_point[1])
    elif isinstance(geom_a, MultiLineString):
        # Use the longest component for direction
        longest_length = 0
        dir_a = None

        for line in geom_a.geoms:
            coords = list(line.coords)
            if len(coords) < 2:
                continue

            line_length = line.length
            if line_length > longest_length:
                longest_length = line_length
                start_point = coords[0]
                end_point = coords[-1]
                dir_a = (end_point[0] - start_point[0], end_point[1] - start_point[1])
    else:
        raise ValueError("LAT must be LineString or MultiLineString")  # noqa: TRY004

    # Normalize direction vector
    dir_magnitude = np.sqrt(dir_a[0] ** 2 + dir_a[1] ** 2)
    if dir_magnitude == 0:
        raise ValueError("Direction vector has zero magnitude")

    dir_a = (dir_a[0] / dir_magnitude, dir_a[1] / dir_magnitude)

    # TODO there's probably a better way to work out perp. vector and dot product
    # using Shapely, but I am very tired
    # Calculate perpendicular vector (to the left)
    perp_vector = (-dir_a[1], dir_a[0])

    # Vector from centroid_a to centroid_b
    vec_ab = (centroid_b.x - centroid_a.x, centroid_b.y - centroid_a.y)

    # Calculate dot product
    dot_product = vec_ab[0] * perp_vector[0] + vec_ab[1] * perp_vector[1]

    # Determine the side
    if dot_product > 0:
        return "left"
    else:
        return "right"


def cast_smoothed_rays(
    input_linestring, window=500, ray_length=1000, right=False
) -> list[Point]:
    """
    Smooth rays cast from input LineString

    An implementation of the ray smoothing technique described by DSAS:
    Emily A Himmelstoss, Rachel E Henderson, Meredith G Kratzmann, and Amy S Farris.
    Digital shoreline analysis system (dsas) version 5.0 user guide.
    Technical Report, US Geological Survey, 2018
    """
    if window <= 0:
        raise ValueError("Smoothing window size must be positive")
    if ray_length <= 0:
        raise ValueError("Ray length must be positive")
    rays = []

    for vertex in input_linestring.coords:
        vertex_distance = input_linestring.project(Point(vertex))

        # Get points half window before / after, clamped to line ends
        smoother_start_pos = max(0, vertex_distance - window / 2)
        smoother_end_pos = min(input_linestring.length, vertex_distance + window / 2)

        # make points
        smoother_start_point = np.array(
            input_linestring.interpolate(smoother_start_pos).coords[0]
        )
        smoother_end_point = np.array(
            input_linestring.interpolate(smoother_end_pos).coords[0]
        )
        vertex_point = np.array(vertex)

        # Check for collinearity using cross product
        v1 = vertex_point - smoother_start_point
        v2 = smoother_end_point - smoother_start_point
        # Convert to 3D vectors by adding z=0 to keep NumPy 2 happy
        v1_3d = np.array([v1[0], v1[1], 0])
        v2_3d = np.array([v2[0], v2[1], 0])
        cross_prod = np.cross(v1_3d, v2_3d)[2]

        if (
            abs(cross_prod) < SMALL_EPSILON
        ):  # Using small epsilon for floating point comparison
            # For collinear points, use the direction vector directly
            direction = v2 / np.linalg.norm(v2)
            # Create perpendicular vector (consistently with non-collinear case)
            perp_vec = (
                np.array([direction[1], -direction[0]])
                if right
                else np.array([-direction[1], direction[0]])
            )
            ray = LineString([vertex, vertex + perp_vec * ray_length])
            rays.append(ray)
            continue

        # Original smoothing logic for non-collinear points

        # smoothing_vec will be rotated from the input LineString segment that vertex is on
        # if start_pos, vertex, and end_pos are not collinear
        # (i.e. the line has "turned" and the window has "seen" the turn)
        smoothing_vec = smoother_end_point - smoother_start_point
        perp_vec = (
            np.array([smoothing_vec[1], -smoothing_vec[0]])
            if right
            else np.array([-smoothing_vec[1], smoothing_vec[0]])
        )

        # Normalize to unit vector
        perp_vec = perp_vec / np.linalg.norm(perp_vec)
        ray = LineString([vertex, vertex + perp_vec * ray_length])
        rays.append(ray)

    return rays


def cast_snell_rays(
    input_linestring,
    origin_distance=3500,
    origin_angle=0,
    ray_length=10000,
    ray_interval=10,
    refractive_index_ratio=0.9,
    right=False,
) -> tuple[list[LineString], list[LineString]]:
    """
    Cast rays using Snell's law refraction at the LAT (lowest astronomical tide) line.

    Creates an origin line by finding the seaward edge of LAT's bounding box, translating
    it seaward, rotating it, and scaling it. Rays are cast perpendicular from this line
    toward LAT where they refract according to Snell's law.

    Parameters
    ----------
    input_linestring : LineString
        The LAT line where refraction occurs
    origin_distance : float
        Distance to translate the origin line seaward
    origin_angle : float
        Angle in degrees to rotate the origin line (0 = north-to-south)
    ray_length : float
        Length of refracted rays after crossing LAT
    ray_interval : float
        Distance between rays along the origin line (in meters)
    refractive_index_ratio : float
        n1/n2 where n1 is refractive index seaward (deep water) and n2 is shoreward (shallow)
        Typical value ~0.9 for wave refraction from deep to shallow water
    right : bool
        If True, seaward is to the right when looking from start to end of LAT.
        If False, seaward is to the left.

    Returns
    -------
    tuple[list[LineString], list[LineString]] :
        - [0]: Refracted rays from LAT line traveling shoreward
        - [1]: Incident rays from origin line to LAT line

    """
    if origin_distance <= 0:
        raise ValueError("Origin distance must be positive")
    if ray_length <= 0:
        raise ValueError("Ray length must be positive")
    if ray_interval <= 0:
        raise ValueError("Ray interval must be positive")

    # Get bounding box of LAT line
    minx, miny, maxx, maxy = input_linestring.bounds

    # Determine which edge is seaward based on the 'right' parameter
    # First, get general direction of LAT line
    coords = np.array(input_linestring.coords)
    start_pt = coords[0]
    end_pt = coords[-1]
    lat_direction = end_pt - start_pt
    lat_angle = np.degrees(np.arctan2(lat_direction[1], lat_direction[0]))

    # Normalize angle to [0, 360)
    lat_angle = lat_angle % 360

    # Determine which bbox edge is seaward
    # The perpendicular to LAT points right if 'right' is True
    if right:
        perp_angle = (lat_angle - 90) % 360
    else:
        perp_angle = (lat_angle + 90) % 360

    # Determine which edge to use based on perpendicular direction
    # Angles: 0=East, 90=North, 180=West, 270=South
    if 315 <= perp_angle or perp_angle < 45:  # Pointing mostly East
        origin_edge = LineString([(maxx, miny), (maxx, maxy)])  # Right edge
        translate_x, translate_y = origin_distance, 0
    elif 45 <= perp_angle < 135:  # Pointing mostly North
        origin_edge = LineString([(minx, maxy), (maxx, maxy)])  # Top edge
        translate_x, translate_y = 0, origin_distance
    elif 135 <= perp_angle < 225:  # Pointing mostly West
        origin_edge = LineString([(minx, miny), (minx, maxy)])  # Left edge
        translate_x, translate_y = -origin_distance, 0
    else:  # 225 <= perp_angle < 315, pointing mostly South
        origin_edge = LineString([(minx, miny), (maxx, miny)])  # Bottom edge
        translate_x, translate_y = 0, -origin_distance

    # Transform the origin edge: translate, rotate, then scale
    # First translate seaward
    origin_line = translate(origin_edge, xoff=translate_x, yoff=translate_y)

    # Calculate scale factor to ensure origin line extends well beyond LAT
    # The origin line needs to be long enough that rays from its ends can still hit LAT extremes
    # after rotation. Use the diagonal of the bounding box as a reference
    bbox_diagonal = np.sqrt((maxx - minx) ** 2 + (maxy - miny) ** 2)
    origin_edge_length = origin_edge.length

    # We want the origin line to be at least as long as the bbox diagonal
    # plus some margin to account for rotation and ensure coverage
    desired_length = bbox_diagonal * 1.5
    scale_factor = max(desired_length / origin_edge_length, 1.2)

    # Get center for rotation and scaling
    center = origin_line.centroid

    # Rotate by origin_angle (around center of origin line)
    origin_line = rotate(origin_line, origin_angle, origin=center)

    # Scale by adaptive factor
    origin_line = scale(
        origin_line, xfact=scale_factor, yfact=scale_factor, origin=center
    )

    # Generate ray starting points along origin line
    origin_length = origin_line.length
    num_rays = int(origin_length / ray_interval) + 1

    # Determine ray direction (perpendicular to origin line, toward LAT)
    # Get origin line direction
    origin_coords = np.array(origin_line.coords)
    origin_dir = origin_coords[-1] - origin_coords[0]
    origin_dir = origin_dir / np.linalg.norm(origin_dir)

    # Perpendicular direction should point toward LAT
    # Check which perpendicular points toward LAT centroid
    perp1 = np.array([-origin_dir[1], origin_dir[0]])
    perp2 = -perp1

    lat_centroid = np.array(input_linestring.centroid.coords[0])
    origin_centroid = np.array(origin_line.centroid.coords[0])
    to_lat = lat_centroid - origin_centroid

    # Choose perpendicular that points more toward LAT
    ray_dir = perp1 if np.dot(perp1, to_lat) > 0 else perp2

    # Determine how far rays need to travel to ensure they pass LAT
    # Use the bounding box to find maximum required distance
    max_ray_dist = max(maxx - minx, maxy - miny) + 2 * origin_distance

    refracted_rays = []
    incident_rays = []

    # Cast rays from origin line
    for i in range(num_rays):
        # Get point along origin line
        distance_along = i * ray_interval
        if distance_along > origin_length:
            break

        origin_pt = origin_line.interpolate(distance_along)
        origin_coords = np.array(origin_pt.coords[0])

        # Create ray toward LAT
        ray_end = origin_coords + ray_dir * max_ray_dist
        ray = LineString([origin_coords, ray_end])

        # Find intersection with LAT
        intersection = ray.intersection(input_linestring)

        if intersection.is_empty:
            continue

        # Get the first intersection point
        if hasattr(intersection, "geoms"):
            # Multiple intersections, use the closest
            int_point = min(
                intersection.geoms, key=lambda p: Point(origin_coords).distance(p)
            )
        else:
            int_point = intersection

        if int_point.geom_type != "Point":
            continue

        int_coords = np.array(int_point.coords[0])

        # Calculate incident direction (normalized)
        incident_vec = int_coords - origin_coords
        incident_dir = incident_vec / np.linalg.norm(incident_vec)

        # Calculate local normal at intersection
        int_distance = input_linestring.project(int_point)
        delta = min(10, input_linestring.length * 0.01)
        before_dist = max(0, int_distance - delta)
        after_dist = min(input_linestring.length, int_distance + delta)

        before_pt = np.array(input_linestring.interpolate(before_dist).coords[0])
        after_pt = np.array(input_linestring.interpolate(after_dist).coords[0])

        tangent = after_pt - before_pt
        tangent = tangent / np.linalg.norm(tangent)

        # Normal should point shoreward (same side as rays are coming from)
        local_normal = np.array([-tangent[1], tangent[0]])
        if np.dot(local_normal, incident_dir) > 0:
            local_normal = -local_normal

        # Apply Snell's law
        cos_theta_i = -np.dot(incident_dir, local_normal)

        if cos_theta_i < 0:
            # Ray hitting from wrong side
            continue

        # Clamp to avoid numerical errors
        cos_theta_i = np.clip(cos_theta_i, 0, 1)
        sin_theta_i = np.sqrt(1 - cos_theta_i**2)

        # Calculate refracted angle
        sin_theta_r = refractive_index_ratio * sin_theta_i

        if sin_theta_r > 1:  # Total internal reflection
            sin_theta_r = 1
            cos_theta_r = 0
        else:
            cos_theta_r = np.sqrt(1 - sin_theta_r**2)

        # Calculate refracted direction
        if sin_theta_i < 1e-10:  # Nearly perpendicular incidence
            refracted_dir = incident_dir
        else:
            # Project incident direction onto tangent
            incident_tangent = (
                incident_dir - np.dot(incident_dir, local_normal) * local_normal
            )
            incident_tangent = incident_tangent / np.linalg.norm(incident_tangent)

            # Refracted direction
            refracted_dir = -cos_theta_r * local_normal + sin_theta_r * incident_tangent

        # Create rays
        refracted_end = int_coords + refracted_dir * ray_length
        refracted_ray = LineString([int_coords, refracted_end])
        incident_ray = LineString([origin_coords, int_coords])

        refracted_rays.append(refracted_ray)
        incident_rays.append(incident_ray)

    return refracted_rays, incident_rays
