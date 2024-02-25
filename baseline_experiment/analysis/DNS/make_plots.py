import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

def set_style():
	sns.set_context("paper")
	sns.set(font="serif")

	sns.set_style("white", {
		"font.family": "serif"
		})

def get_list(filename):
	with open(filename, 'r') as f:
		X = [int(line.strip()) for line in f]

	X = [x for x in X if x < 16]
	return X

def get_both_lists(directory, filetype):
	n_1_file = directory+'n-1_' + filetype + '.txt'
	bt_file = directory+'backtracked_' + filetype + '.txt'

	n_1 = get_list(n_1_file)
	bt = get_list(bt_file)

	return n_1, bt

def make_plot(list1, list2, title):
	fig, ax = plt.subplots()

	ax = sns.ecdfplot(data=list1, ax=ax)
	ax = sns.ecdfplot(data=list2, ax=ax)

	ax.legend(['N-1 IPs', 'Backtracked IPs'], loc='lower right')
	ax.set_title(title)
	ax.set_xlabel("Distance of target IP from reference IP")
	max_dist = max(max(list1), max(list2))
	x_ticks = range(0, max_dist+2, 1)
	ax.set_xticks(x_ticks)
	ax.set_yticks(np.arange(0, 1.1, 0.1))

	figname = '_'.join(title.split(' '))+'.png'
	plt.savefig('plots/'+figname)
	plt.clf()

if __name__ == '__main__':
	if not os.path.exists('plots/'):
		os.mkdir('plots/')

	set_style()

	# DNS FROM CONTROL
	n_1, bt = get_both_lists('./distances/', 'from_control')
	make_plot(n_1, bt, 'DNS Baseline Distances From Control')
	
