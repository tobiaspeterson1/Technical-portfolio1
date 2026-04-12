"""
Teknisk konfigurationshantering
================================
Demonstrerar hur man tolkar och hanterar tekniska
integrationsspecifikationer via konfigurationsfiler:

  - YAML-konfiguration med miljö-specifika inställningar
  - .env-filer för hemligheter (aldrig i versionshantering)
  - Validering av konfiguration vid uppstart
  - Konfigurationsklasser med typsäkra värden

Kör: python config_manager.py
"""

import os
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ── Konfigurationsklasser ─────────────────────────────────────────────────────

@dataclass
class DatabaseConfig:
    host:     str
    port:     int
    name:     str
    user:     str
    password: str = field(repr=False)  # Dölj lösenord i utskrift

    def connection_string(self) -> str:
        return f"postgresql://{self.user}:***@{self.host}:{self.port}/{self.name}"


@dataclass
class ApiConfig:
    base_url:    str
    timeout_sec: int
    max_retries: int
    api_key:     str = field(repr=False)

    def masked_key(self) -> str:
        """Visar bara de fyra sista tecknen i API-nyckeln."""
        return f"****{self.api_key[-4:]}" if len(self.api_key) > 4 else "****"


@dataclass
class BatchJobConfig:
    schedule_cron: str
    inbox_path:    str
    outbox_path:   str
    max_file_size_mb: int
    allowed_extensions: list[str]


@dataclass
class AppConfig:
    environment: str
    log_level:   str
    database:    DatabaseConfig
    api:         ApiConfig
    batch_job:   BatchJobConfig


# ── YAML-konfigurationsfiler ──────────────────────────────────────────────────

YAML_CONFIG = """
# app-config.yaml
# Teknisk integrationsspecifikation – applikationskonfiguration
# -----------------------------------------------------------------
# VIKTIGT: Känsliga värden (lösenord, API-nycklar) ska ALDRIG
# lagras här. De läses från miljövariabler eller .env-filer.
# -----------------------------------------------------------------

environment: production
log_level: INFO

database:
  host: db.internal.company.se
  port: 5432
  name: app_production
  user: app_user
  # password läses från miljövariabeln DB_PASSWORD

api:
  base_url: https://api.partner.se/v2
  timeout_sec: 30
  max_retries: 3
  # api_key läses från miljövariabeln API_KEY

batch_job:
  schedule_cron: "0 6 * * 1-5"   # Vardagar 06:00
  inbox_path: /data/integration/inbox
  outbox_path: /data/integration/outbox
  max_file_size_mb: 50
  allowed_extensions:
    - .csv
    - .json
    - .xml
"""

# Simulerade miljövariabler (i verkligheten satta av servern eller .env)
SIMULATED_ENV = {
    "DB_PASSWORD": "s3cr3t-db-passw0rd",
    "API_KEY":     "sk-prod-abc123xyz789",
    "APP_ENV":     "production",
}


# ── Konfigurationsladdning ────────────────────────────────────────────────────

def load_config(yaml_content: str, env: dict) -> AppConfig:
    """
    Laddar och validerar konfiguration från YAML + miljövariabler.
    Kastar ValueError om obligatoriska värden saknas.
    """
    raw = yaml.safe_load(yaml_content)

    # Läs hemligheter från miljövariabler
    db_password = env.get("DB_PASSWORD") or os.environ.get("DB_PASSWORD")
    api_key     = env.get("API_KEY")     or os.environ.get("API_KEY")

    # Validera att hemligheter finns
    missing = []
    if not db_password:
        missing.append("DB_PASSWORD")
    if not api_key:
        missing.append("API_KEY")
    if missing:
        raise ValueError(f"Obligatoriska miljövariabler saknas: {', '.join(missing)}")

    # Bygg typade konfigurationsobjekt
    db_raw  = raw["database"]
    api_raw = raw["api"]
    bj_raw  = raw["batch_job"]

    return AppConfig(
        environment=raw["environment"],
        log_level=raw["log_level"],
        database=DatabaseConfig(
            host=db_raw["host"],
            port=int(db_raw["port"]),
            name=db_raw["name"],
            user=db_raw["user"],
            password=db_password,
        ),
        api=ApiConfig(
            base_url=api_raw["base_url"],
            timeout_sec=int(api_raw["timeout_sec"]),
            max_retries=int(api_raw["max_retries"]),
            api_key=api_key,
        ),
        batch_job=BatchJobConfig(
            schedule_cron=bj_raw["schedule_cron"],
            inbox_path=bj_raw["inbox_path"],
            outbox_path=bj_raw["outbox_path"],
            max_file_size_mb=int(bj_raw["max_file_size_mb"]),
            allowed_extensions=bj_raw["allowed_extensions"],
        ),
    )


def validate_config(config: AppConfig):
    """Kör affärsregler på den laddade konfigurationen."""
    errors = []

    if config.database.port not in range(1, 65536):
        errors.append(f"Ogiltigt databasport: {config.database.port}")

    if config.api.timeout_sec < 1 or config.api.timeout_sec > 300:
        errors.append(f"API timeout måste vara 1–300 sekunder, fick {config.api.timeout_sec}")

    if config.batch_job.max_file_size_mb < 1:
        errors.append("max_file_size_mb måste vara minst 1")

    if config.log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        errors.append(f"Ogiltigt log_level: {config.log_level}")

    if errors:
        raise ValueError("Konfigurationsvalideringsfel:\n" + "\n".join(f"  - {e}" for e in errors))


# ── Demonstration ─────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("KONFIGURATIONSHANTERING – DEMONSTRATION")
    print("=" * 55)

    # 1. Ladda och validera konfiguration
    print("\n[1] Laddar konfiguration från YAML + miljövariabler...")
    config = load_config(YAML_CONFIG, SIMULATED_ENV)
    validate_config(config)
    print("    ✅ Konfiguration laddad och validerad utan fel.\n")

    # 2. Visa laddad konfiguration (utan hemligheter)
    print("[2] Aktiv konfiguration:")
    print(f"    Miljö         : {config.environment}")
    print(f"    Log-nivå      : {config.log_level}")
    print(f"    Databas-URL   : {config.database.connection_string()}")
    print(f"    API-URL       : {config.api.base_url}")
    print(f"    API-nyckel    : {config.api.masked_key()}  ← maskerad")
    print(f"    Batchschema   : {config.batch_job.schedule_cron}  (vardagar 06:00)")
    print(f"    Tillåtna format: {', '.join(config.batch_job.allowed_extensions)}")

    # 3. Testa felhantering vid saknad miljövariabel
    print("\n[3] Testar felhantering – saknad miljövariabel...")
    try:
        load_config(YAML_CONFIG, {})  # Inga env-variabler
    except ValueError as e:
        print(f"    ✅ Korrekt fel fångat: {e}\n")

    # 4. Generera .env.example-fil
    env_example = """# .env.example
# Kopiera till .env och fyll i riktiga värden.
# Lägg ALDRIG .env i versionshantering (lägg till i .gitignore).

DB_PASSWORD=ditt-databaslösenord-här
API_KEY=din-api-nyckel-här
APP_ENV=development
"""
    Path("env.example").write_text(env_example)
    print("[4] Skapade env.example – mall för lokala miljövariabler.")

    print("\n✅ Demonstration klar!")
    Path("env.example").unlink(missing_ok=True)


if __name__ == "__main__":
    main()
