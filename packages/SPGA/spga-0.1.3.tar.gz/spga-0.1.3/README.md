# SPGA: Simple and Personalizable Genetic Algorithm

[![PyPI version](https://img.shields.io/pypi/v/spga.svg)](https://pypi.org/project/spga/)
[![Python versions](https://img.shields.io/pypi/pyversions/spga.svg)](https://pypi.org/project/spga/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Overview
SPGA is a lightweight Python framework for building customizable genetic algorithms. Designed for education and production, it offers:
- Full control over genetic operations
- Clean generational workflow
- Built-in progress visualization
- Minimal dependencies (NumPy + Matplotlib)
- Pre-built genetic operators


```bash
pip install spga
```

## Quickstart
```python
import math
import random
import numpy as np
from spga import (
    genetic_algorithm,
    Solution,
    create_genetic_operations,
    tournament_selection,
    mean_crossover,
    uniform_mutation
)

# 1. Problem configuration
SEARCH_SPACE = (0, 12.55)  # Search space boundaries
POPULATION_SIZE = 100
NUM_ITERATIONS = 100

def population_generator(**kwargs):

    return [Solution(
        solution=[random.uniform(*SEARCH_SPACE)],
        fitness=None
    ) for _ in range(kwargs['population_size'])]

def evaluate_fitness(individual, **kwargs):

    x = individual.solution[0]
    if x > SEARCH_SPACE[1] or x < SEARCH_SPACE[0]:
        return 0
    return math.sin(x) * (x ** 2)

# 4. Algorithm configuration
ga_args = {
    'population_size': POPULATION_SIZE,
    'num_iterations': NUM_ITERATIONS,
    'optimization': 'max',  # Optimization direction
    'tournament_size': 3,  # Number of individuals in tournament
    'mutation_probability': 0.15,  # Probability of mutation
    'crossover_probability': 0.8,    # Probability of crossover (disabled here)
    'max_its_with_enhancing': 20  # Max iterations without improvement
}

# Configure genetic operations pipeline
genetic_operations = create_genetic_operations(
    selection_func=tournament_selection,
    crossover_func=mean_crossover,
    mutation_func=uniform_mutation,
    elitism=True
)

# 5. Algorithm execution
result = genetic_algorithm(
    population_generator=population_generator,
    evaluate_fitness=evaluate_fitness,
    genetic_operations=genetic_operations,
    args=ga_args,
    verbose=True,
    plot=True
)
# 6. Results output
print("\n--- FINAL RESULTS ---")
print(f"Best solution found: x = {result.best_solution[0]:.4f}")
print(f"Function value: f(x) = {result.best_fitness:.4f}")
```



## Custom Genetic Operators

### Custom Selection Operator

```python
from spga import BaseOperator

def custom_tournament(population, **kargs):
    optimization = kargs['optimization']
    tournament_size = kargs.get('tournament_size', 3)
    new_population = []
    for i in range(len(population)):
        tournament = random.sample(population, tournament_size)
        if optimization == 'max':
            best = max(tournament, key=lambda x: x.fitness)
        else:
            best = min(tournament, key=lambda x: x.fitness)
        new_population.append(best)
    return new_population
```
## Custom Crossover Operator

```python

def custom_uniform_crossover(parent1, parent2, **kargs):
    child1,child2 = [],[]
    for i in range(len(parent1.solution)):
        if random.random() < 0.5:
            child1.append(parent1.solution[i])
            child2.append(parent2.solution[i])
        else:
            child1.append(parent2.solution[i])
            child2.append(parent1.solution[i])
    return Solution(solution=child1, fitness=None),Solution(solution=child2, fitness=None)
```
### Custom Selection Operator

```python

def custom_constant_mutation(individual, **kargs):
    for i in range(len(individual.solution)):
        index = random.randint(0, len(individual.solution)-1)
        fact = 1.0
        if random.random() < 0.5:
            fact = -1.0
        individual.solution[index] = individual.solution[index] + fact * 0.01
    return individual
```
## Key Features

### Progress Tracking
```python

result = genetic_algorithm(..., plot=True)  # Auto-generates fitness plot
```

### Progress Tracking
```python
args = {
    'population_size': 50,
    'num_iterations': 200,
    'optimization': 'min',
    'early_stop': True,  # Stop if solution is good enough
    'log_scale': True    # Plot fitness in log scale
}
```

# Documentation

# Contributing

Contributions welcome! Please submit:

- Bug reports via issues

- Feature requests via issues