import os
import sys
import time
import pandas as pd
import requests
from datetime import datetime

# List of target cities in Pakistan
CITIES = [
    {"city": "Karachi", "province": "Sindh", "lat": 24.8607, "lon": 67.0011},
    {"city": "Lahore", "province": "Punjab", "lat": 31.5204, "lon": 74.3587},
    {"city": "Islamabad", "province": "Federal Capital Territory", "lat": 33.6844, "lon": 73.0479},
    {"city": "Peshawar", "province": "Khyber Pakhtunkhwa", "lat": 34.0151, "lon": 71.5249},
    {"city": "Quetta", "province": "Balochistan", "lat": 30.1798, "lon": 66.9750},
    {"city": "Muzaffarabad", "province": "Jammu and Kashmir", "lat": 34.3700, "lon": 73.4700}
]

def get_user_years():
    """Reads start and end years from command line or interactive user prompt."""
    current_year = datetime.now().year
    
    if len(sys.argv) == 3:
        try:
            start_yr = int(sys.argv[1])
            end_yr = int(sys.argv[2])
            return start_yr, end_yr
        except ValueError:
            print("Invalid command line arguments. Falling back to interactive prompts.\n")

    print("="*60)
    print("      PAKISTAN CITIES HISTORICAL WEATHER DOWNLOADER       ")
    print("="*60)
    
    while True:
        try:
            start_yr = int(input(f"Enter START Year (e.g., 1947 to {current_year}): "))
            if 1940 <= start_yr <= current_year:
                break
            print(f"Please enter a valid year between 1940 and {current_year}.")
        except ValueError:
            print("Invalid input. Please enter a numerical year.")

    while True:
        try:
            end_yr = int(input(f"Enter END Year (e.g., {start_yr} to {current_year}): "))
            if start_yr <= end_yr <= current_year:
                break
            print(f"End year must be between {start_yr} and {current_year}.")
        except ValueError:
            print("Invalid input. Please enter a numerical year.")

    return start_yr, end_yr


def fetch_city_historical_weather(start_year, end_year):
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # If the end year is the current year, use today's date as the cutoff limit
    if end_year == datetime.now().year:
        end_date_str = today_str
    else:
        end_date_str = f"{end_year}-12-31"

    start_date_str = f"{start_year}-01-01"

    print(f"\nTarget Date Range: {start_date_str} to {end_date_str}")
    
    all_city_dfs = []
    
    for item in CITIES:
        city = item["city"]
        province = item["province"]
        lat = item["lat"]
        lon = item["lon"]
        
        cache_file = f"weather_{city.lower().replace(' ', '_')}_{start_year}_{end_year}.csv"
        
        # Check for cached dataset
        if os.path.exists(cache_file):
            print(f"\n[CACHE HIT] Loading cached data for {city} from '{cache_file}'...")
            df_monthly = pd.read_csv(cache_file)
            all_city_dfs.append(df_monthly)
            continue

        print(f"\nFetching historical weather for {city}, {province} ({start_year}–{end_year})...")
        
        url = (
            f"https://archive-api.open-meteo.com/v1/archive?"
            f"latitude={lat}&longitude={lon}&"
            f"start_date={start_date_str}&end_date={end_date_str}&"
            f"daily=temperature_2m_mean,temperature_2m_max,temperature_2m_min,precipitation_sum&"
            f"timezone=Asia%2FKarachi"
        )
        
        success = False
        retries = 0
        
        while not success and retries < 3:
            try:
                r = requests.get(url, timeout=40)
                
                # Handle API rate limits (HTTP 429)
                if r.status_code == 429:
                    print("  ⚠️ Rate limit reached. Pausing for 60 seconds to reset limits...")
                    time.sleep(60)
                    retries += 1
                    continue
                
                if r.status_code == 200:
                    daily_data = r.json().get("daily", {})
                    
                    df_daily = pd.DataFrame({
                        "date": pd.to_datetime(daily_data.get("time", [])),
                        "tas": daily_data.get("temperature_2m_mean", []),
                        "tasmax": daily_data.get("temperature_2m_max", []),
                        "tasmin": daily_data.get("temperature_2m_min", []),
                        "pr": daily_data.get("precipitation_sum", [])
                    })
                    
                    df_daily["Year"] = df_daily["date"].dt.year
                    df_daily["Month"] = df_daily["date"].dt.month
                    df_daily["Date"] = df_daily["date"].dt.strftime("%Y-%m")
                    
                    # Aggregate daily to monthly records
                    df_monthly = df_daily.groupby(["Year", "Month", "Date"]).agg({
                        "tas": "mean",
                        "tasmax": "mean",
                        "tasmin": "mean",
                        "pr": "sum"
                    }).reset_index()
                    
                    df_monthly.insert(0, "City", city)
                    df_monthly.insert(1, "Province", province)
                    df_monthly.insert(2, "Latitude", lat)
                    df_monthly.insert(3, "Longitude", lon)
                    
                    df_monthly["tas"] = df_monthly["tas"].round(2)
                    df_monthly["tasmax"] = df_monthly["tasmax"].round(2)
                    df_monthly["tasmin"] = df_monthly["tasmin"].round(2)
                    df_monthly["pr"] = df_monthly["pr"].round(2)
                    
                    # Cache file per city
                    df_monthly.to_csv(cache_file, index=False)
                    all_city_dfs.append(df_monthly)
                    print(f"  ✓ Retrieved {len(df_monthly)} monthly records for {city}.")
                    success = True
                    
                    # Pausing briefly between cities to respect API limits
                    time.sleep(12)
                else:
                    print(f"  ✗ API Error HTTP {r.status_code}: {r.text[:150]}")
                    break
            except Exception as e:
                print(f"  ✗ Error: {e}")
                break

    # Save final combined files
    if all_city_dfs:
        master_df = pd.concat(all_city_dfs, ignore_index=True)
        
        output_excel = f"pakistan_cities_weather_{start_year}_{end_year}.xlsx"
        output_csv = f"pakistan_cities_weather_{start_year}_{end_year}.csv"
        
        master_df.to_excel(output_excel, index=False)
        master_df.to_csv(output_csv, index=False)
        
        print("\n" + "="*60)
        print("Data extraction complete!")
        print(f"Saved dataset to '{output_excel}' and '{output_csv}'.")
        return master_df
    else:
        print("\nNo data retrieved.")
        return None

if __name__ == "__main__":
    start_yr, end_yr = get_user_years()
    fetch_city_historical_weather(start_yr, end_yr)