# Testresultat – Körda scripts

## SQL – sql_demo.py
✅ Alla 5 queries kördes utan fel mot SQLite-databas

## API-testning – test_api.py
✅ 17 av 17 tester godkända (pytest)
- 6 GET-tester
- 2 negativa tester
- 4 POST-tester
- 5 parametriserade tester

## Batchjobb – batch_job.py
✅ 3 filer bearbetade, 5 rader godkända
✅ 2 felaktiga rader korrekt identifierade och loggade

## Konfiguration – config_manager.py
✅ YAML-konfiguration laddad och validerad
✅ Felhantering testad – saknade miljövariabler fångades korrekt
