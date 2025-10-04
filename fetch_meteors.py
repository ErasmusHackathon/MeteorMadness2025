import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# NASA API configuration
NASA_API_KEY = os.getenv('NASA_API_KEY')
if not NASA_API_KEY:
    raise ValueError("NASA_API_KEY not found in environment variables. Please check your .env file.")
BASE_URL = 'https://api.nasa.gov/neo/rest/v1/feed'

def fetch_meteor_data(start_date=None, end_date=None):
    """
    Fetch meteor (NEO) data from NASA's API for a given date range.
    If no dates provided, fetches data for today and the next 7 days.
    """
    if start_date is None:
        start_date = datetime.now().strftime('%Y-%m-%d')
    if end_date is None:
        # NASA API limits to 7 days of data per request
        end_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    
    params = {
        'start_date': start_date,
        'end_date': end_date,
        'api_key': NASA_API_KEY
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def save_data(data, filename='meteor_data.json'):
    """
    Save the meteor data to a local file.
    """
    # Create data directory if it doesn't exist
    os.makedirs('data/all_meteors', exist_ok=True)
    filepath = os.path.join('data/all_meteors', filename)
    
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Data successfully saved to {filepath}")
    except Exception as e:
        print(f"Error saving data: {e}")

def process_meteor_data(data):
    """
    Process the raw NASA API data into a more structured format.
    Returns a pandas DataFrame with relevant information.
    """
    meteor_list = []
    
    for date, daily_data in data['near_earth_objects'].items():
        for neo in daily_data:
            meteor_info = {
                'date': date,
                'id': neo['id'],
                'name': neo['name'],
                'diameter_min_km': neo['estimated_diameter']['kilometers']['estimated_diameter_min'],
                'diameter_max_km': neo['estimated_diameter']['kilometers']['estimated_diameter_max'],
                'is_potentially_hazardous': neo['is_potentially_hazardous_asteroid'],
                'close_approach_date': neo['close_approach_data'][0]['close_approach_date'],
                'miss_distance_km': float(neo['close_approach_data'][0]['miss_distance']['kilometers']),
                'relative_velocity_kph': float(neo['close_approach_data'][0]['relative_velocity']['kilometers_per_hour'])
            }
            meteor_list.append(meteor_info)
    
    df = pd.DataFrame(meteor_list)
    return df

def validate_date(date_str):
    """Validate the date format"""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m-%d')
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format. Please use YYYY-MM-DD format")

def validate_date_range(start_date, end_date):
    """Validate that the date range doesn't exceed 7 days"""
    if not start_date or not end_date:
        return
        
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    date_diff = (end - start).days
    
    if date_diff > 7:
        raise ValueError(f"Date range cannot exceed 7 days. Your range is {date_diff} days. The NASA API has a 7-day limit.")

def main():
    parser = argparse.ArgumentParser(description='Fetch Near Earth Object (NEO) data from NASA API')
    parser.add_argument('--start-date', type=validate_date,
                      help='Start date in YYYY-MM-DD format (default: today)')
    parser.add_argument('--end-date', type=validate_date,
                      help='End date in YYYY-MM-DD format (default: start_date + 7 days)')
    args = parser.parse_args()
    
    try:
        validate_date_range(args.start_date, args.end_date)
        
        # Fetch the meteor data
        print("Fetching meteor data from NASA API...")
        data = fetch_meteor_data(args.start_date, args.end_date)
        
        if data:
            # Save raw data
            save_data(data)
            
            # Process and save structured data
            df = process_meteor_data(data)
            
    except ValueError as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main()
