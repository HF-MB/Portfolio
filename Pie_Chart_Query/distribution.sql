-- Sales Distribution per Demand Status
WITH extracted AS (
  SELECT
    s.requestID, 
    s.sold AS sold,
    s.capacity AS capacity,
    s.capacity - s.sold AS available,
    s.demandStatus AS DS,
    s.statusUpdate,
    TIMESTAMP_SECONDS(CAST(r.changePage AS INT64)) AS changePage_ts_utc,
    s.timestamp AS result_timestamp,
    q.timestamp AS request_timestamp,
    q.producttype AS product
  FROM steering.results s
  JOIN steering.requests q
    ON s.requestID = q.requestID
  WHERE s.timestamp >= TIMESTAMP(DATETIME '2025-09-01 00:00:00', 'Europe/Berlin') -- selling start
    AND q.timestamp >= TIMESTAMP(DATETIME '2025-09-01 00:00:00', 'Europe/Berlin')
    AND q.audience = 'Adult'
    AND s.error IS NULL
),

-- one snapshot per (product, statusUpdate). Necessary because in each status Update several prices are calculated for the same producttype – several audience, tickettype etc. combinations. But the DS is the same in each producttype.
snapshots AS (
  SELECT
    product,
    statusUpdate,
    MIN(DP) AS DS,                    -- DS constant in every audience and tickettype combination per product/update
    MIN(available) AS available       -- available seat should be non-increasing; choose MIN across dupes
  FROM extracted
  GROUP BY product, statusUpdate
),

-- compute taken deltas across successive updates; attribute changing availability to DS 
deltas AS (
  SELECT
    product,
    statusUpdate,
    DS,
    available AS avail_curr,
    LEAD(available) OVER (PARTITION BY product ORDER BY statusUpdate) AS avail_next,
    available - LEAD(available) OVER (PARTITION BY product ORDER BY statusUpdate) AS sold_between_updates
  FROM snapshots
  -- WHERE product ="VIP" /* Insert a product ID for audits, Result will only show the seats taken for this products and the calculated PGs for the taken seats.
)

/*
-- (A) Optional: Demand Status per product attribution (for audits)
SELECT product, DS, SUM(sold_between_updates) AS seats_sold
FROM deltas
WHERE sold_between_updates > 0
GROUP BY product, DS
ORDER BY DS, product;
*/

-- (B) Final KPI for pie: seats sold by DS over all products
SELECT
  DS,
  SUM(sold_between_updates) AS seats_sold,
  SAFE_DIVIDE(
    SUM(sold_between_updates),
    SUM(SUM(sold_between_updates)) OVER ()
  ) AS share
FROM deltas
WHERE sold_between_updates > 0           -- ignore zero-move intervals
GROUP BY DS
ORDER BY DS;