import math


LAYOUT_OPTIONS = ("grid", "hex_width", "hex_length")
EPSILON = 0.001


def generate_grid(width, length, distance, margin=0):
    if width <= 0 or length <= 0:
        return []
    cols = max(1, int(math.floor(width / distance)) + 1)
    rows = max(1, int(math.floor(length / distance)) + 1)
    x_gap = width / (cols - 1) if cols > 1 else 0
    y_gap = length / (rows - 1) if rows > 1 else 0
    x0 = margin if cols > 1 else margin + width / 2
    y0 = margin if rows > 1 else margin + length / 2
    return [(x0 + c * x_gap, y0 + r * y_gap) for r in range(rows) for c in range(cols)]


def generate_hex(width, length, distance, margin=0):
    if width <= 0 or length <= 0:
        return []
    metrics = _hex_metrics(width, length, distance)
    even_cols = metrics["even_cols"]
    x_gap = metrics["x_gap"]
    rows = metrics["rows"]
    y_gap = metrics["y_gap"]
    y0 = margin if rows > 1 else margin + length / 2
    centers = []

    for row in range(rows):
        offset = x_gap / 2 if row % 2 and even_cols > 1 else 0
        cols = _fit_count(width, x_gap, offset) if x_gap else 1
        if cols <= 0:
            continue
        x0 = margin + offset if x_gap else margin + width / 2
        y = y0 + row * y_gap
        for col in range(cols):
            x = x0 + col * x_gap
            if margin - 0.001 <= x <= margin + width + 0.001:
                centers.append((x, y))
    return centers


def generate_hex_along_length(width, length, distance, margin=0):
    transposed = generate_hex(length, width, distance, 0)
    centers = [(margin + y, margin + x) for x, y in transposed]
    centers.sort(key=lambda point: (point[1], point[0]))
    return centers


def generate_hex_oriented(width, length, distance, margin=0, orientation="width"):
    if orientation == "length":
        return generate_hex_along_length(width, length, distance, margin)
    return generate_hex(width, length, distance, margin)


def mode_orientation_for_option(option):
    if option == "grid":
        return "grid", "width"
    if option == "hex_length":
        return "hex", "length"
    return "hex", "width"


def generate_layout_option(width, length, distance, margin=0, option="hex_width"):
    mode, orientation = mode_orientation_for_option(option)
    if mode == "grid":
        return generate_grid(width, length, distance, margin)
    return generate_hex_oriented(width, length, distance, margin, orientation)


def rank_layout_options(width, length, distance, margin=0, radius=0):
    ranked = []
    for index, option in enumerate(LAYOUT_OPTIONS):
        centers = generate_layout_option(width, length, distance, margin, option)
        overlap = overlap_area_ratio(centers, radius)
        ranked.append(
            {
                "option": option,
                "centers": centers,
                "count": len(centers),
                "overlap": overlap,
                "rank": index,
            }
        )
    ranked.sort(key=lambda item: (-item["count"], item["overlap"], item["rank"]))
    return ranked


def _fit_count(span, gap, offset=0):
    if gap <= 0:
        return 1
    remaining = span - offset
    if remaining < -EPSILON:
        return 0
    return int(math.floor((remaining + EPSILON) / gap)) + 1


def _hex_candidate_gaps(width, length, distance):
    max_cols = max(1, int(math.floor(width / distance)) + 1)
    if max_cols <= 1:
        return [0]

    gaps = {distance}
    for cols in range(2, max_cols + 1):
        gaps.add(width / (cols - 1))
        gaps.add(width / (cols - 0.5))

    max_rows = max(1, int(math.floor(length / max(distance / 2, EPSILON))) + 1)
    for rows in range(2, max_rows + 1):
        target_gap = length / (rows - 1)
        if 0 < target_gap < distance:
            gaps.add(2 * math.sqrt(max(0, distance * distance - target_gap * target_gap)))

    return sorted(gap for gap in gaps if distance - EPSILON <= gap <= width + EPSILON)


def _hex_metrics_for_gap(width, length, distance, x_gap):
    if x_gap <= 0:
        rows = max(1, int(math.floor(length / distance)) + 1)
        y_gap = length / (rows - 1) if rows > 1 else 0
        return {
            "even_cols": 1,
            "odd_cols": 1,
            "rows": rows,
            "x_gap": 0,
            "y_gap": y_gap,
            "count": rows,
            "min_nearest": y_gap if rows > 1 else float("inf"),
        }

    even_cols = max(1, _fit_count(width, x_gap))
    odd_cols = max(0, _fit_count(width, x_gap, x_gap / 2))
    min_row_gap = max(distance / 2, math.sqrt(max(0, distance * distance - (x_gap / 2) ** 2)))
    rows = max(1, int(math.floor((length + EPSILON) / min_row_gap)) + 1)
    y_gap = length / (rows - 1) if rows > 1 else 0
    even_rows = (rows + 1) // 2
    odd_rows = rows // 2
    count = even_rows * even_cols + odd_rows * odd_cols
    nearest_candidates = []
    if even_cols > 1:
        nearest_candidates.append(x_gap)
    if rows > 1:
        nearest_candidates.append(math.hypot(x_gap / 2, y_gap))
    min_nearest = min(nearest_candidates) if nearest_candidates else float("inf")

    return {
        "even_cols": even_cols,
        "odd_cols": odd_cols,
        "rows": rows,
        "x_gap": x_gap,
        "y_gap": y_gap,
        "count": count,
        "min_nearest": min_nearest,
    }


def _hex_metrics(width, length, distance):
    candidates = [_hex_metrics_for_gap(width, length, distance, gap) for gap in _hex_candidate_gaps(width, length, distance)]
    return max(
        candidates,
        key=lambda item: (
            item["even_cols"],
            item["count"],
            item["min_nearest"],
            item["x_gap"],
            item["y_gap"],
        ),
    )


def nearest_distances(centers):
    result = []
    for i, (x1, y1) in enumerate(centers):
        nearest = None
        for j, (x2, y2) in enumerate(centers):
            if i == j:
                continue
            distance = math.hypot(x1 - x2, y1 - y2)
            nearest = distance if nearest is None else min(nearest, distance)
        result.append(nearest)
    return result


def circle_intersection_area(radius, distance):
    if radius <= 0 or distance >= 2 * radius:
        return 0
    if distance <= 0:
        return math.pi * radius * radius
    return (
        2 * radius * radius * math.acos(distance / (2 * radius))
        - 0.5 * distance * math.sqrt(max(0, 4 * radius * radius - distance * distance))
    )


def overlap_area_ratio(centers, radius):
    if radius <= 0 or not centers:
        return 0
    overlap_area = 0
    for i, (x1, y1) in enumerate(centers):
        for x2, y2 in centers[i + 1:]:
            overlap_area += circle_intersection_area(radius, math.hypot(x1 - x2, y1 - y2))
    total_area = len(centers) * math.pi * radius * radius
    return overlap_area / total_area if total_area else 0


def layout_recipe(mode, field_width, field_length, distance, margin, radius, orientation="width"):
    center_inset = margin + radius
    usable_w = max(0, field_width - 2 * center_inset)
    usable_l = max(0, field_length - 2 * center_inset)

    if mode == "grid":
        cols = max(1, int(math.floor(usable_w / distance)) + 1)
        rows = max(1, int(math.floor(usable_l / distance)) + 1)
        x_gap = usable_w / (cols - 1) if cols > 1 else 0
        y_gap = usable_l / (rows - 1) if rows > 1 else 0
        return {
            "layout": "grid",
            "items": [
                {"label": "Repeat across", "value": x_gap},
                {"label": "Repeat up", "value": y_gap},
            ],
        }

    if orientation == "length":
        metrics = _hex_metrics(usable_l, usable_w, distance)
        repeat_up = metrics["x_gap"]
        repeat_across = metrics["y_gap"]
        first_col = center_inset if metrics["rows"] > 1 else center_inset + usable_w / 2
        first_y = center_inset if metrics["even_cols"] > 1 else center_inset + usable_l / 2
        second_col = first_col + repeat_across if metrics["rows"] > 1 else first_col
        second_col_y = first_y + repeat_up / 2 if metrics["even_cols"] > 1 else first_y

        return {
            "layout": "hex",
            "items": [
                {"label": "Repeat up", "value": repeat_up},
                {"label": "Column 2 from bottom", "value": second_col_y},
                {"label": "Column 2 from left", "value": second_col},
                {"label": "Repeat columns across", "value": repeat_across},
            ],
        }

    metrics = _hex_metrics(usable_w, usable_l, distance)
    x_gap = metrics["x_gap"]
    y_gap = metrics["y_gap"]
    x_start = center_inset if metrics["even_cols"] > 1 else center_inset + usable_w / 2
    y_start = center_inset if metrics["rows"] > 1 else center_inset + usable_l / 2
    second_row_x = x_start + x_gap / 2 if metrics["even_cols"] > 1 else x_start
    second_row = y_start + y_gap if metrics["rows"] > 1 else y_start

    return {
        "layout": "hex",
        "items": [
            {"label": "Repeat across", "value": x_gap},
            {"label": "Row 2 from left", "value": second_row_x},
            {"label": "Row 2 from bottom", "value": second_row},
            {"label": "Repeat rows up", "value": y_gap},
        ],
    }


def layout_guides(mode, field_width, field_length, distance, margin, radius, orientation="width"):
    center_inset = margin + radius
    usable_w = max(0, field_width - 2 * center_inset)
    usable_l = max(0, field_length - 2 * center_inset)

    guides = []

    if mode == "grid":
        cols = max(1, int(math.floor(usable_w / distance)) + 1)
        rows = max(1, int(math.floor(usable_l / distance)) + 1)
        x_gap = usable_w / (cols - 1) if cols > 1 else 0
        y_gap = usable_l / (rows - 1) if rows > 1 else 0
        x_start = center_inset if cols > 1 else center_inset + usable_w / 2
        y_start = center_inset if rows > 1 else center_inset + usable_l / 2

        guides.extend(
            [
                {
                    "axis": "x",
                    "track": 0,
                    "from": x_start,
                    "to": x_start + x_gap,
                    "label": f"{x_gap:.2f} m",
                    "value": x_gap,
                },
                {
                    "axis": "y",
                    "track": 0,
                    "from": y_start,
                    "to": y_start + y_gap,
                    "label": f"{y_gap:.2f} m",
                    "value": y_gap,
                },
            ]
        )
        return guides

    if orientation == "length":
        metrics = _hex_metrics(usable_l, usable_w, distance)
        repeat_up = metrics["x_gap"]
        repeat_across = metrics["y_gap"]
        x_start = center_inset if metrics["rows"] > 1 else center_inset + usable_w / 2
        y_start = center_inset if metrics["even_cols"] > 1 else center_inset + usable_l / 2
        second_col = x_start + repeat_across if metrics["rows"] > 1 else x_start
        second_col_y = y_start + repeat_up / 2 if metrics["even_cols"] > 1 else y_start

        guides.extend(
            [
                {
                    "axis": "y",
                    "track": 0,
                    "from": y_start,
                    "to": y_start + repeat_up,
                    "label": f"{repeat_up:.2f} m",
                    "value": repeat_up,
                },
                {
                    "axis": "y",
                    "track": 1,
                    "from": 0,
                    "to": second_col_y,
                    "label": f"{second_col_y:.2f} m",
                    "value": second_col_y,
                },
                {
                    "axis": "x",
                    "track": 0,
                    "from": 0,
                    "to": second_col,
                    "label": f"{second_col:.2f} m",
                    "value": second_col,
                },
                {
                    "axis": "x",
                    "track": 1,
                    "from": x_start,
                    "to": x_start + repeat_across,
                    "label": f"{repeat_across:.2f} m",
                    "value": repeat_across,
                },
            ]
        )
        return guides

    metrics = _hex_metrics(usable_w, usable_l, distance)
    x_gap = metrics["x_gap"]
    y_gap = metrics["y_gap"]
    x_start = center_inset if metrics["even_cols"] > 1 else center_inset + usable_w / 2
    y_start = center_inset if metrics["rows"] > 1 else center_inset + usable_l / 2
    second_row_x = x_start + x_gap / 2 if metrics["even_cols"] > 1 else x_start
    second_row = y_start + y_gap if metrics["rows"] > 1 else y_start

    guides.extend(
        [
            {
                "axis": "x",
                "track": 0,
                "from": x_start,
                "to": x_start + x_gap,
                "label": f"{x_gap:.2f} m",
                "value": x_gap,
            },
            {
                "axis": "x",
                "track": 1,
                "from": 0,
                "to": second_row_x,
                "label": f"{second_row_x:.2f} m",
                "value": second_row_x,
            },
            {
                "axis": "y",
                "track": 0,
                "from": 0,
                "to": second_row,
                "label": f"{second_row:.2f} m",
                "value": second_row,
            },
            {
                "axis": "y",
                "track": 1,
                "from": y_start,
                "to": y_start + y_gap,
                "label": f"{y_gap:.2f} m",
                "value": y_gap,
            },
        ]
    )
    return guides
