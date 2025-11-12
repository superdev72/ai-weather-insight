# 🌦️ AI-Powered Weather Insight Engine

## Overview

This prototype demonstrates an AI-powered workflow that integrates **two distinct data sources** (one structured, one unstructured), cleans and combines the data into a SQLite database, enriches it using OpenAI's GPT-4o-mini, and exposes results through a Streamlit dashboard.

## Architecture

### Data Flow

```
┌─────────────────┐     ┌──────────────────┐
│  Source 1: CSV  │     │ Source 2: API    │
│  (Structured)   │     │ (Structured +    │
│  City Metadata  │     │  Unstructured)   │
└────────┬────────┘     └────────┬─────────┘
         │                       │
         └───────────┬───────────┘
                     │
         ┌───────────▼───────────┐
         │  Clean & Combine      │
         │  Data Processing      │
         └───────────┬───────────┘
                     │
         ┌───────────▼───────────┐
         │  LLM Enrichment       │
         │  (GPT-4o-mini)        │
         └───────────┬───────────┘
                     │
         ┌───────────▼───────────┐
         │  SQLite Database      │
         │  (Persistent Storage) │
         └───────────┬───────────┘
                     │
         ┌───────────▼───────────┐
         │  Streamlit Dashboard  │
         │  (User Interface)      │
         └───────────────────────┘
```

### Components

1. **Data Sources**

   - **Source 1 (Structured)**: CSV file (`data/cities_metadata.csv`) containing city metadata (country, population, timezone, coordinates)
   - **Source 2 (Structured + Unstructured)**: OpenWeatherMap API providing structured metrics (temperature, humidity, wind speed) and unstructured text descriptions

2. **Data Processing**

   - Data cleaning: Normalizes city names, handles missing values, rounds numeric values
   - Data combination: Merges metadata from CSV with weather data from API
   - Validation: Ensures data integrity before enrichment

3. **LLM Enrichment**

   - Uses OpenAI GPT-4o-mini to classify unstructured weather descriptions
   - Categories: Clear, Cloudy, Rainy, Stormy, Snowy, Extreme
   - Includes validation to ensure output matches expected categories

4. **Data Persistence**

   - SQLite database (`weather_insights.db`) stores all processed records
   - Enables historical analysis and trend tracking
   - Unique constraint on (city, timestamp) prevents duplicates

5. **User Interface**
   - Streamlit dashboard with two tabs:
     - **Run Workflow**: Execute the full pipeline for new cities
     - **View History**: Browse and analyze historical data

## Design Decisions

### Why Two Separate Data Sources?

The requirement explicitly asks for "at least two sources (one structured, one unstructured)." While OpenWeatherMap provides both, using a separate CSV file for city metadata demonstrates:

- **Separation of concerns**: Static reference data vs. dynamic API data
- **Real-world scenarios**: Most production systems integrate multiple data sources
- **Data integration skills**: Shows ability to combine heterogeneous data

### Why SQLite?

- **Simplicity**: No external dependencies, perfect for prototypes
- **Persistence**: Meets the requirement for "simple database or table"
- **Portability**: Single file, easy to share and version control
- **Production path**: Can easily migrate to PostgreSQL/MySQL when scaling

### Why GPT-4o-mini?

- **Cost-effective**: Lower cost than GPT-4 for classification tasks
- **Fast**: Quick response times for real-time workflows
- **Sufficient**: Classification tasks don't require the full power of GPT-4
- **Scalable**: Lower token costs enable processing many records

### Workflow Orchestration

The workflow is orchestrated using **pure Python functions** rather than external tools (n8n, LangChain) because:

- **Transparency**: Easy to understand and modify
- **No dependencies**: Reduces setup complexity
- **Demonstrates skills**: Shows ability to design clean, maintainable workflows
- **Production-ready**: Can easily be refactored into Airflow/Dagster if needed

## Features

- ✅ Pulls data from **two sources** (CSV + API)
- ✅ Cleans and combines data into SQLite database
- ✅ Uses LLM (GPT-4o-mini) to enrich/classify data
- ✅ Orchestrates workflow with Python functions
- ✅ Exposes results through Streamlit dashboard
- ✅ Historical data viewing and analysis
- ✅ Error handling and validation

## Tech Stack

- **Language**: Python 3.11+
- **Framework**: Streamlit (dashboard)
- **Database**: SQLite (data persistence)
- **APIs**:
  - OpenWeatherMap API (weather data)
  - OpenAI API (LLM enrichment)
- **Libraries**: pandas, requests, python-dotenv

## Setup

1. **Clone this repo:**

   ```bash
   git clone https://github.com/yourname/ai-weather-insight.git
   cd ai-weather-insight
   ```

2. **Create virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file:**

   ```bash
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_MODEL=gpt-4o-mini
   OPENWEATHER_API_KEY=your_openweather_api_key
   ```

5. **Run the application:**

   ```bash
   streamlit run app.py
   ```

   The dashboard will open in your browser at `http://localhost:8501`

## Usage

1. **Run Workflow Tab:**

   - Enter city names (comma-separated)
   - Click "Run Workflow"
   - View results with AI-enriched categories
   - Data is automatically saved to database

2. **View History Tab:**
   - Browse historical records
   - Adjust the slider to control number of records
   - View category distribution chart

## How to Scale This

### Short-term (1-3 months)

1. **Add Caching**

   - Cache LLM responses for identical weather descriptions
   - Reduce API costs and improve response times

2. **Batch Processing**

   - Process multiple cities in parallel using `concurrent.futures`
   - Add rate limiting to respect API quotas

3. **Enhanced Error Handling**
   - Retry logic with exponential backoff
   - Dead letter queue for failed records
   - Comprehensive logging

### Medium-term (3-6 months)

1. **Database Migration**

   - Move from SQLite to PostgreSQL for concurrent access
   - Add indexes for common queries
   - Implement connection pooling

2. **Workflow Orchestration**

   - Migrate to Airflow or Dagster for production workflows
   - Add scheduling (e.g., daily weather updates)
   - Implement data quality checks

3. **API Layer**
   - Expose REST API using FastAPI
   - Add authentication and rate limiting
   - Enable programmatic access

### Long-term (6+ months)

1. **Real-time Processing**

   - Use Kafka/Redis for streaming data
   - Implement event-driven architecture
   - Add WebSocket support for live updates

2. **Advanced Analytics**

   - Time-series analysis for weather trends
   - Predictive models for weather forecasting
   - Anomaly detection

3. **Multi-region Deployment**

   - Containerize with Docker
   - Deploy on Kubernetes
   - Add monitoring (Prometheus, Grafana)
   - Implement CI/CD pipelines

4. **Cost Optimization**
   - Fine-tune smaller models for classification
   - Implement model caching and batching
   - Use vector databases for semantic search

## Project Structure

```
ai-weather-insight/
├── app.py                 # Main application and workflow
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── setup.cfg             # Code formatting config
├── data/
│   └── cities_metadata.csv  # Structured city data (Source 1)
└── weather_insights.db    # SQLite database (generated)
```

## Notes

- The database file (`weather_insights.db`) is created automatically on first run
- City metadata CSV should be updated if you want to add more cities
- API keys are required for both OpenAI and OpenWeatherMap
- Free tier OpenWeatherMap API has rate limits (60 calls/minute)

## License

MIT
