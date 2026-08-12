import logging
import requests
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

# 1. ログの設定（時刻・ログレベル・メッセージを表示）
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# 設定値
KEY_PATH = "gcp_key.json"
PROJECT_ID = "de-portfolio-2026"
DATASET_ID = "raw_data"
TABLE_NAME = "japan_postcode"
TABLE_ID = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_NAME}"

# APIのURL（※テスト時にここを変更します）
# 存在しない不正なURLに変更
# API_URL = "https://zipcloud.ibsnet.co.jp/api/invalid_endpoint_test"
API_URL = "https://zipcloud.ibsnet.co.jp/api/search?zipcode=1000005"

def run_etl():
    logging.info("--- ETL処理を開始します ---")
    
    try:
        # 2. Extract (データ取得)
        logging.info(f"APIからデータを取得中: {API_URL}")
        response = requests.get(API_URL, timeout=10)
        
        # HTTPステータスコードが 4xx/5xx の場合に例外を発生させる
        response.raise_for_status()
        
        data = response.json()
        results = data.get("results")
        
        if not results:
            raise ValueError("APIレスポンス内に該当するデータが含まれていません。")

        # 3. Transform (データ加工)
        logging.info("データを Pandas DataFrame に変換・加工中...")
        df = pd.json_normalize(results)

        # 4. Load (BigQueryへロード)
        logging.info("BigQuery 認証情報を読み込み中...")
        credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
        client = bigquery.Client(credentials=credentials, project=PROJECT_ID)

        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_TRUNCATE"
        )

        logging.info(f"BigQuery ({TABLE_ID}) へのロードを開始...")
        job = client.load_table_from_dataframe(df, TABLE_ID, job_config=job_config)
        job.result()  # 処理完了まで待機

        logging.info(f"✅ ETL処理が正常に完了しました！（挿入件数: {job.output_rows} 行）")

    # --- 例外処理（Catch） ---
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ [通信/APIエラー] リクエストに失敗しました: {e}")
    except ValueError as e:
        logging.error(f"❌ [データエラー] データ形式に問題があります: {e}")
    except Exception as e:
        logging.error(f"❌ [予期せぬエラー] 処理を中断しました: {e}")

if __name__ == "__main__":
    run_etl()