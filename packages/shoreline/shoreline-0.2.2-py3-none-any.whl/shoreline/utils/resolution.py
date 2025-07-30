from shapely.geometry import LineString, Point


def properly_order_linestrings(multilinestring):
    """
    Quick and dirty linestring sorting

    This is required because cleaning up isobaths in QGIS often introduces
    out-of-order linestrings, which means you can't merge / union the MultiLineString
    into a LineString.
    This undoubtedly has horrible performance on big geometries, but processors are fast
    """
    # Extract individual linestrings
    line_segments = list(multilinestring.geoms)

    if len(line_segments) <= 1:
        return (
            multilinestring
            if isinstance(multilinestring, LineString)
            else line_segments[0]
        )

    # Create a copy of segments to work with
    remaining_segments = line_segments.copy()

    # Start with the first segment
    ordered_segments = [remaining_segments.pop(0)]

    # Keep track of the endpoints of our growing linestring
    start_point = Point(ordered_segments[0].coords[0])
    end_point = Point(ordered_segments[0].coords[-1])

    # Continue until all segments are connected
    while remaining_segments:
        best_segment = None
        best_idx = -1
        best_reverse = False
        best_distance = float("inf")
        connect_to_start = False

        # Find the segment that best connects to either end
        for i, segment in enumerate(remaining_segments):
            seg_start = Point(segment.coords[0])
            seg_end = Point(segment.coords[-1])

            # Check distances to start point
            dist_start_to_seg_start = start_point.distance(seg_start)
            dist_start_to_seg_end = start_point.distance(seg_end)

            # Check distances to end point
            dist_end_to_seg_start = end_point.distance(seg_start)
            dist_end_to_seg_end = end_point.distance(seg_end)

            # Find minimum distance and corresponding configuration
            min_dist = min(
                dist_start_to_seg_start,
                dist_start_to_seg_end,
                dist_end_to_seg_start,
                dist_end_to_seg_end,
            )

            if min_dist < best_distance:
                best_distance = min_dist
                best_idx = i
                best_segment = segment

                # Determine orientation and connection point
                if min_dist == dist_start_to_seg_start:
                    connect_to_start = True
                    best_reverse = True
                elif min_dist == dist_start_to_seg_end:
                    connect_to_start = True
                    best_reverse = False
                elif min_dist == dist_end_to_seg_start:
                    connect_to_start = False
                    best_reverse = False
                else:  # min_dist == dist_end_to_seg_end
                    connect_to_start = False
                    best_reverse = True

        # Add the best segment
        remaining_segments.pop(best_idx)

        if best_reverse:
            best_segment = LineString(list(reversed(best_segment.coords)))

        # Add to the appropriate end of our ordered segments
        if connect_to_start:
            ordered_segments.insert(0, best_segment)
            start_point = Point(ordered_segments[0].coords[0])
        else:
            ordered_segments.append(best_segment)
            end_point = Point(ordered_segments[-1].coords[-1])

    # Merge all ordered segments
    merged_coords = []
    for i, segment in enumerate(ordered_segments):
        if i == 0:
            # Include all points from first segment
            merged_coords.extend(list(segment.coords))
        else:
            # Skip first point from subsequent segments (to avoid duplication)
            merged_coords.extend(list(segment.coords)[1:])

    return LineString(merged_coords)


def redistribute_vertices(geom, distance):
    """
    Increase or decrease the "resolution" of an input LineString by evenly distributing vertices
    at distance
    """
    if geom.geom_type == "LineString":
        num_vert = int(round(geom.length / distance))  # noqa RUF046
        if num_vert == 0:
            num_vert = 1
        return LineString(
            [
                geom.interpolate(float(n) / num_vert, normalized=True)
                for n in range(num_vert + 1)
            ]
        )
    elif geom.geom_type == "MultiLineString":
        parts = [redistribute_vertices(part, distance) for part in geom]
        return type(geom)([p for p in parts if not p.is_empty])
    else:
        raise ValueError(f"Unhandled geometry {geom.geom_type}")
