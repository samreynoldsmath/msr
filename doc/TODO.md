# TODO

## Documentation
- [x] update README
- [x] update CHANGELOG

## Graph library
  - [x] Export graphs in old code to JSON files
  - [x] Make loader for JSON files
  - [x] All graphs on up to six vertices
  - [x] Complete graphs
  - [ ] Complete bipartite graphs
  - [x] Cycle graphs
  - [x] Path graphs
  - [x] Star graphs
  - [x] Wheel graphs
  - [ ] Hypercube graphs
  - [x] House graph
  - [x] Petersen graph

## Algorithms
- [x] use semidefinite programming (`cvxpy`) for upper bound
  - [ ] search over flipping signs of sparsity constraints
- [ ] edge deletion estimates
  - [x] edge addition
  - [ ] edge deletion
- [ ] proper induced covers (upper bound)
  - [x] special case for cut vertices
  - [ ] greedy partition search
- [ ] block-correction decomposition
  - [x] maximal independent sets
  - [ ] maximum independent sets
  - [x] lower bound
  - [x] upper bound
  - [ ] avoid combinatorial explosion?
- [ ] Prove that reduced graph satisfies $2\leq\dim(G)\leq n-2$
- [ ] Cut-vertex: Tarjan's algorithm
- [ ] multiprocessing for graph generation

## Cleanup
- [x] remove deprecated methods from `simple_undirected_graph`
- [x] remove deprecated modules from `graph/graph_lib/`
- [x] add `graph_lib/six_vert/`

## Unit tests
- [ ] Graph functionality
  - [ ] Add / remove edges
  - [ ] Add / remove vertices
  - [ ] Neighbors / degree
  - [ ] Connected components
  - [ ] Pendant
  - [ ] Subdivision
  - [ ] Redundant vertex
  - [ ] Duplicate pair
- [ ] MSR bounds
  - [ ] Special cases
  - [ ] Isolated vertices
  - [ ] Disconnected graphs
  - [ ] Graphs on up to six vertices
- [ ] SDP upper bound
  - [ ] Graphs on up to six vertices

## Benchmarks
- [x] count number of correct msr predictions with `msr_bounds()`

## Features
- [x] improved visualization (entropy minimization)
- [x] jupyter notebook examples
