## [2023 Sep 07] 0.8.0 Exhaustive BCD
- Introduced exhaustive BCD
  - `bcd_exhaustive` computes a lower bound on MSR by considering all possible independent sets
  - Added `independent_sets` method to `graph` that returns a list of all independent sets

## [2023 Sep 06] 0.7.2 Lookup
- `sdp_signed_simple` now performs an unsigned SDP before switching signs
- Simplified logic of bounding reduced graphs
- Moved strategy configuration to `msr/strategy_config.py`
- Modified `bounds_from_edge_addition` to prioritize vertices with high degree
- Modified `bounds_from_edge_removal` to prioritize vertices with low degree
- Restructured tests to make it obvious for which graph the test failed
- Logger tweaks

## [2023 Sep 04] 0.7.1 Lookup
- Moved logger to `msr/log_config.py`
  - Logger object passed to functions as needed
- `file_io` tweaks
  - Added default save directory for graphs with `SAVED_GRAPH_DIR=msr/graph/saved`
  - Graphs files now use `.graph` filenames
  - Graphs are saved by default to `SAVED_GRAPH_DIR` with filename `n{num_vertices}k{hash}.graph`
- Updated `msr_batch` to use `SAVED_GRAPH_DIR` by default
- Added subdirectories to `msr/soln` to store graphs by number of vertices and number of edges to reduce search time
- Removed redundant functions from `generate` module
- Added test for graph hashing

## [2023 Sep 04] 0.7.0 Lookup
- Added `msr/lookup.py` to manage known MSR bounds
  - Graph bounds stored in `msr/soln' under a file name generated from the hash of a representative of its isomorphism class (min hash)
- Modified `msr_bounds` to use lookup table when simple methods fail, and to add new bounds to the table after computing them

## [2023 Sep 03] 0.6.2 Signed SDP
- Modified edges to be considered in signed-cyclic SDP to only include edges that are part of an *induced* even cycle
- Added `induced_subgraph` method to `graph`
- logger tweaks

## [2023 Sep 02] 0.6.1 Signed SDP
- SDP tweaks
  - Added cyclic-search version that only uses edges that are part of an even cycle
  - Fixed bug that gave incorrect bounds for some graphs due to incorrect constraints
  - Added safety check to ensure that constraints are satisfied
- Added maximum independent set algorithm to `graph`, now used by BCD
- Added `tests` directory, with so far only one test for MSR on graphs on six vertices or less
  - Known values stored in `msr/soln`, which a future version will use in a lookup table

## [2023 Sep 01] 0.6.0 Signed SDP
- Introduced signed SDP relaxation
  - Simple version flips exactly one edge sign at a time
  - Full version flips all possible edge signs at a time
  - Added logger
  - `msr_bounds` should now be able to find tight bounds for any graph (but not necessarily in a reasonable amount of time)
- Restructured `msr_bounds`
  - Added a strategy manager
  - Added `msr` wrapper function
- Improved drawing
  - Added multiprocessing for drawing multiple graphs
  - Split embedding functions into separate module
  - Added spring embedding
  - Added spectral embedding
- Changed name assignment when loading graphs from file
- Added check against OEIS for number of connected graphs on $n$ vertices up to isomorphism for generating graphs
- Added dev tools
  - Configuration file for `mypy`
  - `requirements-dev.txt`

## [2023 Aug 28] 0.5.2 Style and Structure
- Converted all files to PEP8 style using `black`, `isort`, and `mypy`
- Renamed `simple_undirected_graph` to `graph
- Moved `graph_lib` and `generate` modules to `graph`
- Renamed `msr/graph/graph_lib` directory to `msr/graph/saved`
- Minor optimization of graph generator to use less memory
  - Generating n=8 graphs takes ~4 hours

## [2023 Aug 19] 0.5.1 Generation Optimizations
- Restructured `graph_lib/generate.py` to use `simple_undirected_graph` class
- Added hash method to `simple_undirected_graph` class
- Rather than checking for isomorphism against all graphs in the list, generate all elements of isomorphism class and check against those
  - `multiprocessing` is used to permute the edges and compute the new hash
- Changed examples to Jupyter notebooks

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
- Added logger and removed most print statements
- Added benchmark to see how well the algorithm works on all six-vertex graphs