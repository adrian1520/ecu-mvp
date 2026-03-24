# Module Loader (Core)

## Cel
Ładować minimalny kontekst operacyjny przed wykonaniem zadania i utrzymywać spójność stanu projektu w repo.

## Kolejność ładowania
1. `memory/system_context.json`
2. `memory/session_log.json`
3. `memory/projects/project_x.json` (lub wskazany projekt)
4. `knowledge/01_identity.md`
5. `knowledge/02_rules.md`
6. `knowledge/03_execution.md`

## Reguły
- Jeżeli plik nie istnieje: loguj brak i kontynuuj, ale odpowiedź kończ `⚠ BRAK DANYCH` gdy brak jest krytyczny.
- Po każdej zmianie planu aktualizuj `memory/projects/<project>.json`.
- Repozytorium zawsze ma priorytet nad pamięcią konwersacji.
