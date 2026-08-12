import os
import requests
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

# 1. GCP サービスアカウントによる認証設定
KEY_PATH = "gcp_key.json"
PROJECT_ID = "de-portfolio-2026"
DATASET_ID = "raw_data"
TABLE_NAME = "japan_postcode"
TABLE_ID = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_NAME}"

credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
client = bigquery.Client(credentials=credentials, project=PROJECT_ID)

# 2. APIデータ取得 ＆ Pandas DataFrame に変換
url = "https://zipcloud.ibsnet.co.jp/api/search?zipcode=1000005"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    results = data.get("results", [])
    df = pd.json_normalize(results)
    print("--- 送信するデータ ---")
    print(df)
else:
    raise Exception(f"APIリクエスト失敗: {response.status_code}")

# 3. BigQuery へのロード設定（既存テーブルがある場合は全件上書き）
job_config = bigquery.LoadJobConfig(
    write_disposition="WRITE_TRUNCATE"  # 計画通りの全置き換え（上書き）設定
)

# 4. DataFrame を BigQuery へロード実行
print("\nBigQuery へデータを送信中...")
job = client.load_table_from_dataframe(df, TABLE_ID, job_config=job_config)
job.result()  # ロード完了まで待機

print(f"✅ 成功: {job.output_rows} 行のデータを {TABLE_ID} に書き込みました！")