# MSR: Minimum Semidefinite Rank
Sam Reynolds (2023)

Fariborz Maseeh Department of Mathematics and Statistics

Portland State University

## Description
The minimum semidefinite rank problem seeks the minimum rank of a square,
symmetric, positive semidefinite subject sparsity constraints.
That is, we seek $\min\text{rank}(A)$ such that $A \succeq0$ with
$A_{ij} \neq 0$ for $ij \in E$ and
$A_{ij} = 0$ for $ij \notin E$ and $i\neq j$.
Note that the diagonal entries $A_{ii}$ are left arbitrary.
The *edge set* $E$ can be thought of as the edge set of a simple,
undirected graph $G$.
The minimum semidefinite rank of $G$ is denoted by $\text{msr}(G)$.

This project seeks an approximation of $\text{msr}(G)$ using a relaxation
of the objective function $\text{rank}(A)$ to the trace $\text{tr}(A)$
and cast the problem as a semidefinite program. Furthermore, the sparsity
constraints $A_{ij} \neq 0$ for $ij \in E$ are nonconvex, and we instead
use $A_{ij} \geq \varepsilon$ for some fixed $\varepsilon > 0$.
By introducing slack variables, the feasible set can be shown to be a
spectrahedron.
These constraints are a proper subset of the original sparsity constraints,
and for some graphs (e.g. the 4-cycle), the SDP returns an estimation of
$\text{msr}(G)$ that is strictly larger than the exact solution.
Further investigation is required to determine which types of graphs have
a minimum rank postive semidefinite generalized adjacency matrix with
nonnegative entries.

## Dependencies
This project is written in Python 3.10 and uses the following packages:
* numpy
* cvxpy

## Comments
* This repository is part of a final project for MTH 610, Spring 2023.