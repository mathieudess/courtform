from court_layout import (
    generate_grid,
    generate_hex,
    generate_hex_along_length,
    generate_hex_oriented,
    generate_layout_option,
    layout_guides,
    layout_recipe,
    nearest_distances,
    overlap_area_ratio,
    rank_layout_options,
)


def test_court_circles_stay_inside_field_when_radius_is_used_as_inset():
    field_width = 40
    field_length = 60
    radius = 5
    edge_margin = 1
    center_inset = edge_margin + radius
    centers = generate_hex(
        width=field_width - 2 * center_inset,
        length=field_length - 2 * center_inset,
        distance=12,
        margin=center_inset,
    )

    assert centers
    assert all(radius <= x <= field_width - radius for x, _ in centers)
    assert all(radius <= y <= field_length - radius for _, y in centers)


def test_grid_keeps_centers_inside_usable_rectangle():
    centers = generate_grid(width=38, length=58, distance=12, margin=1)

    assert len(centers) == 20
    assert all(1 <= x <= 39 for x, _ in centers)
    assert all(1 <= y <= 59 for _, y in centers)
    assert min(d for d in nearest_distances(centers) if d is not None) >= 12


def test_grid_stretches_spare_room_in_each_axis():
    centers = generate_grid(width=24, length=30, distance=12, margin=0)
    xs = sorted({round(x, 3) for x, _ in centers})
    ys = sorted({round(y, 3) for _, y in centers})

    assert xs == [0, 12, 24]
    assert ys == [0, 15, 30]
    assert min(d for d in nearest_distances(centers) if d is not None) == 12


def test_hex_adds_staggered_rows_and_respects_spacing():
    centers = generate_hex(width=38, length=58, distance=12, margin=1)
    distances = nearest_distances(centers)

    assert len(centers) == 21
    assert any(abs(x - 7.333) < 0.001 for x, _ in centers)
    assert min(d for d in distances if d is not None) >= 12 - 0.001


def test_hex_single_column_respects_minimum_distance():
    centers = generate_hex(width=3, length=30, distance=17, margin=8.5)
    distances = nearest_distances(centers)

    assert len(centers) == 2
    assert min(d for d in distances if d is not None) >= 17


def test_hex_narrow_field_regression_respects_minimum_distance():
    radius = 8.5
    usable_w = 20 - 2 * radius
    usable_l = 47 - 2 * radius
    centers = generate_hex(width=usable_w, length=usable_l, distance=17, margin=radius)
    distances = nearest_distances(centers)

    assert len(centers) == 2
    assert min(d for d in distances if d is not None) >= 17


def test_hex_along_length_respects_minimum_distance():
    centers = generate_hex_along_length(width=40, length=60, distance=12, margin=0)
    distances = nearest_distances(centers)

    assert centers
    assert all(0 <= x <= 40 for x, _ in centers)
    assert all(0 <= y <= 60 for _, y in centers)
    assert min(d for d in distances if d is not None) >= 12 - 0.001


def test_hex_along_length_is_the_transposed_hex_layout():
    along_width = generate_hex(width=70, length=30, distance=12, margin=0)
    along_length = generate_hex_along_length(width=30, length=70, distance=12, margin=0)
    expected = sorted([(y, x) for x, y in along_width], key=lambda point: (point[1], point[0]))

    assert along_length == expected
    assert generate_hex_oriented(width=30, length=70, distance=12, margin=0, orientation="length") == expected
    assert generate_layout_option(width=30, length=70, distance=12, margin=0, option="hex_length") == expected


def test_hex_length_does_not_stretch_away_a_full_staggered_line():
    field_width = 51
    field_length = 90
    radius = 8.5
    distance = 13
    usable_w = field_width - 2 * radius
    usable_l = field_length - 2 * radius
    centers = generate_layout_option(usable_w, usable_l, distance, radius, option="hex_length")
    row_centers = generate_layout_option(usable_w, usable_l, distance, radius, option="hex_width")
    column_counts = {}
    for x, _ in centers:
        column_counts[round(x, 3)] = column_counts.get(round(x, 3), 0) + 1

    assert len(centers) == 24
    assert len(row_centers) == 21
    assert centers != row_centers
    assert sorted(column_counts.values()) == [6, 6, 6, 6]
    assert min(d for d in nearest_distances(centers) if d is not None) >= distance


def test_layout_options_are_ranked_by_count_then_overlap():
    ranked = rank_layout_options(width=23, length=43, distance=12, margin=8.5, radius=8.5)

    assert ranked[0]["count"] == max(item["count"] for item in ranked)
    same_count = [item for item in ranked if item["count"] == ranked[0]["count"]]
    assert ranked[0]["overlap"] == min(item["overlap"] for item in same_count)
    assert {item["option"] for item in ranked} == {"grid", "hex_width", "hex_length"}


def test_layout_recipe_stays_compact():
    grid_recipe = layout_recipe("grid", 40, 60, 12, 1, 5)
    hex_recipe = layout_recipe("hex", 40, 60, 12, 1, 5)
    length_hex_recipe = layout_recipe("hex", 40, 60, 12, 1, 5, orientation="length")
    grid_guides = layout_guides("grid", 40, 60, 12, 1, 5)
    hex_guides = layout_guides("hex", 40, 60, 12, 1, 5)
    length_hex_guides = layout_guides("hex", 40, 60, 12, 1, 5, orientation="length")

    assert [item["label"] for item in grid_recipe["items"]] == ["Repeat across", "Repeat up"]
    assert [item["label"] for item in hex_recipe["items"]] == [
        "Repeat across",
        "Row 2 from sideline",
        "Repeat rows up",
    ]
    assert [item["label"] for item in length_hex_recipe["items"]] == [
        "Repeat up",
        "Column 2 from sideline",
        "Repeat columns across",
    ]
    assert len(grid_guides) == 2
    assert len(hex_guides) == 3
    assert len(length_hex_guides) == 3
    assert all(item["label"].endswith("m") for item in grid_guides + hex_guides + length_hex_guides)
    assert [item["axis"] for item in grid_guides] == ["x", "y"]
    assert [item["axis"] for item in hex_guides] == ["x", "y", "y"]
    assert [item["axis"] for item in length_hex_guides] == ["y", "x", "x"]
    assert [item["track"] for item in hex_guides] == [0, 0, 1]
    assert [item["track"] for item in length_hex_guides] == [0, 0, 1]


def test_overlap_area_ratio_uses_circle_area():
    assert overlap_area_ratio([(0, 0), (10, 0)], radius=5) == 0

    ratio = overlap_area_ratio([(0, 0), (5, 0)], radius=5)

    assert 0 < ratio < 1
