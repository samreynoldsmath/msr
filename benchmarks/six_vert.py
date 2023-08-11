import sys
import os

current_dir = os.getcwd()
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)

import msr
import timeit

def main():
	"""
	Benchmark the implementation of msr_bounds() by computing bounds on all
	112 connected graphs on 6 vertices (up to isomorphism). A report on how
	accurate the bounds are is generated. A rough estimate of efficiency is
	obtained with timing the execution with timeit.
	"""

	# number of graphs in test set
	num_graphs = 112

	# number of graphs with incorrect bounds
	not_tight = 0
	wrong = 0
	wrong_or_not_tight = 0
	d_lo_less_than_known = 0
	d_lo_greater_than_known = 0
	d_hi_less_than_known = 0
	d_hi_greater_than_known = 0

	for i in range(1, num_graphs + 1):
		filename = f'../msr/graph/graph_lib/six_vert/n6_{i}.json'
		G = msr.graph.load(filename)

		d_lo, d_hi = msr.msr_bounds(G)

		# check if lower bound is correct
		d_lo_ok = d_lo < G.known_msr
		d_lo_good = d_lo == G.known_msr
		d_lo_bad = d_lo > G.known_msr

		# check if upper bound is correct
		d_hi_ok = d_hi > G.known_msr
		d_hi_good = d_hi == G.known_msr
		d_hi_bad = d_hi < G.known_msr

		# bounds are correct but not tight
		if d_lo_ok:
			d_lo_less_than_known += 1
		if d_hi_ok:
			d_hi_greater_than_known += 1
		if d_lo_ok or d_hi_ok:
			not_tight += 1
			msg = 'pass'

		# bounds are incorrect
		if d_lo_bad:
			d_lo_greater_than_known += 1
		if d_hi_bad:
			d_hi_less_than_known += 1
		if d_lo_bad or d_hi_bad:
			wrong += 1
			msg = 'fail'

		# count total mistakes
		if not d_lo_good or not d_hi_good:
			wrong_or_not_tight += 1
			if wrong_or_not_tight == 1:
				print('       i  d_lo  msr  d_hi')
			print('%s %4d %4d %4d %4d' % (msg, i, d_lo, G.known_msr, d_hi))

	# final results
	print(f'{wrong + not_tight} out of ' +
       f'{num_graphs} graphs had bounds that did not coincide with known msr')

	print(f'{wrong} out of {num_graphs} graphs had ' +
       '\033[91mincorrect\033[0m bounds')
	print(f'\t{d_lo_greater_than_known} out of {num_graphs} graphs had ' +
       'd_lo > known_msr')
	print(f'\t{d_hi_less_than_known} out of {num_graphs} graphs had ' +
       'd_hi < known_msr')

	print(f'{not_tight} out of {num_graphs} graphs had ' +
       '\033[93mcorrect\033[0m ' +
        'but not tight bounds')
	print(f'\t{d_lo_less_than_known} out of {num_graphs} graphs had ' +
       'd_lo < known_msr')
	print(f'\t{d_hi_greater_than_known} out of {num_graphs} graphs had ' +
       'd_hi > known_msr')

if __name__ == '__main__':
    t = timeit.timeit(main, number=1)
    print(f'Execution time: {t:.4f} seconds')