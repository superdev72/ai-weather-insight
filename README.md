# 🌦️ AI-Powered Weather Insight Engine

## Overview

This prototype demonstrates an AI-powered workflow integrating structured (OpenWeatherMap API) and unstructured (textual weather description) data.  
The data is enriched using OpenAI's GPT-4o-mini to classify weather into human-friendly categories.

## Features

- Fetches real-time weather data
- Uses LLM to interpret weather descriptions
- Simple Streamlit dashboard to visualize results

## Tech Stack

- Python
- Streamlit
- OpenWeatherMap API
- OpenAI GPT-4o-mini
- dotenv, requests, pandas

## Setup

1. Clone this repo:

   ```bash
   git clone https://github.com/yourname/ai-weather-insight.git
   cd ai-weather-insight
   ```

2. Create .env file:

   ```bash
   OPENAI_API_KEY=your_key
   OPENAI_MODEL=gpt-4o-mini
   OPENWEATHER_API_KEY=your_key
   ```

3. Install dependencies:
   ```python
   pip install -r requirements.txt
   ```
4. Run:
   ```python
   streamlit run app.py
   ```
