import logging
from datetime import datetime, timezone
import requests
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

# 設定ファイルの読み込み
import config

# 1. ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)


def fetch_data(url: str) -> list:
    """Extract: APIから生のJSONデータを取得する関数"""
    logging.info(f"[Extract] APIからデータ取得中: {url}")
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def transform_data(raw_data: list) -> pd.DataFrame:
    """Transform: 生データを分析用の Pandas DataFrame に整形・型変換する関数"""
    logging.info("[Transform] データ加工および DataFrame 変換中...")
    if not raw_data:
        raise ValueError("取得データが空です。")

    tokyo_data = raw_data[0]
    publishing_office = tokyo_data.get("publishingOffice", "気象庁")
    report_datetime_str = tokyo_data.get("reportDatetime", "")

    time_series = tokyo_data.get("timeSeries", [])
    if not time_series:
        raise ValueError("APIレスポンス内に timeSeries データが見つかりません。")

    weather_series = time_series[0]
    areas = weather_series.get("areas", [])

    records = []
    for area in areas:
        area_name = area.get("area", {}).get("name", "")
        weathers = area.get("weathers", [])
        weather_text = weathers[0] if weathers else "不明"

        records.append({
            "publishing_office": str(publishing_office),
            "report_datetime": pd.to_datetime(report_datetime_str),
            "area_name": str(area_name),
            "weather_text": str(weather_text),
            "loaded_at": datetime.now(timezone.utc)
        })

    df = pd.DataFrame(records)

    # 型の明確化
    df["publishing_office"] = df["publishing_office"].astype(str)
    df["area_name"] = df["area_name"].astype(str)
    df["weather_text"] = df["weather_text"].astype(str)

    return df


def load_to_bigquery(df: pd.DataFrame, table_id: str, key_path: str, project_id: str) -> int:
    """Load: DataFrame を BigQuery へ書き込む関数 (戻り値: 挿入行数)"""
    logging.info(f"[Load] BigQuery ({table_id}) への書き込み準備中...")
    credentials = service_account.Credentials.from_service_account_file(key_path)
    client = bigquery.Client(credentials=credentials, project=project_id)

    job_config = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField("publishing_office", "STRING"),
            bigquery.SchemaField("report_datetime", "TIMESTAMP"),
            bigquery.SchemaField("area_name", "STRING"),
            bigquery.SchemaField("weather_text", "STRING"),
            bigquery.SchemaField("loaded_at", "TIMESTAMP"),
        ],
        write_disposition="WRITE_TRUNCATE"
    )

    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()  # ロード終了待機
    return job.output_rows


def main():
    """メイン実行エントリポイント"""
    logging.info("=== ETL パイプライン処理開始 ===")
    try:
        # 1. Fetch (config.API_URL を参照)
        raw_data = fetch_data(config.API_URL)
        
        # 2. Transform
        df = transform_data(raw_data)
        logging.info(f"加工後データ:\n{df}")

        # 3. Load (config の定数を参照)
        inserted_rows = load_to_bigquery(
            df=df,
            table_id=config.TABLE_ID,
            key_path=config.KEY_PATH,
            project_id=config.PROJECT_ID
        )
        logging.info(f"✅ ETL処理完了: {inserted_rows} 行のデータをロードしました。")

    except Exception as e:
        logging.error(f"❌ パイプライン実行中にエラーが発生しました: {e}")


if __name__ == "__main__":
    main()