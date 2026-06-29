import pandas as pd
import numpy as np
import os

np.random.seed(42)

VEHICLES = [f"EV-{str(i).zfill(3)}" for i in range(1, 51)]
DATES = pd.date_range("2024-01-01", "2024-12-31", freq="D")
MODELS = ["Rivian R1T", "Rivian R1S", "Rivian EDV"]

records = []

for vehicle_id in VEHICLES:
    model = np.random.choice(MODELS)
    base_battery_health = np.random.uniform(88, 100)
    base_range = np.random.uniform(260, 320)
    anomaly_vehicle = np.random.random() < 0.16  # ~8 of 50 flagged

    for i, date in enumerate(DATES):
        battery_health = base_battery_health - (i * np.random.uniform(0.005, 0.015))
        range_km = base_range - (i * np.random.uniform(0.02, 0.06))
        charge_cycles = int(i * np.random.uniform(0.4, 0.7))
        temperature_c = np.random.normal(28, 6)
        mileage_km = i * np.random.uniform(80, 160)

        if anomaly_vehicle and i > 200:
            battery_health -= np.random.uniform(5, 15)
            range_km -= np.random.uniform(30, 70)
            temperature_c += np.random.uniform(8, 18)

        records.append({
            "vehicle_id": vehicle_id,
            "model": model,
            "date": date.strftime("%Y-%m-%d"),
            "battery_health_pct": round(max(battery_health, 0), 2),
            "range_km": round(max(range_km, 0), 2),
            "charge_cycles": charge_cycles,
            "temperature_c": round(temperature_c, 2),
            "mileage_km": round(mileage_km, 2)
        })

df = pd.DataFrame(records)
os.makedirs("seeds", exist_ok=True)
df.to_csv("seeds/fleet_telemetry.csv", index=False)
print(f"Generated {len(df):,} rows across {len(VEHICLES)} vehicles.")