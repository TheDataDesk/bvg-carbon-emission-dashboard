# main.py

from time_series import load_emission_data, forecast_emissions, detect_anomalies
from visualize import plot_forecast, plot_anomalies
from emission import calculate_distance_km, estimate_emission
import matplotlib.pyplot as plt
import os

# -----------------------------------
# Setup Directories
# -----------------------------------
os.makedirs('plots', exist_ok=True)
os.makedirs('data', exist_ok=True)

# -----------------------------------
# 1. Load Emission Data
# -----------------------------------
df = load_emission_data('data/data.json')
print("Loaded Data Sample:\n", df.head())

# -----------------------------------
# 2. Emissions by Transport Mode
# -----------------------------------
emissions_by_mode = df.groupby('transport_mode')['emission_kg'].sum().sort_values(ascending=False)
print("\nTotal Emissions by Transport Mode:\n", emissions_by_mode)

# Plot Emissions by Mode
emissions_by_mode.plot(kind='bar', title='Total Emissions by Transport Mode', figsize=(8,5))
plt.ylabel('Emissions (kg CO2)')
plt.xlabel('Transport Mode')
plt.tight_layout()
plt.savefig('plots/emissions_by_mode.png')
plt.close()

# -----------------------------------
# 3. Daily Emissions by Transport Mode (Stacked Bar)
# -----------------------------------
daily_mode = df.groupby([df.index.date, 'transport_mode']).sum().unstack().fillna(0)
daily_mode.columns = daily_mode.columns.droplevel()
daily_mode.plot(kind='bar', stacked=True, figsize=(12,6), title='Daily Emissions by Transport Mode')
plt.ylabel('Emissions (kg CO2)')
plt.tight_layout()
plt.savefig('plots/daily_emissions_stacked.png')
plt.close()

# -----------------------------------
# 4. Emissions by User
# -----------------------------------
emissions_by_user = df.groupby('user_id')['emission_kg'].sum().sort_values(ascending=False)
print("\nTotal Emissions by User:\n", emissions_by_user)

# Plot Emissions by User
emissions_by_user.plot(kind='bar', title='Total Emissions by User', figsize=(8,5), color='green')
plt.ylabel('Emissions (kg CO2)')
plt.xlabel('User ID')
plt.tight_layout()
plt.savefig('plots/emissions_by_user.png')
plt.close()

# Save emissions by user to CSV
emissions_by_user.to_csv('data/emissions_by_user.csv')

# -----------------------------------
# 5. Forecast Emissions (Next 7 Days)
# -----------------------------------
model, forecast = forecast_emissions(df)
plot_forecast(model, forecast, save_path='plots/forecast.png')

# -----------------------------------
# 6. Detect Anomalies
# -----------------------------------
df_anomalies = detect_anomalies(df)
plot_anomalies(df_anomalies, save_path='plots/anomalies.png')

# -----------------------------------
# 7. Summary Generation + Carbon Offset
# -----------------------------------
total_emission = df['emission_kg'].sum()
recent = df.resample('D').sum().tail(7)
recent_total = recent['emission_kg'].sum()
anomaly_days = df_anomalies[df_anomalies['anomaly'] == -1].shape[0]

offset_cost_per_kg = 0.01  # $0.01 per kg CO2
total_offset_cost = total_emission * offset_cost_per_kg

summary_text = (
    f"Summary Report:\n"
    f"In the last 7 days, total emissions were {recent_total:.2f} kg CO2.\n"
    f"Total emissions over 30 days: {total_emission:.2f} kg CO2.\n"
    f"{anomaly_days} anomaly days were detected.\n"
    f"Estimated Carbon Offset Cost: ${total_offset_cost:.2f} (at ${offset_cost_per_kg:.2f} per kg CO2)\n"
    f"Suggested Action: Investigate the anomaly days for unusual travel patterns or data errors. "
    f"Consider strategies to reduce emissions on high-output days."
)

print("\n📝 Summary:\n", summary_text)

with open('data/emission_summary.txt', 'w') as f:
    f.write(summary_text)

# -----------------------------------
# 8. Markdown Report Generator
# -----------------------------------
with open('report.md', 'w') as f:
    f.write("# Emission Analysis Report\n\n")
    f.write(f"**Total Emissions (30 days):** {total_emission:.2f} kg CO₂\n\n")
    f.write(f"**Last 7 Days Emissions:** {recent_total:.2f} kg CO₂\n\n")
    f.write(f"**Anomaly Days Detected:** {anomaly_days}\n\n")
    f.write(f"**Carbon Offset Estimate:** ${total_offset_cost:.2f}\n\n")
    f.write("## Summary\n\n")
    f.write(summary_text + "\n\n")
    f.write("## Visualizations\n\n")
    f.write("![Emissions by Mode](plots/emissions_by_mode.png)\n\n")
    f.write("![Daily Emissions](plots/daily_emissions_stacked.png)\n\n")
    f.write("![Emissions by User](plots/emissions_by_user.png)\n\n")
    f.write("![Forecast](plots/forecast.png)\n\n")
    f.write("![Anomalies](plots/anomalies.png)\n")
