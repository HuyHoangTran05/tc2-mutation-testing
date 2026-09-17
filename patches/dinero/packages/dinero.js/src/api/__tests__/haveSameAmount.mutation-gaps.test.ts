import { USD } from '../../currencies';
import { createNumberDinero } from 'test-utils';

import { haveSameAmount } from '..';

// Mutation-testing gap (TC2 mutant 78): every existing test compares exactly
// two objects, so `every` and `some` cannot be told apart.
describe('haveSameAmount with more than two objects', () => {
  const dinero = createNumberDinero;

  it('returns false when only the last amount differs', () => {
    const d1 = dinero({ amount: 1000, currency: USD });
    const d2 = dinero({ amount: 1000, currency: USD });
    const d3 = dinero({ amount: 2000, currency: USD });

    expect(haveSameAmount([d1, d2, d3])).toBe(false);
  });
  it('returns true when all three amounts are equal', () => {
    const d1 = dinero({ amount: 1000, currency: USD });
    const d2 = dinero({ amount: 10000, currency: USD, scale: 3 });
    const d3 = dinero({ amount: 1000, currency: USD });

    expect(haveSameAmount([d1, d2, d3])).toBe(true);
  });
});
