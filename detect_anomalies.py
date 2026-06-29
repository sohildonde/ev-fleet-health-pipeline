import duckdb
import pandas as pd
import numpy as np

DB_PATH = r"C:\Users\sohil\fleet_project\fleet_analytics\fleet.duckdb"

con = duckdb.connect(DB_PATH)
df = con.execute("SELECT * FROM main.mart_vehicle_health").df()
con.close()

print(f"Loaded {len(df)} vehicles from mart_vehicle_health")

for col in ["avg_battery_health", "avg_range_km", "avg_temp_c"]:
    mean = df[col].mean()
    std = df[col].std()
    df[f"zscore_{col}"] = (df[col] - mean) / std

THRESHOLD = 1.8
df["anomaly_battery"] = df["zscore_avg_battery_health"] < -THRESHOLD
df["anomaly_range"]   = df["zscore_avg_range_km"] < -THRESHOLD
df["anomaly_temp"]    = df["zscore_avg_temp_c"] > THRESHOLD

df["is_anomaly"] = df["anomaly_battery"] | df["anomaly_range"] | df["anomaly_temp"]

df["severity_score"] = (
    df["anomaly_battery"].astype(int) +
    df["anomaly_range"].astype(int) +
    df["anomaly_temp"].astype(int)
)

flagged = df[df["is_anomaly"]].sort_values("severity_score", ascending=False)
print(f"\nVehicles flagged for anomaly: {len(flagged)}")
print(flagged[["vehicle_id", "model", "avg_battery_health", "avg_range_km", "avg_temp_c", "severity_score"]].to_string(index=False))

df.to_csv("fleet_health_scored.csv", index=False)
print(f"\nExported fleet_health_scored.csv")