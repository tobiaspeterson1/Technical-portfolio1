# 🛠️ Technical Portfolio – Application Specialist

## Why this matters for an Application Specialist

An Application Specialist bridges customers and developers — configuring systems, validating integrations, testing solutions and troubleshooting data flows. Every project in this portfolio reflects exactly that:

| Project | Skill demonstrated | Why it matters |
|---|---|---|
| SQL | Query, filter and aggregate data | Analyse delivery data, debug integrations, find anomalies |
| API Testing | Validate REST APIs automatically | Verify carrier integrations return correct data and handle errors |
| Batch Job | Automate file processing with logging | Process high-volume delivery data, catch and log failures |
| Config Management | Handle YAML, .env and secrets | Configure and deploy solutions across environments |

---

## 📁 Projects

### 1. SQL – Data Analysis
**Problem:** Need to extract and analyse order data across multiple related tables.

**Solution:** Built a SQLite database simulating an e-commerce system with customers, orders, products and order lines. Wrote five SQL queries covering JOIN, GROUP BY, subqueries and aggregation.

**Output:** Structured query results showing top customers by revenue, best-selling products and returning customers.

![SQL output](Skärmbild%202026-04-15%20145753.png)

```
sql-queries/
└── sql_demo.py        ← Run queries against local SQLite database
```

---

### 2. API Testing – Integration Validation
**Problem:** Need to verify that a REST API returns correct data, handles errors and meets performance requirements.

**Solution:** Built structured automated tests using pytest — covering status codes, schema validation, negative test cases and response time.

**Output:** 17/17 tests passed. Covers GET, POST, PUT, DELETE and parametrised schema checks.

![API test results](Skärmbild%202026-04-15%20145937.png)

```
api-testing/
└── test_api.py        ← Run: pytest api-testing/ -v
```

---

### 3. Batch Job – Automated File Processing
**Problem:** Need to automatically process incoming data files, validate content, log errors and archive processed files.

**Solution:** Built a Python batch script that reads CSV files from an inbox, validates each row, saves clean data as JSON to an outbox, logs all errors with row and reason, and produces a job summary.

**Output:** 3 files processed, 5 valid rows saved, 2 invalid rows detected and logged — without crashing.

![Batch job output](Skärmbild%202026-04-15%20150053.png)

```
batch-scripts/
├── batch_job.py       ← Main script
├── inbox/             ← Incoming CSV files
├── outbox/            ← Processed JSON output
├── logs/              ← Timestamped log files
└── archive/           ← Processed originals
```

---

### 4. Config Management – Technical Configuration
**Problem:** Need to manage application settings across environments without hardcoding sensitive values in source code.

**Solution:** Built a configuration system that loads settings from YAML and secrets from environment variables, validates all values on startup and masks sensitive data in logs.

**Output:** Config loaded and validated successfully. Missing environment variables caught and reported correctly.

![Config output](Skärmbild%202026-04-15%20150153.png)

```
config-management/
├── config_manager.py  ← Main script
└── env.example        ← Template for local environment variables
```
| Integration Pipeline | End-to-end order flow | Validate data, call API, log outcomes, split success/failed records |

### 4. Config Management
---

### 5. End-to-End Order Integration Flow
**Problem:** Incoming order data needs to be validated, sent to an external system, and split into successful and failed records for follow-up.

**Solution:** Built a single-script integration pipeline that reads CSV input, applies 6 validation rules, sends valid orders to an API, logs all outcomes and writes success and failed records to separate output files.

**Output:** 2 orders processed successfully, 6 failures detected across three categories – validation error, integration error and system error.

![Integration pipeline output](Skärmbild%202026-04-15%20152826.png)
---

## 🚀 Getting Started

```bash
# Clone the repo
git clone https://github.com/tobiaspeterson1/Technical-portfolio1.git
cd Technical-portfolio1

# Install dependencies
pip install -r requirements.txt

# Run SQL demo
python sql-queries/sql_demo.py

# Run API tests
pytest api-testing/ -v

# Run batch job
python batch-scripts/batch_job.py

# Run config demo
python config-management/config_manager.py
```

## 📋 Requirements

- Python 3.10+
- pip

---

## ✅ Test Results

All scripts have been run and verified locally. See [RESULTS.md](./RESULTS.md) for full output.

---

*Built to demonstrate practical technical skills relevant to an Application Specialist role.*


