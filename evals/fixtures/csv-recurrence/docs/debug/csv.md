# CSV defect history

- Symptom: exported notes become multiple columns or rows.
- Prior attempt: trim blank lines. Plain rows passed, but quoted notes still failed.
- Disproven assumption: removing blank lines is sufficient to restore CSV record boundaries.
- Do not repeat without new evidence: another whitespace-only patch.
- Current implementation and test results take precedence over this history.
