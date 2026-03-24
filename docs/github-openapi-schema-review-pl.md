# Review schematu OpenAPI (GitHub Controller dla Custom GPT)

Data przeglądu: 2026-03-24.

## Ocena ogólna
Schemat jest **bliski działającej wersji**, ale w obecnej formie ma kilka błędów krytycznych względem REST API GitHub i kilka braków funkcjonalnych dla „GPT programisty”.

## Krytyczne poprawki (must-have)

1. **`DELETE /repos/{owner}/{repo}/contents/{path}` wymaga requestBody**
   - W Twoim schema brak `requestBody`.
   - W GitHub API wymagane są co najmniej: `message` i `sha`.

2. **`GET /repos/{owner}/{repo}/actions/runs/{run_id}/logs` zwykle zwraca redirect (302), nie 200 JSON**
   - Dobrze dodać odpowiedzi `302` (Location do pobrania archiwum) oraz błędy.

3. **Brak endpointu listy workflowów (`GET /repos/{owner}/{repo}/actions/workflows`)**
   - U Ciebie jest trigger przez `workflow_id`, ale nie ma jak pobrać ID/filename workflowów.

4. **`workflow_id` powinno przyjmować ID albo nazwę pliku workflow**
   - W praktyce GitHub akceptuje np. `1234567` lub `ci.yml`.
   - Daj `oneOf: [integer, string]`.

5. **`POST /repos/{owner}/{repo}/issues` nie powinno wymagać `body`**
   - Wystarczy `title`; `body` jest opcjonalne.

6. **Brak sekcji auth (`securitySchemes`)**
   - Dla Custom GPT Tooling to często konieczne (Bearer token).

## Braki funkcjonalne pod „GPT programistę”

1. **Brak „patch file” jako operacji semantycznej**
   - GitHub nie ma natywnego HTTP PATCH dla `/contents/{path}`.
   - Najczęstszy wzorzec:
     - `GET /contents/{path}` (pobierz + sha),
     - lokalna modyfikacja tekstu,
     - `PUT /contents/{path}` z nowym base64 + `sha`.

2. **Brak listowania commitów (`GET /repos/{owner}/{repo}/commits`)**
   - Masz tylko `getCommit` po refie. Dla historii i diagnostyki przyda się lista.

3. **Brak endpointów branch update/sync**
   - Przy automatyzacji często potrzebne `PATCH /git/refs/{ref}` (przesunięcie refa).

4. **Brak endpointów check-runs / artifacts (opcjonalnie, ale praktyczne)**
   - Do diagnozy CI często przydatne: artifacts, check-runs, annotations.

## Minimalny pakiet poprawek (fragmenty)

```yaml
components:
  securitySchemes:
    githubToken:
      type: http
      scheme: bearer
      bearerFormat: PAT
security:
  - githubToken: []
```

```yaml
/repos/{owner}/{repo}/contents/{path}:
  delete:
    operationId: deleteFile
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [message, sha]
            properties:
              message: { type: string }
              sha: { type: string }
              branch: { type: string }
    responses:
      "200": { description: File deleted }
```

```yaml
/repos/{owner}/{repo}/actions/workflows:
  get:
    operationId: listWorkflows
    summary: List repository workflows
    parameters:
      - name: owner
        in: path
        required: true
        schema: { type: string }
      - name: repo
        in: path
        required: true
        schema: { type: string }
    responses:
      "200": { description: Workflows list }
```

```yaml
/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches:
  post:
    parameters:
      - name: workflow_id
        in: path
        required: true
        schema:
          oneOf:
            - type: integer
            - type: string
```

```yaml
/repos/{owner}/{repo}/actions/runs/{run_id}/logs:
  get:
    responses:
      "302": { description: Redirect to logs archive }
      "404": { description: Run not found }
```

```yaml
/repos/{owner}/{repo}/issues:
  post:
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [title]
            properties:
              title: { type: string }
              body: { type: string }
```

## Rekomendacje jakościowe

- Dodaj wspólne odpowiedzi błędów: `401`, `403`, `404`, `409`, `422`.
- Ujednolić nazewnictwo operationId (czasownik + rzeczownik).
- W opisie `createOrUpdateFile` doprecyzuj, że `content` musi być base64 (jeśli warstwa tool nie enkoduje automatycznie).
- Dodaj paginację (`per_page`, `page`) tam, gdzie listy mogą być duże (runs, issues, PRs, branches).

## Wniosek

Schema jest dobra jako baza, ale wymaga kilku poprawek kontraktowych, żeby działała niezawodnie z GitHub REST i była kompletna dla kontrolera repo w Custom GPT.
