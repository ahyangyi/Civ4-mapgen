The Antaeus Map Generator
=========================

## Usage
Put the `Antaeus.py` into the `PublicMaps` directory of your Civilization IV intallation.

## Major Modes

### IID
Each grid has the same distribution, ending in ultimately chaotic map.

This mode began as a learning exercise, but it was deemed interesting enough to be kept.

![IID Example](https://raw.githubusercontent.com/ahyangyi/Civ4-mapgen/master/images/iid.jpg)

### Fractal
Fractal-flame-based map generation. The resulting map is unpredictable, and tends to have long mountain ranges, island chains and lake chains (for canal lovers).

Map is guaranteed to be connected. That is, every two grid are connected by a path without mountains.

![Fractal Example](https://raw.githubusercontent.com/ahyangyi/Civ4-mapgen/master/images/fractal.jpg)

### Riveria
Draw “rivers” consisting of water tiles. Navy is probably necessary, but it is not going to dominate your game, since even if the land is not connected, adjacent continents are close to each other.

![Riveria Example](https://raw.githubusercontent.com/ahyangyi/Civ4-mapgen/master/images/riveria.jpg)

### Shader
Draws water, hills and mountains in broad strokes. Will probably contain one cluster of mountains and one big ocean, but the distribution and shape unpredictable.

![Shader Example](https://raw.githubusercontent.com/ahyangyi/Civ4-mapgen/master/images/shader.jpg)

## Minor Options
Default water level and climate options are supported.

Maps can be generated in various symmetry. Note that the option does not guarantee any symmetry in placement of starting locations.

![2-way rotational symmetry](https://raw.githubusercontent.com/ahyangyi/Civ4-mapgen/master/images/symmetry.jpg)

Multiple climate modes are provided.
