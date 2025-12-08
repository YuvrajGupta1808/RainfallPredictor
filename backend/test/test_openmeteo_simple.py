"""
Simple test to demonstrate Open-Meteo API calls for both models.
This shows the exact API endpoints and parameters used.
"""

import json
from datetime import datetime, timedelta


def show_hourly_api_example():
    """Show example API call for hourly model."""
    print("\n" + "="*80)
    print("HOURLY MODEL - Open-Meteo API Call")
    print("="*80 + "\n")
    
    # Example for Tokyo
    latitude = 35.6762
    longitude = 139.6503
    
    # For recent data (last 5 days), use forecast API
    url = "https://api.open-meteo.com/v1/forecast"
    
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "surface_pressure",
            "wind_speed_10m",
            "wind_direction_10m",
            "cloud_cover"
        ]),
        "timezone": "auto",
        "past_days": 1,
        "forecast_days": 1
    }
    
    print("📍 Location: Tokyo, Japan")
    print(f"   Coordinates: ({latitude}, {longitude})")
    print(f"\n🌐 API Endpoint:")
    print(f"   {url}")
    print(f"\n📋 Parameters:")
    for key, value in params.items():
        print(f"   {key}: {value}")
    
    print(f"\n🔗 Full URL:")
    param_str = "&".join([f"{k}={v}" for k, v in params.items()])
    print(f"   {url}?{param_str}")
    
    print(f"\n📊 Expected Response:")
    print("""   {
     "hourly": {
       "time": ["2024-12-08T00:00", "2024-12-08T01:00", ...],
       "temperature_2m": [15.2, 14.8, ...],
       "relative_humidity_2m": [65, 68, ...],
       "surface_pressure": [1013.2, 1013.5, ...],
       "wind_speed_10m": [10.5, 11.2, ...],
       "wind_direction_10m": [180, 185, ...],
       "cloud_cover": [45, 50, ...]
     }
   }""")
    
    print(f"\n✨ Processing:")
    print(f"   1. Fetch 24 hours of data")
    print(f"   2. Add time features (hour, month, sin/cos encodings)")
    print(f"   3. Normalize using predefined mean/std")
    print(f"   4. Format as (24, 12) array")
    print(f"   5. Feed to hourly model → predict next hour rainfall")


def show_daily_api_example():
    """Show example API call for daily model."""
    print("\n" + "="*80)
    print("DAILY MODEL - Open-Meteo API Call")
    print("="*80 + "\n")
    
    # Example for London
    latitude = 51.5074
    longitude = -0.1278
    
    # Calculate dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # For recent data, use forecast API
    url = "https://api.open-meteo.com/v1/forecast"
    
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": ",".join([
            "temperature_2m_mean",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "wind_speed_10m_max",
            "wind_direction_10m_dominant",
            "shortwave_radiation_sum",
            "relative_humidity_2m_mean",
            "surface_pressure_mean",
            "cloud_cover_mean",
            "dew_point_2m_mean"
        ]),
        "timezone": "auto",
        "past_days": 30,
        "forecast_days": 1
    }
    
    print("📍 Location: London, UK")
    print(f"   Coordinates: ({latitude}, {longitude})")
    print(f"\n🌐 API Endpoint:")
    print(f"   {url}")
    print(f"\n📋 Parameters:")
    for key, value in params.items():
        if key == "daily":
            print(f"   {key}: [11 daily parameters]")
        else:
            print(f"   {key}: {value}")
    
    print(f"\n📊 Expected Response:")
    print("""   {
     "daily": {
       "time": ["2024-11-08", "2024-11-09", ..., "2024-12-08"],
       "temperature_2m_mean": [12.5, 13.2, ...],
       "temperature_2m_max": [15.8, 16.5, ...],
       "temperature_2m_min": [9.2, 10.1, ...],
       "precipitation_sum": [2.5, 0.0, ...],
       "wind_speed_10m_max": [15.2, 12.8, ...],
       "wind_direction_10m_dominant": [180, 190, ...],
       "relative_humidity_2m_mean": [75, 72, ...],
       "surface_pressure_mean": [1013, 1015, ...],
       "cloud_cover_mean": [65, 45, ...],
       "dew_point_2m_mean": [8.5, 9.2, ...]
     }
   }""")
    
    print(f"\n✨ Processing:")
    print(f"   1. Fetch 30 days of data")
    print(f"   2. Add time features (month, sin/cos encodings)")
    print(f"   3. Add lag features (precip_lag_1, precip_lag_3, temp_mean_lag_1)")
    print(f"   4. Add rolling features (precip_roll7)")
    print(f"   5. Add location features (lat, lon)")
    print(f"   6. Normalize using data's own mean/std")
    print(f"   7. Format as (30, 18) array")
    print(f"   8. Feed to daily model → predict next day's rainfall")


def show_historical_api_example():
    """Show example API call for historical data."""
    print("\n" + "="*80)
    print("HISTORICAL DATA - Open-Meteo Archive API")
    print("="*80 + "\n")
    
    latitude = 40.7128
    longitude = -74.0060
    
    # For data older than 5 days, use archive API
    url = "https://archive-api.open-meteo.com/v1/archive"
    
    # Example: Get data from 30 days ago
    end_date = datetime.now() - timedelta(days=30)
    start_date = end_date - timedelta(days=30)
    
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "daily": "temperature_2m_mean,precipitation_sum",
        "timezone": "auto"
    }
    
    print("📍 Location: New York, USA")
    print(f"   Coordinates: ({latitude}, {longitude})")
    print(f"   Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"\n🌐 API Endpoint:")
    print(f"   {url}")
    print(f"\n📋 Parameters:")
    for key, value in params.items():
        print(f"   {key}: {value}")
    
    print(f"\n💡 Note:")
    print(f"   - Archive API: For data older than 5 days")
    print(f"   - Forecast API: For recent data (last 5 days)")
    print(f"   - Both APIs have the same response format")


def show_api_comparison():
    """Show comparison between hourly and daily APIs."""
    print("\n" + "="*80)
    print("API COMPARISON - Hourly vs Daily")
    print("="*80 + "\n")
    
    comparison = [
        ("Aspect", "Hourly Model", "Daily Model"),
        ("-" * 20, "-" * 30, "-" * 30),
        ("Time window", "24 hours", "30 days"),
        ("Data points", "24", "30"),
        ("Features per point", "12", "18"),
        ("Input shape", "(24, 12)", "(30, 18)"),
        ("API endpoint", "hourly", "daily"),
        ("Prediction", "Next hour rainfall (mm/h)", "Next day rainfall (mm/day)"),
        ("Use case", "Short-term forecast", "Next-day forecast"),
        ("Update frequency", "Hourly", "Daily"),
    ]
    
    for row in comparison:
        print(f"   {row[0]:<20} | {row[1]:<30} | {row[2]:<30}")


def main():
    """Show all API examples."""
    print("\n" + "="*80)
    print("OPEN-METEO API INTEGRATION GUIDE")
    print("Testing both Hourly and Daily weather data endpoints")
    print("="*80)
    
    show_hourly_api_example()
    show_daily_api_example()
    show_historical_api_example()
    show_api_comparison()
    
    print("\n" + "="*80)
    print("TESTING INSTRUCTIONS")
    print("="*80 + "\n")
    
    print("To test the actual API calls:")
    print("\n1. Install dependencies:")
    print("   cd backend")
    print("   source venv/bin/activate  # or venv\\Scripts\\activate on Windows")
    print("   pip install -r requirements.txt")
    
    print("\n2. Run the full API test:")
    print("   python test_openmeteo_api.py")
    
    print("\n3. Or test manually with curl:")
    print("   # Hourly data")
    print('   curl "https://api.open-meteo.com/v1/forecast?latitude=35.6762&longitude=139.6503&hourly=temperature_2m,relative_humidity_2m&past_days=1"')
    
    print("\n   # Daily data")
    print('   curl "https://api.open-meteo.com/v1/forecast?latitude=51.5074&longitude=-0.1278&daily=temperature_2m_mean,precipitation_sum&past_days=30"')
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
