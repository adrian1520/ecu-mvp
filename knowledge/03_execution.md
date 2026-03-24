# 03 Execution
## Standardowy cykl
1. Read context (memory + project).
2. Plan (krótki, krokowy).
3. Write (plik/stan).
4. Execute (`repositoryDispatch` lub `triggerWorkflow`).
5. Monitor (`listWorkflowRuns` -> `getWorkflowRun` -> `getWorkflowRunLogs`).
6. Report + stop.

## Komendy systemowe
- wczytaj kontekst
- zapisz projekt
- otwórz projekt
- odczytaj pamięć
