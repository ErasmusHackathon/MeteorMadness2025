import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import glob
import os
import json

def load_latest_data():
    """Load the most recent meteor data from JSON file and convert to CSV"""
    # Look for JSON file in all_meteors directory
    json_file = 'data/all_meteors/meteor_data.json'
    if not os.path.exists(json_file):
        raise FileNotFoundError("No meteor data found. Please run fetch_meteors.py first.")
    
    # Load and process the JSON data
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Process the data into a DataFrame
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
    df['date'] = pd.to_datetime(df['date'])
    df['close_approach_date'] = pd.to_datetime(df['close_approach_date'])
    
    # Create visualization directory and save processed data
    os.makedirs('data/all_meteors/visualization', exist_ok=True)
    df.to_csv('data/all_meteors/visualization/processed_meteors.csv', index=False)
    print("Processed data saved to data/all_meteors/visualization/processed_meteors.csv")
    
    return df

def plot_hazard_distribution(df):
    """Create a pie chart showing distribution of potentially hazardous asteroids"""
    plt.figure(figsize=(10, 6))
    hazard_counts = df['is_potentially_hazardous'].value_counts()
    plt.pie(hazard_counts, labels=['Safe', 'Potentially Hazardous'], 
            autopct='%1.1f%%', colors=['lightgreen', 'coral'])
    plt.title('Distribution of Potentially Hazardous Near Earth Objects')
    plt.savefig('data/all_meteors/visualization/hazard_distribution.png')
    plt.close()

def plot_size_vs_distance(df):
    """Create a scatter plot of asteroid size vs miss distance"""
    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(df['diameter_max_km'], df['miss_distance_km'] / 1000, 
                alpha=0.6, c=df['is_potentially_hazardous'].map({True: 'red', False: 'blue'}))
    
    # Add legend
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                                markerfacecolor='blue', label='Safe', markersize=10),
                      plt.Line2D([0], [0], marker='o', color='w', 
                                markerfacecolor='red', label='Potentially Hazardous', markersize=10)]
    plt.legend(handles=legend_elements)
    
    plt.xlabel('Maximum Diameter (km)')
    plt.ylabel('Miss Distance (thousand km)')
    plt.title('Asteroid Size vs Miss Distance')
    
    # Add logarithmic scale for better visualization
    plt.xscale('log')
    plt.yscale('log')
    
    plt.savefig('data/all_meteors/visualization/size_vs_distance.png')
    plt.close()

def plot_velocity_histogram(df):
    """Create a histogram of relative velocities"""
    plt.figure(figsize=(12, 6))
    sns.histplot(data=df, x='relative_velocity_kph', bins=30, hue='is_potentially_hazardous',
                palette=['blue', 'red'])
    plt.xlabel('Relative Velocity (km/h)')
    plt.ylabel('Count')
    plt.title('Distribution of Asteroid Velocities')
    plt.savefig('data/all_meteors/visualization/velocity_distribution.png')
    plt.close()

def plot_approaches_timeline(df):
    """Create a timeline of close approaches"""
    plt.figure(figsize=(15, 8))
    
    # Create scatter plot with size based on diameter
    sizes = df['diameter_max_km'] * 100  # Scale the sizes to be visible
    scatter = plt.scatter(df['close_approach_date'], df['miss_distance_km'] / 1000,
                         c=df['is_potentially_hazardous'].map({True: 'red', False: 'blue'}),
                         alpha=0.6, s=sizes)
    
    # Add legend
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', 
                   label='Safe', markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', 
                   label='Potentially Hazardous', markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', 
                   label='Size Scale', markersize=5),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', 
                   label='', markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', 
                   label='', markersize=15)
    ]
    plt.legend(handles=legend_elements, title='Legend\nSize indicates diameter')
    
    plt.xlabel('Close Approach Date')
    plt.ylabel('Miss Distance (thousand km)')
    plt.title('Timeline of Close Approaches')
    plt.xticks(rotation=45)
    
    # Add grid for better readability
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('data/all_meteors/visualization/approaches_timeline.png')
    plt.close()

def create_summary_statistics(df):
    """Create and save summary statistics"""
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
    
    # Save statistics to a text file
    with open('data/all_meteors/visualization/summary_statistics.txt', 'w') as f:
        f.write("Near Earth Objects Analysis Summary\n")
        f.write("==================================\n\n")
        for key, value in stats.items():
            if isinstance(value, float):
                f.write(f"{key}: {value:,.2f}\n")
            else:
                f.write(f"{key}: {value}\n")

def main():
    try:
        # Load the data
        print("Loading meteor data...")
        df = load_latest_data()
        
        print("Creating visualizations...")
        # Create various plots
        plot_hazard_distribution(df)
        plot_size_vs_distance(df)
        plot_velocity_histogram(df)
        plot_approaches_timeline(df)
        
        # Generate summary statistics
        create_summary_statistics(df)
        
        print("\nFiles created in data/all_meteors/visualization/:")
        print("- processed_meteors.csv")
        print("- hazard_distribution.png")
        print("- size_vs_distance.png")
        print("- velocity_distribution.png")
        print("- approaches_timeline.png")
        print("- summary_statistics.txt")
        
    except FileNotFoundError as e:
        print(f"\nError: {e}")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()