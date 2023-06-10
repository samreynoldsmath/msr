import matplotlib.pyplot as plt
from numpy import zeros, cos, sin, pi
from .graph import graph

def draw_graph(G: graph):
    x = circular_embedding(n=G.num_vert)
    plt.figure()
    draw_embedding(x, E=G.edges)
    plt.show()

def circular_embedding(n):
    # circular planar embedding
    x = zeros((n, 2))
    for i in range(n):
        x[i, 0] = cos((i * 2 + 0.5) * pi / n)
        x[i, 1] = sin((i * 2 + 0.5) * pi / n)
    return x

def draw_embedding(x, E):
    # draw vertices
    plt.plot(x[:, 0], x[:, 1], 'ko')
    plt.axis('scaled')
    # draw edges
    for edge in E:
        u = edge[0] - 1
        v = edge[1] - 1
        plt.plot(x[[u, v], 0],x[[u, v], 1], 'k')
    for i in range(x.shape[0]):
        plt.text(x[i, 0] + 0.05, x[i, 1] + 0.05, '%d'%(i + 1))