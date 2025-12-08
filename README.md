# Rainfall Prediction Chat Application

An AI-powered weather prediction chatbot that uses natural language processing to understand queries about rainfall and weather conditions for any city in the world.

## Features

- **Natural Language Queries**: Ask questions naturally like:
  - "Will it rain in Tokyo tomorrow?"
  - "What's the weather in Paris?"
  - "Show me yesterday's rainfall in London"
  - "New York weather next hour"

- **Time-Based Predictions**: Query weather for:
  - Current conditions (now)
  - Future predictions (next hour, tomorrow, in 2 days)
  - Historical data (yesterday, 2 days ago)

- **Location Intelligence**: 
  - Automatically extracts city names from queries
  - Remembers your last queried location
  - Supports cities worldwide

- **ML-Powered Predictions with Automatic Model Selection**: 
  - **Hourly Model**: Transformer model for short-term rainfall predictions (< 18 hours)
  - **Daily Model**: Global transformer model for next-day rainfall predictions (≥ 18 hours)
  - **Smart Selection**: Automatically chooses the best model based on your query

## Architecture

### Backend (Python/FastAPI)
- **NLP Service**: Uses Google Gemini AI to parse natural language queries
- **Weather Service**: Fetches historical weather data from Open-Meteo API
- **Prediction Service**: PyTorch Transformer model for rainfall prediction
- **Location Service**: Extracts and geocodes city names

### Frontend (React/TypeScript)
- Modern chat interface with message history
- Real-time API integration
- Location context management
- Responsive design with Tailwind CSS

## Setup

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
```

5. Add your Gemini API key to `.env`:
```
GEMINI_API_KEY=your_api_key_here
```

Get your API key from: https://makersuite.google.com/app/apikey

6. Ensure model files are in the backend directory:
   - `checkpoint_best.pt` - Hourly prediction model
   - `daily_transformer_global.pt` - Daily prediction model (optional)

7. Start the server:
```bash
uvicorn main:app --reload
```

Backend will run on http://localhost:8000

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file (optional):
```bash
cp .env.example .env
```

4. Start development server:
```bash
npm run dev
```

Frontend will run on http://localhost:5173

## Usage Examples

Once both servers are running, open http://localhost:5173 and try these queries:

### Basic Queries
- "Tokyo" - Current weather in Tokyo
- "Will it rain in London?" - Rainfall prediction for London
- "Paris weather" - Weather conditions in Paris

### Time-Based Queries
- "Tokyo weather tomorrow" - 24-hour forecast
- "Will it rain in London next hour?" - 1-hour prediction
- "Paris rainfall yesterday" - Historical data from 24 hours ago
- "New York weather 2 days ago" - Historical data from 48 hours ago

### Location Changes
- "Change location to Berlin" - Switch to Berlin
- "Show me weather in Sydney" - Query Sydney weather

### Help & Info
- "help" - Get usage instructions
- "hello" - Greeting and introduction

## API Endpoints

### POST /api/chat
Main chat endpoint for hourly weather predictions.

**Request:**
```json
{
  "message": "Will it rain in Tokyo tomorrow?",
  "current_location": {
    "city": "Tokyo",
    "latitude": 35.6762,
    "longitude": 139.6503
  }
}
```

**Response:**
```json
{
  "response": "Weather prediction text...",
  "location": {
    "city": "Tokyo",
    "latitude": 35.6762,
    "longitude": 139.6503
  },
  "prediction": {
    "rain_mm": 2.5,
    "rain_log": 0.916,
    "chance_of_rain": 50.0
  }
}
```

### POST /api/chat/daily
Daily rainfall prediction endpoint using the global daily model.

**Request:**
```json
{
  "message": "Will it rain tomorrow in London?",
  "current_location": {
    "city": "London",
    "latitude": 51.5074,
    "longitude": -0.1278
  }
}
```

**Response:**
```json
{
  "response": "Daily prediction text...",
  "location": {
    "city": "London",
    "latitude": 51.5074,
    "longitude": -0.1278
  },
  "prediction": {
    "rain_mm": 5.2,
    "rain_log": 1.75,
    "chance_of_rain": 52.0
  }
}
```

### GET /health
Health check endpoint.

## Technology Stack

### Backend
- FastAPI - Web framework
- PyTorch - ML model inference
- Google Gemini AI - NLP parsing
- Open-Meteo API - Weather data
- httpx - Async HTTP client
- pandas/numpy - Data processing

### Frontend
- React 18 - UI framework
- TypeScript - Type safety
- Vite - Build tool
- Tailwind CSS - Styling
- React Query - Data fetching
- React Router - Navigation

## Model Details

### Hourly Prediction Model (`checkpoint_best.pt`)
Transformer-based architecture for short-term rainfall prediction:
- Input: 24 hours of weather features (temperature, humidity, pressure, wind, cloud cover)
- Output: Rainfall prediction (mm/h) and probability
- Features: 12 normalized features including cyclical time encodings

### Daily Prediction Model (`daily_transformer_global.pt`)
Global transformer model for next-day rainfall prediction:
- Input: 30 days of daily weather features from Open-Meteo API
- Output: Next day's rainfall prediction (mm/day) and probability
- Features: 18 features including temperature, humidity, pressure, wind, precipitation lags, and location
- Training: Trained on data from 32 cities worldwide for global coverage
- Data Source: Open-Meteo API daily weather data

## Troubleshooting

### Backend Issues
- **Model not loading**: Ensure `checkpoint_best.pt` is in the backend directory
- **API errors**: Check that GEMINI_API_KEY is set in `.env`
- **Weather data errors**: Some locations may not have historical data available

### Frontend Issues
- **Connection errors**: Ensure backend is running on port 8000
- **CORS errors**: Backend CORS is configured for localhost:5173, 3000, and 8080

## License

MIT
