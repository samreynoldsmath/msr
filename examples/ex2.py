import sys
import os

current_dir = os.getcwd()
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)

import msr

def main():
	ct = 0
	for k in range(1, 113):
		filename = f'../msr/graph/graph_lib/six_vert/n6_{k}.json'
		G = msr.graph.load(filename)
		d = G.known_msr
		r = msr.msr_sdp_upper_bound(G)
		if r > d:
			ct += 1
			print(k, d, r, r - d)
	print(ct)

if __name__ == '__main__':
	main()