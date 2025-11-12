import os
import sqlite3
import requests
import pandas as pd
import streamlit as st
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

# ========== Load environment variables ==========
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not OPENAI_API_KEY or not OPENWEATHER_API_KEY:
    st.error(
        "Missing API keys. Please set OPENAI_API_KEY and "
        "OPENWEATHER_API_KEY in .env file"
    )
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

# Database setup
DB_PATH = "weather_insights.db"


# ========== Database Functions ==========
def init_database():
    """Initialize SQLite database with weather insights table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS weather_insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            country TEXT,
            population INTEGER,
            temperature REAL,
            humidity REAL,
            wind_speed REAL,
            description TEXT,
            ai_category TEXT,
            timestamp TEXT,
            UNIQUE(city, timestamp)
        )
    """
    )
    conn.commit()
    conn.close()


def save_to_database(df):
    """Save enriched data to SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("weather_insights", conn, if_exists="append", index=False)
    conn.close()


def load_from_database(limit=100):
    """Load historical data from database"""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        f"SELECT * FROM weather_insights ORDER BY timestamp DESC LIMIT {limit}", conn
    )
    conn.close()
    return df


# ========== Step 1: Fetch data from two sources ==========
def fetch_city_metadata(city_name):
    """
    Source 1: Structured data from CSV file
    Returns city metadata (country, population, timezone, coordinates)
    """
    csv_path = Path(__file__).parent / "data" / "cities_metadata.csv"
    try:
        df = pd.read_csv(csv_path)
        city_data = df[df["city"].str.lower() == city_name.lower()]
        if not city_data.empty:
            return city_data.iloc[0].to_dict()
        return None
    except Exception as e:
        st.warning(f"Could not load city metadata for {city_name}: {e}")
        return None


def fetch_weather_data(city_name):
    """
    Source 2: Unstructured + structured data from OpenWeatherMap API
    Returns structured weather metrics and unstructured text description
    """
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    url = f"{base_url}?q={city_name}&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code != 200:
            st.warning(f"Failed to fetch weather for {city_name}: {res.status_code}")
            return None

        data = res.json()
        structured = {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
        }
        # Unstructured text description
        unstructured = data["weather"][0]["description"]

        return structured, unstructured
    except Exception as e:
        st.warning(f"Error fetching weather for {city_name}: {e}")
        return None


# ========== Step 2: Clean and combine data ==========
def clean_and_combine_data(city_name, metadata, weather_data):
    """Clean and combine data from both sources"""
    if not weather_data:
        return None

    structured_weather, unstructured_text = weather_data

    # Combine structured data from both sources
    population = None
    if metadata and pd.notna(metadata.get("population")):
        population = int(metadata.get("population"))

    combined = {
        "city": city_name,
        "country": metadata.get("country") if metadata else None,
        "population": population,
        "temperature": round(structured_weather["temperature"], 2),
        "humidity": round(structured_weather["humidity"], 2),
        "wind_speed": round(structured_weather["wind_speed"], 2),
        "description": unstructured_text,
        "timestamp": datetime.now().isoformat(),
    }

    return combined


# ========== Step 3: Use LLM to enrich data ==========
def classify_weather(text):
    """Use LLM to classify weather description into categories"""
    prompt = (
        f"Classify the following weather description into one of these "
        f"categories: Clear, Cloudy, Rainy, Stormy, Snowy, or Extreme.\n\n"
        f"Weather description: {text}\n\nReturn only the category name:"
    )

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0.3,
        )
        result = response.choices[0].message.content.strip()
        # Validate result is one of expected categories
        valid_categories = ["Clear", "Cloudy", "Rainy", "Stormy", "Snowy", "Extreme"]
        if result in valid_categories:
            return result
        return "Unknown"
    except Exception as e:
        st.error(f"OpenAI API error: {e}")
        return "Unknown"


# ========== Step 4: Orchestrate workflow ==========
def build_weather_table(cities):
    """Main workflow: fetch, clean, enrich, and persist data"""
    records = []

    for city in cities:
        # Fetch from two sources
        metadata = fetch_city_metadata(city)  # Source 1: CSV
        weather_data = fetch_weather_data(city)  # Source 2: API

        if not weather_data:
            continue

        # Clean and combine
        combined = clean_and_combine_data(city, metadata, weather_data)
        if not combined:
            continue

        # Enrich with LLM
        combined["ai_category"] = classify_weather(combined["description"])

        records.append(combined)

    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)

    # Save to database
    try:
        save_to_database(df)
        st.success(f"Saved {len(df)} records to database")
    except Exception as e:
        st.warning(f"Could not save to database: {e}")

    return df


# ========== Step 5: Streamlit UI ==========
# Initialize database
init_database()

st.title("🌦️ AI-Powered Weather Insight Dashboard")
st.write(
    """
    This prototype demonstrates an AI-powered workflow that:
    - Pulls data from **two sources**: CSV (structured city metadata)
      and OpenWeatherMap API (structured + unstructured)
    - Cleans and combines the data
    - Uses GPT-4o-mini to classify weather descriptions
    - Persists results to SQLite database
    - Displays results in this dashboard
    """
)

tab1, tab2 = st.tabs(["Run Workflow", "View History"])

with tab1:
    # Show available cities from CSV
    csv_path = Path(__file__).parent / "data" / "cities_metadata.csv"
    try:
        csv_df = pd.read_csv(csv_path)
        available_cities = csv_df["city"].tolist()
        with st.expander("📋 Available cities in CSV (click to see)"):
            st.write(
                f"**{len(available_cities)} cities** with metadata available: "
                f"{', '.join(available_cities)}"
            )
            st.caption(
                "These cities will have country and population data from the CSV file."
            )
    except Exception:
        st.warning("Could not load cities_metadata.csv")

    cities_input = st.text_input(
        "Enter cities (comma separated):", "New York, London, Tokyo"
    )
    cities = [c.strip() for c in cities_input.split(",") if c.strip()]

    if st.button("Run Workflow"):
        if not cities:
            st.error("Please enter at least one city")
        else:
            with st.spinner("Fetching and analyzing weather data..."):
                df = build_weather_table(cities)
                if not df.empty:
                    st.success("Workflow completed!")

                    # Show data source information
                    st.info(
                        "📊 **Data Sources:** "
                        "Weather data from OpenWeatherMap API | "
                        "City metadata (country, population) from CSV file"
                    )

                    # Highlight which cities have CSV metadata
                    cities_with_metadata = df[df["country"].notna()]["city"].tolist()
                    cities_without_metadata = df[df["country"].isna()]["city"].tolist()

                    if cities_with_metadata:
                        cities_list = ", ".join(cities_with_metadata)
                        st.success(f"✅ Found CSV metadata for: {cities_list}")
                    if cities_without_metadata:
                        cities_list = ", ".join(cities_without_metadata)
                        st.warning(
                            f"⚠️ No CSV metadata found for: {cities_list} "
                            f"(check data/cities_metadata.csv)"
                        )

                    st.dataframe(df, use_container_width=True)

                    # Show summary statistics
                    st.subheader("Summary Statistics")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Cities Processed", len(df))
                    with col2:
                        avg_temp = f"{df['temperature'].mean():.1f}°C"
                        st.metric("Avg Temperature", avg_temp)
                    with col3:
                        st.metric("Categories", df["ai_category"].nunique())
                else:
                    st.error("No data retrieved. Please check city names and API keys.")

with tab2:
    st.subheader("Historical Data")
    limit = st.slider("Number of records to display", 10, 200, 50)
    historical_df = load_from_database(limit=limit)

    if not historical_df.empty:
        st.dataframe(historical_df, use_container_width=True)

        # Show category distribution
        if "ai_category" in historical_df.columns:
            st.subheader("Weather Category Distribution")
            category_counts = historical_df["ai_category"].value_counts()
            st.bar_chart(category_counts)
    else:
        st.info("No historical data yet. Run the workflow to generate data.")
