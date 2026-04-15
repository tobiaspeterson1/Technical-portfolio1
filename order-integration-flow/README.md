# Project 5: End-to-End Order Integration Flow

## What it does

Reads incoming orders from a CSV file, validates each record, sends valid orders to an API, and splits the results into successful and failed records — with full logging throughout.

```
orders.csv
    │
    ▼
[ Validate ]──── ❌ failed_records.csv
    │
    ▼
[ Send to API ]── ❌ failed_records.csv
    │
    ▼
[ success.csv ]
    │
    ▼
[ integration.log ]
```

---

## Why this matters

<img width="1472" height="1126" alt="image" src="https://github.com/user-attachments/assets/84e330c8-239a-4cbf-a28e-087c2c70c821" />


## Flow

orders.csv → [Validate] → pass → [Send to API] → 201 → [Log] → [Write output]
                       ↘ fail                  ↘ 400/500
                              ↘ failed_records.csv ↙

| Skill | Where it's shown |
|---|---|
| Data validation | 6 business rules per order |
| API integration | POST request with response handling |
| Error handling | 3 failure types: validation, integration, system |
| Logging | Timestamped log per run |
| Support-friendly output | `failed_records.csv` with failure reason per order |

---

## Project structure

```
order-integration-flow/
├── integration_pipeline.py   ← Single script, full pipeline
├── input/
│   └── orders.csv            ← 8 test orders, 3 failure scenarios
├── output/
│   ├── success.csv           ← Successfully processed orders
│   └── failed_records.csv    ← Failed orders with reason
└── logs/
    └── integration.log       ← Timestamped log per run
```

---

## Validation rules

| Field | Rule |
|---|---|
| `order_id` | Must not be empty |
| `customer_id` | Must not be empty |
| `email` | Must contain @ |
| `amount` | Must be a number greater than 0 |
| `currency` | Must be SEK, EUR or USD |
| `order_date` | Must follow YYYY-MM-DD format |

---

## Test scenarios

| Order | Scenario |
|---|---|
| 1001 | ✅ Valid |
| 1002 | ❌ Validation – invalid email |
| 1003 | ❌ Validation – negative amount |
| 1004 | ✅ Valid |
| 1005 | ❌ System error – API returns 500 |
| 1006 | ❌ Integration error – API returns 400 |
| 1007 | ❌ Validation – unsupported currency (GBP) |
| 1008 | ❌ Validation – wrong date format |

---

## How to run

```bash
cd order-integration-flow
pip install requests
python integration_pipeline.py
```
