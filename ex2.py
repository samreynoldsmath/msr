from msr import msr, vert6

def main():
	ct = 0
	for k in range(1, 113):
		G, d = vert6.six_verts(k)
		r = msr(G)
		if r > d:
			ct += 1
			print(k, d, r, r - d)
	print(ct)

if __name__ == '__main__':
	main()