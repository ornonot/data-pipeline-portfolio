# Data Pipeline Portfolio (dbt + BigQuery + GitHub Actions)

本リポジトリは、Google BigQuery と dbt を用いたデータパイプライン構築、および GitHub Actions による CI/CD 自動化環境のポートフォリオです。

---

## 🏗 システム構成図 (Architecture)
```mermaid
flowchart TD
    subgraph GCP["Google Cloud Platform"]
        BQ[("BigQuery<br>(de-portfolio-2026)")]
    end

    subgraph CI_CD["GitHub Actions (CI/CD)"]
        GA["dbt CI/CD Pipeline<br>(.github/workflows/pipeline.yml)"]
        ENV["Environment Setup<br>(Python 3.10 / dbt-bigquery)"]
        RUN["dbt Execution<br>(dbt run --full-refresh / dbt test)"]
    end

    subgraph Notification["Slack WorkSpace"]
        SLACK["dbt-notification"]
    end

    Developer["Developer"] -->|"Git Push / PR / Manual Trigger"| GA
    GA --> ENV
    ENV --> RUN
    RUN -->|"Service Account Auth"| BQ
    RUN -->|"Success / Failure Alert"| SLACK
```
## 🛠 技術スタック (Tech Stack)

| カテゴリ | 採用技術 / ツール | 役割 |
|---|---|---|
| **Data Warehouse** | Google BigQuery | データの格納・変換エンジンの実行環境 |
| **Data Transformation** | dbt (dbt-bigquery 1.12+) | データモデルの定義・ビルド・テスト |
| **CI/CD** | GitHub Actions | パイプラインの自動実行・手動実行（workflow_dispatch） |
| **Notification** | Slack Incoming Webhook | 実行結果（成功 / 失敗）の自動通知 |
| **Language** | SQL / Python 3.10 | データモデル記述および実行環境 |
