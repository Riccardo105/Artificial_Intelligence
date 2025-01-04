import copy
import time
import heapq


class Containers:
    def __init__(self, num, weight):
        self.num = num
        self.weight = weight


# defining initial state

initial_bays = [[(1, "light")], [], [(2, "heavy")], []]
initial_crane_position = 2
initial_crane_container_held = (3, "heavy")
initial_cost = 0

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


def goal_state(state):
    # Iterate over each bay
    for bay in state[0][0]:
        print(bay)
        # Extract the numbers of the containers in the current bay



all_actions = ["DROP", "PICK", "LEFT", "RIGHT"]


# use to validate the agent's action
def is_action_valid(state, action):
    if perform_action(state, action):
        return True
    else:
        return False


def heuristic_function(state):
    estimated_cost = 0
    bay_index_1 = None

    # iterating through the bays to look for target containers
    for i, bay in enumerate(state[0][0]):
        for j, container in enumerate(bay):
            if container[0] == 1:
                # first check is if next container is 2
                # second check (is first false) is num of containers above target (increase cost)
                bay_index_1 = i
                if j + 1 < len(bay):
                    if not bay[j + 1][0] == 2:
                        estimated_cost += len(bay) - j - 1
            if bay_index_1 is not None:  # once container 1 has been iterated through
                if container[0] in (2, 3):
                    # first check is num of containers above target (increase cost)
                    # second check is distance to container 1 (increase cost)
                    estimated_cost += len(bay) - j - 1
                    estimated_cost += abs(i - bay_index_1)

    if state[0][2] != 0 and state[0][2][0] in (2, 3):
        # first check is if crane is trying to pick up target container (decrease cost)
        # second check is distance to container 1 (dynamically increase. decrease)
        estimated_cost -= estimated_cost - 1
        estimated_cost += abs(state[0][1] - bay_index_1)

    return estimated_cost


def astar(initial_state, possible_actions=all_actions):
    frontier = []

    initial_g = initial_state[1]
    initial_h = heuristic_function(initial_state)
    counter = 0
    # state is pushed to frontier with value of f and actions list
    heapq.heappush(frontier, (initial_g + initial_h, counter, (copy.deepcopy(initial_state), [])))
    start = time.time()

    while frontier:

        current_f, counter, (state, actions) = heapq.heappop(frontier)
        print(state, actions)

        if goal_state(state):
            perform_action_sequence(state, actions)
            return True
        for action in possible_actions:
            # if the action is applicable in the given state
            if is_action_valid(state, action):
                # apply the action
                new_state = perform_action(state, action)

                new_g_cost = state[1] + new_state[1]
                new_h_cost = heuristic_function(new_state)
                new_f_cost = new_g_cost + new_h_cost
                heapq.heappush(frontier, (new_f_cost, counter,  (copy.deepcopy(new_state), actions + [action])))
                counter += 1

        # while not always necessary, it is a good idea in practice
        # to limit the execution of a potentially non-terminating
        # algorithm. For example by limiting the time it has available
        # before forcing it to terminate

        end = time.time()
        if end-start > 20:
            raise TimeoutError("Execution is taking too long to terminate.")



print(heuristic_function(initial_state))
