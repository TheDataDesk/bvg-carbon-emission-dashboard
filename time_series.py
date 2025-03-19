# time_series.py

import json
import pandas as pd
from datetime import datetime
from emission import calculate_distance_km, estimate_emission
from prophet import Prophet
from sklearn.ensemble import IsolationForest

# Load data from JSON and calculate emissions, including user_id
def load_emission_data(json_file):
    with open(json_file) as f:
        data = json.load(f)

    records = []

    for entry in data:
        trip_time = datetime.fromisoformat(entry['dateTime'].replace("Z", "+00:00"))
        from_loc = entry['fromStops'][0]['location']
        to_loc = entry['toStops'][0]['location']

        distance = calculate_distance_km(
            from_loc['latitude'], from_loc['longitude'],
            to_loc['latitude'], to_loc['longitude']
        )

        transport_mode = entry.get('transportMode', 'train')
        user_id = entry.get('user_id', 'unknown')
        emission = estimate_emission(distance, mode=transport_mode)

        records.append({
            'datetime': trip_time,
            'emission_kg': emission,
            'transport_mode': transport_mode,
            'user_id': user_id
        })

    df = pd.DataFrame(records)
    df.set_index('datetime', inplace=True)
    return df

# Forecast emissions for all users combined
def forecast_emissions(df, days=7):
    df_daily = df[['emission_kg']].resample('D').sum().reset_index()
    df_daily['datetime'] = df_daily['datetime'].dt.tz_localize(None)  # Remove timezone for Prophet
    df_daily.columns = ['ds', 'y']

    model = Prophet()
    model.fit(df_daily)
    future = model.make_future_dataframe(periods=days)
    forecast = model.predict(future)
    return model, forecast

# Detect anomalies in daily emission totals
def detect_anomalies(df):
    df_daily = df[['emission_kg']].resample('D').sum()
    model = IsolationForest(contamination=0.1, random_state=42)
    df_daily['anomaly'] = model.fit_predict(df_daily[['emission_kg']])
    return df_daily
