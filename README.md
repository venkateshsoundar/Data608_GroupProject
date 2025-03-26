# Data608

1. api_daily_S3.py:
   
- This script is designed to run daily to fetch the latest weather data from the API. The data pulled is for two days prior because the API typically takes some time to update. Once the data is fetched, it is stored in an S3 bucket for easy access and further processing.

2. api_historical_S3.ipynb:
   
- This Jupyter notebook is used to fetch historical weather data from January 2024 to March 2025. The data is pulled from the API, and then the DataFrame is saved as a CSV file in an S3 bucket.

3. api_historical_RDS.ipynb:

- This notebook represents an attempt to store the historical weather data in an RDS (Relational Database Service) instead of an S3 bucket. The code involves fetching the same historical data and attempting to push it into an RDS database (likely using psycopg2 for PostgreSQL or another database client).
