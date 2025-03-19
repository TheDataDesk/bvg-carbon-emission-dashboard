# summarize.py
import openai

openai.api_key = 'YOUR_API_KEY'  # Replace with environment variable for security

def generate_summary(df_anomalies):
    recent = df_anomalies[-7:]  # Last 7 days
    total_emission = recent['emission_kg'].sum()
    anomalies = recent[recent['anomaly'] == -1]

    prompt = (
        f"In the past week, total carbon emissions were {total_emission:.2f} kg. "
        f"There were {len(anomalies)} anomalies. Summarize these results for a report."
    )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    summary = response['choices'][0]['message']['content']
    return summary
