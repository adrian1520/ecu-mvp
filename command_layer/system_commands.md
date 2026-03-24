# Command Layer

## Komendy
1. **wczytaj kontekst**
   - Czyta: `memory/system_context.json`, `memory/session_log.json`, `memory/projects/project_x.json`.
2. **zapisz projekt**
   - Zapisuje JSON projektu do `memory/projects/{project}.json`.
3. **otwórz projekt**
   - Odczytuje `memory/projects/{project}.json`.
4. **odczytaj pamięć**
   - Odczytuje wszystkie kluczowe pliki `memory/*.json` wymagane przez bieżące zadanie.

## Konwencja odpowiedzi
- Sukces: podaj wykonane operationId + plik.
- Błąd: podaj operationId + kod odpowiedzi + krótki powód.
