import { calculator } from '../../../calculator/number';

import { distribute } from '../distribute';

const distributeFn = distribute(calculator);

// Mutation-testing gap (TC2 mutants 297, 298): the existing
// "does not hang with amounts larger than MAX_SAFE_INTEGER" test splits the
// amount evenly, so the remainder loop never runs and its guard is untested.
// With 1e33 split in three, the remainder is far above 2^53 and subtracting 1
// has no effect, which is exactly the case the guard protects against.
describe('distribute when the remainder loses precision', () => {
  it('returns three shares that still add up to the amount', () => {
    const amount = 1e33;
    const shares = distributeFn(amount, [1, 1, 1]);

    expect(shares).toHaveLength(3);
    expect(shares[0] + shares[1] + shares[2]).toBe(amount);
  });
  it('returns non-negative shares for uneven ratios', () => {
    const shares = distributeFn(1e33, [3, 7]);

    expect(shares).toHaveLength(2);
    shares.forEach((share) => expect(share).toBeGreaterThanOrEqual(0));
  });
});
