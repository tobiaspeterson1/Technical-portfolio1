# 🛠️ Technical Portfolio – Application Specialist Skills

Detta repo demonstrerar tekniska färdigheter inom fyra nyckelområden relevanta för rollen som **Applikationsspecialist**.

---

## 📁 Projektöversikt

### 1. SQL – Databashantering
📂 `sql-queries/sql_demo.py`

Skriver SQL-queries mot en SQLite-databas med simulerad verksamhetsdata (kunder, ordrar, produkter). Visar förmågan att analysera, filtrera och aggregera data på ett strukturerat sätt.

**Tekniker:** SQLite, SELECT, JOIN, GROUP BY, subqueries, aggregering

---

### 2. API-integration & Testning
📂 `api-testing/test_api.py`

Strukturerade automatiserade tester av ett externt REST API. Inkluderar statuskodvalidering, schema-kontroll och felscenarier – precis som en Applikationsspecialist gör i praktiken.

**Tekniker:** Python, pytest, requests, JSON-validering, felhantering

---

### 3. Scripts & Batchjobbhantering
📂 `batch-scripts/batch_job.py`

Automatiserade Python-scripts som körs schemalagt: filbearbetning, loggning och felhantering. Simulerar verkliga batchjobb i en integrationsmiljö.

**Tekniker:** Python, schemaläggning, loggning, filhantering, CSV/JSON

---

### 4. Teknisk Konfiguration
📂 `config-management/config_manager.py`

Hanterar applikationskonfiguration via YAML och `.env`-filer. Visar hur man separerar konfiguration från kod och tolkar tekniska integrationsspecifikationer.

**Tekniker:** YAML, miljövariabler, .env-filer, uppstartsvalidering

---

## 🚀 Kom igång

```bash
# Klona repot
git clone https://github.com/tobiaspeterson1/Technical-portfolio.git
cd Technical-portfolio

# Installera beroenden
pip install -r requirements.txt

# Kör API-testerna
pytest api-testing/ -v

# Kör SQL-demo
python sql-queries/sql_demo.py

# Kör batchjobb
python batch-scripts/batch_job.py

# Kör konfigurationsDemo
python config-management/config_manager.py
```

## 📋 Krav

- Python 3.10+
- pip (pakethanterare)

---

*Portfolio byggt för att visa praktisk teknisk kompetens inom applikationsspecialistarbete.*
