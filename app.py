import os
import requests
import pandas as pd
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

# ========== Load environment variables ==========
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)


# ========== Step 1: Fetch structured + unstructured weather data ==========
def fetch_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    res = requests.get(url)
    if res.status_code != 200:
        st.error(f"Failed to fetch data for {city}")
        return None

    data = res.json()
    structured = {
        "city": city,
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "wind_speed": data["wind"]["speed"],
    }

    # This is unstructured (text description)
    unstructured = data["weather"][0]["description"]

    return structured, unstructured


# ========== Step 2: Use LLM to enrich data ==========
def classify_weather(text):
    prompt = f"Classify the following weather description as one of: Clear, Cloudy, Rainy, Stormy, Snowy, or Extreme.\nDescription: {text}\nAnswer:"
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
        )
        result = response.choices[0].message.content.strip()
        return result
    except Exception as e:
        st.error(f"OpenAI API error: {e}")
        return "Unknown"


# ========== Step 3: Orchestrate workflow ==========
def build_weather_table(cities):
    records = []
    for city in cities:
        data = fetch_weather(city)
        if not data:
            continue
        structured, text = data
        structured["description"] = text
        structured["ai_category"] = classify_weather(text)
        records.append(structured)
    return pd.DataFrame(records)


# ========== Step 4: Streamlit UI ==========
st.title("🌦️ AI-Powered Weather Insight Dashboard")
st.write(
    "This app fetches live weather data, uses GPT-4o-mini to classify the weather type, and displays results in real time."
)

cities_input = st.text_input(
    "Enter cities (comma separated):", "New York, London, Tokyo"
)
cities = [c.strip() for c in cities_input.split(",") if c.strip()]

if st.button("Run Workflow"):
    with st.spinner("Fetching and analyzing weather data..."):
        df = build_weather_table(cities)
        st.success("Done!")
        st.dataframe(df)
