# Orbit simulator :satellite:

High precision satellite orbit simulation based on [skyfield](http://rhodesmill.org/skyfield/) library.

**Features:**

- You can either use existing satellites (from [NORAD database](http://celestrak.com/)) or create your own custom satellite by defining [orbital elements](https://en.wikipedia.org/wiki/Orbital_elements)
- It can simulate position of the sun and day/night terminator line
- Output ground path in CSV
- Generate animations
- Calculate MLTAN

## Examples

- [1_ground_path_simulation.ipynb](./1_ground_path_simulation.ipynb)
- [2_visualization.ipynb](./2_visualization.ipynb)
- [3_animation.ipynb](./3_animation.ipynb)
- [4_custom_satellites.ipynb](./4_custom_satellites.ipynb)
- [5_MLTAN.ipynb](./5_MLTAN.ipynb)

## Sources

- https://en.wikipedia.org/wiki/Simplified_perturbations_models
- http://rhodesmill.org/skyfield/
- https://en.wikipedia.org/wiki/Terminator_%28solar%29
- https://github.com/SciTools/cartopy