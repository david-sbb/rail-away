import json
from collections import defaultdict

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

import numpy as np

num_outputs = 300000


# ---------------------------------------------------------------------------
# 1. Vectorized arrival time conversion using pd.to_timedelta.
def convert_arrivals_to_minutes(series: pd.Series) -> pd.Series:
    # Use pandas to_timedelta (vectorized) and convert total seconds to minutes.
    td = pd.to_timedelta(series, errors='coerce')
    return (td.dt.total_seconds() // 60).astype("Int64")


# ---------------------------------------------------------------------------
# 2. Compute reachable stops / average travel times.
def compute_reachable_and_travel_times(stop_times_file: str, stops_file: str):
    """
    Reads stops and stop_times files and computes:
      • stops_info: {stop_id: {stop_lat, stop_lon, stop_name}}
      • reachable_stops: {origin stop_id: set(destination stop_ids)}
      • avg_travel_times: {(origin, destination): average travel time in minutes}

    Optimizations:
      - Vectorized time conversion.
      - Filtering early to include only stop_ids starting with "85".
      - Clean stop_ids once.
      - (For testing, stop early after 5 OD pairs; remove the breaks for full runs.)
    """
    global num_outputs

    # Read stops, filter for those starting with "85" and clean stop_id.
    stops_df = pd.read_csv(stops_file)
    req_stops_cols = {'stop_id', 'stop_lat', 'stop_lon', 'stop_name'}
    if not req_stops_cols.issubset(stops_df.columns):
        raise ValueError(f"Missing columns in stops file. Required: {req_stops_cols}")

    filtered_stops_df = stops_df[stops_df['stop_id'].astype(str).str.startswith("85")].copy()
    # Clean stop_id: use only part before ':'
    filtered_stops_df.loc[:, "stop_id"] = filtered_stops_df["stop_id"].str.split(":").str[0]
    filtered_stops_df = filtered_stops_df.drop_duplicates(subset='stop_id', keep='first')
    stops_info = filtered_stops_df.set_index('stop_id')[['stop_lat', 'stop_lon', 'stop_name']].to_dict('index')

    # Read stop_times.
    stop_times_df = pd.read_csv(stop_times_file)
    req_stop_times_cols = {'trip_id', 'stop_id', 'stop_sequence', 'arrival_time'}
    if not req_stop_times_cols.issubset(stop_times_df.columns):
        raise ValueError(f"Missing columns in stop_times file. Required: {req_stop_times_cols}")

    # Ensure stop_sequence is numeric.
    stop_times_df['stop_sequence'] = stop_times_df['stop_sequence'].astype(int)
    # Convert arrival time strings to minutes (vectorized).
    stop_times_df['arrival_mins'] = convert_arrivals_to_minutes(stop_times_df['arrival_time'])

    # Filter stop_times on stop_id (only process stops starting with '85')
    stop_times_df = stop_times_df[stop_times_df['stop_id'].astype(str).str.startswith("85")].copy()
    # Clean the stop_id column once.
    stop_times_df.loc[:, "stop_id"] = stop_times_df["stop_id"].str.split(":").str[0]

    reachable_stops = defaultdict(set)  # origin -> set(destinations)
    travel_times = defaultdict(list)  # (origin, destination) -> list of travel times in minutes

    # Process each trip (groupby trip_id).
    for trip_id, group in stop_times_df.groupby('trip_id'):
        group_sorted = group.sort_values('stop_sequence')
        stops_list = group_sorted['stop_id'].tolist()
        arrival_list = group_sorted['arrival_mins'].tolist()
        n = len(stops_list)
        for i in range(n):
            origin = stops_list[i]
            origin_arrival = arrival_list[i]
            if pd.isna(origin_arrival):
                continue
            for j in range(i + 1, n):
                destination = stops_list[j]
                dest_arrival = arrival_list[j]
                if pd.isna(dest_arrival):
                    continue
                travel_time = dest_arrival - origin_arrival
                if travel_time < 0:  # Skip negative travel times.
                    continue
                # Both origin & destination are already cleaned and start with "85"
                reachable_stops[origin].add(destination)
                travel_times[(origin, destination)].append(travel_time)

                # For testing: break early after >5 OD pairs.
                if len(travel_times) >= num_outputs:
                    break
            if len(travel_times) >= num_outputs:
                break
        if len(travel_times) >= num_outputs:
            break

    avg_travel_times = {k: int(sum(v) / len(v)) for k, v in travel_times.items() if v}
    return stops_info, dict(reachable_stops), avg_travel_times


# ---------------------------------------------------------------------------
# 3. is_within_500m using geopandas (used later in CSV writing).
def is_within_500m(lat1: float, lon1: float, lat2: float, lon2: float) -> bool:
    """Check if (lat2, lon2) is within 500 meters of (lat1, lon1) via reprojection."""
    pt1 = Point(lon1, lat1)
    pt2 = Point(lon2, lat2)
    gdf = gpd.GeoDataFrame({'geometry': [pt1, pt2]}, crs='EPSG:4326')
    gdf_proj = gdf.to_crs(epsg=3857)
    distance = gdf_proj.geometry.iloc[0].distance(gdf_proj.geometry.iloc[1])
    return distance <= 500


# ---------------------------------------------------------------------------
# 4. Build a GeoDataFrame for features to speed up repeated spatial queries.
def build_features_gdf(features: list) -> gpd.GeoDataFrame:
    """Create a GeoDataFrame (and build a spatial index) from a list of GeoJSON features."""
    rows = []
    for feature in features:
        geom = feature.get("geometry", {})
        typ = geom.get("type", "").lower()
        coords = None
        if typ == "point":
            coords = geom.get("coordinates")
        elif typ == "linestring" and geom.get("coordinates"):
            coords = geom.get("coordinates")[0]
        elif typ in ("multilinestring","multipolygon", "polygon") and geom.get("coordinates"):
            coords = geom.get("coordinates")[0][0]

            if isinstance(coords[0], np.ndarray) or isinstance(coords[0], list):
                coords = coords[0]
        else:
            print(typ)
        if coords is not None:
            rows.append({"feature": feature, "geometry": Point(coords[0], coords[1])})
    if rows:
        gdf = gpd.GeoDataFrame(rows, crs="EPSG:4326")
        gdf = gdf.to_crs(epsg=3857)
        _ = gdf.sindex  # build the spatial index
    else:
        gdf = gpd.GeoDataFrame([], columns=["feature", "geometry"], crs="EPSG:4326").to_crs(epsg=3857)
    return gdf


# ---------------------------------------------------------------------------
# 5. Write average travel times to CSV; use spatial index to quickly filter features
def write_avg_travel_times_to_csv(features: list, avg_travel_times: dict, stops_info: dict, output_file: str):
    """
    Outputs a CSV file with columns:
      from_stop_id, from_stop_lon, from_stop_lat, from_stop_name,
      to_stop_id, to_stop_name, to_stop_lon, to_stop_lan, travel_time,
      type, stop_features
    For each OD pair, quickly queries features within 500 m at the destination.
    """
    rows = []
    # Pre-build GeoDataFrame for spatial queries.
    features_gdf = build_features_gdf(features)

    for (origin, destination), travel_time in avg_travel_times.items():
        origin_info = stops_info.get(origin)
        destination_info = stops_info.get(destination)
        if origin_info is None or destination_info is None:
            continue

        # Build destination point and buffer.
        dest_pt = Point(destination_info["stop_lon"], destination_info["stop_lat"])
        dest_gdf = gpd.GeoDataFrame([{"dest": destination}], geometry=[dest_pt], crs="EPSG:4326").to_crs(epsg=3857)
        dest_point_proj = dest_gdf.geometry.iloc[0]
        buffer_500 = dest_point_proj.buffer(500)

        # Query features using spatial index.
        idx = list(features_gdf.sindex.intersection(buffer_500.bounds))
        possible = features_gdf.iloc[idx]
        matching = possible[possible.intersects(buffer_500)]

        feature_types = []
        feature_list = []
        for _, row_feat in matching.iterrows():
            feat = row_feat["feature"]
            props = feat.get("properties", {})
            ftype = props.get("route") or props.get("leisure") or props.get("tourism")
            if ftype is None:
                ftype = "arts" if props.get("museum") is not None else None

            if ftype is not None:
                feature_types.append(ftype)
                feature_list.append(feat)

        out_row = {
            "from_stop_id": origin,
            "from_stop_name": origin_info["stop_name"],
            "from_stop_lon": origin_info["stop_lon"],
            "from_stop_lat": origin_info["stop_lat"],
            "to_stop_id": destination,
            "to_stop_name": destination_info["stop_name"],
            "to_stop_lon": destination_info["stop_lon"],
            "to_stop_lan": destination_info["stop_lat"],
            "travel_time": travel_time,
            "type": json.dumps(feature_types, ensure_ascii=False),
            "stop_features": json.dumps(feature_list, ensure_ascii=False)
        }
        rows.append(out_row)
        if len(rows) % 10000 == 0:
            print(f"Processed {len(rows)} rows.")

    df = pd.DataFrame(rows).sort_values(by="from_stop_id")
    df.to_csv(output_file, index=False)
    print(f"CSV file written to: {output_file}")


# ---------------------------------------------------------------------------
# 6. Parse GeoJSON features.
def parse_geojson_line_string_features(file_path: str) -> list:
    """
    Reads a GeoJSON file and returns a list of features excluding those with a uic_ref property.
    Supports FeatureCollection or a plain list.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if isinstance(data, dict) and data.get("type") == "FeatureCollection":
        features = data.get("features", [])
    elif isinstance(data, list):
        features = data
    else:
        raise ValueError("Invalid GeoJSON structure.")

    # Filter out features with "uic_ref" in properties.
    return [feat for feat in features if not (feat.get("properties") or {}).get("uic_ref")]


# ---------------------------------------------------------------------------
# Example usage:
if __name__ == "__main__":
    stops_file_path = "gtfs/stops.txt"
    stop_times_file_path = "gtfs/stop_times.txt"
    geojson_file = "export_hike-swim-culture.geojson"  # Update as needed

    try:
        stops_info, reachable_stops, avg_travel_times = compute_reachable_and_travel_times(
            stop_times_file_path, stops_file_path
        )
        print("Processed stops, reachable stops, and average travel times.")
    except Exception as e:
        print(f"An error occurred: {e}")

    try:
        features = parse_geojson_line_string_features(geojson_file)
        print("Number of GeoJSON features read:", len(features))
    except Exception as e:
        print("Error reading GeoJSON:", e)

    write_avg_travel_times_to_csv(features, avg_travel_times, stops_info, "export.csv")
