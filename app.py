import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from time_series import load_emission_data, forecast_emissions, detect_anomalies

st.set_page_config(page_title="BVG Emission Dashboard", layout="wide")

PRIMARY_BVG = "#FFD500"  # Yellow
BLACK = "#000000"
WHITE = "#FFFFFF"

def update_plotly_layout(fig, title=""):
    fig.update_layout(
        title=dict(text=title, font=dict(color=BLACK, size=16)),
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        font=dict(color=BLACK, size=14),
        xaxis=dict(showgrid=True, gridcolor="#E5E5E5", zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#E5E5E5", zeroline=False),
        margin=dict(l=50, r=50, t=60, b=50)
    )

# Dashboard title
st.markdown(
    f"""
    <div style='display:flex; align-items:center; gap:20px;'>
        <h1 style='color:black;'>🚍 BVG Carbon Emission Dashboard</h1>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("""
            
##### Project Overview
This dashboard visualizes carbon emissions from Berlin's public transport system based on data from the **BVG (Berliner Verkehrsbetriebe)** API. By analyzing emission data from various transport modes, we estimate the CO2 footprint of public transportation and provide insights into current and future emissions trends.

Key insights are provided, including:
- **Total emissions by transport mode**
- **Daily emissions trends**
- **Top emission days**
- **Emission forecast for the next 7 days**
- **Anomaly detection for unusual emission patterns**

The dashboard helps users understand emission trends and supports climate action by forecasting future emissions, identifying peak days, and promoting emission-reducing practices.
""")

df = load_emission_data("data/data.json")
df.index = pd.to_datetime(df.index).tz_convert("UTC")
min_ts = df.index.min()
max_ts = df.index.max()

date_range = st.date_input("Select Date Range", [min_ts.date(), max_ts.date()], min_value=min_ts.date(), max_value=max_ts.date())
start_ts = pd.Timestamp(date_range[0]).tz_localize("UTC")
end_ts = pd.Timestamp(date_range[1]).tz_localize("UTC")
df_filtered = df[(df.index >= start_ts) & (df.index <= end_ts)]

modes = df_filtered["transport_mode"].unique().tolist()
selected_modes = st.multiselect("Filter by Transport Mode", options=modes, default=modes)
df_filtered = df_filtered[df_filtered["transport_mode"].isin(selected_modes)]

# Total Emissions by Transport Mode
st.subheader("Total Emissions by Transport Mode")
st.markdown("""
This graph shows the **total carbon emissions by transport mode**. It helps identify which modes of public transport, such as buses, trams, and trains, are contributing the most to the city's carbon footprint.
""")
mode_group = df_filtered.groupby("transport_mode")["emission_kg"].sum().reset_index()
fig_mode = px.bar(mode_group, x="transport_mode", y="emission_kg", color_discrete_sequence=[PRIMARY_BVG])
update_plotly_layout(fig_mode)
st.plotly_chart(fig_mode, use_container_width=True)

# Daily Emissions
st.subheader("Daily Emissions")
st.markdown("""
This graph shows the **cumulative daily emissions** over time. It allows us to track the emissions for each day and observe the trends in carbon emissions on a daily basis over the selected period.
""")
daily_emissions = df_filtered.resample("D").sum(numeric_only=True).reset_index()
fig_area = px.area(daily_emissions, x="datetime", y="emission_kg", color_discrete_sequence=[PRIMARY_BVG], title="Cumulative Daily Emissions")
update_plotly_layout(fig_area)
st.plotly_chart(fig_area, use_container_width=True)

# Daily Emissions with Top 5 Impact
st.subheader("Daily Emissions with Top 5 Impact")
st.markdown("""
This chart shows all daily emissions, with the **top 5 highest-emission days** highlighted in black. It helps identify the days when emissions spiked the most, providing insight into peak emission events.
""")
top5 = daily_emissions.sort_values(by="emission_kg", ascending=False).head(5)
fig_all_days = px.bar(daily_emissions, x="datetime", y="emission_kg", color_discrete_sequence=[PRIMARY_BVG], title="All Emission Days")
fig_all_days.add_trace(go.Bar(
    x=top5["datetime"], 
    y=top5["emission_kg"], 
    marker_color="grey",  # Highlight top 5 bars in black
    name="Top 5 Days"
))
update_plotly_layout(fig_all_days)
st.plotly_chart(fig_all_days, use_container_width=True)

# Emission Forecast using Prophet (Next 7 Days)
st.subheader("Emission Forecast using Prophet (Next 7 Days)")
st.markdown("""
This forecast predicts the emissions for the **next 7 days** using the **Prophet model**. It gives an insight into future trends, helping stakeholders anticipate emissions and plan mitigation efforts.
""")
model, forecast = forecast_emissions(df_filtered)
fig_forecast = px.line(forecast, x="ds", y="yhat", color_discrete_sequence=[PRIMARY_BVG])
update_plotly_layout(fig_forecast)
st.plotly_chart(fig_forecast, use_container_width=True)

# Anomaly Detection
st.subheader("Anomaly Detection")
st.markdown("""
This scatter plot visualizes **anomalies in emissions**. Days marked in red represent anomalous emissions, which might be caused by disruptions, unexpected traffic, or errors in data collection. Identifying these anomalies helps in detecting unusual patterns in emissions.
""")
df_anomalies = detect_anomalies(df_filtered).reset_index()
df_anomalies["status"] = df_anomalies["anomaly"].map({1: "Normal", -1: "Anomaly"})
fig_anom = px.scatter(df_anomalies, x="datetime", y="emission_kg", color="status", color_discrete_map={"Normal": PRIMARY_BVG, "Anomaly": "red"})
update_plotly_layout(fig_anom)
st.plotly_chart(fig_anom, use_container_width=True)

# Berlin Sustainability Estimate
st.subheader("Berlin Sustainability Estimate (Based on 60 Days Data)")
st.markdown("""
This graph shows how many years **Berlin can sustain its current emission rate** before exceeding the **global CO2 emission limit** set by the **IPCC**. The estimate is based on 60 days of emission data, illustrating the need for **urgent climate action**.
""")
# Example value for total CO2 emissions in kg over 60 days
total_emission_60_days = 10_000_000  # Replace this with your actual emission data for 60 days in kg

# Calculate the daily emission rate
daily_emission_kg = total_emission_60_days / 60  # Emissions per day in kg

# Extrapolate the annual emissions
annual_emission_kg = daily_emission_kg * 365  # Annual emissions in kg

# Global emission limit (40 Gt = 40,000,000,000,000 kg)
world_emission_limit_kg = 4e10  # 40 Gt = 40,000,000,000,000 kg

# Calculate the number of years Berlin can emit at the current annual rate before exceeding the global emission limit
survival_years_berlin = world_emission_limit_kg / annual_emission_kg

# Create the bar chart to show Berlin's sustainability estimate
fig_survival = px.bar(
    x=["Years Berlin Can Sustain This Rate"],
    y=[survival_years_berlin],
    color_discrete_sequence=["#FFCD00"]  # Primary color for the bar chart
)

# Add short hovertext with updated text
fig_survival.update_traces(
    hovertemplate=(
        "Based on the global limit set by the IPCC:<br>"
        "Berlin's emissions will exceed the limit in {0:.0f} years.<br>"
        "Urgent action is needed to mitigate climate change."
        "<extra></extra>"  # Hides additional information like trace name (if any)
    ).format(survival_years_berlin),  # Dynamically insert the calculated number of years
    hoverinfo="text"  # Ensure only hover text is shown
)

# Update the plot layout
fig_survival.update_layout(
    title="Berlin Sustainability Estimate",
    xaxis_title="Emissions Sustainability",
    yaxis_title="Years",
    showlegend=False
)

# Display the bar chart using Streamlit with a unique key argument
st.plotly_chart(fig_survival, use_container_width=True, key="berlin_sustainability_estimate_chart_unique_001")

# Key Emission Stats
st.subheader("Key Emission Stats")
total_emission = df_filtered["emission_kg"].sum()
daily_recent = df_filtered.resample("D").sum(numeric_only=True).tail(7)["emission_kg"].sum()
anomalies_count = df_anomalies[df_anomalies["anomaly"] == -1].shape[0]
offset_cost = total_emission * 0.01
st.markdown(f"**Total Emissions:** {total_emission:.2f} kg CO₂")
st.markdown(f"**Last 7 Days Emissions:** {daily_recent:.2f} kg CO₂")
st.markdown(f"**Anomaly Days Detected:** {anomalies_count}")
st.markdown(f"**Carbon Offset Estimate:** ${offset_cost:.2f} *(at $0.01 per kg CO₂)*")

st.markdown("""
    <hr>
    <div style="text-align: center; font-size: 12px; color: #777;">
        <h4>Contact</h4>
        <p>
            <a href="https://www.linkedin.com/in/sirishajp/" target="_blank">LinkedIn</a> |
            <a href="https://github.com/TheDataDesk" target="_blank">GitHub</a> |
            <a href="https://thedatadesk.github.io/sirishaportfolio/" target="_blank">Portfolio</a>
        </p>
        <p>Developed by Sirisha Padmasekhar (TheDataDesk)</p>
    </div>
    """, unsafe_allow_html=True)
