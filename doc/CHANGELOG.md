## [2023 Aug 10] 0.3.0 Combinatorial MSR
- Updated school project to a "usable" package
- Reworked graph representation (now using sets rather than lists)
  - `edge` class
  - `simple_undirected_graph` class
- Added functionality to load/save graphs to/from .json files
- Added `msr_bounds` function to compute upper and lower bounds on the MSR
  - Operates semi-recursively
  - Checks special cases
  - Computes bounds for each component
  - Performs a "smoothing" operation to reduce size of the graph
  (removes pendants, subdivisions, redundant vertices, duplicate pairs)
  - Finds lower bound by checking subgraphs
  - Finds upper bound with an SDP approach
  - Finds bounds via edge addition
- Added logging and removed most print statements
- Added benchmark to see how well the algorithm works on all six-vertex graphs