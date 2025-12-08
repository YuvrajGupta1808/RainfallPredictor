"""
Test script to verify location extraction and weather service integration.
"""

import asyncio
import json
from utils.location_service import extract_location_with_gemini
from utils.weather_service import fetch_weather_data, fetch_daily_weather_data
from utils.prediction_service import load_model, load_daily_model, predict_rainfall, predict_daily_rainfall


async def test_full_pipeline(user_message: str, model):
    """Test the full pipeline: extract location -> fetch weather data -> predict."""
    
    print(f"User message: '{user_message}'")
    print("=" * 80)
    
    try:
        # Step 1: Extract location from message
        print("\n[1] Extracting location from message...")
        city, latitude, longitude = await extract_location_with_gemini(user_message)
        print(f"✓ Location extracted: {city}")
        print(f"  Coordinates: ({latitude}, {longitude})")
        
        # Step 2: Fetch weather data (automatically uses location's timezone)
        print(f"\n[2] Fetching weather data for {city}...")
        weather_data_2d, df = await fetch_weather_data(latitude, longitude)
        
        print(f"✓ Successfully fetched {len(df)} hours of weather data")
        print(f"  Time range: {df['time'].min()} to {df['time'].max()}")
        print(f"  Data shape: {len(weather_data_2d)} timesteps × {len(weather_data_2d[0])} features")
        
        # Step 3: Run prediction
        print(f"\n[3] Running rainfall prediction...")
        prediction = predict_rainfall(model, weather_data_2d)
        
        print(f"\n{'='*80}")
        print("PREDICTION RESULT:")
        print('='*80)
        print(f"  Rainfall:        {prediction['rain_mm']} mm/h")
        print(f"  Chance of rain:  {prediction['chance_of_rain']}%")
        print(f"  Log value:       {prediction['rain_log']}")
        
        # Interpretation
        if prediction['rain_mm'] < 0.1:
            status = "No rain expected"
        elif prediction['rain_mm'] < 1.0:
            status = "Light rain possible"
        elif prediction['rain_mm'] < 5.0:
            status = "Moderate rain expected"
        else:
            status = "Heavy rain expected"
        
        print(f"  Status:          {status}")
        print('='*80)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


async def test_daily_pipeline(user_message: str, model):
    """Test the daily prediction pipeline: extract location -> fetch daily data -> predict."""
    
    print(f"User message: '{user_message}'")
    print("=" * 80)
    
    try:
        # Step 1: Extract location from message
        print("\n[1] Extracting location from message...")
        city, latitude, longitude = await extract_location_with_gemini(user_message)
        print(f"✓ Location extracted: {city}")
        print(f"  Coordinates: ({latitude}, {longitude})")
        
        # Step 2: Fetch daily weather data (past 30 days)
        print(f"\n[2] Fetching daily weather data for {city}...")
        weather_data_2d, df = await fetch_daily_weather_data(latitude, longitude, days=30)
        
        print(f"✓ Successfully fetched {len(df)} days of weather data")
        print(f"  Time range: {df['time'].min()} to {df['time'].max()}")
        print(f"  Data shape: {len(weather_data_2d)} days × {len(weather_data_2d[0])} features")
        
        # Step 3: Run prediction
        print(f"\n[3] Running daily rainfall prediction...")
        prediction = predict_daily_rainfall(model, weather_data_2d)
        
        print(f"\n{'='*80}")
        print("DAILY PREDICTION RESULT:")
        print('='*80)
        print(f"  Daily Rainfall:  {prediction['rain_mm']} mm/day")
        print(f"  Chance of rain:  {prediction['chance_of_rain']}%")
        print(f"  Log value:       {prediction['rain_log']}")
        
        # Interpretation
        if prediction['rain_mm'] < 1.0:
            status = "No significant rain expected"
        elif prediction['rain_mm'] < 10.0:
            status = "Light rain possible"
        elif prediction['rain_mm'] < 30.0:
            status = "Moderate rain expected"
        else:
            status = "Heavy rain expected"
        
        print(f"  Status:          {status}")
        print('='*80)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run tests with different user messages."""
    
    print("\n" + "="*80)
    print("RAINFALL PREDICTION API TEST")
    print("="*80)
    
    # Load hourly model
    print("\nLoading hourly model from checkpoint_best.pt...")
    try:
        hourly_model = load_model("checkpoint_best.pt")
        print("✓ Hourly model loaded successfully\n")
    except Exception as e:
        print(f"⚠ Warning: Could not load hourly model: {e}\n")
        hourly_model = None
    
    # Load daily model
    print("Loading daily model from daily_transformer_global.pt...")
    try:
        daily_model = load_daily_model("daily_transformer_global.pt")
        print("✓ Daily model loaded successfully\n")
    except Exception as e:
        print(f"⚠ Warning: Could not load daily model: {e}\n")
        daily_model = None
    
    # Test hourly predictions
    if hourly_model:
        test_messages = [
            "Will it rain in Delhi next hour?",
            "What's the weather in Mumbai?",
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n{'=' * 80}")
            print(f"HOURLY TEST {i}/{len(test_messages)}")
            print(f"{'=' * 80}")
            await test_full_pipeline(message, hourly_model)
    
    # Test daily predictions
    if daily_model:
        daily_test_messages = [
            "Will it rain tomorrow in Tokyo?",
            "What's the weather forecast for London?",
        ]
        
        for i, message in enumerate(daily_test_messages, 1):
            print(f"\n{'=' * 80}")
            print(f"DAILY TEST {i}/{len(daily_test_messages)}")
            print(f"{'=' * 80}")
            await test_daily_pipeline(message, daily_model)
    
    print(f"\n{'=' * 80}")
    print("ALL TESTS COMPLETE")
    print('='*80 + "\n")
        


if __name__ == "__main__":
    asyncio.run(main())
