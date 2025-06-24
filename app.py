from flask import Flask, request, jsonify
import pandas as pd
from utils import find_recommendations

SAMPLE_DATA_PATH = "data/sample_data.csv"
PARAMETRIC_TRAVEL = 0.30  # a maximum of 30% of time is devoted to travel

app = Flask(__name__)

# Load CSV into memory once at startup
DATAFRAME_CACHE = pd.read_csv(SAMPLE_DATA_PATH)
DATAFRAME_CACHE["starting_point_lon"] = pd.to_numeric(
    DATAFRAME_CACHE["starting_point_lon"], errors="coerce"
)
DATAFRAME_CACHE["starting_point_lat"] = pd.to_numeric(
    DATAFRAME_CACHE["starting_point_lat"], errors="coerce"
)
DATAFRAME_CACHE["time_travel"] = pd.to_numeric(
    DATAFRAME_CACHE["time_travel"], errors="coerce"
)
DATAFRAME_CACHE.dropna(
    subset=["starting_point_lon", "starting_point_lat", "time_travel"], inplace=True
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
        df["starting_point_lon"] = pd.to_numeric(
            df["starting_point_lon"], errors="coerce"
        )
        df["starting_point_lat"] = pd.to_numeric(
            df["starting_point_lat"], errors="coerce"
        )
        df["time_travel"] = pd.to_numeric(df["time_travel"], errors="coerce")
        df.dropna(
            subset=["starting_point_lon", "starting_point_lat", "time_travel"],
            inplace=True,
        )
        DATAFRAME_CACHE = df
        return jsonify({"status": "reloaded"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
