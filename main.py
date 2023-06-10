import msr

# define graph G
G = msr.graph_lib.cycle(6)
G.add_edge([1, 3])

# compute msr(G)
print(msr.msr(G))

# draw a graph embedding
msr.draw_graph(G)