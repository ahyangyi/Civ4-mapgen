The Antaeus Map Generator
=========================

## Usage
Put the `Antaeus.py` into the `PublicMaps` directory of your Civilization IV intallation.

## Major Modes

### IID
Each grid has the same distribution, ending in ultimately chaotic map.

This mode began as a learning exercise, but it was deemed interesting enough to be kept.

### Fractal
Iterative fractal-based map generation. The resulting map is unpredictable, and tends to have long mountain ranges, island chains and lake chains (for canal lovers).

Map is guaranteed to be connected. That is, every two grid are connected by a path without mountains.

![Typical Map](https://raw.githubusercontent.com/ahyangyi/Civ4-mapgen/master/images/map.jpg)

### Riveria
Draw rivers to split the map into random regions. Navy is probably necessary, but it is not going to dominate your game, since adjacent continents are close to each other.

## Minor Options
Default water level and climate options are supported.

Maps can be generated in various symmetry. Note that the option does not guarantee any symmetry in placement of starting locations.

Multiple climate modes are provided.
