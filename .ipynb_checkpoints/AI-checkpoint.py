import copy
import time
import heapq


class Containers:
    def __init__(self, num, weight):
        self.num = num
        self.weight = weight


# defining initial state

initial_bays = [[(3, "heavy"), ], [(1, "light"), (6, "light"),], [], [(4, "light"),  (2, "heavy"), (5, "light")], [], []]
initial_crane_position = 5
initial_crane_container_held = 0
initial_cost = 0

''' initial state tuple composed ot state at [0] and cost at [1]
    to access elements of state we'll use state[0][index of element needed]'''
initial_state = ([initial_bays, initial_crane_position, initial_crane_container_held], 0)


def print_state(state_and_time):
    state = state_and_time[0]
    for i in range(len(state[0])):
        if i == state[1]:
            print(str(state[0][i])+" <-["+str(state[2])+"]-")
        else:
            print(str(state[0][i]))
    print("Total cost: "+str(state_and_time[1]))
    print()


def perform_action(state, action):
    new_state = copy.deepcopy(state[0])  # Copy the entire state (bays, crane position, container held)

    new_state_cost = state[1]  # Track the current cost
    if action == "RIGHT":
        if new_state[1] >= (len(new_state[0]) - 1):  # If already at the rightmost bay
            return None
        new_state[1] += 1  # Move crane to the right
        cost = 3
        if new_state[2] != 0:
            if new_state[2][1] == "heavy":
                cost += 1
    elif action == "LEFT":
        if new_state[1] <= 0:  # If already at the leftmost bay
            return None
        new_state[1] -= 1  # Move crane to the left
        cost = 3
        if new_state[2] != 0:
            if new_state[2][1] == "heavy":
                cost += 1
    elif action == "DROP":

        if new_state[2] == 0:  # If no container is held
            return None
        if len([new_state[1]]) >= 4:  # Check if the current bay has already 4 containers
            return None
        cost = 5 - len([new_state[1]])  # cost based on num of containers before drop off
        container = new_state[2]
        new_state[2] = 0  # Drop the container
        new_state[0][new_state[1]].append(container)  # Add the container to the current bay
    elif action == "PICK":
        if new_state[2] != 0:  # If a container is already held
            return None
        if len(new_state[0][new_state[1]]) == 0:  # If no containers in the current bay
            return None
        cost = 5 - len([new_state[1]])  # cost based on num of containers before pick up
        container = new_state[0][new_state[1]].pop()  # Pick up the top container
        new_state[2] = container
    else:
        return None  # Invalid action

    return new_state, new_state_cost + cost


# use to validate the agent's action
def is_action_valid(state, action):
    if perform_action(state, action):
        return True
    else:
        return False


def perform_action_sequence(state, actions):
    new_state = state
    for action in actions:
        print(f"Performing action: {action}")
        result = perform_action(new_state, action)
        if result is None:  # If the action is invalid, stop processing
            print(f"Action '{action}' is invalid in the current state.")
            return None
        new_state = result  # Update the state to the result of the action
        print_state(new_state)  # Print the state after each action
    print(f"Actions taken: {actions}")
    return new_state


def heuristic_function(previous_state, current_state):
    """ NOTE: we are generally decreasing estimation when state is believed to be optimal
        and increasing estimation when state is believed to not be optimal"""

    estimated_cost = 0
    # Initialize the dictionary to store bay indices for containers 1, 2, and 3
    current_bay_indices = {1: None, 2: None, 3: None}
    previous_bay_indices = {1: None, 2: None, 3: None}

    # check if containers are in crane and update bay indices according to crane position
    if current_state[0][2] != 0:
        container_id = current_state[0][2][0]
        if container_id in current_bay_indices:
            current_bay_indices[container_id] = current_state[0][1]
    if previous_state is not None and previous_state[0][2] != 0:
        container_id = previous_state[0][2][0]
        if container_id in previous_bay_indices:
            previous_bay_indices[container_id] = previous_state[0][1]

    # Loop through the rest of the bays and update the bay indices for containers 1, 2, and 3
    for i, bay in enumerate(current_state[0][0]):
        for container in bay:
            if container[0] in current_bay_indices:
                current_bay_indices[container[0]] = i
    if previous_state is not None:
        for i, bay in enumerate(previous_state[0][0]):
            for container in bay:
                if container[0] in previous_bay_indices:
                    previous_bay_indices[container[0]] = i

    # checks on container 1
    current_bay_index_1 = current_bay_indices[1]
    previous_bay_index_1 = previous_bay_indices[1]

    if current_bay_index_1 is not None:
        bay_at_index_1 = current_state[0][0][current_bay_index_1]
        # iterate through containers at 1's location
        for idx, container in enumerate(bay_at_index_1):
            if container[0] == 1:
                # increase estimation if 1 is not lowest
                if idx > 0:
                    estimated_cost += 1
                # decrease estimation if 1 is lowest
                elif idx == 0:
                    estimated_cost -= 1
                # increase estimation by num of containers above 1 if not 2
                if idx + 1 < len(bay_at_index_1):
                    if not bay_at_index_1[idx + 1][0] == 2:
                        estimated_cost += len(bay_at_index_1) - idx - 1
        # decrease cost if crane is holding cont 1 above an empty bay (good path to explore)
        if current_state[0][2] != 0 and current_state[0][2][0] == 1 and current_state[0][1] == current_bay_index_1 \
                and len(bay_at_index_1) == 0:
            estimated_cost -= 2

    # check current explored state against previous state
    if previous_bay_index_1 is not None:
        # assign previous 1's bay
        bay_at_index_1 = previous_state[0][0][previous_bay_index_1]
        containers_above_1 = []
        # find index of 1 in previous state
        for idx, container in enumerate(bay_at_index_1):
            if container[0] == 1:
                # assign all containers above 1 for use later
                containers_above_1 = bay_at_index_1[idx + 1:]
                ''' if container 1 is currently in crane, 
                    assigns estimation according to position of 1 in the previous state'''
                if current_state[0][2] != 0 and current_state[0][2][0] == 1:
                    if idx > 0:
                        estimated_cost -= 2
                    else:
                        estimated_cost += 2
        # if container picked up by crane was previously on 1 decrease cost
        if current_state[0][2] != 0:
            crane_container = current_state[0][2]
            for container in containers_above_1:
                if container == crane_container:
                    estimated_cost -= 2

    # checks on container 2
    current_bay_index_2 = current_bay_indices[2]
    previous_bay_index_2 = previous_bay_indices[2]
    if current_bay_index_2 is not None:
        ''' default checks are:
            - distance to container 1
            - if in same location as container 1:
                - if correctly above 1
                - num of containers above it'''
        # check distance to container 1
        estimated_cost += abs(current_bay_index_2 - current_bay_index_1)
        bay_at_index_2 = current_state[0][0][current_bay_index_2]
        for idx, container in enumerate(bay_at_index_2):
            if container[0] == 2:
                # check if container 2 is in the same bay as 1 but not above it
                if current_bay_index_2 == current_bay_index_1 and idx > 0 and bay_at_index_2[idx - 1][0] != 1:
                    estimated_cost += 1
                    estimated_cost += len(bay_at_index_2) - idx - 1

    # check current explored state against previous state
    if previous_bay_index_2 is not None:
        ''' if container 2 was picked up checks against two scenarios:
            - cont 2 was in same bay as cont 1
            - cont 2 was not in same bay as cont 1'''
        if current_state[0][2] != 0 and current_state[0][2][0] == 2:
            # checks if container 2 was in same bay as 1
            if previous_bay_index_2 == current_bay_index_1:
                bay_at_index_1 = previous_state[0][0][previous_bay_index_1]
                for idx, container in enumerate(bay_at_index_1):
                    if container[0] == 1:
                        # if container 1 was at the right position and container 2 was on top of it increase estimation
                        if idx == 0 and idx + 1 < len(bay_at_index_1) and bay_at_index_1[idx + 1][0] == 2:
                            estimated_cost += 2
                        # if container 1 was at the right position but container 2 was not on top of it decrease estimation
                        elif idx == 0 and idx + 1 < len(bay_at_index_1) and bay_at_index_1[idx + 1][0] != 2:
                            estimated_cost -= 2
                        # if container 1 was in the wrong position decrease cost
                        elif idx > 0:
                            estimated_cost -= 2
            # if container 2 was not on top of 1 decrease estimation
            elif previous_bay_index_2 != current_bay_index_1:
                estimated_cost -= 2

    # checks on container 3
    current_bay_index_3 = current_bay_indices[3]
    previous_bay_index_3 = previous_bay_indices[3]
    if current_bay_index_3 is not None:
        ''' default checks are:
                    - distance to container 1
                    - if in same location as container 1:
                        - if correctly above 2 and 1
                        - num of containers above it'''
        # check distance to container 1
        estimated_cost += abs(current_bay_index_3 - current_bay_index_1)
        bay_at_index_3 = current_state[0][0][current_bay_index_3]
        for idx, container in enumerate(bay_at_index_3):
            if container[0] == 3:
                # check if container 3 is in the same bay as 1 and not above it 2 and 1
                if current_bay_index_3 == current_bay_index_1 and idx > 0 and bay_at_index_3[idx - 1][0] != 2 \
                        and bay_at_index_3[idx - 2][0] != 1:
                    estimated_cost += 1
                    estimated_cost += len(bay_at_index_3) - idx - 1

    if previous_bay_index_3 is not None:
        ''' if container 3 was picked up checks against two scenarios:
                - cont 3 was in same bay as cont 1 and 2
                - cont 3 was not in same bay as cont 1 or 2'''
        # checks if the crane picked up container 3
        if current_state[0][2] != 0 and current_state[0][2][0] == 3:
            # checks if container 3 in same bay as 1 and 2
            if previous_bay_index_3 == current_bay_index_1 == current_bay_index_2:
                bay_at_index_1 = previous_state[0][0][current_bay_index_1]
                for idx, container in enumerate(bay_at_index_1):
                    if container[0] == 1:
                        # if container 1 was and cont 2 and 3 were stacked above it increase cost
                        if idx == 0 and idx + 1 < len(bay_at_index_1) and bay_at_index_1[idx + 1][0] == 2 and idx + 2 < len(bay_at_index_1) and bay_at_index_1[idx + 2][0] == 3:
                            estimated_cost += 2
                        # if container 1 was in the wrong position cont 2 and 1 were not below 3 decrease cost
                        elif idx > 0 or (idx + 1 < len(bay_at_index_1) and bay_at_index_1[idx + 1][0] != 2) or (idx + 2 < len(bay_at_index_1) and bay_at_index_1[idx + 2][0] != 3):
                            estimated_cost -= 2
            # checks if container 3 was not in same bay as 1 2
            elif previous_bay_index_3 != current_bay_index_1 or previous_bay_index_3 != current_bay_index_2:
                estimated_cost -= 2
    return estimated_cost


all_actions = ["DROP", "PICK", "LEFT", "RIGHT"]

def is_goal_state(state):
    bays, crane_position, crane_container_held = state[0]

    # Iterate through the bays
    for i, bay in enumerate(bays):
        # Check if this bay contains containers 1, 2, and 3 in order
        if [container[0] for container in bay] == [1, 2, 3]:
            # Check if the crane is not in the same bay
            if crane_position != i:
                return True

    # If we haven't returned True by now, it's not a goal state
    return False


def astar(initial_state, possible_actions=all_actions):

    """ A* algorithm will:
     1) hash the states in te frontier (for comparison purposes)
     2) pop state with lowest f from frontier
     3) flag the popped state as explored
     4) check if the goal state is reached
     5) apply actions to the state
     6) if any new state derived for the actions has already been explored, skip to next
     7) hash the new state
     8) add it to the frontier"""

    frontier = {}  # store states to be explored
    explored_states = []  # store states already explored

    initial_g = initial_state[1]
    initial_h = heuristic_function(None, initial_state)

    start = time.time()  # Time tracking restored

    # Hash the initial state
    state_hash = hash(str(initial_state))
    frontier[state_hash] = (initial_g + initial_h, (initial_state, []))

    while frontier:
        # Find the state with the smallest f-cost
        current_state_hash = min(frontier, key=lambda x: frontier[x][0])
        current_f, (state, actions) = frontier.pop(current_state_hash)

        # Mark the state as explored
        if tuple(state[0]) not in explored_states:  # Convert state[0] to tuple
            explored_states.append(tuple(state[0]))

        # Check if goal state is reached
        if is_goal_state(state):
            print("Initial State:")
            print_state(initial_state)
            print("Goal found:", str(actions).replace("[", "").replace("]", ""))
            perform_action_sequence(initial_state, actions)
            return True

        # Explore the next states
        for action in possible_actions:
            if is_action_valid(state, action):
                new_state = perform_action(state, action)

                # Skip already explored states
                if tuple(new_state[0]) in explored_states:
                    continue

                # Calculate costs
                new_g_cost = state[1] + new_state[1]
                new_h_cost = heuristic_function(state, new_state)
                new_f_cost = new_g_cost + new_h_cost

                # Hash the new state
                new_state_hash = hash(str(new_state))

                # Add the new state to the frontier
                frontier[new_state_hash] = (new_f_cost, (new_state, actions + [action]))

        # Check for timeout
        end = time.time()
        if end - start > 20:
            raise TimeoutError("Execution is taking too long to terminate.")


astar(initial_state)
