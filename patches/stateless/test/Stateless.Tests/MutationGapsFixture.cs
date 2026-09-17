using System;
using System.Collections.Generic;
using Xunit;

namespace Stateless.Tests
{
    /// <summary>
    /// Tests for gaps found by the TC2 mutation testing pilot (Stryker.NET survivors).
    /// </summary>
    public class MutationGapsFixture
    {
        // Mutant 1579: the existing test only checks the exception type, which the
        // unhandled-trigger path also throws. Check the message and that the
        // unhandled-trigger callback is not used instead.
        [Fact]
        public void MultipleNonExclusiveGuards_ReportsMultipleTransitions_NotUnhandledTrigger()
        {
            var sm = new StateMachine<State, Trigger>(State.A);
            var x = sm.SetTriggerParameters<int>(Trigger.X);
            sm.Configure(State.A)
                .PermitIf(x, State.B, i => i % 2 == 0)
                .PermitIf(x, State.C, i => i == 2);
            var unhandledCalled = false;
            sm.OnUnhandledTrigger((state, trigger) => unhandledCalled = true);

            var ex = Assert.Throws<InvalidOperationException>(() => sm.Fire(x, 2));

            Assert.Contains("Multiple permitted exit transitions", ex.Message);
            Assert.False(unhandledCalled);
            Assert.Equal(State.A, sm.State);
        }

        // Mutants 1635 and 1636 (1636 had no coverage): moving from a nested substate
        // to its grandparent must exit the intermediate parent but not the grandparent.
        [Fact]
        public void TransitionFromNestedSubstateToGrandparent_ExitsIntermediateParentOnly()
        {
            var exited = new List<State>();
            var sm = new StateMachine<State, Trigger>(State.A);
            sm.Configure(State.C)
                .OnExit(() => exited.Add(State.C));
            sm.Configure(State.B)
                .SubstateOf(State.C)
                .OnExit(() => exited.Add(State.B));
            sm.Configure(State.A)
                .SubstateOf(State.B)
                .OnExit(() => exited.Add(State.A))
                .Permit(Trigger.X, State.C);

            sm.Fire(Trigger.X);

            Assert.Equal(State.C, sm.State);
            Assert.Equal(new[] { State.A, State.B }, exited);
        }

        // Mutant 1706 (no coverage): PermitIf with several guards on a
        // two-parameter trigger.
        [Fact]
        public void PermitIf_TwoParameterTrigger_WithMultipleGuards()
        {
            var sm = new StateMachine<State, Trigger>(State.A);
            var x = sm.SetTriggerParameters<int, string>(Trigger.X);
            sm.Configure(State.A).PermitIf(x, State.B,
                Tuple.Create<Func<int, string, bool>, string>((i, s) => i > 0, "positive"),
                Tuple.Create<Func<int, string, bool>, string>((i, s) => s == "ok", "ok"));

            Assert.Throws<InvalidOperationException>(() => sm.Fire(x, 1, "no"));
            Assert.Equal(State.A, sm.State);

            sm.Fire(x, 1, "ok");
            Assert.Equal(State.B, sm.State);
        }

        // Mutant 1707 (no coverage): the same for a three-parameter trigger.
        [Fact]
        public void PermitIf_ThreeParameterTrigger_WithMultipleGuards()
        {
            var sm = new StateMachine<State, Trigger>(State.A);
            var x = sm.SetTriggerParameters<int, string, bool>(Trigger.X);
            sm.Configure(State.A).PermitIf(x, State.B,
                Tuple.Create<Func<int, string, bool, bool>, string>((i, s, b) => i > 0, "positive"),
                Tuple.Create<Func<int, string, bool, bool>, string>((i, s, b) => b, "flag"));

            Assert.Throws<InvalidOperationException>(() => sm.Fire(x, 1, "any", false));
            Assert.Equal(State.A, sm.State);

            sm.Fire(x, 1, "any", true);
            Assert.Equal(State.B, sm.State);
        }
    }
}
