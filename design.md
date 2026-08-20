# データパイプライン仕様書 (design.md)

**1. システム概要**
気象庁のオープンデータAPIから日々の天気予報データを取得し、Pandasで加工した上で BigQuery の `raw_data` データセットに格納するETLパイプライン。

**2. データソース定義**
* **ソース名:** 気象庁 天気予報API
* **URL:** https://www.jma.go.jp/bosai/forecast/data/forecast/130000.json
* **データフォーマット:** JSON
* **認証要否:** 不要

**3. 取得データ項目 (Extract / Transform)**
* `publishingOffice`: 発表機関（例: 気象庁）
* `reportDatetime`: 予報発表日時
* `area.name`: 予報対象地域名（例: 東京都）
* `weather`: 天気予報テキスト（例: 晴れ 時々 くもり）

**4. BigQuery テーブル定義 (Load)**
* **データセットID:** `raw_data`
* **テーブル名:** `weather_forecast`
* **書き込み方式:** `WRITE_TRUNCATE` (全件上書きロード)

| カラム名 (Column) | データ型 (Type) | 備考 (Description) |
|---|---|---|
| publishing_office | STRING | 発表機関名 |
| report_datetime | TIMESTAMP | 予報発表日時 |
| area_name | STRING | 対象地域名 |
| weather_text | STRING | 天気詳細 |
| loaded_at | TIMESTAMP | パイプライン実行日時 |