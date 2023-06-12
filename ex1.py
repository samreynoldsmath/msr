import msr

def main():
	four_cycle_example()
	five_cycle_example()
	house_example()
	even_chord_example()
	odd_chord_example()

def four_cycle_example():
	print('Four cycle:')
	G = msr.graph_lib.cycle(4)
	d = 2
	r = msr.msr(G, debug=True)
	print('\tExact \t', d)
	print('\tApprox \t', r)

def five_cycle_example():
	print('Five cycle:')
	G = msr.graph_lib.cycle(5)
	d = 3
	r = msr.msr(G, debug=True)
	print('\tExact \t', d)
	print('\tApprox \t', r)

def house_example():
	print('House:')
	G = msr.graph_lib.cycle(5)
	G.add_edge([1, 3])
	d = 3
	r = msr.msr(G, debug=True)
	print('\tExact \t', d)
	print('\tApprox \t', r)

def even_chord_example():
	print('Even chord:')
	G = msr.graph_lib.cycle(6)
	G.add_edge([1, 4])
	d = 4
	r = msr.msr(G, debug=True)
	print('\tExact \t', d)
	print('\tApprox \t', r)

def odd_chord_example():
	print('Odd chord:')
	G = msr.graph_lib.cycle(6)
	G.add_edge([1, 3])
	d = 4
	r = msr.msr(G, debug=True)
	print('\tExact \t', d)
	print('\tApprox \t', r)
	print('')

if __name__ == '__main__':
	main()