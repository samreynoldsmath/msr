from .graph import graph
from . import graph_lib

def six_verts(idx: int):

	if idx == 1:
		G = graph_lib.complete(6)
		d = 1

	elif idx == 2:
		G = graph_lib.complete(6)
		G.remove_edge([1, 2])
		d = 2

	elif idx == 3:
		G = graph_lib.complete(6)
		G.remove_edge([1, 3])
		G.remove_edge([1, 5])
		d = 2

	elif idx == 4:
		G = graph_lib.complete(6)
		G.remove_edge([1, 3])
		G.remove_edge([4, 6])
		d = 2

	elif idx == 5:
		G = graph_lib.complete(6)
		G.remove_edge([1, 3])
		G.remove_edge([1, 4])
		G.remove_edge([1, 5])
		d = 2

	elif idx == 6:
		G = graph_lib.complete(6)
		G.remove_edge([1, 3])
		G.remove_edge([3, 5])
		G.remove_edge([1, 5])
		d = 3

	elif idx == 7:
		G = graph(6, [
			[1, 2], [1, 3], [1, 4], [1, 5], [1, 6],
			[2, 3], [2, 4], [2, 5], [2, 6],
			[3, 4],
			[4, 5],
			[5, 6]
		])
		d = 3

	elif idx == 8:
		G = graph_lib.wheel(6)
		G.add_edge([1, 3])
		G.add_edge([2, 4])
		d = 2

	elif idx == 9:
		G = graph_lib.cycle(6)
		G.add_edges([
			[1, 3], [3, 5], [5, 1],
			[2, 4], [4, 6], [6, 2]
		])
		d = 2

	elif idx == 10:
		G = graph_lib.complete(5)
		G.set_num_vert(6)
		G.add_edge([1, 6])
		d = 2

	elif idx == 11:
		G = graph(6, [
			[1, 2], [1, 3],
			[2, 4], [2, 5], [2, 6],
			[3, 4], [3, 5], [3, 6],
			[4, 5], [5, 6]
		])
		d = 3

	elif idx == 12:
		G = graph(6, [
			[1, 2], [1, 3], [1, 4], [1, 5], [1, 6],
			[2, 3],
			[3, 4], [3, 5],
			[4, 5], [4, 6],
			[5, 6]
		])
		d = 3

	elif idx == 13:
		G = graph(6, [
			[1, 2], [1, 3], [1, 4], [1, 5], [1, 6],
			[2, 3], [2, 4], [2, 5], [2, 6],
			[3, 4], [5, 6]
		])
		d = 2

	elif idx ==14:
		G = graph_lib.complete(5)
		G.set_num_vert(6)
		G.remove_edge([1, 2])
		G.add_edges([
			[1, 6], [6, 2]
		])
		d = 2

	elif idx == 15:
		G = graph_lib.cycle(4)
		G.set_num_vert(6)
		G.add_edges([
			[5, 1], [5, 2], [5, 3], [5, 4],
			[6, 1], [6, 2], [6, 5]
		])
		d = 3

	elif idx == 16:
		G = graph_lib.cycle(6)
		G.add_edges([
			[1, 3], [1, 4], [1, 5],
			[2, 5], [3, 6]
		])
		d = 3

	elif idx == 17:
		G = graph_lib.cycle(6)
		G.add_edges([
			[1, 4], [2, 5], [3, 6],
			[1, 3], [4, 6]
		])
		d = 2

	elif idx == 18:
		G = graph(6, [
			[1, 3], [1, 4], [1, 5], [1, 6],
			[2, 3], [2, 4], [2, 5], [2, 6],
			[3, 4],
			[4, 5],
			[5, 6]
		])
		d = 3

	elif idx == 19:
		G = graph_lib.path(5)
		G.set_num_vert(6)
		G.add_edges([
			[4, 1], [4, 2], [4, 3], [4, 6],
			[6, 1], [6, 2], [6, 3]
		])
		d = 3

	elif idx == 20:
		G = graph_lib.path(5)
		G.set_num_vert(6)
		G.add_edges([
			[5, 2], [5, 3], [5, 4], [5, 6],
			[6, 2], [6, 3], [6, 4]
		])
		d = 3

	elif idx == 21:
		G = graph(6, [
			[1, 2], [1, 3], [1, 4], [1, 5], [1, 6],
			[2, 3], [2, 4], [2, 5], [2, 6],
			[5, 6]
		])
		d = 3

	elif idx == 22:
		G = graph_lib.cycle(5)
		G.set_num_vert(6)
		G.add_edges([
			[6, 1], [6, 3], [6, 4],
			[1, 3], [1, 4]
		])
		d = 3

	elif idx == 23:
		G = graph_lib.cycle(6)
		G.add_edges([
			[2, 5], [2, 6],
			[3, 5], [3, 6]
		])
		d = 3

	elif idx == 24:
		G = graph(6, [
			[1, 2], [1, 3], [1, 4],
			[2, 3], [2, 4],
			[3, 4], [3, 5], [3, 6],
			[4, 5], [5, 6]
		])
		d = 3

	elif idx == 25:
		G = graph(6, [
			[1, 2], [1, 3],
			[2, 3], [2, 4], [2, 5], [2, 6],
			[3, 4], [3, 5], [3, 6],
			[4, 5], [5, 6]
		])
		d = 3

	elif idx == 26:
		G = graph_lib.complete(4)
		G.set_num_vert(6)
		G.add_edges([
			[5, 4], [5, 6],
			[6, 2], [6, 3]
		])
		d = 3

	elif idx == 27:
		G = graph_lib.wheel(5)
		G.set_num_vert(6)
		G.add_edges([
			[1, 6], [2, 6]
		])
		d = 3

	elif idx == 28:
		G = graph_lib.wheel(6)
		d = 3

	elif idx == 29:
		G = graph_lib.wheel(5)
		G.set_num_vert(6)
		G.add_edges([
			[6, 1], [6, 3]
		])
		d = 3

	elif idx == 30:
		G = graph_lib.cycle(6)
		G.add_edges([
			[1, 3], [4, 6], [2, 4], [3, 5]
		])
		d = 3

	elif idx == 31:
		G = graph_lib.cycle(4)
		G.set_num_vert(6)
		G.add_edges([
			[5, 1], [5, 2], [5, 3],
			[6, 1], [6, 3], [6, 4]
		])
		d = 2

	elif idx == 32:
		G = graph_lib.cycle(6)
		G.add_edges([
			[1, 4], [2, 5], [3, 6], [1, 3]
		])
		d = 3

	elif idx == 33:
		G = graph(6, [
			[1, 2], [2, 3], [2, 4], [2, 5], [2, 6],
			[3, 4], [3, 5], [4, 5], [5, 6]
		])
		d = 3

	elif idx == 34:
		G = graph(6, [
			[1, 2], [2, 3], [2, 4], [2, 5],
			[3, 4], [3, 5], [4, 5], [4, 6], [5, 6]
		])
		d = 3

	elif idx == 35:
		G = graph(6, [
			[1, 2], [2, 3], [2, 4],
			[3, 4], [3, 5], [3, 6],
			[4, 5], [4, 6], [5, 6]
		])
		d = 3

	elif idx == 36:
		G = graph_lib.complete(4)
		G.set_num_vert(6)
		G.add_edges([
			[5, 4], [5, 6], [6, 4]
		])
		d = 2

	elif idx == 37:
		G = graph(6, [
			[1, 2], [1, 3], [1, 4], [1, 5], [1, 6],
			[2, 3], [2, 4], [2, 5], [2, 6]
		])
		d = 4

	elif idx == 38:
		G = graph(6, [
			[1, 2], [2, 3], [2, 4], [2, 5], [2, 6],
			[3, 4], [3, 5], [4, 6], [5, 6]
		])
		d = 3

	elif idx == 39:
		G = graph_lib.wheel(5)
		G.set_num_vert(6)
		G.add_edge([6, 4])
		d = 3

	elif idx == 40:
		G = graph_lib.cycle(5)
		G.set_num_vert(6)
		G.add_edges([
			[1, 3], [1, 4],
			[6, 1], [6, 4]
		])
		d = 4

	elif idx == 41:
		G = graph_lib.cycle(5)
		G.set_num_vert(6)
		G.add_edges([
			[2, 5], [6, 1], [6, 2], [6, 5]
		])
		d = 3

	elif idx == 42:
		G = graph_lib.cycle(num_vert=6)
		G.add_edges([
			[1, 3],
			[3, 5],
			[5, 1]
		])
		d = 3

	elif idx == 43:
		G = graph_lib.cycle(6)
		G.add_edges([
			[1, 3], [1, 4], [1, 5]
		])
		d = 4

	elif idx == 44:
		G = graph_lib.cycle(6)
		G.add_edges([
			[1, 5], [2, 4], [1, 4]
		])
		d = 4

	elif idx == 45:
		G = graph(6, [
			[1, 2], [1, 3], [2, 3], [2, 4], [2, 6],
			[3, 4], [3, 6], [4, 5], [5, 6]
		])
		d = 3

	elif idx == 46:
		G = graph_lib.cycle(5)
		G.set_num_vert(6)
		G.add_edges([
			[2, 5], [6, 2], [6, 3], [6, 5]
		])
		d = 3

	elif idx == 47:
		G = graph_lib.wheel(6)
		G.remove_edge([1, 6])
		d = 3

	elif idx == 48:
		G = graph_lib.cycle(5)
		G.set_num_vert(6)
		G.add_edges([
			[2, 5], [6, 2], [6, 3], [6, 4]
		])
		d = 3

	elif idx == 49:
		G = graph_lib.cycle(4)
		G.set_num_vert(6)
		G.add_edges([
			[5, 1], [5, 3], [5, 6], [6, 1], [6, 3]
		])
		d = 3

	elif idx == 50:
		G = graph_lib.cycle(4)
		G.set_num_vert(6)
		G.add_edges([
			[5, 2], [5, 3], [5, 4], [5, 6], [6, 1]
		])
		d = 3

	elif idx == 51:
		G = graph(6, [
			[1, 2], [1, 3], [2, 3],
			[4, 5], [5, 6], [4, 6],
			[1, 4], [2, 5], [3, 6]
		])
		d = 3

	elif idx == 52:
		G = graph_lib.cycle(6)
		G. add_edges([
			[1, 4], [2, 5], [3, 6]
		])
		d = 3

	elif idx == 53:
		G = graph_lib.complete(4)
		G.set_num_vert(6)
		G.add_edges([
			[1, 5], [1, 6]
		])
		d = 3

	elif idx == 54:
		G = graph_lib.complete(4)
		G.set_num_vert(6)
		G.add_edges([
			[1, 5], [2, 6]
		])
		d = 3

	elif idx == 55:
		G = graph_lib.complete(4)
		G.set_num_vert(6)
		G.add_edges([
			[1, 5], [5, 6]
		])
		d = 3

	elif idx == 56:
		G = graph_lib.cycle(4)
		G.set_num_vert(6)
		G.add_edges([
			[2, 4], [2, 5], [4, 5], [4, 6]
		])
		d = 4

	elif idx == 57:
		G = graph_lib.cycle(4)
		G.set_num_vert(6)
		G.add_edges([
			[2, 4], [2, 5], [4, 5], [5, 6]
		])
		d = 4

	elif idx == 58:
		G = graph_lib.cycle(5)
		G.set_num_vert(6)
		G.add_edges([
			[1, 3], [1, 4], [1, 6]
		])
		d = 4

	elif idx == 59:
		G = graph_lib.cycle(5)
		G.set_num_vert(6)
		G.add_edges([
			[1, 3], [1, 4], [3, 6]
		])
		d = 4

	elif idx == 60:
		G = graph_lib.cycle(5)
		G.set_num_vert(6)
		G.add_edges([
			[1, 3], [1, 4], [2, 6]
		])
		d = 4

	elif idx == 61:
		G = graph_lib.cycle(4)
		G.set_num_vert(6)
		G.add_edges([
			[1 ,3], [1, 5], [1, 6], [5, 6]
		])
		d = 3

	elif idx == 62:
		G = graph_lib.cycle(4)
		G.set_num_vert(6)
		G.add_edges([
			[2, 4], [1, 5], [1, 6], [5, 6]
		])
		d = 3

	elif idx == 63:
		G = graph_lib.cycle(4)
		G.set_num_vert(6)
		G.add_edges([
			[5, 1], [5, 2], [5, 4], [1, 6]
		])
		d = 3

	elif idx == 64:
		G = graph_lib.cycle(4)
		G.set_num_vert(6)
		G.add_edges([
			[5, 1], [5, 2], [5, 3], [1, 6]
		])
		d = 3

	elif idx == 65:
		G = graph_lib.cycle(4)
		G.set_num_vert(6)
		G.add_edges([
			[5, 4], [5, 2], [5, 3], [1, 6]
		])
		d = 3

	elif idx == 66:
		G = graph_lib.cycle(5)
		G.set_num_vert(6)
		G.add_edges([
			[2, 5], [2, 6], [5, 6]
		])
		d = 4

	elif idx == 67:
		G = graph_lib.cycle(6)
		G.add_edges([
			[1, 3], [1, 4]
		])
		d = 4

	elif idx == 68:
		G = graph_lib.cycle(6)
		G.add_edges([
			[1, 3], [1, 5]
		])
		d = 4

	elif idx == 69:
		G = graph_lib.cycle(5)
		G.set_num_vert(6)
		G.add_edges([
			[6, 1], [6, 2], [6, 3]
		])
		d = 3

	elif idx == 70:
		G = graph_lib.cycle(6)
		G.add_edges([
			[1, 3], [4, 6]
		])
		d = 4

	elif idx == 71:
		G = graph_lib.cycle(5)
		G.set_num_vert(6)
		G.add_edges([
			[1, 6], [6 ,3], [1, 4]
		])
		d = 4

	elif idx == 72:
		G = graph_lib.cycle(5)
		G.set_num_vert(6)
		G.add_edges([
			[1, 6], [6 ,3], [6, 4]
		])
		d = 3

	elif idx == 73:
		G = graph_lib.cycle(4)
		G.set_num_vert(6)
		G.add_edges([
			[1, 5], [1, 6], [3, 5], [3, 6]
		])
		d = 4

	elif idx == 74:
		G = graph_lib.cycle(6)
		G.add_edges([
			[1, 4], [2, 5]
		])
		d = 3

	elif idx == 75:
		G = graph_lib.cycle(4)
		G.set_num_vert(6)
		G.add_edges([
			[1, 3], [1, 5], [1, 6]
		])
		d = 4

	elif idx == 76:
		G = graph_lib.cycle(4)
		G.set_num_vert(6)
		G.add_edges([
			[1, 3], [1, 5], [3, 6]
		])
		d = 4

	elif idx == 77:
		G = graph_lib.cycle(4)
		G.set_num_vert(6)
		G.add_edges([
			[1, 3], [1, 5], [2, 6]
		])
		d = 4

	elif idx == 78:
		G = graph_lib.cycle(4)
		G.set_num_vert(6)
		G.add_edges([
			[2, 4], [1, 5], [1, 6]
		])
		d = 4

	elif idx == 79:
		G = graph_lib.star(6)
		G.add_edges([
			[1, 2], [3, 4]
		])
		d = 3

	elif idx == 80:
		G = graph_lib.cycle(4)
		G.set_num_vert(6)
		G.add_edges([
			[2, 4], [1, 5], [3, 6]
		])
		d = 4

	elif idx == 81:
		G = graph_lib.cycle(4)
		G.set_num_vert(6)
		G.add_edges([
			[1, 3], [1, 5], [5, 6]
		])
		d = 4

	elif idx == 82:
		G = graph_lib.cycle(4)
		G.set_num_vert(6)
		G.add_edges([
			[2, 4], [1, 5], [5, 6]
		])
		d = 4

	elif idx == 83:
		G = graph_lib.path(4)
		G.set_num_vert(6)
		G.add_edges([
			[1, 5], [5, 2], [2, 6], [6, 3]
		])
		d = 3

	elif idx == 84:
		G = graph_lib.path(4)
		G.set_num_vert(6)
		G.add_edges([
			[1, 5], [5, 2], [4, 6], [6, 3]
		])
		d = 3

	elif idx == 85:
		G = graph_lib.cycle(5)
		G.set_num_vert(6)
		G.add_edges([
			[1, 3], [1, 6]
		])
		d = 4

	elif idx == 86:
		G = graph_lib.cycle(5)
		G.set_num_vert(6)
		G.add_edges([
			[1, 3], [2, 6]
		])
		d = 4

	elif idx == 87:
		G = graph_lib.cycle(5)
		G.set_num_vert(6)
		G.add_edges([
			[1, 3], [5, 6]
		])
		d = 4

	elif idx == 88:
		G = graph_lib.cycle(4)
		G.set_num_vert(6)
		G.add_edges([
			[1, 5], [1, 6], [5, 6]
		])
		d = 3

	elif idx == 89:
		G = graph_lib.cycle(6)
		G.add_edge([1, 3])
		d = 4

	elif idx == 90:
		G = graph_lib.cycle(4)
		G.set_num_vert(6)
		G.add_edges([
			[1, 5], [5, 3], [1, 6]
		])
		d = 4

	elif idx == 91:
		G = graph_lib.cycle(4)
		G.set_num_vert(6)
		G.add_edges([
			[1, 5], [5, 3], [2, 6]
		])
		d = 4

	elif idx == 92:
		G = graph_lib.cycle(6)
		G.add_edge([1, 4])
		d = 4

	elif idx == 93:
		G = graph_lib.cycle(4)
		G.set_num_vert(6)
		G.add_edges([
			[1, 5], [5, 6], [6, 3]
		])
		d = 4

	elif idx == 94:
		G = graph_lib.complete(3)
		G.set_num_vert(6)
		G.add_edges([
			[1, 4], [1, 5], [1, 6]
		])
		d = 4

	elif idx == 95:
		G = graph_lib.complete(3)
		G.set_num_vert(6)
		G.add_edges([
			[1, 4], [1, 5], [2, 6]
		])
		d = 4

	elif idx == 96:
		G = graph_lib.complete(3)
		G.set_num_vert(6)
		G.add_edges([
			[1, 4], [2, 5], [3, 6]
		])
		d = 4

	elif idx == 97:
		G = graph_lib.complete(3)
		G.set_num_vert(6)
		G.add_edges([
			[1, 4], [1, 5], [5, 6]
		])
		d = 4

	elif idx == 98:
		G = graph_lib.complete(3)
		G.set_num_vert(6)
		G.add_edges([
			[1, 4], [2, 5], [5, 6]
		])
		d = 4

	elif idx == 99:
		G = graph_lib.complete(3)
		G.set_num_vert(6)
		G.add_edges([
			[1, 4], [4, 5], [4, 6]
		])
		d = 4

	elif idx == 100:
		G = graph_lib.complete(3)
		G.set_num_vert(6)
		G.add_edges([
			[1, 4], [4, 5], [5, 6]
		])
		d = 4

	elif idx == 101:
		G = graph_lib.cycle(4)
		G.set_num_vert(6)
		G.add_edges([
			[1, 5], [1, 6]
		])
		d = 4

	elif idx == 102:
		G = graph_lib.cycle(4)
		G.set_num_vert(6)
		G.add_edges([
			[1, 5], [2, 6]
		])
		d = 4

	elif idx == 103:
		G = graph_lib.cycle(4)
		G.set_num_vert(6)
		G.add_edges([
			[1, 5], [3, 6]
		])
		d = 4

	elif idx == 104:
		G = graph_lib.cycle(4)
		G.set_num_vert(6)
		G.add_edges([
			[1, 5], [5, 6]
		])
		d = 4

	elif idx == 105:
		G = graph_lib.cycle(5)
		G.set_num_vert(6)
		G.add_edges([
			[1, 6]
		])
		d = 4

	elif idx == 106:
		G = graph_lib.cycle(6)
		d = 4

	elif idx == 107:
		G = graph_lib.star(6)
		d = 5

	elif idx == 108:
		G = graph_lib.star(5)
		G.set_num_vert(6)
		G.add_edge([5, 6])
		d = 5

	elif idx == 109:
		G = graph_lib.path(4)
		G.set_num_vert(6)
		G.add_edges([
			[2, 5], [3, 6]
		])
		d = 5

	elif idx == 110:
		G = graph_lib.path(4)
		G.set_num_vert(6)
		G.add_edges([
			[2, 5], [5, 6]
		])
		d = 5

	elif idx == 111:
		G = graph_lib.path(5)
		G.set_num_vert(6)
		G.add_edge([2, 6])
		d = 5

	elif idx == 112:
		G = graph_lib.path(6)
		d = 5

	else:
		raise ValueError(
			'There are only 112 connected graphs on 6 vertices'
		)

	return G, d