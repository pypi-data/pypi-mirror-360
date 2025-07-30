import pygad
import random
import numpy

num_generations = 1

initial_population = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                      [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                      [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                      [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                      [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                      [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                      [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                      [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                      [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                      [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]]

def population_gene_constraint(gene_space=None,
                               gene_type=float,
                               num_genes=10,
                               mutation_by_replacement=False,
                               random_mutation_min_val=-1,
                               random_mutation_max_val=1,
                               init_range_low=-4,
                               init_range_high=4,
                               random_seed=123,
                               crossover_type='single_point',
                               initial_population=None,
                               parent_selection_type='sss',
                               multi_objective=False,
                               gene_constraint=None,
                               allow_duplicate_genes=True):

    def fitness_func_no_batch_single(ga, solution, idx):
        return random.random()

    def fitness_func_no_batch_multi(ga, solution, idx):
        return [random.random(), random.random()]

    if multi_objective == True:
        fitness_func = fitness_func_no_batch_multi
    else:
        fitness_func = fitness_func_no_batch_single

    ga_instance = pygad.GA(num_generations=num_generations,
                           num_parents_mating=5,
                           fitness_func=fitness_func,
                           sol_per_pop=10,
                           num_genes=num_genes,
                           gene_space=gene_space,
                           gene_type=gene_type,
                           initial_population=initial_population,
                           parent_selection_type=parent_selection_type,
                           init_range_low=init_range_low,
                           init_range_high=init_range_high,
                           random_mutation_min_val=random_mutation_min_val,
                           random_mutation_max_val=random_mutation_max_val,
                           allow_duplicate_genes=allow_duplicate_genes,
                           mutation_by_replacement=mutation_by_replacement,
                           random_seed=random_seed,
                           crossover_type=crossover_type,
                           gene_constraint=gene_constraint,
                           save_solutions=True,
                           suppress_warnings=False)

    ga_instance.run()

    return ga_instance

#### Single-Objective
def test_initial_population_int_by_replacement():
    gene_constraint=[lambda x,v: [val for val in v if val>=8],
                     lambda x,v: [val for val in v if val>=8],
                     lambda x,v: [val for val in v if 5>=val>=1],
                     lambda x,v: [val for val in v if 5>val>3],
                     lambda x,v: [val for val in v if val<2]]
    ga_instance = population_gene_constraint(gene_constraint=gene_constraint,
                                             init_range_low=0,
                                             init_range_high=10,
                                             random_mutation_min_val=0,
                                             random_mutation_max_val=10,
                                             num_genes=5,
                                             gene_type=int,
                                             mutation_by_replacement=True)
    initial_population = ga_instance.initial_population

    assert numpy.all(initial_population[:, 0] >= 8), "Not all values in column 0 are >= 8"
    assert numpy.all(initial_population[:, 1] >= 8), "Not all values in column 1 are >= 8"
    assert numpy.all(initial_population[:, 2] >= 1), "Not all values in column 2 are >= 1"
    assert numpy.all((initial_population[:, 2] >= 1) & (initial_population[:, 2] <= 5)), "Not all values in column 2 between 1 and 5 (inclusive)"
    assert numpy.all(initial_population[:, 3] == 4), "Not all values in column 3 between 3 and 5 (exclusive)"
    assert numpy.all(initial_population[:, 4] < 2), "Not all values in column 4 < 2"
    print("All constraints are met")

def test_initial_population_int_by_replacement_no_duplicates():
    gene_constraint=[lambda x,v: [val for val in v if val>=5],
                     lambda x,v: [val for val in v if val>=5],
                     lambda x,v: [val for val in v if val>=5],
                     lambda x,v: [val for val in v if val>=5],
                     lambda x,v: [val for val in v if val>=5]]
    ga_instance = population_gene_constraint(gene_constraint=gene_constraint,
                                             init_range_low=1,
                                             init_range_high=10,
                                             random_mutation_min_val=1,
                                             random_mutation_max_val=10,
                                             gene_type=int,
                                             num_genes=5,
                                             mutation_by_replacement=True,
                                             allow_duplicate_genes=False)

    num_duplicates = 0
    for idx, solution in enumerate(ga_instance.solutions):
        num = len(solution) - len(set(solution))
        if num != 0:
            print(solution, idx)
        num_duplicates += num

    assert num_duplicates == 0

    initial_population = ga_instance.initial_population
    # print(initial_population)

    assert numpy.all(initial_population[:, 0] >= 5), "Not all values in column 0 >= 5"
    assert numpy.all(initial_population[:, 1] >= 5), "Not all values in column 1 >= 5"
    assert numpy.all(initial_population[:, 2] >= 5), "Not all values in column 2 >= 5"
    assert numpy.all(initial_population[:, 3] >= 5), "Not all values in column 3 >= 5"
    assert numpy.all(initial_population[:, 4] >= 5), "Not all values in column 4 >= 5"
    print("All constraints are met")

def test_initial_population_int_by_replacement_no_duplicates2():
    gene_constraint=[lambda x,v: [val for val in v if val>=98],
                     lambda x,v: [val for val in v if val>=98],
                     lambda x,v: [val for val in v if 20<val<40],
                     lambda x,v: [val for val in v if val<40],
                     lambda x,v: [val for val in v if val<50],
                     lambda x,v: [val for val in v if val<100]]
    ga_instance = population_gene_constraint(gene_constraint=gene_constraint,
                                             random_mutation_min_val=1,
                                             random_mutation_max_val=100,
                                             init_range_low=1,
                                             init_range_high=100,
                                             gene_type=int,
                                             num_genes=6,
                                             crossover_type=None,
                                             mutation_by_replacement=True,
                                             allow_duplicate_genes=False)

    num_duplicates = 0
    for idx, solution in enumerate(ga_instance.solutions):
        num = len(solution) - len(set(solution))
        if num != 0:
            print(solution, idx)
        num_duplicates += num

    assert num_duplicates == 0

    initial_population = ga_instance.initial_population
    # print(initial_population)

    assert numpy.all(initial_population[:, 0] >= 98), "Not all values in column 0 are >= 98"
    assert numpy.all(initial_population[:, 1] >= 98), "Not all values in column 1 are >= 98"
    assert numpy.all((initial_population[:, 2] > 20) & (initial_population[:, 2] < 40)), "Not all values in column 2 between 20 and 40 (exclusive)"
    assert numpy.all(initial_population[:, 3] < 40), "Not all values in column 3 < 40"
    assert numpy.all(initial_population[:, 4] < 50), "Not all values in column 4 < 50"
    assert numpy.all(initial_population[:, 5] < 100), "Not all values in column 4 < 100"
    print("All constraints are met")

def test_initial_population_float_by_replacement_no_duplicates():
    gene_constraint=[lambda x,v: [val for val in v if val>=5],
                     lambda x,v: [val for val in v if val>=5],
                     lambda x,v: [val for val in v if val>=5],
                     lambda x,v: [val for val in v if val>=5],
                     lambda x,v: [val for val in v if val>=5]]
    ga_instance = population_gene_constraint(gene_constraint=gene_constraint,
                                             init_range_low=1,
                                             init_range_high=10,
                                             gene_type=[float, 1],
                                             num_genes=5,
                                             crossover_type=None,
                                             mutation_by_replacement=False,
                                             allow_duplicate_genes=False)

    num_duplicates = 0
    for idx, solution in enumerate(ga_instance.solutions):
        num = len(solution) - len(set(solution))
        if num != 0:
            print(solution, idx)
        num_duplicates += num

    assert num_duplicates == 0

    initial_population = ga_instance.initial_population
    # print(initial_population)

    assert numpy.all(initial_population[:, 0] >= 5), "Not all values in column 0 >= 5"
    assert numpy.all(initial_population[:, 1] >= 5), "Not all values in column 1 >= 5"
    assert numpy.all(initial_population[:, 2] >= 5), "Not all values in column 2 >= 5"
    assert numpy.all(initial_population[:, 3] >= 5), "Not all values in column 3 >= 5"
    assert numpy.all(initial_population[:, 4] >= 5), "Not all values in column 4 >= 5"
    print("All constraints are met")

def test_initial_population_float_by_replacement_no_duplicates2():
    gene_constraint=[lambda x,v: [val for val in v if val>=1],
                     lambda x,v: [val for val in v if val>=1],
                     lambda x,v: [val for val in v if val>=1],
                     lambda x,v: [val for val in v if val>=1],
                     lambda x,v: [val for val in v if val>=1]]
    ga_instance = population_gene_constraint(gene_constraint=gene_constraint,
                                             init_range_low=1,
                                             init_range_high=2,
                                             gene_type=[float, 1],
                                             num_genes=5,
                                             crossover_type=None,
                                             mutation_by_replacement=False,
                                             allow_duplicate_genes=False)

    num_duplicates = 0
    for idx, solution in enumerate(ga_instance.solutions):
        num = len(solution) - len(set(solution))
        if num != 0:
            print(solution, idx)
        num_duplicates += num

    assert num_duplicates == 0

    initial_population = ga_instance.initial_population
    # print(initial_population)

    assert numpy.all(initial_population[:, 0] >= 1), "Not all values in column 0 >= 1"
    assert numpy.all(initial_population[:, 1] >= 1), "Not all values in column 1 >= 1"
    assert numpy.all(initial_population[:, 2] >= 1), "Not all values in column 2 >= 1"
    assert numpy.all(initial_population[:, 3] >= 1), "Not all values in column 3 >= 1"
    assert numpy.all(initial_population[:, 4] >= 1), "Not all values in column 4 >= 1"
    print("All constraints are met")

def test_initial_population_float_by_replacement_no_duplicates_None_constraints():
    gene_constraint=[lambda x,v: [val for val in v if val>=1],
                     None,
                     lambda x,v: [val for val in v if val>=1],
                     None,
                     lambda x,v: [val for val in v if val>=1]]
    ga_instance = population_gene_constraint(gene_constraint=gene_constraint,
                                             init_range_low=1,
                                             init_range_high=2,
                                             gene_type=[float, 1],
                                             num_genes=5,
                                             crossover_type=None,
                                             mutation_by_replacement=False,
                                             allow_duplicate_genes=False)

    num_duplicates = 0
    for idx, solution in enumerate(ga_instance.solutions):
        num = len(solution) - len(set(solution))
        if num != 0:
            print(solution, idx)
        num_duplicates += num

    assert num_duplicates == 0

    initial_population = ga_instance.initial_population
    # print(initial_population)

    assert numpy.all(initial_population[:, 0] >= 1), "Not all values in column 0 >= 1"
    assert numpy.all(initial_population[:, 1] >= 1), "Not all values in column 1 >= 1"
    assert numpy.all(initial_population[:, 2] >= 1), "Not all values in column 2 >= 1"
    assert numpy.all(initial_population[:, 3] >= 1), "Not all values in column 3 >= 1"
    assert numpy.all(initial_population[:, 4] >= 1), "Not all values in column 4 >= 1"
    print("All constraints are met")

if __name__ == "__main__":
    #### Single-objective
    print()
    test_initial_population_int_by_replacement()
    print()
    test_initial_population_int_by_replacement_no_duplicates()
    print()
    test_initial_population_int_by_replacement_no_duplicates2()
    print()
    test_initial_population_float_by_replacement_no_duplicates()
    print()
    test_initial_population_float_by_replacement_no_duplicates2()
    print()
    test_initial_population_float_by_replacement_no_duplicates_None_constraints()
    print()
