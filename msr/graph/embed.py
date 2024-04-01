"""
Module for embedding graphs in the plane.
"""

import numpy as np

from .graph import SimpleGraph


def embed(
    G: SimpleGraph, embedding: str
) -> tuple[np.ndarray, np.ndarray, float]:
    """Embeds G in the plane using adj_mat specified embedding."""
    if embedding == "circular":
        x, y = circular_embedding(G)
    if embedding == "random":
        x, y = random_embedding(G)
    elif embedding == "spring":
        x, y = spring_embedding(G)
    elif embedding == "min_entropy":
        x, y = rubber_electric_embedding(G)
    elif embedding == "spectral":
        x, y = spectral_embedding(G)
    else:
        raise ValueError(f'Invalid embedding type "{embedding}"')

    # compute diameter
    diam = 0
    for i in range(G.num_verts):
        for j in range(G.num_verts):
            x_ij = x[i] - x[j]
            y_ij = y[i] - y[j]
            diam = max(diam, np.sqrt(x_ij**2 + y_ij**2))

    return x, y, diam


def circular_embedding(G: SimpleGraph) -> tuple[np.ndarray, np.ndarray]:
    """
    Embeds G in the plane using adj_mat circular embedding.
    """
    n = G.num_verts
    theta = 2 * np.pi / n
    x = np.zeros((n,))
    y = np.zeros((n,))
    for i in range(G.num_verts):
        x[i] = np.cos(i * theta)
        y[i] = np.sin(i * theta)
    return x, y


def random_embedding(G: SimpleGraph) -> tuple[np.ndarray, np.ndarray]:
    """
    Embeds G in the plane using adj_mat random embedding.
    """
    n = G.num_verts
    x = 2 * np.random.random((n,)) - 1
    y = 2 * np.random.random((n,)) - 1
    return x, y


def rubber_electric_embedding(G: SimpleGraph) -> tuple[np.ndarray, np.ndarray]:
    """
    Returns an embedding of G in the plane that minimizes the entropy of the
    edge lengths, which are imagined to be rubber bands, and a repulsive force
    between vertices that is proportional to the inverse square of the distance,
    which is imagined to be an electric force.
    """

    tol = 1e-4
    max_iter = int(1e6)
    h = 5e-3

    electric_constant = 3.0
    spring_constant = 1.0
    friction_constant = 0.2

    n = G.num_verts

    x, y = random_embedding(G)

    dx = np.zeros((n,))
    dy = np.zeros((n,))

    ddx = np.zeros((n,))
    ddy = np.zeros((n,))

    lap_mat = G.laplacian()

    for _ in range(max_iter):
        # update acceleration
        ddx, ddy = _coulomb_repulsive_force(x, y)

        ddx *= electric_constant
        ddy *= electric_constant

        ddx -= spring_constant * lap_mat @ x
        ddy -= spring_constant * lap_mat @ y

        ddx -= friction_constant * dx
        ddy -= friction_constant * dy

        # check for convergence
        if sum(dx**2 + dy**2 + ddx**2 + ddy**2) < tol:
            break

        # update position
        x += h * dx
        y += h * dy

        # update velocity
        dx += h * ddx
        dy += h * ddy

    # center the embedding at the origin
    x -= sum(x) / n
    y -= sum(y) / n

    return x, y


def _coulomb_repulsive_force(
    x: np.ndarray, y: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    n = len(x)
    force_x = np.zeros((n,))
    force_y = np.zeros((n,))
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            x_ij = x[i] - x[j]
            y_ij = y[i] - y[j]
            r3 = (x_ij**2 + y_ij**2) ** 1.5
            r3 = max(1e-12, r3)  # avoid division by zero
            force_x[i] += x_ij / r3
            force_y[i] += y_ij / r3
    return force_x, force_y


def spring_embedding(G: SimpleGraph) -> tuple[np.ndarray, np.ndarray]:
    """
    Returns an embedding of G in the plane that minimizes the entropy of the
    edge lengths, which are imagined to be springs.
    """

    tol = 1e-4
    max_iter = int(1e6)
    h = 5e-3

    n = G.num_verts

    spring_constant = 1.0
    friction_constant = 0.2
    x, y = random_embedding(G)

    dx = np.zeros((n,))
    dy = np.zeros((n,))

    ddx = np.zeros((n,))
    ddy = np.zeros((n,))

    adj_mat = G.adjacency_matrix()

    for _ in range(max_iter):
        ddx, ddy = _spring_force(x, y, adj_mat, spring_constant)

        ddx -= friction_constant * dx
        ddy -= friction_constant * dy

        # check for convergence
        d = sum(ddx**2 + ddy**2)
        if d < tol:
            break

        # update position
        x += h * dx
        y += h * dy

        # update velocity
        dx += h * ddx
        dy += h * ddy

    # center the embedding at the origin
    x -= sum(x) / n
    y -= sum(y) / n

    return x, y


def _spring_force(
    x: np.ndarray, y: np.ndarray, adj_mat: np.ndarray, spring_constant: float
) -> tuple[np.ndarray, np.ndarray]:
    n = len(x)
    force_x = np.zeros((n,))
    force_y = np.zeros((n,))
    for i in range(n):
        for j in range(n):
            if adj_mat[i, j] == 0:
                continue
            x_ij = x[i] - x[j]
            y_ij = y[i] - y[j]
            r = np.sqrt(x_ij**2 + y_ij**2)
            r = max(1e-12, r)  # avoid division by zero
            d = spring_constant * (1 / r - 1)
            force_x[i] += d * x_ij
            force_y[i] += d * y_ij
    return force_x, force_y


def spectral_embedding(G: SimpleGraph) -> tuple[np.ndarray, np.ndarray]:
    """
    Embeds G in the plane using the eigenvectors of the Laplacian matrix.
    """
    lap_mat = G.laplacian()
    vals, vecs = np.linalg.eig(lap_mat)
    idx = vals.argsort()
    vals = vals[idx]
    vecs = vecs[:, idx]
    x = vecs[:, -1]
    y = vecs[:, -2]
    return x, y
