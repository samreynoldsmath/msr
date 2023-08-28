## [2023 Aug 28] 0.5.2 Style and Structure
- [ ] Converted all files to PEP8 style using `black`, `isort`, and `mypy`
- [ ] Renamed `simple_undirected_graph` to `graph
- [ ] Moved `graph_lib` and `generate` modules to `graph`
- [ ] Renamed `msr/graph/graph_lib` directory to `msr/graph/saved`
- [ ] Minor optimization of graph generator to use less memory
  - [ ] Generating n=8 graphs takes ~4 hours

## [2023 Aug 19] 0.5.1 Generation Optimizations
- [ ] Restructured `graph_lib/generate.py` to use `simple_undirected_graph` class
- [ ] Added hash method to `simple_undirected_graph` class
- [ ] Rather than checking for isomorphism against all graphs in the list, generate all elements of isomorphism class and check against those
  - [ ] `multiprocessing` is used to permute the edges and compute the new hash
- [ ] Changed examples to Jupyter notebooks

## [2023 Aug 17] 0.5.0 BCD
- Added maximal independent set algorithm to `simple_undirected_graph`
- Added lower and upper bounds on MSR via BCD
  - n7 benchmark takes ~10 minutes vs ~2.5 hours without BCD

## [2023 Aug 15] 0.4.0 Multiprocessing
- Added an upper bound on MSR by considering cliques and induced covers
- Added 'entropy minimizing' embedding to `graph/draw.py`
- Added compatibility with `networkx` graphs via `msr/graph/convert.py`
- Added `graph/graph_lib/generate.py` to generate all connected graphs on $n$ vertices up to isomorphism
- Added `msr_batch.py` with functions to compute MSR of multiple graphs at a time with `multiprocessing`
- Added scripts to `benchmarks/` to generate and test all connected graphs on $n$ vertices up to isomorphism, save images of the troublemakers, and save them to a single .pdf file
- Removed six-vertex graph files from `graph_lib`, as they can now be generated

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