import { EUR, USD } from '../../currencies';
import { createNumberDinero } from 'test-utils';

import { haveSameCurrency } from '..';

// Mutation-testing gap (TC2 mutant 81): every example test compares exactly two
// objects, so `every` and `some` cannot be told apart. The baseline run only
// killed this mutant by chance through a randomly seeded fast-check property.
describe('haveSameCurrency with more than two objects', () => {
  const dinero = createNumberDinero;

  it('returns false when only the last currency differs', () => {
    const d1 = dinero({ amount: 1000, currency: USD });
    const d2 = dinero({ amount: 500, currency: USD });
    const d3 = dinero({ amount: 1000, currency: EUR });

    expect(haveSameCurrency([d1, d2, d3])).toBe(false);
  });
  it('returns true when all three currencies are equal', () => {
    const d1 = dinero({ amount: 1000, currency: USD });
    const d2 = dinero({ amount: 500, currency: USD });
    const d3 = dinero({ amount: 1, currency: USD });

    expect(haveSameCurrency([d1, d2, d3])).toBe(true);
  });
});
