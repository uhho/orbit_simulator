# Orbit simulator :satellite:

High precision satellite orbit simulation based on [skyfield](http://rhodesmill.org/skyfield/) library.

**Features:**

- You can either use existing satellites (from [NORAD database](http://celestrak.com/)) or create your own custom satellite by defining [orbital elements](https://en.wikipedia.org/wiki/Orbital_elements)
- It can simulate position of the sun and day/night terminator line
- Output ground path in CSV
- Generate animations

## Examples

- [ground_path_simulation.ipynb](./ground_path_simulation.ipynb)
- [visualization.ipynb](./visualization.ipynb)
- [animation.ipynb](./animation.ipynb)
- [custom_satellites.ipynb](./custom_satellites.ipynb)

## Sources

- https://en.wikipedia.org/wiki/Simplified_perturbations_models
- http://rhodesmill.org/skyfield/
- https://en.wikipedia.org/wiki/Terminator_%28solar%29
- https://github.com/SciTools/cartopy