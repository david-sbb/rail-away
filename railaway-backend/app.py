from flask import Flask, request, jsonify
import pandas as pd
from utils import find_recommendations
from utils import clean_stop_features

SAMPLE_DATA_PATH = "data/test-2.csv"
PARAMETRIC_TRAVEL = 0.30  # a maximum of 30% of time is devoted to travel

app = Flask(__name__)

# Load CSV into memory once at startup
DATAFRAME_CACHE = pd.read_csv(SAMPLE_DATA_PATH)
DATAFRAME_CACHE = DATAFRAME_CACHE.rename(
    columns={
        "from_stop_id": "start_station_id",
        "from_stop_name": "start_station_name",
        "from_stop_lon": "start_station_lon",
        "from_stop_lat": "start_station_lat",
        "to_stop_id": "end_station_id",
        "to_stop_name": "end_station_name",
        "to_stop_lon": "end_station_lon",
        "to_stop_lan": "end_station_lat",  # typo fixed: should be 'lat'
    }
)
DATAFRAME_CACHE["start_station_lon"] = pd.to_numeric(
    DATAFRAME_CACHE["start_station_lon"], errors="coerce"
)
DATAFRAME_CACHE["start_station_lat"] = pd.to_numeric(
    DATAFRAME_CACHE["start_station_lat"], errors="coerce"
)
DATAFRAME_CACHE["travel_time"] = pd.to_numeric(
    DATAFRAME_CACHE["travel_time"], errors="coerce"
)


DATAFRAME_CACHE["stop_features"] = DATAFRAME_CACHE["stop_features"].apply(
    clean_stop_features
)
DATAFRAME_CACHE.dropna(
    subset=["start_station_lon", "start_station_lat", "travel_time"], inplace=True
)


@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json()

    try:
        user_lon = float(data["longitude"])
        user_lat = float(data["latitude"])
        time_to_spend = float(data["time_to_spend"])
        activity = data["activity"]
    except (KeyError, ValueError):
        return jsonify({"error": "Invalid input"}), 400

    results = find_recommendations(
        user_lon=user_lon,
        user_lat=user_lat,
        time_to_spend=time_to_spend,
        activity=activity,
        df=DATAFRAME_CACHE,
        travel_percentage=PARAMETRIC_TRAVEL,
    )
    return jsonify(results)


@app.route("/reload_data", methods=["POST"])
def reload_data():
    global DATAFRAME_CACHE
    try:
        df = pd.read_csv("data.csv")
        df["from_stop_lon"] = pd.to_numeric(df["from_stop_lon"], errors="coerce")
        df["from_stop_lat"] = pd.to_numeric(df["from_stop_lat"], errors="coerce")
        df["travel_time"] = pd.to_numeric(df["travel_time"], errors="coerce")
        df.dropna(
            subset=["from_stop_lon", "from_stop_lat", "travel_time"],
            inplace=True,
        )
        DATAFRAME_CACHE = df
        return jsonify({"status": "reloaded"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
