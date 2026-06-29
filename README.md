# EV Fleet Health & Anomaly Detection Pipeline

A end-to-end data engineering pipeline that ingests synthetic EV telematics data, transforms it through a dbt layer on DuckDB, applies Python-based statistical anomaly detection, and surfaces findings in an interactive Plotly dashboard.


## Business Context

Fleet operations managers need early warning signals for vehicle degradation before failures occur. Reactive maintenance after breakdown averages $4,500 per incident. This pipeline proactively flags vehicles showing statistically abnormal battery health, range degradation, or operating temperature — enabling targeted maintenance scheduling before failure.

**Key finding:** 4 of 50 vehicles flagged for proactive maintenance. Estimated cost avoidance if addressed now: $18,000.


## Pipeline Architecture

Raw CSV (synthetic telematics)

└── dbt seed → DuckDB

└── stg_fleet_telemetry (staging model)

└── mart_vehicle_health (mart model)

└── Python Z-score anomaly detection

└── Plotly interactive HTML dashboard


## Tech Stack

| Layer             | Tool                          |
|-------------------|-------------------------------|
| Data storage      | DuckDB                        |
| Transformation    | dbt-duckdb                    |
| Anomaly detection | Python (Pandas, NumPy, SciPy) |
| Visualization     | Plotly                        |
| Version control   | Git / GitHub                  |


## Anomaly Detection Logic

Z-score detection across 3 signals per vehicle:

- **Battery health** — flagged if Z-score < -1.8 (significantly below fleet average)
- **Range km** — flagged if Z-score < -1.8
- **Temperature °C** — flagged if Z-score > +1.8 (significantly above fleet average)

A vehicle is flagged if **any one** signal crosses the threshold. Severity score counts how many signals tripped (1–3).



## How to Run

```bash
# 1. Install dependencies
pip install dbt-duckdb pandas numpy scipy plotly

# 2. Generate synthetic data
python generate_data.py

# 3. Run dbt pipeline
cd fleet_analytics
dbt seed
dbt run
cd ..

# 4. Run anomaly detection
python detect_anomalies.py

# 5. Build dashboard
python build_dashboard.py

# 6. Open dashboard
start fleet_dashboard.html
```


## Project Structure
fleet_project/

├── generate_data.py          # Synthetic telematics data generation

├── detect_anomalies.py       # Z-score anomaly detection

├── build_dashboard.py        # Plotly dashboard builder

├── fleet_analytics/          # dbt project

│   ├── models/

│   │   ├── staging/

│   │   │   └── stg_fleet_telemetry.sql

│   │   └── mart/

│   │       └── mart_vehicle_health.sql

│   └── seeds/

│       └── fleet_telemetry.csv

└── .gitignore


## Limitations & Next Steps

- **Data**: Synthetic dataset; production version would connect to a real telematics API (e.g. Rivian Fleet API, Geotab)
- **Scheduling**: Would add Apache Airflow or Prefect for daily pipeline runs
- **Alerting**: Slack or email alert when new vehicles cross the anomaly threshold
- **ML extension**: Replace Z-score with Isolation Forest or LSTM for time-series anomaly detection