-- 課題クエリ: CTE(WITH句) と JOIN, GROUP BY を使った集計
WITH user_orders AS (
  -- 1. CTE: ユーザー情報と注文情報を結合する一時テーブル
  SELECT 
    u.id AS user_id,
    u.name AS user_name,
    o.order_id,
    o.amount
  FROM `de-portfolio-2026.raw_data.users_sample` AS u
  LEFT JOIN `de-portfolio-2026.raw_data.orders_sample` AS o
    ON u.id = o.user_id
)
-- 2. メインクエリ: ユーザーごとに集計
SELECT 
  user_id,
  user_name,
  COUNT(order_id) AS total_orders,
  COALESCE(SUM(amount), 0) AS total_amount
FROM user_orders
GROUP BY 
  user_id,
  user_name
ORDER BY 
  total_amount DESC;