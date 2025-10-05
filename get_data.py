import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os
import json

# ======================
# CONFIGURATION
# ======================
API_KEY = "hQ7zg9zVpbIK42iHeHX0EOaE3pA2Mu5Fulmfkb8t"  # Replace with your NASA API key
START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 12, 31)
DATA_DIR = "data/all_meteors"
VIS_DIR = os.path.join(DATA_DIR, "visualization")
JSON_FILE = os.path.join(DATA_DIR, "meteor_data_full.json")
CSV_FILE = os.path.join(VIS_DIR, "processed_meteors.csv")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(VIS_DIR, exist_ok=True)

# ======================
# FETCH DATA
# ======================
def fetch_neo_data(start_date, end_date, api_key):
    delta = timedelta(days=7)  # API allows max 7-day range
    all_neos = {}
    current = start_date

    while current <= end_date:
        batch_start = current
        batch_end = min(current + delta, end_date)
        url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={batch_start.date()}&end_date={batch_end.date()}&api_key={api_key}"
        print(f"Fetching data: {batch_start.date()} to {batch_end.date()}")

        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error fetching data: {response.text}")
            current += delta + timedelta(days=1)
            continue

        data = response.json()
        all_neos.update(data['near_earth_objects'])
        current += delta + timedelta(days=1)

    # Save JSON
    with open(JSON_FILE, "w") as f:
        json.dump({"near_earth_objects": all_neos}, f)
    print(f"Full JSON data saved to {JSON_FILE}")
    return all_neos

# ======================
# PROCESS DATA
# ======================
def process_neo_data(all_neos):
    meteor_list = []
    for date, daily_data in all_neos.items():
        for neo in daily_data:
            try:
                meteor_info = {
                    "date": date,
                    "id": neo["id"],
                    "name": neo["name"],
                    "diameter_min_km": neo["estimated_diameter"]["kilometers"]["estimated_diameter_min"],
                    "diameter_max_km": neo["estimated_diameter"]["kilometers"]["estimated_diameter_max"],
                    "is_potentially_hazardous": neo["is_potentially_hazardous_asteroid"],
                    "close_approach_date": neo["close_approach_data"][0]["close_approach_date"],
                    "miss_distance_km": float(neo["close_approach_data"][0]["miss_distance"]["kilometers"]),
                    "relative_velocity_kph": float(neo["close_approach_data"][0]["relative_velocity"]["kilometers_per_hour"])
                }
                meteor_list.append(meteor_info)
            except Exception as e:
                print(f"Skipping NEO {neo.get('id', 'unknown')}: {e}")

    df = pd.DataFrame(meteor_list)
    df["date"] = pd.to_datetime(df["date"])
    df["close_approach_date"] = pd.to_datetime(df["close_approach_date"])
    df.to_csv(CSV_FILE, index=False)
    print(f"Processed CSV saved to {CSV_FILE}")
    return df


# ======================
# VISUALIZATIONS
# ======================
def plot_hazard_distribution(df):
    plt.figure(figsize=(10,6))
    hazard_counts = df["is_potentially_hazardous"].value_counts()
    plt.pie(hazard_counts, labels=['Safe','Hazardous'], autopct='%1.1f%%', colors=['lightgreen','coral'])
    plt.title("Distribution of Potentially Hazardous NEOs")
    plt.savefig(os.path.join(VIS_DIR,"hazard_distribution.png"))
    plt.close()

def plot_size_vs_distance(df):
    plt.figure(figsize=(12,8))
    plt.scatter(df['diameter_max_km'], df['miss_distance_km']/1000, 
                c=df['is_potentially_hazardous'].map({True:'red', False:'blue'}),
                alpha=0.6)
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel("Maximum Diameter (km)")
    plt.ylabel("Miss Distance (thousand km)")
    plt.title("Asteroid Size vs Miss Distance")
    plt.savefig(os.path.join(VIS_DIR,"size_vs_distance.png"))
    plt.close()

def plot_velocity_histogram(df):
    plt.figure(figsize=(12,6))
    sns.histplot(data=df, x='relative_velocity_kph', bins=30, hue='is_potentially_hazardous', palette=['blue','red'])
    plt.xlabel("Relative Velocity (km/h)")
    plt.ylabel("Count")
    plt.title("Asteroid Velocity Distribution")
    plt.savefig(os.path.join(VIS_DIR,"velocity_distribution.png"))
    plt.close()

def plot_approaches_timeline(df):
    plt.figure(figsize=(15,8))
    sizes = df['diameter_max_km']*100
    plt.scatter(df['close_approach_date'], df['miss_distance_km']/1000,
                c=df['is_potentially_hazardous'].map({True:'red', False:'blue'}),
                alpha=0.6, s=sizes)
    plt.xlabel("Close Approach Date")
    plt.ylabel("Miss Distance (thousand km)")
    plt.title("Timeline of Close Approaches")
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(VIS_DIR,"approaches_timeline.png"))
    plt.close()

# ======================
# SUMMARY STATISTICS
# ======================
def create_summary_statistics(df):
    stats = {
        'Total NEOs': len(df),
        'Potentially Hazardous': df['is_potentially_hazardous'].sum(),
        'Average Diameter (km)': df['diameter_max_km'].mean(),
        'Average Miss Distance (km)': df['miss_distance_km'].mean(),
        'Average Velocity (km/h)': df['relative_velocity_kph'].mean(),
        'Closest Approach (km)': df['miss_distance_km'].min(),
        'Largest Object (km)': df['diameter_max_km'].max(),
        'Date Range': f"{df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}"
    }
    with open(os.path.join(VIS_DIR,"summary_statistics.txt"), "w") as f:
        f.write("Near Earth Objects Analysis Summary\n")
        f.write("==================================\n\n")
        for key, value in stats.items():
            if isinstance(value,float):
                f.write(f"{key}: {value:,.2f}\n")
            else:
                f.write(f"{key}: {value}\n")

# ======================
# MAIN FUNCTION
# ======================
def main():
    try:
        all_neos = fetch_neo_data(START_DATE, END_DATE, API_KEY)
        df = process_neo_data(all_neos)
        plot_hazard_distribution(df)
        plot_size_vs_distance(df)
        plot_velocity_histogram(df)
        plot_approaches_timeline(df)
        create_summary_statistics(df)
        print("\nAll files created in:", VIS_DIR)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
    