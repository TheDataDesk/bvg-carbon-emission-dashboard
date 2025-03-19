# data_collector.py (Collect real data, fallback to simulate if needed)

import requests
import json
import os
import random
from datetime import datetime, timedelta
from emission import calculate_distance_km, estimate_emission

BASE_URL = 'https://v6.bvg.transport.rest'
user_ids = ['user_1', 'user_2', 'user_3']  # Simulate 3 users

# Fetch closest stop
def get_closest_stop(address):
    params = {'query': address, 'results': 1}
    try:
        response = requests.get(f'{BASE_URL}/locations', params=params)
        response.raise_for_status()
        data = response.json()
        for item in data:
            if item['type'] in ['stop', 'station']:
                return item
    except Exception:
        return None

# Fetch journey data from BVG API
def get_journey_data(from_id, to_id, date_time):
    url = f'{BASE_URL}/journeys?from={from_id}&to={to_id}&departure={date_time}&results=1&language=en'
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None

# Read existing data
def read_existing_data(filename='data/data.json'):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            try:
                data = json.load(f)
                return data if isinstance(data, list) else [data]
            except:
                return []
    return []

# Append new data
def append_data_to_file(new_entry, filename='data/data.json'):
    existing_data = read_existing_data(filename)
    existing_data.append(new_entry)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        json.dump(existing_data, f, indent=4)

# Generate synthetic location
def random_location():
    return {
        'latitude': round(52.5 + random.uniform(-0.1, 0.1), 6),
        'longitude': round(13.4 + random.uniform(-0.1, 0.1), 6)
    }

# Collect real data or simulate if not available
def collect_data_with_fallback(start_address, dest_address, days=60, journeys_per_day=3):
    from_stop = get_closest_stop(start_address)
    to_stop = get_closest_stop(dest_address)

    if not from_stop or not to_stop:
        print("Could not fetch valid stops. Switching to simulation only.")
        from_stop = {'location': random_location()}
        to_stop = {'location': random_location()}

    transport_modes = ['train', 'bus', 'subway', 'tram']
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days)
    current_date = start_date

    while current_date <= end_date:
        for _ in range(journeys_per_day):
            simulated_datetime = datetime.combine(current_date, datetime.min.time()) + timedelta(
                hours=random.choice([8, 12, 18]),
                minutes=random.randint(0, 59))

            api_datetime = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            simulated_date_str = simulated_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')

            user_id = random.choice(user_ids)
            transport_mode = random.choice(transport_modes)
            journey_data = get_journey_data(from_stop.get('id', ''), to_stop.get('id', ''), api_datetime)

            # If real data not available, simulate journey
            if not journey_data:
                from_loc = random_location()
                to_loc = random_location()
            else:
                from_loc = from_stop['location']
                to_loc = to_stop['location']

            distance = calculate_distance_km(from_loc['latitude'], from_loc['longitude'],
                                             to_loc['latitude'], to_loc['longitude'])
            emission = estimate_emission(distance, transport_mode)

            entry = {
                'user_id': user_id,
                'startingAddress': start_address,
                'destinationAddress': dest_address,
                'dateTime': simulated_date_str,
                'transportMode': transport_mode,
                'fromStops': [{'location': from_loc}],
                'toStops': [{'location': to_loc}],
                'emission_kg': emission
            }

            append_data_to_file(entry)
            status = "Simulated" if not journey_data else "Real"
            print(f"{status} | Date: {simulated_date_str} | User: {user_id} | Mode: {transport_mode}")
        current_date += timedelta(days=1)

if __name__ == '__main__':
    collect_data_with_fallback('Brandenburg Gate', 'East Side Gallery', days=60, journeys_per_day=3)