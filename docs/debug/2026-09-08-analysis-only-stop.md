# Recurring stop after diagnosis

## Symptom

The user still reports final causal explanations with no repair after versions 0.2.2 and 0.2.3. Their exact failing task and response have been requested but are not yet available.

## Hypothesis and scoped change

The previous Diagnose route described investigation without a local transition to implementation, despite global completion requirements. This is a possible instruction weakness, not an established cause of the actual incidents. Version 0.2.4 explicitly retains implementation and verification as pending after diagnosis and preserves existing repair authorization through contextual “帮我看看” feedback.

## Evidence

One baseline and one candidate known-cause fixture both repaired the defect and passed five immutable tests. One candidate analysis-only fixture remained byte-identical. The actual premature stop remains unreproduced; see ../../evals/results/0.2.4-smoke.md for the baseline snapshot limitation. All 20 helper tests passed. Targeted local installation/config inspection found one Silverlocks installation and no listed conflicting workflow override, but this does not prove which instructions the host loaded in the failing conversation.

## Do not repeat without new evidence

Do not declare the recurring issue fixed from wording changes or easy passing examples. Do not add unattended continuation loops or hooks. Do not blame the model or host without a failing trace.

## Next distinguishing evidence

Inspect the user's original task, last response, tool activity, and active skill instructions. Determine whether repair authorization was lost, the skill was not loaded, an actual blocker occurred, or execution ended despite a pending available action. Reproduce that case against complete baseline and candidate snapshots before claiming the cause resolved.
