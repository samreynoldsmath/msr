"""
Module for representing simple undirected graphs.
"""

from __future__ import annotations

from copy import copy
from typing import Optional

from numpy import ndarray, zeros


class UndirectedEdge:
    """An undirected edge between two vertices."""

    endpoints: set[int]

    def __init__(self, i: int, j: int) -> None:
        self.set_endpoints(i, j)

    def __str__(self) -> str:
        return str(self.endpoints)

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UndirectedEdge):
            raise TypeError("Can only compare undirected edges.")
        return self.endpoints == other.endpoints

    def __hash__(self) -> int:
        i, j = self.endpoints
        return hash((i, j))

    def set_endpoints(self, i: int, j: int) -> None:
        """Sets the endpoints of the edge to the given vertices."""
        if not isinstance(i, int) or not isinstance(j, int):
            raise TypeError("Endpoints must be integers.")
        if i < 0 or j < 0:
            raise ValueError("Endpoints cannot be negative.")
        if i == j:
            raise ValueError("Loops are not allowed.")
        self.endpoints = {i, j}


class SimpleGraph:
    """A simple undirected graph."""

    num_verts: int
    edges: set[UndirectedEdge]
    known_msr: Optional[int]
    _is_connected_flag: Optional[bool]

    def __init__(self, num_verts: int) -> None:
        self.set_num_verts(num_verts)
        self.edges = set()
        self._is_connected_flag = None
        self.known_msr = None

    def __str__(self) -> str:
        s = self.hash_id()
        s += "\nNumber of edges: " + str(self.num_edges())
        s += "\nEdges:"
        for k, e in enumerate(self.edges):
            s += f"\n{k:3d}\t{str(e)}"
        return s

    def __repr__(self) -> str:
        return str(self)

    def __copy__(self):
        G = SimpleGraph(self.num_verts)
        G.edges = self.edges.copy()
        return G

    def __hash__(self):
        n = self.num_verts
        n_choose_2 = n * (n - 1) // 2
        binary_list = [0] * n_choose_2
        for i in range(n - 1):
            for j in range(i + 1, n):
                if self.is_edge(i, j):
                    ij = j - 1 + (i * (2 * n - 3 - i)) // 2
                    binary_list[ij] = 1
        binary_str = "".join([str(b) for b in binary_list])
        return int(binary_str, 2)

    def hash_id(self) -> str:
        """Returns a unique identifier for the graph."""
        return f"n{self.num_verts}k{hash(self)}"

    ### CONSTRUCTION ##########################################################

    def build_from_hash(self, hash_id: int) -> None:
        """
        Builds the graph from its hash value.
        """
        n = self.num_verts
        n_choose_2 = n * (n - 1) // 2
        if hash_id < 0 or hash_id >= 2**n_choose_2:
            raise ValueError("Hash value out of bounds.")
        binary = bin(hash_id)[2:].zfill(n_choose_2)
        self.edges = set()
        for i in range(n - 1):
            for j in range(i + 1, n):
                if binary[0] == "1":
                    self.add_edge(i, j)
                binary = binary[1:]

    ### VERTICES ##############################################################

    def set_num_verts(self, num_verts: int) -> None:
        """Sets the number of vertices in the graph."""
        if num_verts < 1:
            raise ValueError("Must have a positive number of vertices")
        self.num_verts = num_verts

    def remove_vert(
        self, i: int, still_connected: Optional[bool] = None
    ) -> None:
        """Removes the given vertex from the graph."""
        if self.num_verts < 2:
            raise ValueError(
                "Cannot remove a vertex from a graph with fewer"
                + " than two vertices."
            )
        if i < 0 or i >= self.num_verts:
            raise ValueError("Vertex index out of bounds.")
        # remove edges incident to i
        for j in range(self.num_verts):
            if self.is_edge(i, j):
                self.remove_edge(i, j)
        # shift vertices after i down by one
        for j in range(i + 1, self.num_verts):
            for k in range(self.num_verts):
                if self.is_edge(j, k):
                    self.remove_edge(j, k)
                    self.add_edge(j - 1, k)
        self.num_verts -= 1
        self._is_connected_flag = still_connected

    def vert_neighbors(self, i: int) -> set[int]:
        """Returns the set of neighbors of the given vertex."""
        if i < 0 or i >= self.num_verts:
            raise ValueError("Vertex index out of bounds.")
        return {j for j in range(self.num_verts) if self.is_edge(i, j)}

    def vert_deg(self, i: int) -> int:
        """Returns the degree of the given vertex."""
        return len(self.vert_neighbors(i))

    def num_isolated_verts(self) -> int:
        """Returns the number of isolated vertices in the graph."""
        return len([i for i in range(self.num_verts) if self.vert_deg(i) == 0])

    def permute_verts(self, perm: list[int]) -> SimpleGraph:
        """ "
        Returns a graph with vertices permuted according to the given list.
        """
        if not set(perm) == set(range(self.num_verts)):
            raise ValueError(
                "Permutation list must be a permutation of the" + " vertices."
            )
        H = SimpleGraph(self.num_verts)
        for e in self.edges:
            i, j = e.endpoints
            H.add_edge(perm[i], perm[j])
        return H

    def get_a_cut_vert(self) -> int | None:
        """
        Returns the index of a cut vertex in the graph, or None if there are
        no cut vertices.
        """
        for i in range(self.num_verts):
            if self.vert_is_cut_vert(i):
                return i
        return None

    def get_cut_verts(self) -> set[int]:
        """Returns the set of cut vertices in the graph."""
        # TODO: Tarjan's algorithm is more efficient
        return {i for i in range(self.num_verts) if self.vert_is_cut_vert(i)}

    ### INDEPENDENT SETS ######################################################

    def is_independent_set(self, vert_idx_set: set[int]) -> bool:
        """Returns True if S is an independent set."""
        return all(
            not self.is_edge(i, j)
            for i in vert_idx_set
            for j in vert_idx_set
            if i != j
        )

    def maximal_independent_set(self) -> set[int]:
        """
        DEPRECATED: networkx has a better implementation of this function.

        Returns a maximal independent set of vertices in the graph, using a
        greedy algorithm based on vertex degree.
        """

        indep_set = set()
        candidates = set(range(self.num_verts))

        while len(candidates) > 0:
            # pick a candidate vertex of minimum degree
            i = min(candidates, key=self.vert_deg)

            # add i to the independent set
            indep_set.add(i)

            # remove i and its neighbors from the set of candidates
            candidates.remove(i)
            neighborhood = self.vert_neighbors(i)
            for j in neighborhood:
                candidates.discard(j)

        return indep_set

    def maximum_independent_set(self) -> set[int]:
        """Returns a maximum independent set."""

        alpha = 0
        num_subgraphs = 2**self.num_verts
        for k in range(num_subgraphs - 1, 0, -1):
            binary = bin(k)[2:].zfill(self.num_verts)
            candidate_size = binary.count("1")
            if candidate_size <= alpha:
                continue
            candidate = set()
            for i, bit in enumerate(binary):
                if bit == "1":
                    candidate.add(i)
            if self.is_independent_set(candidate):
                alpha = candidate_size
                indep_set = candidate.copy()
        return indep_set

    def independent_sets(self) -> list[set[int]]:
        """Returns a list of all independent sets."""
        indep_sets = []
        num_subgraphs = 2**self.num_verts
        for k in range(num_subgraphs - 1, 0, -1):
            binary = bin(k)[2:].zfill(self.num_verts)
            candidate = set()
            for i, bit in enumerate(binary):
                if bit == "1":
                    candidate.add(i)
            if self.is_independent_set(candidate):
                indep_sets.append(candidate.copy())
        return indep_sets

    ### VERTEX TESTS ##########################################################

    def vert_is_pendant(self, i: int) -> bool:
        """Returns True if the given vertex is a pendant vertex."""
        return self.vert_deg(i) == 1

    def vert_is_subdivided(self, i: int) -> bool:
        """Returns True if the given vertex is subdivided."""
        if self.vert_deg(i) != 2:
            return False
        j, k = self.vert_neighbors(i)
        return not self.is_edge(j, k)

    def vert_is_redundant(self, i: int) -> bool:
        """
        Returns True if the given vertex is adjacent to every other vertex.
        """
        return self.vert_deg(i) == self.num_verts - 1

    def verts_are_duplicate_pair(self, i: int, j: int) -> bool:
        """Returns True if i,j are adjacent and have the same neighbors."""
        if not self.is_edge(i, j):
            return False
        neighborhood_i = self.vert_neighbors(i)
        neighborhood_i.remove(j)
        neighborhood_j = self.vert_neighbors(j)
        neighborhood_j.remove(i)
        return neighborhood_i == neighborhood_j

    def vert_is_cut_vert(self, i: int) -> bool:
        """Returns True if the given vertex is a cut vertex."""
        if self.num_verts < 3:
            return False
        if self.vert_deg(i) < 2:
            return False
        G = copy(self)
        G.remove_vert(i)
        return not G.is_connected()

    ### EDGES #################################################################

    def num_edges(self) -> int:
        """Returns the number of edges in the graph."""
        return len(self.edges)

    def add_edge(self, i: int, j: int) -> None:
        """Adds an edge between the given vertices."""
        if i > self.num_verts or j > self.num_verts:
            raise ValueError("Vertex index out of bounds.")
        self.edges.add(UndirectedEdge(i, j))
        self._is_connected_flag = None

    def remove_edge(self, i: int, j: int) -> None:
        """Removes the edge between the given vertices."""
        self.edges.discard(UndirectedEdge(i, j))
        self._is_connected_flag = None

    def is_edge(self, i: int, j: int) -> bool:
        """Returns True if there is an edge between the given vertices."""
        if i == j:
            return False
        return UndirectedEdge(i, j) in self.edges

    ### INDUCED SUBGRAPHS #####################################################

    def induced_subgraph(self, vert_set: set[int]) -> SimpleGraph:
        """
        Returns the induced subgraph on the given set of vertices.
        """
        H = SimpleGraph(len(vert_set))
        vert_list = list(vert_set)
        for i in range(len(vert_set)):
            for j in range(i + 1, len(vert_set)):
                if self.is_edge(vert_list[i], vert_list[j]):
                    H.add_edge(i, j)
        return H

    ### COMPONENTS ############################################################

    def connected_components(self) -> list[SimpleGraph]:
        """
        Returns a list of graph objects, where each object is
        a connected component of the graph.
        """
        component_vert_idx = self.connected_components_vert_idx()
        components = []
        for verts in component_vert_idx:
            num_verts = len(verts)
            verts_list = list(verts)
            H = SimpleGraph(num_verts)
            for i in range(num_verts):
                for j in range(i + 1, num_verts):
                    if self.is_edge(verts_list[i], verts_list[j]):
                        H.add_edge(i, j)
            H.set_connected_flag(True)
            components.append(H)
        return components

    def connected_components_vert_idx(self) -> list[set[int]]:
        """
        Returns a list of set of vertex indices, where each set of vertex
        indices is a connected component of the graph.
        """
        component_index_list = []
        visited: set[int] = set()
        for i in range(self.num_verts):
            if i not in visited:
                this_component_idx_set = self.bfs(i)
                visited = visited.union(this_component_idx_set)
                component_index_list.append(this_component_idx_set)
        self._is_connected_flag = len(component_index_list) == 1
        return component_index_list

    def bfs(self, i: int) -> set[int]:
        """
        Returns the set of vertices reachable from the given vertex by a
        breadth-first search.
        """
        if i < 0 or i >= self.num_verts:
            raise ValueError("Vertex index out of bounds.")
        reachable = set(
            [
                i,
            ]
        )
        frontier = set(
            [
                i,
            ]
        )
        while len(frontier) > 0:
            new_frontier = set()
            for j in frontier:
                for k in self.vert_neighbors(j):
                    if not k in reachable:
                        reachable.add(k)
                        new_frontier.add(k)
            frontier = new_frontier
        return reachable

    ### INDUCED COVERS ########################################################

    def get_induced_cover_from_cut_vert(self) -> list[SimpleGraph]:
        """
        Returns a list of induced subgraphs, where any two distinct subgraphs
        intersect at a single vertex (which is necessarily a cut vertex).
        """
        cut_vert_idx = self.get_a_cut_vert()
        if cut_vert_idx is None:
            return [
                self,
            ]

        # construct a proper induced cover
        H = copy(self)
        H.remove_vert(cut_vert_idx)
        component_vert_idx = H.connected_components_vert_idx()
        cover = []
        for verts in component_vert_idx:
            num_verts = len(verts)
            verts_list = list(verts)
            verts_list.append(cut_vert_idx)
            H = SimpleGraph(num_verts)
            for i in range(num_verts):
                for j in range(i + 1, num_verts):
                    if self.is_edge(verts_list[i], verts_list[j]):
                        H.add_edge(i, j)
            H.set_connected_flag(True)
            cover.append(H)
        return cover

    ### GRAPH TESTS ###########################################################

    def set_connected_flag(self, flag: bool) -> None:
        """Sets the connected flag to the given value."""
        self._is_connected_flag = flag

    def is_connected(self) -> bool:
        """Returns True if the graph is connected."""
        if self.num_verts == 1:
            return True
        if self._is_connected_flag is None:
            self.connected_components_vert_idx()
        if self._is_connected_flag is None:
            raise RuntimeError("Could not determine connectedness of graph.")
        return bool(self._is_connected_flag)

    def is_empty(self) -> bool:
        """Returns True if the graph has no edges."""
        return self.num_edges() == 0

    def is_complete(self) -> bool:
        """Returns True if every vertex is adjacent to every other vertex."""
        return self.num_edges() == self.num_verts * (self.num_verts - 1) // 2

    def is_a_tree(self) -> bool:
        """Returns True if the graph is connected and has no cycles."""
        if not self.is_connected():
            return False
        return self.num_edges() == self.num_verts - 1

    def is_k_regular(self, k: int) -> bool:
        """Returns True if every vertex has degree k."""
        return all(self.vert_deg(i) == k for i in range(self.num_verts))

    def is_a_cycle(self) -> bool:
        """Returns True if the graph is a cycle."""
        if not self.is_connected():
            return False
        return self.is_k_regular(2)

    ### MATRIX REPRESENTATIONS ################################################

    def adjacency_matrix(self) -> ndarray:
        """Returns the graph Laplacian matrix."""
        n = self.num_verts
        adj_mat = zeros((n, n), dtype=int)
        for e in self.edges:
            i, j = e.endpoints
            adj_mat[i, j] = 1
            adj_mat[j, i] = 1
        return adj_mat

    def laplacian(self) -> ndarray:
        """Returns the graph Laplacian matrix."""
        n = self.num_verts
        lap_mat = zeros((n, n), dtype=int)
        for e in self.edges:
            i, j = e.endpoints
            lap_mat[i, j] = -1
            lap_mat[j, i] = -1
            lap_mat[i, i] += 1
            lap_mat[j, j] += 1
        return lap_mat
