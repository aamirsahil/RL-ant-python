# RL-ant-python

Base code for reinforcement-based ant pheromone trail production.

The project implements a grid-based ant simulation in which agents use Q-learning to choose actions such as depositing pheromone, following pheromone trails, and moving randomly. An optional neural-network component is used for the agent's internal state/memory experiments.

## Repository structure

```text
RL-ant-python/
│
├── main.py
├── internal_external_multi.py
├── cellular.py
└── README.md
```

### `cellular.py`

Provides the generic cellular-world simulation framework.

The main components are:

* `World` — manages the grid and the collection of agents.
* `Agent` — provides basic movement, orientation, sensing, and interaction with the grid.
* `Cell` — base cell representation used by the world.

### `internal_external_multi.py`

Contains the ant-specific implementation.

Important components:

* `Cell` — extends the cell representation with:

  * `isHome`
  * `isFood`
  * `homePher`
  * `foodPher`

* `Agent` — extends `cellular.Agent` and implements:

  * Q-learning
  * pheromone deposition
  * pheromone following
  * random movement
  * food/home state
  * internal neural-network state
  * agent birth/death/rebirth experiments

* `run()` — creates the world, loads the map, creates the ants, and executes the simulation.

### `main.py`

Provides the main experiment driver.

The current `main.py` configures a study and launches multiple simulations using Python's multiprocessing module. It calls:

```python
internal_external_multi.multiProcessSimulation(
    os.cpu_count(),
    lst,
    main
)
```

The current configuration runs five simulations and saves their output using `pickle`.

## Requirements

The code is Python-based and uses the standard library modules including:

* `random`
* `pickle`
* `multiprocessing`
* `json`
* `os`
* `sys`

The simulation also imports two project dependencies:

```python
import qlearn
import backprop
```

Therefore, `qlearn.py` and `backprop.py` must be available in the Python import path before the simulation can run. They are currently imported by `internal_external_multi.py` but are not present in the repository's current top-level file listing.

## Running the simulation

Clone the repository:

```bash
git clone https://github.com/aamirsahil/RL-ant-python.git
cd RL-ant-python
```

Then run:

```bash
python main.py
```

or, explicitly with Python 3:

```bash
python3 main.py
```

On Windows:

```powershell
py main.py
```

`main.py` is the intended entry point for the complete experiment. It imports `internal_external_multi`, configures the experiment, and starts the multiprocessing simulation.

## Running the core simulation directly

The simulation can also be invoked directly from Python:

```python
import internal_external_multi

data = internal_external_multi.run(
    4.0,
    exper=internal_external_multi.experiment
)
```

The `run()` function:

1. Creates a `cellular.World`.
2. Loads the map specified by `map`.
3. Finds the home cells.
4. Creates `antCount` agents.
5. Places the agents at home.
6. Runs the simulation for `time` iterations.
7. Records agent positions, actions, pheromone state, food collection, Q-values, rewards, and dropper state.

This execution path is implemented in `internal_external_multi.py`.

## Main simulation parameters

The default parameters defined in `internal_external_multi.py` include:

| Parameter         | Default | Description                      |
| ----------------- | ------: | -------------------------------- |
| `width`           |    `30` | World width                      |
| `height`          |    `30` | World height                     |
| `antCount`        |    `10` | Number of ants                   |
| `time`            |  `1000` | Simulation iterations            |
| `dispersionRate`  |  `0.04` | Pheromone diffusion rate         |
| `evaporationRate` |  `0.99` | Pheromone retention rate         |
| `posReward`       |    `10` | Reward for completing a trip     |
| `negReward`       |    `-1` | Reward/penalty for movement      |
| `qEpsilon`        |   `0.4` | Q-learning exploration parameter |
| `qLambda`         |  `0.95` | Q-learning discount parameter    |
| `qAlpha`          |   `0.2` | Q-learning learning rate         |
| `qEpsilon_decay`  |  `0.01` | Exploration decay                |
| `learningRate`    |   `0.2` | Neural-network learning rate     |
| `nnHidden`        |     `5` | Number of hidden units           |
| `updateTimes`     |   `100` | Internal update iterations       |
| `trainingTimes`   |    `10` | Internal NN training iterations  |

These are defined near the beginning of `internal_external_multi.py`.

## Available agent actions

The default action set is:

```python
actions = [0, 1, 2, 3, 4]
```

The actions correspond to:

```text
0 → drop home pheromone
1 → drop food pheromone
2 → follow home pheromone
3 → follow food pheromone
4 → move randomly
```

Additional actions can be enabled:

```text
5 → internal state change: -1
6 → internal state change: +1
```

Thus, experiments using:

```python
actions = [0, 1, 2, 3, 4, 5, 6]
```

enable the complete action space.

## Pheromone dynamics

Each cell maintains two pheromone concentrations:

```python
homePher
foodPher
```

During a cell update, pheromone diffuses toward the average concentration of neighboring cells:

```python
self.homePher += (
    havg - self.homePher
) * dispersionRate

self.foodPher += (
    favg - self.foodPher
) * dispersionRate
```

The pheromone then evaporates:

```python
self.homePher *= evaporationRate
self.foodPher *= evaporationRate
```

Values are bounded to `[0, 1]`, and concentrations below `0.001` are removed.

## Q-learning

Each ant owns its own Q-learning object:

```python
self.ai = qlearn.QLearn(
    epsilon=qEpsilon,
    lambd=qLambda,
    alpha=qAlpha,
    epsilon_decay=qEpsilon_decay,
    q=q
)
```

The agent constructs a state from:

```python
(
    homePheromoneLevel,
    foodPheromoneLevel,
    pheromoneTime
)
```

The Q-learning agent then selects an action:

```python
choice = self.ai.do(state)
```

and the selected action determines the ant's subsequent behavior.

## Neural-network component

The ant can also contain an internal neural network:

```python
self.internal = backprop.NN(...)
```

Depending on the experiment configuration, the network receives either three or five state values.

The internal state can include:

* whether the ant is at home
* whether the ant is at food
* home pheromone level
* food pheromone level
* internal memory/state

The neural network is primarily used by the internal-state experiments rather than the basic external pheromone-only configuration.

## Experiment studies

`main.py` defines four study configurations:

```text
Study 1:
Internal state NN = enabled
Pheromone-level NN = disabled
Actions = [0,1,2,3,4]

Study 2:
Internal state NN = enabled
Pheromone-level NN = disabled
Actions = [0,1,2,3,4,5,6]

Study 3:
Internal state NN = disabled
Pheromone-level NN = enabled
Actions = [0,1,2,3,4,5,6]

Study 4:
Internal state NN = enabled
Pheromone-level NN = enabled
Actions = [0,1,2,3,4,5,6]
```

The current `main.py` selects:

```python
study = 1
```

and runs the `QPass` experiment.

## Output

The simulation records data for each agent, including:

```text
id
x
y
action
sense
food
q
reward
dropper
```

The resulting data is serialized using Python `pickle`:

```python
pickle.dump(data, fl)
```

The current `main.py` therefore produces `.dat` files containing the recorded simulation data.

## Execution overview

The high-level execution is:

```text
main.py
   │
   ▼
configure experiment
   │
   ▼
internal_external_multi.run()
   │
   ├── create World
   │
   ├── load map
   │
   ├── create Agents
   │       │
   │       ├── QLearn
   │       └── NN
   │
   └── simulation loop
           │
           ├── World.update()
           │
           ├── Agent.update()
           │      │
           │      ├── observe state
           │      ├── receive reward
           │      ├── Q-learning
           │      ├── choose action
           │      └── execute action
           │
           └── record simulation data
```
