# Premier League Performance Analytics

An end-to-end data engineering and analytics project analyzing team performance throughout the **2025/26 English Premier League season**. The project automates data extraction, transformation, and storage in PostgreSQL, using SQL and an interactive dashboard to explore team statistics and performance trends.

## Tech Stack
- **Python (Pandas, Requests):** Data extraction and transformation
- **PostgreSQL & SQL:** Data storage and analysis
- **Streamlit & Plotly:** Interactive dashboard and visualizations
- **Docker:** Containerized deployment
- **GitHub Actions:** Automated data pipeline

## Key Features
- ETL pipeline for Premier League match data
- Relational database with SQL-based analytics
- Interactive team comparisons and league standings
- Performance tracking, including goals, points, match results, and recent form
- Automated data refresh and reproducible deployment

## Getting Started

Clone the repository and launch the application using Docker:

```bash
docker compose up --build
```

Once running, access the dashboard at **http://localhost:8501**.

## Data Source

Historical Premier League match data provided by [Football-Data.co.uk](https://www.football-data.co.uk/).
