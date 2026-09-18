# Mutation run comparison

- Before: `20260917-145311-stateless-baseline (38.3 s, 0 added test files)`
- After: `20260918-142647-stateless-after-tests (43.0 s, 1 added test files)`

| Metric | Before | After |
| --- | --- | --- |
| Score (detected / valid) | 85/97 = 87.6% | 90/97 = 92.8% |
| Excluding reviewed equivalents | 85/95 = 89.5% | 90/95 = 94.7% |
| Killed | 85 | 90 |
| Timeout | 0 | 0 |
| Survived | 6 | 4 |
| NoCoverage | 6 | 3 |
| CompileError | 20 | 20 |
| RuntimeError | 0 | 0 |

## Mutants that changed status

| Id | File | Line | Mutator | Before | After | Verdict |
| --- | --- | ---: | --- | --- | --- | --- |
| 1579 | `src/Stateless/StateRepresentation.cs` | 95 | Statement mutation | Survived | Killed | real_gap |
| 1635 | `src/Stateless/StateRepresentation.cs` | 205 | LogicalNotExpression to un-LogicalNotExpression mutation | Survived | Killed | real_gap |
| 1636 | `src/Stateless/StateRepresentation.cs` | 206 | Block removal mutation | NoCoverage | Killed | real_gap |
| 1706 | `src/Stateless/TransitionGuard.cs` | 45 | Block removal mutation | NoCoverage | Killed | real_gap |
| 1707 | `src/Stateless/TransitionGuard.cs` | 52 | Block removal mutation | NoCoverage | Killed | real_gap |
