import { USD } from '../../currencies';
import { createBigintDinero, createNumberDinero, castToBigintCurrency } from 'test-utils';

import { allocate } from '..';

// Mutation-testing gap (TC2 mutants 24, 31, 32): the existing negative-ratio
// tests only use all-negative ratios, which are already rejected because no
// ratio is positive. A mix of negative and positive ratios must be rejected too.
describe('allocate with mixed negative and positive ratios', () => {
  it('throws for number amounts', () => {
    const d = createNumberDinero({ amount: 100, currency: USD });

    expect(() => allocate(d, [-50, 150])).toThrow('[Dinero.js] Ratios are invalid.');
  });
  it('throws when the negative ratio comes last', () => {
    const d = createNumberDinero({ amount: 100, currency: USD });

    expect(() => allocate(d, [150, -50])).toThrow('[Dinero.js] Ratios are invalid.');
  });
  it('throws for bigint amounts', () => {
    const d = createBigintDinero({
      amount: 100n,
      currency: castToBigintCurrency(USD),
    });

    expect(() => allocate(d, [-50n, 150n])).toThrow('[Dinero.js] Ratios are invalid.');
  });
});
