import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

df = pd.read_csv("fleet_health_scored.csv")

flagged_count = int(df["is_anomaly"].sum())
total = len(df)
cost_avoidance = flagged_count * 4500

df_heat = df.sort_values("is_anomaly", ascending=False).reset_index(drop=True)
zscore_cols = ["zscore_avg_battery_health", "zscore_avg_range_km", "zscore_avg_temp_c"]
signal_labels = ["Battery Health", "Range km", "Temperature °C"]
z_matrix = df_heat[zscore_cols].T.values.tolist()
vehicle_labels = [f"⚠ {v}" if a else v for v, a in zip(df_heat["vehicle_id"], df_heat["is_anomaly"])]

flagged_df = df[df["is_anomaly"]].sort_values("severity_score", ascending=False)[
    ["vehicle_id","model","avg_battery_health","avg_range_km","avg_temp_c","severity_score"]
].copy()
flagged_df.columns = ["Vehicle","Model","Avg Battery %","Avg Range km","Avg Temp °C","Signals Tripped"]

cell_colors = []
for col in flagged_df.columns:
    if col == "Avg Battery %":
        cell_colors.append(["#7f1d1d" if v < 87 else "#0f172a" for v in flagged_df[col]])
    elif col == "Avg Range km":
        cell_colors.append(["#7f1d1d" if v < 260 else "#0f172a" for v in flagged_df[col]])
    elif col == "Avg Temp °C":
        cell_colors.append(["#7f1d1d" if v > 33.5 else "#0f172a" for v in flagged_df[col]])
    else:
        cell_colors.append(["#1e293b"] * len(flagged_df))

fig = make_subplots(
    rows=3, cols=2,
    subplot_titles=(
        "🚨 Flagged Vehicles — Immediate Review Required",
        "Z-Score Heatmap — Which Signal Tripped Each Vehicle",
        "Battery Health Ranking",
        "Range km Ranking",
        "Average Temperature by Vehicle", ""
    ),
    specs=[
        [{"type": "table"},  {"type": "heatmap"}],
        [{"type": "xy"},     {"type": "xy"}],
        [{"type": "xy", "colspan": 2}, None]
    ],
    row_heights=[0.28, 0.32, 0.28],
    vertical_spacing=0.10,
    horizontal_spacing=0.06
)

# Row 1 Left: flagged vehicles table
fig.add_trace(go.Table(
    header=dict(
        values=["<b>" + c + "</b>" for c in flagged_df.columns],
        fill_color="#7f1d1d",
        font=dict(color="white", size=13),
        align="left", height=32
    ),
    cells=dict(
        values=[flagged_df[c] for c in flagged_df.columns],
        fill_color=cell_colors,
        font=dict(color="white", size=12),
        align="left", height=28
    )
), row=1, col=1)

# Row 1 Right: Z-score heatmap
# Battery and Range: low Z = bad (blue). Temperature: high Z = bad (red).
# Build per-signal z rows with correct orientation
z_battery = df_heat["zscore_avg_battery_health"].tolist()
z_range   = df_heat["zscore_avg_range_km"].tolist()
z_temp    = df_heat["zscore_avg_temp_c"].tolist()

# Flip battery and range so that "bad" (low) = red, "good" (high) = blue
z_battery_flipped = [-v for v in z_battery]
z_range_flipped   = [-v for v in z_range]
# Temperature: high = bad = red, keep as-is

z_matrix_fixed = [z_battery_flipped, z_range_flipped, z_temp]
signal_labels_fixed = ["Battery Health", "Range km", "Temperature °C"]

fig.add_trace(go.Heatmap(
    z=z_matrix_fixed,
    x=vehicle_labels,
    y=signal_labels_fixed,
    colorscale=[
        [0.0,  "#1e293b"],
        [0.4,  "#334155"],
        [0.55, "#334155"],
        [1.0,  "#dc2626"]
    ],
    zmin=0, zmax=3,
    hovertemplate="<b>%{x}</b><br>%{y}: Risk level = %{z:.2f}<extra></extra>",
    colorbar=dict(
        title=dict(text="Risk Level", font=dict(color="white")),
        tickfont=dict(color="white"),
        tickvals=[0, 1.8, 3],
        ticktext=["Normal", "⚠ Threshold", "Critical"],
        len=0.28, y=0.85
    )
), row=1, col=2)

# Row 2 Left: Battery health bar + avg line
df_bat = df.sort_values("avg_battery_health").reset_index(drop=True)
bat_avg = df["avg_battery_health"].mean()
fig.add_trace(go.Bar(
    x=df_bat["vehicle_id"], y=df_bat["avg_battery_health"],
    marker_color=df_bat["is_anomaly"].map({True: "#ef4444", False: "#3b82f6"}),
    hovertemplate="<b>%{x}</b><br>Battery: %{y:.1f}%<extra></extra>", name=""
), row=2, col=1)
fig.add_trace(go.Scatter(
    x=df_bat["vehicle_id"], y=[bat_avg] * len(df_bat),
    mode="lines", line=dict(color="#94a3b8", dash="dash", width=1.5),
    hoverinfo="skip", name=""
), row=2, col=1)

# Row 2 Right: Range bar + avg line
df_range = df.sort_values("avg_range_km").reset_index(drop=True)
range_avg = df["avg_range_km"].mean()
fig.add_trace(go.Bar(
    x=df_range["vehicle_id"], y=df_range["avg_range_km"],
    marker_color=df_range["is_anomaly"].map({True: "#ef4444", False: "#22c55e"}),
    hovertemplate="<b>%{x}</b><br>Range: %{y:.1f} km<extra></extra>", name=""
), row=2, col=2)
fig.add_trace(go.Scatter(
    x=df_range["vehicle_id"], y=[range_avg] * len(df_range),
    mode="lines", line=dict(color="#94a3b8", dash="dash", width=1.5),
    hoverinfo="skip", name=""
), row=2, col=2)

# Row 3: Temperature bar + avg line + threshold annotation
df_temp = df.sort_values("avg_temp_c", ascending=False).reset_index(drop=True)
temp_avg = df["avg_temp_c"].mean()
temp_threshold = temp_avg + (1.8 * df["avg_temp_c"].std())
fig.add_trace(go.Bar(
    x=df_temp["vehicle_id"], y=df_temp["avg_temp_c"],
    marker_color=df_temp["is_anomaly"].map({True: "#ef4444", False: "#f59e0b"}),
    hovertemplate="<b>%{x}</b><br>Avg Temp: %{y:.1f}°C<extra></extra>", name=""
), row=3, col=1)
fig.add_trace(go.Scatter(
    x=df_temp["vehicle_id"], y=[temp_avg] * len(df_temp),
    mode="lines", line=dict(color="#94a3b8", dash="dash", width=1.5),
    hoverinfo="skip", name="fleet avg"
), row=3, col=1)
fig.add_trace(go.Scatter(
    x=df_temp["vehicle_id"], y=[temp_threshold] * len(df_temp),
    mode="lines", line=dict(color="#ef4444", dash="dot", width=1.5),
    hoverinfo="skip", name="anomaly threshold"
), row=3, col=1)

# Annotations for temp chart lines
fig.add_annotation(
    x=df_temp["vehicle_id"].iloc[-1], y=temp_avg,
    text="fleet avg", showarrow=False,
    font=dict(color="#94a3b8", size=10),
    xanchor="left", yanchor="bottom",
    row=3, col=1
)
fig.add_annotation(
    x=df_temp["vehicle_id"].iloc[-1], y=temp_threshold,
    text="⚠ anomaly threshold (+1.8σ)", showarrow=False,
    font=dict(color="#ef4444", size=10),
    xanchor="left", yanchor="bottom",
    row=3, col=1
)

fig.update_layout(
    title=dict(
        text=(
            f"EV Fleet Health & Anomaly Detection Dashboard<br>"
            f"<sup><span style='color:#ef4444'>⚠ {flagged_count} of {total} vehicles flagged for proactive maintenance"
            f" — Est. cost avoidance if addressed now: ${cost_avoidance:,}</span></sup>"
        ),
        font=dict(size=22, color="white"), x=0.5
    ),
    paper_bgcolor="#0f172a",
    plot_bgcolor="#1e293b",
    font=dict(color="white"),
    showlegend=False,
    height=1150,
    margin=dict(l=140, r=80, t=100, b=40)
)

fig.update_xaxes(showgrid=False, color="white", tickfont=dict(size=8))
fig.update_yaxes(showgrid=True, gridcolor="#334155", color="white")

fig.write_html("fleet_dashboard.html")
print(f"Dashboard saved. {flagged_count} vehicles flagged. Est. cost avoidance: ${cost_avoidance:,}")