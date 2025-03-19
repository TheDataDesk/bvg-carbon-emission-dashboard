# visualize.py

import matplotlib.pyplot as plt
from prophet.plot import plot_plotly
import plotly.io as pio

# For saving plotly plots as PNG
pio.kaleido.scope.default_format = "png"

def plot_forecast(model, forecast, save_path=None):
    fig = plot_plotly(model, forecast)
    if save_path:
        fig.write_image(save_path)  # Save to file
    else:
        fig.show()

def plot_anomalies(df_anomalies, save_path=None):
    plt.figure(figsize=(10,5))
    normal = df_anomalies[df_anomalies['anomaly'] == 1]
    anomalies = df_anomalies[df_anomalies['anomaly'] == -1]

    plt.plot(normal.index, normal['emission_kg'], label='Normal')
    plt.scatter(anomalies.index, anomalies['emission_kg'], color='red', label='Anomaly')
    plt.title("Daily Emissions with Anomalies")
    plt.legend()
    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()

