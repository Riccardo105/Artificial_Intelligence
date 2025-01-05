

initial_bays = [[(1, "light"),  (2, "heavy"), ], [(6, "light"),], [(3, "heavy")], [(4, "light"),], [(5, "light")], []]
initial_crane_position = 5
initial_crane_container_held = 0
initial_cost = 1

initial_state = ([initial_bays, initial_crane_position, initial_crane_container_held], 0)

next_bays = [[(2, "heavy")], [(6, "light"),], [(3, "heavy")], [(4, "light"),], [(5, "light")], []]
next_crane_position = 5
next_crane_container_held = (1, "light")
next_cost = 0

next_state = ([next_bays, next_crane_position, next_crane_container_held], 0)


def heuristic_function(previous_state, current_state, previous_crane_position=None):
    estimated_cost = 0
    # Initialize the dictionary to store bay indices for containers 1, 2, and 3
    current_bay_indices = {1: None, 2: None, 3: None}
    previous_bay_indices = {1: None, 2: None, 3: None}

    # check that crane is not stuck in a right-left loop
    current_crane_position = current_state[0][1]
    if current_crane_position == previous_crane_position:
        estimated_cost += 10

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
        print(current_bay_index_1)
        print(current_crane_position)
        print(current_state[0][2][0])
        print(bay_at_index_1)
        for idx, container in enumerate(bay_at_index_1):
            # check if container 1 is not the lowest (increase cost)
            if container[0] == 1:
                if idx > 0:
                    estimated_cost += 1
                # check how many containers are on top of 1 that are not 2 (increase cost)
                if idx + 1 < len(bay_at_index_1):
                    if not bay_at_index_1[idx + 1][0] == 2:
                        estimated_cost += len(bay_at_index_1) - idx - 1
        if current_state[0][2] != 0 and current_state[0][2][0] == 1 and current_state[0][1] == current_bay_index_1 \
        and len(bay_at_index_1) == 0:
            estimated_cost -= 15

    if previous_bay_index_1 is not None:
        bay_at_index_1 = previous_state[0][0][previous_bay_index_1]
        containers_above_1 = []
        # check if container 1 is picked up when it was in wrong position (decrease) when in correct position (increase)
        for idx, container in enumerate(bay_at_index_1):
            if container[0] == 1:
                containers_above_1 = bay_at_index_1[idx + 1:]
                if current_state[0][2] != 0 and current_state[0][2][0] == 1:
                    if idx > 0:
                        estimated_cost -= 5
                    else:
                        estimated_cost += 5
            if current_state[0][2] != 0 and current_state[0][2][0] == 2 and current_state[0][1] == bay_at_index_1 \
                    and bay_at_index_1[0][0] == 1 and len(bay_at_index_1) == 1:
                estimated_cost -= 5
        # check if trying to pick up a container that was previously bocking 1 (decrease cost)
        if current_state[0][2] != 0:
            crane_container = current_state[0][2]  # Container in the crane
            for container in containers_above_1:
                if container == crane_container:
                    estimated_cost -= 5

    # checks on container 2
    current_bay_index_2 = current_bay_indices[2]
    previous_bay_index_2 = previous_bay_indices[2]
    if current_bay_index_2 is not None:
        # check distance to container 1
        estimated_cost += abs(current_bay_index_2 - current_bay_index_1)
        bay_at_index_2 = current_state[0][0][current_bay_index_2]
        for idx, container in enumerate(bay_at_index_2):
            if container[0] == 2:
                # check if container 2 is in the same bay as 1 but not above it
                if current_bay_index_2 == current_bay_index_1 and idx > 0 and bay_at_index_2[idx - 1][0] != 1 :
                    estimated_cost += 1
                    estimated_cost += len(bay_at_index_2) - idx - 1

    if previous_bay_index_2 is not None:
        # checks if the crane picked up container 3
        if current_state[0][2] != 0 and current_state[0][2][0] == 2:
            # checks if container 2 was in same bay as 1
            if previous_bay_index_2 == current_bay_index_1:
                bay_at_index_1 = previous_state[0][0][previous_bay_index_1]
                for idx, container in enumerate(bay_at_index_1):
                    if container[0] == 1:
                        print(idx)
                        print(bay_at_index_1)
                        # if container 1 was at the right position increase cost
                        if idx == 0 and bay_at_index_1[idx + 1][0] == 2:
                            estimated_cost += 5
                        # if container 1 was in the wrong position increase cost
                        elif idx > 0 or bay_at_index_1[idx + 1][0] != 2:
                            estimated_cost -= 5
                # checks if container 2 was not above 1
            elif previous_bay_index_2 != current_bay_index_1:
                estimated_cost -= 5

    # checks on container 3
    current_bay_index_3 = current_bay_indices[3]
    previous_bay_index_3 = previous_bay_indices[3]
    if current_bay_index_3 is not None:
        # check distance to container 1
        estimated_cost += abs(current_bay_index_3 - current_bay_index_1)
        bay_at_index_3 = current_state[0][0][current_bay_index_3]
        for idx, container in enumerate(bay_at_index_3):
            if container[0] == 3:
                # check if container 3 is in the same bay as 1 and not above it 2 and 1
                if current_bay_index_3 == current_bay_index_1 and idx > 0 and bay_at_index_3[idx - 1][0] != 2 and bay_at_index_3[idx - 2][0] != 1:
                    estimated_cost += 1
                    estimated_cost += len(bay_at_index_3) - idx - 1

    if previous_bay_index_3 is not None:
        # checks if the crane picked up container 3
        if current_state[0][2] != 0 and current_state[0][2][0] == 3:
            # checks if container 3 was above 2
            if previous_bay_index_3 == current_bay_index_1 == current_bay_index_2:
                bay_at_index_1 = previous_state[0][0][current_bay_index_1]
                for idx, container in enumerate(bay_at_index_1):
                    if container[0] == 1:
                        # if container 1 was at the right position increase cost
                        if idx == 0 and bay_at_index_1[idx + 1][0] == 2 and bay_at_index_1[idx + 2][0] == 3:
                            print("hello")
                            estimated_cost += 5
                        # if container 1 was in the wrong position decrease cost
                        elif idx > 0 or bay_at_index_1[idx + 1][0] != 2 or bay_at_index_1[idx + 2][0] != 3:
                            estimated_cost -= 5
            # checks if container 3 was not in same bay as 1 2
            elif previous_bay_index_3 != current_bay_index_1 and previous_bay_index_3 != current_bay_index_2:
                estimated_cost += 5

    return estimated_cost


print(heuristic_function(initial_state, next_state))


