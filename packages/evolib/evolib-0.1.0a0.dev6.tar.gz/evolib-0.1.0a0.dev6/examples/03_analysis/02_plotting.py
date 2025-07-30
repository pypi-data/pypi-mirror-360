"""
Example 03-02 - Plotting

This example shows how to visualize the evolution history collected during a run.
It demonstrates how to:

- Access history data from the population
- Plot fitness statistics over generations
- Interpret trends using matplotlib
"""

from evolib import (
    Indiv,
    Pop,
    Strategy,
    evolve_mu_lambda,
    mse_loss,
    simple_quadratic,
)
from evolib.utils.plotting import plot_fitness


def my_fitness(indiv: Indiv) -> None:
    expected = 0.0
    predicted = simple_quadratic(indiv.para.vector)
    indiv.fitness = mse_loss(expected, predicted)


# Setup
my_pop = Pop(config_path="population.yaml")
my_pop.initialize_population()
my_pop.set_functions(fitness_function=my_fitness)

# Evolution
for _ in range(my_pop.max_generations):
    evolve_mu_lambda(my_pop, strategy=Strategy.MU_PLUS_LAMBDA)

# History to DataFrame
history = my_pop.history_logger.to_dataframe()

# Plotting
plot_fitness(history, show=True, save_path="./figures/02_plotting.png")
print("Plot saved to ./figures/02_plotting.png.")
