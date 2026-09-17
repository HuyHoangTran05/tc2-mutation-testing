# Mutation run summary

- Target: `stateless` @ `588f1a1a08`
- Started: 2026-09-17T15:13:16, duration 34.1 s, exit code 0

## Scores

- Mutation score (killed + timeout) / valid: 90/97 = 92.8%
- Score on covered code (excludes NoCoverage): 90/94 = 95.7%
- Excluding reviewed equivalents (2): 90/95 = 94.7%

Timeouts count as detected (Stryker's convention) but are listed separately below.

## Status counts

| Status | Count |
| --- | ---: |
| Killed | 90 |
| Survived | 4 |
| NoCoverage | 3 |
| Timeout | 0 |
| CompileError | 20 |
| RuntimeError | 0 |
| Ignored | 1220 |
| **Total** | **1337** |

## Per file

| File | Killed | Survived | NoCoverage | Timeout | CompileError | RuntimeError | Ignored |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `src/Stateless/GuardCondition.cs` | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| `src/Stateless/OnTransitionedEvent.cs` | 0 | 0 | 0 | 0 | 1 | 0 | 27 |
| `src/Stateless/ReentryTriggerBehaviour.cs` | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| `src/Stateless/StateMachine.Async.cs` | 0 | 0 | 0 | 0 | 6 | 0 | 114 |
| `src/Stateless/StateMachine.cs` | 0 | 0 | 0 | 0 | 4 | 0 | 173 |
| `src/Stateless/StateRepresentation.Async.cs` | 0 | 0 | 0 | 0 | 3 | 0 | 99 |
| `src/Stateless/StateRepresentation.cs` | 73 | 3 | 3 | 0 | 6 | 0 | 36 |
| `src/Stateless/TransitionGuard.cs` | 13 | 1 | 0 | 0 | 0 | 0 | 4 |
| `src/Stateless/TransitioningTriggerBehaviour.cs` | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
