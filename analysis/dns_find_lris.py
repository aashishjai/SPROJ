from utils import get_simple_traces_dns
import glob
import sys
import os


def dns_lris():
	# Find LRIs for DNS traceroutes
	main_dir = sys.argv[1]

	# Get name of VP
	directories = main_dir.split(os.sep)
	if directories[-1] != '':
		results_dir = '_'.join(directories[-1].split('_')[3:])+'_results/dns_results'
	else:
		results_dir = '_'.join(directories[-2].split('_')[3:])+'_results/dns_results'

	if not os.path.exists(results_dir):
		os.makedirs(results_dir)

	# Folder with all the DNS traceroutes
	traceroute_folder = main_dir+'/DNS_pipeline_step_2/step4_traceroute/*_dnstraceroute_.txt'	

	# Input file for DNS traceroutes
	input_file = main_dir + \
		'/DNS_pipeline_step_1/have_auth_no_ip_extended.common_three_runs.txt'
	with open(input_file, 'r') as f:
		input_doms_ips_list = [line.strip().split(' ') for line in f]
	dom_to_ip = {t[0]: t[1] for t in input_doms_ips_list}

	simple_traces, _ = get_simple_traces_dns(traceroute_folder, dom_to_ip)
	print("Total input:", len(dom_to_ip))
	print("Total traces:", len(simple_traces))

	no_trace = []
	with open(results_dir+'/last_responding_ips.tsv', 'w') as f:
		f.write("DOMAIN\tLAST_RESPONDING_IP\tSERVER_IP\tMAX_MERGE\n")
		for dom, dest_ip in dom_to_ip.items():
			try:
				trace = simple_traces[dest_ip]
			except KeyError:
				no_trace.append(dom)
			if trace[-1] == dest_ip:
				max_merge = 0
				for ip in reversed(trace[:-1]):
					if ip != '*':
						lri = ip
						break
					else:
						max_merge += 1
			else:
				max_merge = 0
				for ip in reversed(trace[:-1]):
					if ip != '*':
						lri = ip
						break
			f.write(dom + '\t' + lri + '\t' + dest_ip + '\t' + str(max_merge) + '\n')
	
	print(no_trace)

if __name__ == '__main__':
	dns_lris()
