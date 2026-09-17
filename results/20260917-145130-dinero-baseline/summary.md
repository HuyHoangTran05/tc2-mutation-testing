# Mutation run summary

- Target: `dinero` @ `76b969e519`
- Started: 2026-09-17T14:51:30, duration 101.3 s, exit code 0

## Scores

- Mutation score (killed + timeout) / valid: 348/359 = 96.9%
- Score on covered code (excludes NoCoverage): 348/358 = 97.2%
- Excluding reviewed equivalents (0): 348/359 = 96.9%

Timeouts count as detected (Stryker's convention) but are listed separately below.

## Status counts

| Status | Count |
| --- | ---: |
| Killed | 344 |
| Survived | 10 |
| NoCoverage | 1 |
| Timeout | 4 |
| CompileError | 0 |
| RuntimeError | 0 |
| Ignored | 0 |
| **Total** | **359** |

## Per file

| File | Killed | Survived | NoCoverage | Timeout | CompileError | RuntimeError | Ignored |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `packages/dinero.js/src/core/api/add.ts` | 8 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/api/allocate.ts` | 23 | 3 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/api/compare.ts` | 9 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/api/convert.ts` | 5 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/api/equal.ts` | 7 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/api/greaterThan.ts` | 9 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/api/greaterThanOrEqual.ts` | 9 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/api/hasSubUnits.ts` | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/api/haveSameAmount.ts` | 3 | 1 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/api/haveSameCurrency.ts` | 10 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/api/isNegative.ts` | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/api/isPositive.ts` | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/api/isZero.ts` | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/api/lessThan.ts` | 9 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/api/lessThanOrEqual.ts` | 9 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/api/maximum.ts` | 8 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/api/minimum.ts` | 8 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/api/multiply.ts` | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/api/normalizeScale.ts` | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/api/subtract.ts` | 8 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/api/toDecimal.ts` | 27 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/api/toSnapshot.ts` | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/api/toUnits.ts` | 17 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/api/transformScale.ts` | 5 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/api/trimScale.ts` | 4 | 2 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/divide/down.ts` | 5 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/divide/halfAwayFromZero.ts` | 5 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/divide/halfDown.ts` | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/divide/halfEven.ts` | 5 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/divide/halfOdd.ts` | 5 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/divide/halfTowardsZero.ts` | 5 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/divide/halfUp.ts` | 13 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/divide/up.ts` | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/utils/absolute.ts` | 8 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/utils/compare.ts` | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/utils/computeBase.ts` | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/utils/countTrailingZeros.ts` | 4 | 0 | 0 | 3 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/utils/distribute.ts` | 22 | 2 | 1 | 1 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/utils/equal.ts` | 5 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/utils/getAmountAndScale.ts` | 7 | 1 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/utils/getDivisors.ts` | 7 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/utils/greaterThan.ts` | 5 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/utils/greaterThanOrEqual.ts` | 5 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/utils/isArray.ts` | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/utils/isEven.ts` | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/utils/isHalf.ts` | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/utils/isScaledAmount.ts` | 2 | 1 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/utils/lessThan.ts` | 5 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/utils/lessThanOrEqual.ts` | 5 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/utils/maximum.ts` | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/utils/minimum.ts` | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| `packages/dinero.js/src/core/utils/sign.ts` | 5 | 0 | 0 | 0 | 0 | 0 | 0 |
