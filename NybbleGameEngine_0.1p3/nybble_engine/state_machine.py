
class StateMachine(object):

    class Transition(object):

        def __init__(self):

            # This is a list of boolean functions that tested. If
            # all functions return true then we can go to the next state
            self.conditions = list()

            self.next_state = None

        # A condition is just a function that must evaluate to true or false
        def add_condition(self, function_condition):
            self.conditions.append(function_condition)

        # check to see if the conditions of the transmission all evaluate to true
        def all_conditions_met(self):
            for condition in self.conditions:

                # condition failed
                if not condition():
                    return False
            # all conditions evaluated to true
            return True

    class State(object):
        def __init__(self, name="default"):
            self.name = name

            # a list of transitions to some other state
            self.transitions = list()

        # The init() is basically like a reset. When there is a transition to a new state
        # this function automatically called.
        def init(self):
            pass

        def add_transition(self, new_transition):
            self.transitions.append(new_transition)

        def __eq__(self, other):
            return self.name == other.name

    def __init__(self):
        self.states = list()
        self.current_state = None

    # this function is to update the state machine based on the conditions of the current state
    def update(self):

        # this is the transition that we can traverse between states if all of its conditions are met
        valid_transition = None

        # go through every transition of the current state
        for transition in self.current_state.transitions:

            # make sure that all conditions are met for this transition
            if transition.all_conditions_met():
                valid_transition = transition
                break

        # go to the next state
        if valid_transition is not None:
            self.current_state = valid_transition.next_state

    def add_state(self, new_state):
        self.states.append(new_state)

    def add_transition_from(self, state_a_name, state_b_name, new_transition):

        state_a = self.get_state(state_a_name)
        state_b = self.get_state(state_b_name)

        # failed to find the states
        if state_a is None or state_b is None:
            return

        # add a transition from a to b
        new_transition.next_state = state_b
        state_a.add_transition(new_transition)

    def get_state(self, state_name):
        for state in self.states:
            if state.name == state_name:
                return state
        return None