# Sales Distribution per Demand Status 📊

This SQL query analyzes how ticket sales distribute across **Demand Status (DS)** over time.  
It’s designed for dynamic pricing environments, where each product can move through multiple demand stages as availability changes.

## Overview

The query:
1. **Extracts** snapshots of seat availability and demand status from raw `results` and `requests` tables.  
2. **Deduplicates** data to ensure one entry per product and status update.  
3. **Calculates seat deltas** between consecutive updates to attribute sold tickets to the correct DS value.  
4. **Aggregates** all positive deltas to show the total seats sold and their proportional share per DS.

## Techniques Used
- **CTEs** for modular query structure  
- **Window functions** (`LEAD()`) to calculate change between updates  
- **SAFE_DIVIDE** for robust share calculation  
- **Filtering and aggregation** to isolate meaningful intervals and ignore zero changes  

## Example Output

Below is a simulated example illustrating the result format:

| Row | DS  | seats_sold | share |
|------|-----|-------------|--------|
| 1 | 10% | 243 | 0.1587 |
| 2 | 20% | 212 | 0.1383 |
| 3 | 30% | 147 | 0.0959 |
| 4 | 40% | 109 | 0.0710 |
| 5 | 50% | 97  | 0.0634 |
| 6 | 60% | 103 | 0.0672 |
| 7 | 70% | 122 | 0.0796 |
| 8 | 80% | 159 | 0.1038 |
| 9 | 90% | 178 | 0.1162 |
| 10 | 100% | 160 | 0.1045 |

> **Note:** The above data is for demonstration purposes only.  
> In production, this query runs on live sales data to visualize the distribution of sold seats across demand statuses.

## Purpose

This query helps identify:
- How sales are distributed across different **demand pressures**,   
- And how **availability thresholds** align with actual purchase behavior.

Such insights are essential for fine-tuning **dynamic pricing models** and understanding **sales velocity** patterns.

