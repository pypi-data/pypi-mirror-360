"""Test suite for composite.py - Composite actions."""

import arcade

from actions.base import Action
from actions.composite import parallel, sequence


def create_test_sprite() -> arcade.Sprite:
    """Create a sprite with texture for testing."""
    sprite = arcade.Sprite(":resources:images/items/star.png")
    sprite.center_x = 100
    sprite.center_y = 100
    return sprite


class MockAction(Action):
    """Mock action for testing composite actions."""

    def __init__(self, duration=0.1, name="mock", condition=None, on_stop=None, check_interval=0.0):
        # If no condition provided, use a default one that never completes
        super().__init__(
            condition=condition if condition is not None else lambda: False,
            on_stop=on_stop,
            check_interval=check_interval,
        )
        self.duration = duration
        self.name = name
        self.time_elapsed = 0.0
        self.started = False
        self.stopped = False

    def start(self):
        super().start()
        self.started = True

    def update(self, delta_time: float):
        super().update(delta_time)
        if not self.done:
            self.time_elapsed += delta_time
            if self.time_elapsed >= self.duration:
                self.done = True

    def stop(self):
        super().stop()
        self.stopped = True

    def clone(self) -> "MockAction":
        new_action = MockAction(
            duration=self.duration,
            name=self.name,
            condition=self.condition,
            on_stop=self.on_stop,
            check_interval=self.check_interval,
        )
        new_action.tag = self.tag
        return new_action


class TestSequenceFunction:
    """Test suite for sequence() function."""

    def teardown_method(self):
        """Clean up after each test."""
        Action.clear_all()

    def test_sequence_empty_initialization(self):
        """Test empty sequence initialization."""
        seq = sequence()
        assert len(seq.actions) == 0
        assert seq.current_action is None
        assert seq.current_index == 0

    def test_sequence_with_actions_initialization(self):
        """Test sequence initialization with actions."""
        action1 = MockAction(name="action1")
        action2 = MockAction(name="action2")
        seq = sequence(action1, action2)

        assert len(seq.actions) == 2
        assert seq.actions[0] == action1
        assert seq.actions[1] == action2
        assert seq.current_action is None
        assert seq.current_index == 0

    def test_sequence_empty_completes_immediately(self):
        """Test that empty sequence completes immediately."""
        sprite = create_test_sprite()
        seq = sequence()
        seq.target = sprite
        seq.start()

        assert seq.done

    def test_sequence_starts_first_action(self):
        """Test that sequence starts the first action."""
        sprite = create_test_sprite()
        action1 = MockAction(name="action1")
        action2 = MockAction(name="action2")
        seq = sequence(action1, action2)

        seq.target = sprite
        seq.start()

        assert seq.current_action == action1
        assert seq.current_index == 0
        assert action1.started
        assert not action2.started

    def test_sequence_advances_to_next_action(self):
        """Test that sequence advances to next action when current completes."""
        sprite = create_test_sprite()
        action1 = MockAction(duration=0.05, name="action1")
        action2 = MockAction(duration=0.05, name="action2")
        seq = sequence(action1, action2)

        seq.target = sprite
        seq.start()

        # Update until first action completes
        seq.update(0.06)

        assert action1.done
        assert seq.current_action == action2
        assert seq.current_index == 1
        assert action2.started

    def test_sequence_completes_when_all_actions_done(self):
        """Test that sequence completes when all actions are done."""
        sprite = create_test_sprite()
        action1 = MockAction(duration=0.05, name="action1")
        action2 = MockAction(duration=0.05, name="action2")
        seq = sequence(action1, action2)

        seq.target = sprite
        seq.start()

        # Update until both actions complete
        seq.update(0.06)  # Complete first action
        seq.update(0.06)  # Complete second action

        assert action1.done
        assert action2.done
        assert seq.done
        assert seq.current_action is None

    def test_sequence_stop_stops_current_action(self):
        """Test that stopping sequence stops the current action."""
        sprite = create_test_sprite()
        action1 = MockAction(name="action1")
        action2 = MockAction(name="action2")
        seq = sequence(action1, action2)

        seq.target = sprite
        seq.start()
        seq.stop()

        assert action1.stopped

    def test_sequence_clone(self):
        """Test sequence cloning."""
        action1 = MockAction(name="action1")
        action2 = MockAction(name="action2")
        seq = sequence(action1, action2)

        cloned = seq.clone()

        assert cloned is not seq
        assert len(cloned.actions) == 2
        assert cloned.actions[0] is not action1
        assert cloned.actions[1] is not action2
        assert cloned.actions[0].name == "action1"
        assert cloned.actions[1].name == "action2"


class TestParallelFunction:
    """Test suite for parallel() function."""

    def teardown_method(self):
        """Clean up after each test."""
        Action.clear_all()

    def test_parallel_empty_initialization(self):
        """Test empty parallel initialization."""
        par = parallel()
        assert len(par.actions) == 0

    def test_parallel_with_actions_initialization(self):
        """Test parallel initialization with actions."""
        action1 = MockAction(name="action1")
        action2 = MockAction(name="action2")
        par = parallel(action1, action2)

        assert len(par.actions) == 2
        assert par.actions[0] == action1
        assert par.actions[1] == action2

    def test_parallel_empty_completes_immediately(self):
        """Test that empty parallel completes immediately."""
        sprite = create_test_sprite()
        par = parallel()
        par.target = sprite
        par.start()

        assert par.done

    def test_parallel_starts_all_actions(self):
        """Test that parallel starts all actions simultaneously."""
        sprite = create_test_sprite()
        action1 = MockAction(name="action1")
        action2 = MockAction(name="action2")
        par = parallel(action1, action2)

        par.target = sprite
        par.start()

        assert action1.started
        assert action2.started

    def test_parallel_completes_when_all_actions_done(self):
        """Test that parallel completes when all actions are done."""
        sprite = create_test_sprite()
        action1 = MockAction(duration=0.05, name="action1")
        action2 = MockAction(duration=0.1, name="action2")  # Longer duration
        par = parallel(action1, action2)

        par.target = sprite
        par.start()

        # Update until first action completes
        par.update(0.06)
        assert action1.done
        assert not par.done  # Parallel not done until all actions done

        # Update until second action completes
        par.update(0.05)
        assert action2.done
        assert par.done

    def test_parallel_stops_all_actions(self):
        """Test that stopping parallel stops all actions."""
        sprite = create_test_sprite()
        action1 = MockAction(name="action1")
        action2 = MockAction(name="action2")
        par = parallel(action1, action2)

        par.target = sprite
        par.start()
        par.stop()

        assert action1.stopped
        assert action2.stopped

    def test_parallel_clone(self):
        """Test parallel cloning."""
        action1 = MockAction(name="action1")
        action2 = MockAction(name="action2")
        par = parallel(action1, action2)

        cloned = par.clone()

        assert cloned is not par
        assert len(cloned.actions) == 2
        assert cloned.actions[0] is not action1
        assert cloned.actions[1] is not action2
        assert cloned.actions[0].name == "action1"
        assert cloned.actions[1].name == "action2"


class TestOperatorOverloading:
    """Test suite for operator-based composition (+ for sequence, | for parallel)."""

    def teardown_method(self):
        """Clean up after each test."""
        Action.clear_all()

    def test_plus_operator_creates_sequence(self):
        """Test that the '+' operator creates a sequential action."""
        sprite = create_test_sprite()
        action1 = MockAction(duration=0.05, name="action1")
        action2 = MockAction(duration=0.05, name="action2")

        # Use + operator to create sequence
        sequence_action = action1 + action2
        sequence_action.apply(sprite)

        # Should behave like a sequence
        Action.update_all(0.01)
        assert action1.started
        assert not action2.started

        # Update until first action completes
        Action.update_all(0.06)
        assert action1.done
        assert action2.started

    def test_pipe_operator_creates_parallel(self):
        """Test that the '|' operator creates a parallel action."""
        sprite = create_test_sprite()
        action1 = MockAction(name="action1")
        action2 = MockAction(name="action2")

        # Use | operator to create parallel
        parallel_action = action1 | action2
        parallel_action.apply(sprite)

        # Should behave like a parallel
        Action.update_all(0.01)
        assert action1.started
        assert action2.started

    def test_mixed_operator_composition(self):
        """Test mixing + and | operators for complex compositions."""
        sprite = create_test_sprite()
        action1 = MockAction(duration=0.05, name="action1")
        action2 = MockAction(duration=0.05, name="action2")
        action3 = MockAction(duration=0.05, name="action3")

        # Create a sequence where the second step is parallel actions
        complex_action = action1 + (action2 | action3)
        complex_action.apply(sprite)

        # First action should start
        Action.update_all(0.01)
        assert action1.started
        assert not action2.started
        assert not action3.started

        # After first action completes, parallel actions should start
        Action.update_all(0.06)
        assert action1.done
        assert action2.started
        assert action3.started

    def test_operator_precedence_with_parentheses(self):
        """Test operator precedence with explicit parentheses."""
        sprite = create_test_sprite()
        action1 = MockAction(duration=0.05, name="action1")
        action2 = MockAction(duration=0.05, name="action2")
        action3 = MockAction(duration=0.05, name="action3")

        # Test a + (b | c) - explicit parentheses
        composed = action1 + (action2 | action3)
        composed.apply(sprite)

        Action.update_all(0.01)
        assert action1.started
        assert not action2.started
        assert not action3.started

        Action.update_all(0.06)
        assert action2.started
        assert action3.started


class TestNestedComposites:
    """Test suite for nested composite actions."""

    def teardown_method(self):
        """Clean up after each test."""
        Action.clear_all()

    def test_sequence_of_parallels_with_operators(self):
        """Test sequence containing parallel actions using operators."""
        sprite = create_test_sprite()
        action1 = MockAction(duration=0.05, name="action1")
        action2 = MockAction(duration=0.05, name="action2")
        action3 = MockAction(duration=0.05, name="action3")
        action4 = MockAction(duration=0.05, name="action4")

        # Create sequence of parallels using operators
        composed = (action1 | action2) + (action3 | action4)
        composed.apply(sprite)

        # First parallel should start
        Action.update_all(0.01)
        assert action1.started
        assert action2.started
        assert not action3.started
        assert not action4.started

        # Update until first parallel completes
        Action.update_all(0.06)

        # Second parallel should start
        assert action3.started
        assert action4.started

    def test_parallel_of_sequences_with_operators(self):
        """Test parallel containing sequence actions using operators."""
        sprite = create_test_sprite()
        action1 = MockAction(duration=0.05, name="action1")
        action2 = MockAction(duration=0.05, name="action2")
        action3 = MockAction(duration=0.05, name="action3")
        action4 = MockAction(duration=0.05, name="action4")

        # Create parallel of sequences using operators
        composed = (action1 + action2) | (action3 + action4)
        composed.apply(sprite)

        # Both sequences should start (first actions of each)
        Action.update_all(0.01)
        assert action1.started
        assert not action2.started
        assert action3.started
        assert not action4.started

        # Update until first actions complete
        Action.update_all(0.06)

        # Second actions should start
        assert action2.started
        assert action4.started

    def test_traditional_vs_operator_equivalence(self):
        """Test that operator syntax produces equivalent results to function syntax."""
        sprite1 = create_test_sprite()
        sprite2 = create_test_sprite()

        # Traditional function approach
        action1_func = MockAction(duration=0.05, name="action1")
        action2_func = MockAction(duration=0.05, name="action2")
        traditional = sequence(action1_func, action2_func)
        traditional.apply(sprite1)

        # Operator approach
        action1_op = MockAction(duration=0.05, name="action1")
        action2_op = MockAction(duration=0.05, name="action2")
        operator_based = action1_op + action2_op
        operator_based.apply(sprite2)

        # Both should behave identically
        Action.update_all(0.01)
        assert action1_func.started == action1_op.started
        assert action2_func.started == action2_op.started

        Action.update_all(0.06)
        assert action1_func.done == action1_op.done
        assert action2_func.started == action2_op.started
