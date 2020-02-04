import numpy as np
import random
import copy
import matplotlib.pyplot as plt
import seaborn as sns


def map_init(chance_of_zeros, size):
    our_map = np.zeros((size, size))
    for i in range(0, size):
        for j in range(0, i):
            if random.random() > chance_of_zeros:
                our_map[i][j] = random.random()
                our_map[j][i] = our_map[i][j]

    return our_map


def generate_starting_paths(size, our_map):
    paths = []
    for i in range(0, size):
        paths.append(generate_new_path(our_map))

    return paths


def fitnes(path, our_map):
    the_score = 0
    for i in range(1, len(path)):
        if (our_map[path[i - 1]][path[i]] == 0) and i != len(our_map) - 1:
            print("Something went wrong with our path")
        the_score = the_score + our_map[path[i - 1]][path[i]]

    return the_score


def crossing(a, b):
    elements_in_common = set(a) & set(b)
    if len(elements_in_common) == 2:
        return a, b
    else:
        elements_in_common.remove(0)
        elements_in_common.remove(max(a))
        value = random.sample(elements_in_common, 1)

    cut_a = np.random.choice(np.where(np.isin(a, value))[0])
    cut_b = np.random.choice(np.where(np.isin(b, value))[0])

    new_a1 = copy.deepcopy(a[0:cut_a])
    new_a2 = copy.deepcopy(b[cut_b:])

    new_b1 = copy.deepcopy(b[0:cut_b])
    new_b2 = copy.deepcopy(a[cut_a:])

    new_a = np.append(new_a1, new_a2)
    new_b = np.append(new_b1, new_b2)

    return new_a, new_b


def mutate(path, probability, our_map):
    new_path = copy.deepcopy(path)
    for i in range(1, len(new_path)):
        if random.random() < probability:
            should_go = True
            while should_go:

                possible_values = np.nonzero(our_map[new_path[i - 1]])
                selected_values = random.randint(0, len(possible_values[0]) - 1)
                np.append(new_path, possible_values[0][selected_values])

                if new_path[i] == len(our_map) - 1:
                    should_go = False
                else:
                    i += 1

    return new_path


def generate_new_path(our_map):
    size_of_map = len(our_map)
    path = np.zeros(1, dtype=int)
    should_go = True
    i = 1

    while should_go:

        possible_values = np.nonzero(our_map[path[i - 1]])
        selected_values = random.randint(0, len(possible_values[0]) - 1)
        path = np.append(path, possible_values[0][selected_values])

        if path[i] == size_of_map - 1:
            should_go = False
        else:
            i += 1

    return path


def get_population_score(paths, our_map):
    scores = []
    for i in range(0, len(paths)):
        scores += [fitnes(paths[i], our_map)]

    return scores


def choose_paths_for_crossing(scores):
    array = np.array(scores)
    temp = array.argsort()
    ranks = np.empty_like(temp)
    ranks[temp] = np.arange(len(array))

    fitnes = [len(ranks) - x for x in ranks]

    aggregate_scores = copy.deepcopy(fitnes)

    for i in range(1, len(aggregate_scores)):
        aggregate_scores[i] = fitnes[i] + aggregate_scores[i - 1]

    probability = [x / aggregate_scores[-1] for x in aggregate_scores]

    rand = random.random()

    for i in range(0, len(probability)):
        if rand < probability[i]:
            return i


def main():
    num_of_zeroes = 0.7
    size_of_map = 200
    size_of_population = 30
    num_of_iterations = 100
    num_of_pairs = 9
    num_of_winners_to_keep = 2

    our_map = map_init(num_of_zeroes, size_of_map)

    paths = generate_starting_paths(size_of_population, our_map)

    final_distance = 1000000

    for i in range(0, num_of_iterations):
        new_paths = []

        scores = get_population_score(paths, our_map)

        best = paths[np.argmin(scores)]
        num_of_moves = len(best)
        distance = fitnes(best, our_map)

        if distance != final_distance:
            print('Current iteration is %i and the best steps so far are %i with distance of %f' % (i, num_of_moves, distance))
            draw(our_map, best, i)

        for j in range(0, num_of_pairs):
            new_1, new_2 = crossing(paths[choose_paths_for_crossing(scores)], paths[choose_paths_for_crossing(scores)])
            new_paths = new_paths + [new_1, new_2]

        for j in range(0, len(new_paths)):
            new_paths[j] = np.copy(mutate(new_paths[j], 0.05, our_map))

        new_paths += [paths[np.argmin(scores)]]
        for j in range(1, num_of_winners_to_keep):
            keep = choose_paths_for_crossing(scores)
            new_paths += [paths[keep]]

        while len(new_paths) < size_of_population:
            new_paths += [generate_new_path(our_map)]

        paths = copy.deepcopy(new_paths)

        final_distance = distance


def draw(our_map, path, num_of_iteration):
    sns.heatmap(our_map)

    x = [0.5] + [x + 0.5 for x in path[0:len(path) - 1]] + [len(our_map) - 0.5]
    y = [0.5] + [x + 0.5 for x in path[1:len(path)]] + [len(our_map) - 0.5]

    plt.plot(x, y, marker='o', linewidth=4, markersize=12, linestyle="-", color='white')
    plt.savefig('images/plot_%i.png' % (num_of_iteration), dpi=300)
    plt.show()

main()

