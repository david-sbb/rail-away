import pandas as pd
from typing import List, Dict
from math import radians, sin, cos, sqrt, atan2
import json


def haversine(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    R = 6371.0
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def find_recommendations(
    user_lon: float,
    user_lat: float,
    time_to_spend: float,
    activity: str,
    df: pd.DataFrame,
    travel_percentage: float,
) -> List[Dict[str, str]]:
    # Compute distance to each unique starting point
    sp_coords = df[
        ["start_station_id", "start_station_lon", "start_station_lat"]
    ].drop_duplicates()
    sp_coords["distance"] = sp_coords.apply(
        lambda row: haversine(
            user_lon, user_lat, row["start_station_lon"], row["start_station_lat"]
        ),
        axis=1,
    )

    # Find closest starting point ID
    closest_sp_id = sp_coords.sort_values("distance").iloc[0]["start_station_id"]

    # Filter data
    filtered = df[
        (df["start_station_id"] == closest_sp_id)
        # & (df["stop_features"] == activity)
        & (df["travel_time"] <= travel_percentage * time_to_spend)
    ]

    # Return top 3 by time_travel
    top_results = filtered.sort_values("travel_time").head(3)
    return top_results.to_dict(orient="records")


def clean_stop_features(raw: str) -> str | None:
    try:
        fixed = raw.replace('""', '"')
        json.loads(fixed)  # Validate it parses as JSON
        return fixed  # Return as a readable JSON string
    except Exception:
        return None
