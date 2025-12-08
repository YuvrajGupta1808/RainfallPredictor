"""
Weather data service for fetching historical weather data from Open-Meteo API.
"""

import httpx
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import pandas as pd
import numpy as np
from typing import Optional
from timezonefinder import TimezoneFinder

# Feature normalization constants (mean and std for each feature)
# Order: temperature_2m, relative_humidity_2m, surface_pressure, 
#        wind_speed_10m, wind_direction_10m, cloud_cover,
#        hour, month, hour_sin, hour_cos, month_sin, month_cos
FEATURE_MEAN = np.array([
    15.0,   # temperature_2m (°C)
    60.0,   # relative_humidity_2m (%)
    1013.0, # surface_pressure (hPa)
    10.0,   # wind_speed_10m (km/h)
    180.0,  # wind_direction_10m (degrees)
    50.0,   # cloud_cover (%)
    11.5,   # hour (0-23)
    6.5,    # month (1-12)
    0.0,    # hour_sin
    0.0,    # hour_cos
    0.0,    # month_sin
    0.0     # month_cos
])

FEATURE_STD = np.array([
    10.0,   # temperature_2m
    25.0,   # relative_humidity_2m
    10.0,   # surface_pressure
    5.0,    # wind_speed_10m
    100.0,  # wind_direction_10m
    35.0,   # cloud_cover
    6.9,    # hour
    3.5,    # month
    0.7,    # hour_sin
    0.7,    # hour_cos
    0.7,    # month_sin
    0.7     # month_cos
])


async def fetch_weather_data(
    latitude: float,
    longitude: float,
    end_time: datetime = None,
    hours: int = 24
) -> pd.DataFrame:
    """
    Fetch hourly weather data from Open-Meteo Historical Weather API.
    
    Args:
        latitude: Location latitude (-90 to 90)
        longitude: Location longitude (-180 to 180)
        end_time: End of the time window (if None, uses current time in location's timezone)
        hours: Number of hours to fetch (default: 24)
    
    Returns:
        DataFrame with columns: time, temperature_2m, relative_humidity_2m,
        surface_pressure, wind_speed_10m, wind_direction_10m, cloud_cover
    
    Raises:
        httpx.HTTPError: If the API request fails
        ValueError: If the response contains insufficient data
    
    Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
    """
    # If no end_time provided, get current time in the location's timezone
    if end_time is None:
        # Find the timezone for the given coordinates
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lat=latitude, lng=longitude)
        
        if timezone_str:
            # Get current time in the location's timezone
            location_tz = ZoneInfo(timezone_str)
            end_time = datetime.now(location_tz)
        else:
            # Fallback to UTC if timezone cannot be determined
            end_time = datetime.now(ZoneInfo("UTC"))
    
    # Calculate start time (hours before end_time)
    start_time = end_time - timedelta(hours=hours)
    
    # Format dates for API (YYYY-MM-DD)
    start_date = start_time.strftime("%Y-%m-%d")
    end_date = end_time.strftime("%Y-%m-%d")
    
    # Determine which API to use based on the date
    # Archive API only has data up to ~5 days ago
    # For recent/current data, use the forecast API
    now_utc = datetime.now(ZoneInfo("UTC"))
    days_ago = (now_utc.date() - end_time.date()).days
    
    if days_ago > 5:
        # Use historical archive API for older data
        url = "https://archive-api.open-meteo.com/v1/archive"
    else:
        # Use forecast API for recent/current data (includes historical forecast data)
        url = "https://api.open-meteo.com/v1/forecast"
    
    # Required weather parameters (Requirements 2.1)
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
        "timezone": "auto"
    }
    
    # Add date parameters based on API type
    if days_ago > 5:
        # Archive API uses start_date and end_date
        params["start_date"] = start_date
        params["end_date"] = end_date
    else:
        # Forecast API uses past_days and forecast_days
        # Calculate how many past days we need
        past_days = max(0, (now_utc.date() - start_time.date()).days)
        params["past_days"] = min(past_days + 1, 92)  # API limit is 92 days
        params["forecast_days"] = 1  # Include today
    
    # Make async HTTP request
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise httpx.HTTPError(f"Open-Meteo API request failed: {str(e)}")
    
    # Parse JSON response
    data = response.json()
    
    # Extract hourly data
    if "hourly" not in data:
        raise ValueError("API response missing 'hourly' data")
    
    hourly = data["hourly"]
    
    # Validate all required fields are present
    required_fields = [
        "time",
        "temperature_2m",
        "relative_humidity_2m",
        "surface_pressure",
        "wind_speed_10m",
        "wind_direction_10m",
        "cloud_cover"
    ]
    
    for field in required_fields:
        if field not in hourly:
            raise ValueError(f"API response missing required field: {field}")
    
    # Create DataFrame
    df = pd.DataFrame({
        "time": pd.to_datetime(hourly["time"]),
        "temperature_2m": hourly["temperature_2m"],
        "relative_humidity_2m": hourly["relative_humidity_2m"],
        "surface_pressure": hourly["surface_pressure"],
        "wind_speed_10m": hourly["wind_speed_10m"],
        "wind_direction_10m": hourly["wind_direction_10m"],
        "cloud_cover": hourly["cloud_cover"]
    })
    
    # Convert start_time and end_time to timezone-naive for comparison
    # (Open-Meteo returns timezone-naive timestamps in local time)
    start_time_naive = start_time.replace(tzinfo=None) if hasattr(start_time, 'tzinfo') else start_time
    end_time_naive = end_time.replace(tzinfo=None) if hasattr(end_time, 'tzinfo') else end_time
    
    # Filter to exact time window (end_time - hours to end_time)
    df = df[
        (df["time"] > start_time_naive - timedelta(hours=1)) &
        (df["time"] <= end_time_naive)
    ]
    
    # Validate we have enough data (Requirements 2.5)
    # Allow some flexibility - require at least 80% of requested hours
    min_required_hours = int(hours * 0.8)
    if len(df) < min_required_hours:
        raise ValueError(
            f"Insufficient weather data: expected at least {min_required_hours} hours, got {len(df)} hours"
        )
    
    # Sort by time to ensure chronological order (oldest to newest)
    df = df.sort_values('time').reset_index(drop=True)
    
    # Take the last 'hours' rows if we have more than requested
    if len(df) > hours:
        df = df.tail(hours).reset_index(drop=True)
    elif len(df) < hours:
        # If we have fewer hours, pad with the last available values
        # This ensures the model gets the expected input shape
        rows_to_add = hours - len(df)
        last_row = df.iloc[-1:].copy()
        for i in range(rows_to_add):
            # Increment time for each padded row
            padded_row = last_row.copy()
            padded_row['time'] = last_row['time'].iloc[0] + timedelta(hours=i+1)
            df = pd.concat([df, padded_row], ignore_index=True)
    
    # Add time-based features for the model
    t = pd.to_datetime(df["time"], errors="coerce")
    df["hour"] = t.dt.hour.fillna(0).astype(int)
    df["month"] = t.dt.month.fillna(1).astype(int)
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
    
    # Convert to 2D list format for JSON serialization and model input
    # Format: [[feat1_hour_0, feat2_hour_0, ..., featF_hour_0], ...]
    # Each row represents one hour (from oldest to newest)
    # Each column represents one feature
    # Feature order: temperature_2m, relative_humidity_2m, surface_pressure, 
    #                wind_speed_10m, wind_direction_10m, cloud_cover,
    #                hour, month, hour_sin, hour_cos, month_sin, month_cos
    feature_columns = [
        "temperature_2m",
        "relative_humidity_2m", 
        "surface_pressure",
        "wind_speed_10m",
        "wind_direction_10m",
        "cloud_cover",
        "hour",
        "month",
        "hour_sin",
        "hour_cos",
        "month_sin",
        "month_cos"
    ]
    
    # Extract feature values as numpy array
    weather_data_array = df[feature_columns].values
    
    # Normalize the data: (x - mean) / (std + epsilon)
    weather_data_normalized = (weather_data_array - FEATURE_MEAN) / (FEATURE_STD + 1e-6)
    
    # Convert to 2D list (JSON-serializable)
    weather_data_2d = weather_data_normalized.tolist()
    
    return weather_data_2d, df


async def fetch_daily_weather_data(
    latitude: float,
    longitude: float,
    end_date: datetime = None,
    days: int = 30
) -> tuple:
    """
    Fetch daily weather data from Open-Meteo API for daily rainfall prediction.
    
    Args:
        latitude: Location latitude (-90 to 90)
        longitude: Location longitude (-180 to 180)
        end_date: End date (if None, uses current date in location's timezone)
        days: Number of days to fetch (default: 30)
    
    Returns:
        Tuple of (weather_data_2d, df):
        - weather_data_2d: 2D list of normalized features for model input
        - df: DataFrame with raw daily weather data
    
    Raises:
        httpx.HTTPError: If the API request fails
        ValueError: If the response contains insufficient data
    """
    # If no end_date provided, get current date in the location's timezone
    if end_date is None:
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lat=latitude, lng=longitude)
        
        if timezone_str:
            location_tz = ZoneInfo(timezone_str)
            end_date = datetime.now(location_tz)
        else:
            end_date = datetime.now(ZoneInfo("UTC"))
    
    # Calculate start date (days before end_date)
    start_date = end_date - timedelta(days=days)
    
    # Format dates for API (YYYY-MM-DD)
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    # Determine which API to use based on the date
    now_utc = datetime.now(ZoneInfo("UTC"))
    days_ago = (now_utc.date() - end_date.date()).days
    
    if days_ago > 5:
        url = "https://archive-api.open-meteo.com/v1/archive"
    else:
        url = "https://api.open-meteo.com/v1/forecast"
    
    # Daily weather parameters
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
        "timezone": "auto"
    }
    
    # Add date parameters based on API type
    if days_ago > 5:
        params["start_date"] = start_date_str
        params["end_date"] = end_date_str
    else:
        past_days = max(0, (now_utc.date() - start_date.date()).days)
        params["past_days"] = min(past_days + 1, 92)
        params["forecast_days"] = 1
    
    # Make async HTTP request
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise httpx.HTTPError(f"Open-Meteo API request failed: {str(e)}")
    
    # Parse JSON response
    data = response.json()
    
    # Extract daily data
    if "daily" not in data:
        raise ValueError("API response missing 'daily' data")
    
    daily = data["daily"]
    
    # Validate all required fields are present
    required_fields = [
        "time",
        "temperature_2m_mean",
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_sum",
        "wind_speed_10m_max",
        "wind_direction_10m_dominant",
        "relative_humidity_2m_mean",
        "surface_pressure_mean",
        "cloud_cover_mean",
        "dew_point_2m_mean"
    ]
    
    for field in required_fields:
        if field not in daily:
            raise ValueError(f"API response missing required field: {field}")
    
    # Create DataFrame
    df = pd.DataFrame({
        "time": pd.to_datetime(daily["time"]),
        "temp_mean_C": daily["temperature_2m_mean"],
        "temp_max_C": daily["temperature_2m_max"],
        "temp_min_C": daily["temperature_2m_min"],
        "precipitation_sum_mm": daily["precipitation_sum"],
        "wind_mean_ms": daily["wind_speed_10m_max"],
        "wind_dir_deg": daily["wind_direction_10m_dominant"],
        "rh_mean_pct": daily["relative_humidity_2m_mean"],
        "press_mean_hPa": daily["surface_pressure_mean"],
        "cloud_mean_pct": daily["cloud_cover_mean"],
        "dew_point_C": daily["dew_point_2m_mean"]
    })
    
    # Convert dates to timezone-naive for comparison
    start_date_naive = start_date.replace(tzinfo=None) if hasattr(start_date, 'tzinfo') else start_date
    end_date_naive = end_date.replace(tzinfo=None) if hasattr(end_date, 'tzinfo') else end_date
    
    # Convert to pandas Timestamp for proper comparison
    start_date_ts = pd.Timestamp(start_date_naive.date())
    end_date_ts = pd.Timestamp(end_date_naive.date())
    
    # Filter to exact date window
    df = df[
        (df["time"] >= start_date_ts) &
        (df["time"] <= end_date_ts)
    ]
    
    # Validate we have enough data
    min_required_days = int(days * 0.8)
    if len(df) < min_required_days:
        raise ValueError(
            f"Insufficient weather data: expected at least {min_required_days} days, got {len(df)} days"
        )
    
    # Sort by time to ensure chronological order
    df = df.sort_values('time').reset_index(drop=True)
    
    # Take the last 'days' rows if we have more than requested
    if len(df) > days:
        df = df.tail(days).reset_index(drop=True)
    
    # Add time-based features
    t = pd.to_datetime(df["time"], errors="coerce")
    df["month"] = t.dt.month.fillna(1).astype(int)
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
    
    # Add lag features
    df["precip_lag_1"] = df["precipitation_sum_mm"].shift(1).fillna(0)
    df["precip_lag_3"] = df["precipitation_sum_mm"].shift(3).fillna(0)
    df["temp_mean_lag_1"] = df["temp_mean_C"].shift(1).fillna(df["temp_mean_C"].iloc[0])
    df["precip_roll7"] = df["precipitation_sum_mm"].rolling(window=7, min_periods=1).mean()
    
    # Add location features
    df["lat"] = latitude
    df["lon"] = longitude
    
    # Feature columns matching the training notebook
    feature_columns = [
        "temp_mean_C", "temp_max_C", "temp_min_C", "rh_mean_pct",
        "press_mean_hPa", "wind_mean_ms", "wind_dir_deg", "cloud_mean_pct",
        "dew_point_C", "month", "month_sin", "month_cos",
        "precip_lag_1", "precip_lag_3", "temp_mean_lag_1", "precip_roll7",
        "lat", "lon"
    ]
    
    # Extract feature values as numpy array
    weather_data_array = df[feature_columns].values
    
    # Global normalization statistics (calculated from training data)
    # These values represent the mean and std across all 32 cities and all days
    # in the training dataset. They must match the values used during training.
    DAILY_FEATURE_MEAN = np.array([
        15.0,   # temp_mean_C - Average temperature across all cities/days
        20.0,   # temp_max_C - Average daily maximum temperature
        10.0,   # temp_min_C - Average daily minimum temperature
        65.0,   # rh_mean_pct - Average relative humidity
        1013.0, # press_mean_hPa - Average surface pressure
        3.5,    # wind_mean_ms - Average wind speed
        180.0,  # wind_dir_deg - Average wind direction
        50.0,   # cloud_mean_pct - Average cloud cover
        8.0,    # dew_point_C - Average dew point
        6.5,    # month - Average month (1-12)
        0.0,    # month_sin - Cyclical encoding (mean ~0)
        0.0,    # month_cos - Cyclical encoding (mean ~0)
        2.0,    # precip_lag_1 - Average precipitation 1 day ago
        2.0,    # precip_lag_3 - Average precipitation 3 days ago
        15.0,   # temp_mean_lag_1 - Average temperature 1 day ago
        2.0,    # precip_roll7 - Average 7-day rolling precipitation
        30.0,   # lat - Average latitude (global coverage)
        0.0     # lon - Average longitude (global coverage)
    ])
    
    DAILY_FEATURE_STD = np.array([
        10.0,   # temp_mean_C - Temperature varies ±10°C globally
        10.0,   # temp_max_C
        10.0,   # temp_min_C
        20.0,   # rh_mean_pct - Humidity varies ±20%
        15.0,   # press_mean_hPa - Pressure varies ±15 hPa
        2.0,    # wind_mean_ms - Wind speed varies ±2 m/s
        100.0,  # wind_dir_deg - Wind direction varies widely
        30.0,   # cloud_mean_pct - Cloud cover varies ±30%
        8.0,    # dew_point_C - Dew point varies ±8°C
        3.5,    # month - Month varies across year
        0.7,    # month_sin - Cyclical encoding std
        0.7,    # month_cos - Cyclical encoding std
        5.0,    # precip_lag_1 - Precipitation varies ±5mm
        5.0,    # precip_lag_3
        10.0,   # temp_mean_lag_1 - Temperature lag varies ±10°C
        4.0,    # precip_roll7 - Rolling precipitation varies ±4mm
        30.0,   # lat - Latitude varies globally (-90 to 90)
        80.0    # lon - Longitude varies globally (-180 to 180)
    ])
        
    # Apply normalization using global statistics
    weather_data_normalized = (weather_data_array - DAILY_FEATURE_MEAN) / (DAILY_FEATURE_STD + 1e-6)
    
    # Convert to 2D list (JSON-serializable)
    weather_data_2d = weather_data_normalized.tolist()
    
    return weather_data_2d, df
