import matplotlib.pyplot as plt
from collections import Counter

import seaborn as sns
import pandas as pd
import numpy as np
import os

def set_style():
	'''
	This is run before any plots are made to set the style for each plot
	'''
	sns.set_style("white")
	tex_params = {
		# Use LaTeX to write all text
		"text.usetex": True,
		"font.family": "serif",
		# Use 10pt font in plots, to match 10pt font in document
		"font.size": 10,
		# Make the legend/label fonts a little smaller
		"axes.labelsize": 8,
		"legend.fontsize": 8,
		
		# Turn on ticks
		'ytick.major.size': 3,
		'ytick.major.width': 0.5,
		'ytick.left': True,
		'xtick.major.size': 3,
		'xtick.major.width': 0.5,
		'xtick.bottom': True,

		"xtick.labelsize": 8,
		"ytick.labelsize": 8,
		'figure.autolayout': True
	}
	plt.rcParams.update(tex_params)
	# plt.tight_layout()

def make_plot(distance_lists, title, outer_axis, legends=[]):
	'''
	This makes an ECDF plot using the seaborn library
	Inputs:
		distance_lists: a list of lists that each contain numbers for which we find the ECDF for
		title: the title of the plot
		outer_axis: the axis object on which to plot this. This is to allow this function to be reused with subplots
		legends: the legends for each line, should be the same length as the "lists" list
	'''

	# Draw multiple lines on the same axis
	for i, dist_list in enumerate(distance_lists):
		ls=['-','--','-.',':'][i%4]
		kwargs = {
		'linestyle':ls,
		'linewidth':1
		}
		ax = sns.ecdfplot(data=dist_list, ax=outer_axis, **kwargs)
	
	if len(legends):
		ax.legend(legends, loc='lower right')

	ax.spines['right'].set_visible(False)
	ax.spines['top'].set_visible(False)

	ax.set_title(title)
	ax.set_ylabel("Fraction of Data")
	max_dist = max([max(dist_list) for dist_list in distance_lists])
	x_ticks = range(0, max_dist+2, 1)
	ax.set_xticks(x_ticks)
	ax.set_yticks(np.arange(0, 1.1, 0.1))

	figname = '_'.join(title.split(' '))+'.png'
	# plt.savefig('plots/'+figname)
	# plt.clf()

if __name__ == '__main__':
	# Example implementation

	set_style()

	width = 8.5
	# Calculate height according to golden ratio
	height = width * (5**.5 - 1) / 2
	fig, axes = plt.subplots(1, 2, figsize=(width, height), dpi=300)

	list1 = [1, 2, 3, 4]
	list2 = [2, 2, 2, 2]
	list3 = [1, 2, 4, 5]
	list4 = [1, 2, 3, 3]

	make_plot([list1, list2], 'Example 1', axes[0], ['line1', 'line2'])
	make_plot([list3, list4], 'Example 2', axes[1], ['line1', 'line2'])

	plt.show()
