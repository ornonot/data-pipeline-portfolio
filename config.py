# config.py - 環境設定・定数定義ファイル

# GCP / BigQuery 関連設定
KEY_PATH = "gcp_key.json"
PROJECT_ID = "de-portfolio-2026"
DATASET_ID = "raw_data"
TABLE_NAME = "weather_forecast"
TABLE_ID = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_NAME}"

# データソース（気象庁 API）設定
API_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/130000.json"