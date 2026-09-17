# Mutation run comparison

- Before: `20260917-145130-dinero-baseline (101.3 s, 0 added test files)`
- After: `20260917-150724-dinero-baseline-repeat1 (114.2 s, 0 added test files)`

| Metric | Before | After |
| --- | --- | --- |
| Score (detected / valid) | 348/359 = 96.9% | 347/359 = 96.7% |
| Excluding reviewed equivalents | 348/355 = 98.0% | 347/355 = 97.7% |
| Killed | 344 | 343 |
| Timeout | 4 | 4 |
| Survived | 10 | 11 |
| NoCoverage | 1 | 1 |
| CompileError | 0 | 0 |
| RuntimeError | 0 | 0 |

## Mutants that changed status

| Id | File | Line | Mutator | Before | After | Verdict |
| --- | --- | ---: | --- | --- | --- | --- |
| 81 | `packages/dinero.js/src/core/api/haveSameCurrency.ts` | 14 | MethodExpression | Killed | Survived | real_gap |
