# MSR: Minimum Semidefinite Rank
https://github.com/samreynoldsmath/msr

## Description
Tools to compute the minimum semidefinite rank of a simple undirected graph.

The minimum semidefinite rank of a graph $G$, denoted by $\text{msr}(G)$, is
the smallest rank of a positive semidefinite matrix $A$ such that $A$ is a
generalized adjacency matrix of $G$;
that is, $A_{ij} \neq 0$ if and only if $i \neq j$ and $ij \in E(G)$.
Equivalently, $\text{msr}(G)$ is the smallest dimension $d$ such that every
vertex $i$ of $G$ can be assigned to a vector $x_i \in \mathbb{R}^d$ such for
each $i \neq j$, we have that $x_i \cdot x_j \neq 0$ if and only if
$ij \in E(G)$. Surprisingly, the graph invariant $\text{msr}(G)$ can often be
computed only by consideration of the graph structure, without the need to
actually do any linear algebra.

## Comments
- This package began as a school project for a course on semidefinite
	programming (see the
	[final report](doc/mth610-semidefprog-final-report-reynolds.pdf)).
 - In addition to SDP, this package also uses combinatorial techniques to
	compute bounds on the MSR, some of which are well-known in the literature,
	and some of which are still under development.
 - The package uses a custom graph representation, but supports conversion
  	to\from [networkx](https://networkx.org/) graphs.
- The package is not designed with efficiency in mind, and probably will not
	scale well to large graphs.

## Dependencies
This project is written in Python 3.11 and uses the following packages:
- [cvxpy](https://www.cvxpy.org/) is used to solve semidefinite programs
- [matplotlib](https://matplotlib.org/) is used for visualization
- [networkx](https://networkx.org/) is used for graph isomorphism testing
- [tqdm](https://tqdm.github.io/) is used for progress bars
See [requirements.txt](requirements.txt) for a complete list of dependencies.

## Author
[Sam Reynolds](https://sites.google.com/view/samreynolds)
is a PhD student studying Mathematical Sciences at
[Portland State University](https://www.pdx.edu/math/).

## License
Copyright (c) 2023 under the
[MIT license](LICENSE).
