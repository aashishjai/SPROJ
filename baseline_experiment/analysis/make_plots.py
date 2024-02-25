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
		"font.size": 12,
		# Make the legend/label fonts a little smaller
		"axes.labelsize": 12,
		"legend.fontsize": 12,
		
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

def get_list(filename):
	with open(filename, 'r') as f:
		X = [int(line.strip()) for line in f]

	X = [x for x in X if x < 16]
	X = [1 if x == 0 else x for x in X]
	return X

def get_both_lists(directory, filetype):
	n_1_file = directory+'n-1_' + filetype + '.txt'
	bt_file = directory+'backtracked_' + filetype + '.txt'

	n_1 = get_list(n_1_file)
	bt = get_list(bt_file)

	return n_1, bt

def make_plot(distance_lists, title, outer_axis, legends=[]):
	'''
	This makes an ECDF plot using the seaborn library
	Inputs:
		distance_lists: a list of lists that each contain numbers for which we find the ECDF for
		title: the title of the plot
		outer_axis: the axis object on which to plot this. This is to allow this function to be reused with subplots
		legends: the legends for each line, should be the same length as the "lists" list
	'''

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
	# ax.set_xlabel("Distance of target IP from reference IP")
	ax.set_ylabel("Fraction of Data")
	max_dist = max([max(dist_list) for dist_list in distance_lists])
	x_ticks = range(0, max_dist+2, 1)
	ax.set_xticks(x_ticks)
	ax.set_yticks(np.arange(0, 1.1, 0.1))

	figname = '_'.join(title.split(' '))+'.png'
	# plt.savefig('plots/'+figname)
	# plt.clf()


def calc_false_negatives(dist_list, threshold):
	above_threshold = [dist for dist in dist_list if dist > threshold]
	return float(len(above_threshold)) / float(len(dist_list)) * 100

def pick_thresholds(dist_list):
	for i in range(1, 10):
		fn = calc_false_negatives(dist_list, i)
		print("FN: ", fn, ' Threshold: ', i)
		if fn <= 1.2:
			break

	print("Threshold Picked:", i)
	print()

def get_percentage(dist_list):
	upto_three = [dist for dist in dist_list if 1 < dist <= 3]
	percentage = float(len(upto_three)) / float(len(dist_list)) * 100
	print(percentage)

def write_file(filename, dist_list):
	name = filename.split(os.sep)[-1].split('.')[0] +' N: '
	print(name, len(dist_list))
	with open(filename, 'w') as f:
		f.write("N: " + str(len(dist_list)) + '\n')
		for dist in dist_list:
			f.write(str(dist)+'\n')

def ref_same(x):
	dest_ip = '.'.join(x['server_ip'].split('.')[0:2])
	ref_ip = '.'.join(x['reference_ip'].split('.')[0:2])

	if dest_ip == ref_ip:
		return True
	else:
		return False



if __name__ == '__main__':
	if not os.path.exists('plots/'):
		os.mkdir('plots/')

	raw_files = 'raw_files/'
	if not os.path.exists(raw_files):
		os.mkdir(raw_files)


	set_style()

	# # Reference comparison
	# fig, ax = plt.subplots(dpi=300)

	# df = pd.read_csv('TCP_HTTP/from_control_analysis/simple_tcp_tcp_control/outputs/all_tcp_from_test.csv')
	# df = df[df['distance'] != -1]
	# df = df[df['cdn'] == False]
	# df['ref_same'] = df.apply(ref_same, axis = 1)
	# ref_same = df[df['ref_same'] == True]
	# ref_diff = df[df['ref_same'] == False]

	# ref_same_distances = list(ref_same['distance'])
	# ref_diff_distances = list(ref_diff['distance'])
	# ref_same_total = len(ref_same_distances)
	# ref_diff_total = len(ref_diff_distances)

	# title = "TCP Non-CDN distances - Reference Comparison"
	# legends = ['Reference IP == Server IP', 'Reference IP != Server IP']

	# make_plot([ref_same_distances, ref_diff_distances], title, ax, legends )

	# fig.savefig('plots/reference_ip_comparison.png')
	# exit()


	width = 8.5
	height = width * (5**.5 - 1) / 2
	fig, axes = plt.subplots(2, 2, figsize=(width, height), dpi=150)

	# GET DNS CONTROL
	dns_from_control = get_list('DNS/distances/dns_from_control.txt')
	make_plot([dns_from_control], 'DNS Distances From Control', axes[0, 0], ['DNS'])
	write_file(raw_files+'dns_from_control.txt', dns_from_control)
	get_percentage(dns_from_control)
	pick_thresholds(dns_from_control)

	tcp_directory = 'TCP_HTTP/from_control_analysis/simple_tcp_tcp_control/distances/'
	http_directory = 'TCP_HTTP/from_control_analysis/simple_http_tcp_control/distances/'
	
	# HTTP/TCP FROM CONTROL
	tcp_control = get_list(tcp_directory+'tcp_from_control.txt')
	write_file(raw_files+'tcp_control.txt', tcp_control)
	get_percentage(tcp_control)
	pick_thresholds(tcp_control)
	
	http_control = get_list(http_directory + 'http_from_control.txt')
	write_file(raw_files+'http_control.txt', http_control)
	get_percentage(http_control)
	pick_thresholds(http_control)
	
	make_plot([tcp_control, http_control], 
			'TCP-HTTP Distances From Control',
			axes[0, 1],
			['TCP', 'HTTP']
			)

	# HTTP/TCP FROM TEST CDN
	tcp_test_cdn = get_list(tcp_directory+'tcp_from_test_cdn.txt')
	write_file(raw_files+'tcp_test_cdn.txt', tcp_test_cdn)
	get_percentage(tcp_test_cdn)
	pick_thresholds(tcp_test_cdn)
	
	http_test_cdn = get_list(http_directory + 'http_from_test_cdn.txt')
	write_file(raw_files+'http_test_cdn.txt', http_test_cdn)
	get_percentage(http_test_cdn)
	pick_thresholds(http_test_cdn)
	
	# counts = Counter(tcp_test_cdn)
	# print(counts)
	# counts = Counter(http_test_cdn)
	# print(counts)

	make_plot([tcp_test_cdn, http_test_cdn], 
			'TCP-HTTP Distances From Test - CDN',
			axes[1, 0],
			['TCP', 'HTTP']
			)

	# HTTP/TCP FROM TEST NON-CDN
	tcp_test_non_cdn = get_list(tcp_directory+'tcp_from_test_non_cdn.txt')
	write_file(raw_files+'tcp_test_non_cdn.txt', tcp_test_non_cdn)
	get_percentage(tcp_test_non_cdn)
	pick_thresholds(tcp_test_non_cdn)

	http_test_non_cdn = get_list(http_directory + 'http_from_test_non_cdn.txt')
	write_file(raw_files+'http_test_non_cdn.txt', http_test_non_cdn)
	get_percentage(http_test_non_cdn)
	pick_thresholds(http_test_non_cdn)
	
	# counts = Counter(tcp_test_non_cdn)
	# print(counts)
	# counts = Counter(http_test_non_cdn)
	# print(counts)

	make_plot([tcp_test_non_cdn, http_test_non_cdn], 
			'TCP-HTTP Distances From Test - Non-CDN',
			axes[1, 1],
			['TCP', 'HTTP'] 
			)


	print("DNS:", len(dns_from_control))
	print("TCP:", len(tcp_control)+len(tcp_test_cdn)+len(tcp_test_non_cdn))
	print("HTTP:", len(http_control)+len(http_test_cdn)+len(http_test_non_cdn))

	# fig.tight_layout()
	# for ax in axes.flat:
	    # ax.label_outer()

	plt.savefig('plots/full.png')

	# # HTTP FROM CONTROL
	# n_1, bt = get_both_lists('simple_http_tcp_control/distances/', 'from_control')
	# make_plot(n_1, bt, 'HTTP Baseline Distances From Control')
	
	# # HTTP FROM TEST CDN
	# n_1, bt = get_both_lists('simple_http_tcp_control/distances/', 'from_test_cdn')
	# make_plot(n_1, bt, 'HTTP Baseline Distances From Test - CDN Set')

	# # HTTP FROM TEST NON-CDN
	# n_1, bt = get_both_lists('simple_http_tcp_control/distances/', 'from_test_non_cdn')
	# make_plot(n_1, bt, 'HTTP Baseline Distances From Test - Non-CDN Set')
