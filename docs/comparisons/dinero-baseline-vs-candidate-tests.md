# Mutation run comparison

- Before: `20260917-145130-dinero-baseline (101.3 s, 0 added test files)`
- After: `20260917-151116-dinero-candidate-tests (119.0 s, 4 added test files)`

| Metric | Before | After |
| --- | --- | --- |
| Score (detected / valid) | 348/359 = 96.9% | 354/359 = 98.6% |
| Excluding reviewed equivalents | 348/355 = 98.0% | 354/355 = 99.7% |
| Killed | 344 | 348 |
| Timeout | 4 | 6 |
| Survived | 10 | 5 |
| NoCoverage | 1 | 0 |
| CompileError | 0 | 0 |
| RuntimeError | 0 | 0 |

## Mutants that changed status

| Id | File | Line | Mutator | Before | After | Verdict |
| --- | --- | ---: | --- | --- | --- | --- |
| 24 | `packages/dinero.js/src/core/api/allocate.ts` | 80 | MethodExpression | Survived | Killed | real_gap |
| 31 | `packages/dinero.js/src/core/api/allocate.ts` | 87 | ConditionalExpression | Survived | Killed | real_gap |
| 32 | `packages/dinero.js/src/core/api/allocate.ts` | 87 | LogicalOperator | Survived | Killed | real_gap |
| 78 | `packages/dinero.js/src/core/api/haveSameAmount.ts` | 26 | MethodExpression | Survived | Killed | real_gap |
| 297 | `packages/dinero.js/src/core/utils/distribute.ts` | 68 | ConditionalExpression | Survived | Timeout | real_gap |
| 298 | `packages/dinero.js/src/core/utils/distribute.ts` | 68 | BlockStatement | NoCoverage | Timeout | real_gap |
