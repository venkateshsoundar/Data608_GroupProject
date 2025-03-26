# Data608 Project

This repository contains several scripts designed to fetch, process, and store weather data from an API, as well as interact with AWS services such as S3, DynamoDB, and Lambda. These scripts are structured to automate the data pipeline and facilitate easy access to historical and daily weather data.

### Note:
- **Primary Data Source**: All data is primarily stored in **DynamoDB** for efficient and scalable retrieval.
- **Backup Data Source**: The scripts `api_daily_S3.py` and `api_historical_S3.ipynb` are designed to fetch and store data in **S3** as a backup.

## Scripts Overview

### 1. **`api_daily_S3.py`** 
- **Purpose**: This Python script is designed to run daily and fetch the latest weather data from the API.
- **How it works**: The script pulls data for the day before the current date, as the API typically takes some time to update. Once the data is fetched, it is stored in an **S3 bucket** for backup and further processing. The primary data source will always be DynamoDB.

### 2. **`api_historical_S3.ipynb`** 
- **Purpose**: This Jupyter Notebook fetches historical weather data from January 2024 to March 2025.
- **How it works**: The data is retrieved from the API and saved as a **CSV file in an S3 bucket** for backup purposes. For primary storage, DynamoDB is used.

### 3. **`db_lambda_fetchHisData.py`**
- **Purpose**: This Lambda function fetches weather data from the API and stores it in DynamoDB.
- **How it works**: The script preprocesses, cleans, and transforms the data before storing it in a **DynamoDB table** for further use.

### 4. **`db_lambda_automate.py`**
- **Purpose**: This Lambda function automates the fetching of new weather data from the API via an EventBridge scheduler.
- **How it works**: It regularly fetches new data, performs transformations and cleaning, and appends the updated data to the existing records in **DynamoDB**.

### 5. **`ec2_dbConnect.py`**
- **Purpose**: This Python script is designed to fetch paginated data from DynamoDB to test connectivity between an EC2 instance and the database.
- **How it works**: The script checks whether data retrieval from DynamoDB works correctly on the EC2 instance, which will eventually connect to a Streamlit dashboard for data visualizations.

## Requirements
- Python_version >= "3.9"
- AWS SDK for Python (`boto3`)
- Streamlit (for dashboard integration)
- Jupyter Notebook (for data exploration)
- Required libraries: `pandas`, `requests`, `boto3`, `json`, etc.
