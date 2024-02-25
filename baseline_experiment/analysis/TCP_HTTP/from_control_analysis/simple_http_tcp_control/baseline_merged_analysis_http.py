import os
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.distributions.empirical_distribution import ECDF
from collections import Counter, OrderedDict
import json 

def get_mda_traces(file):
	with open(file, 'r') as f:
		full_dict = json.load(f)

	return full_dict

def get_traces_tcp(input_log_fn):
	all_traces = []
	with open(input_log_fn, 'r') as input_log_obj:
		new_trace = []
		for line in input_log_obj:
			components = line.strip().split(' ')
			if "tcp-traceroute" == components[0]:
				new_trace = list(filter(None, new_trace))
				all_traces.append(new_trace)
				new_trace = []
				my_ip = components[2]
				serv_ip = components[-1]
				new_trace.append(my_ip)
				new_trace.append(serv_ip)
			else:
				if components[2]:
					new_trace.append(components[2])


		all_traces.append(new_trace)
		all_traces = list(filter(None, all_traces))
		return all_traces

def get_traces_http(input_log_fn):
	all_traces = []

	with open(input_log_fn, 'r') as input_log_obj:
		new_trace = []
		for line in input_log_obj:
			components = line.strip().split(' ')
			if 'http-traceroute' == components[0]:
				new_trace = list(filter(None, new_trace))
				all_traces.append(new_trace)

				new_trace = []
				my_ip = components[2]
				domain = components[-1]
				serv_ip = components[-2]
				new_trace.append(domain)
				new_trace.append(my_ip)
				new_trace.append(serv_ip)
			else:
				if components[2]:
					new_trace.append(components[2])

		all_traces.append(new_trace)
		all_traces = list(filter(None, all_traces))
		return all_traces

def get_complete_simple_traces(simple_traces):

	complete_traces = []
	for trace in simple_traces:
		domain = trace[0]
		source_ip = trace[1]
		serv_ip = trace[2]
		
		if serv_ip in trace[3:]:
			# In some cases there is an asterisk after the server IP
			if trace[-1] == '*':
				new_trace = trace[0:3]
				for ip in trace[3:]:
					if ip == serv_ip:
						new_trace.append(ip)
						break
					else:
						new_trace.append(ip)
				trace = new_trace
			complete_traces.append(trace)

	return complete_traces

def get_lri(trace):
	srv_ip = trace[-1]
	num_asterisks = 0
	for ip in trace[::-1]:
		if ip != srv_ip and ip != '*':
			if ip == '*':
				num_asterisks += 1
			return ip, num_asterisks

	return "LRI_NOT_FOUND", num_asterisks

def get_lris(simple_traces):
	result = {}
	relevant_traces = 0
	for trace in simple_traces:
		srv_ip = trace[-1]
		relevant_traces += 1
		result[srv_ip] = get_lri(trace)

	print("LRI Found for:", relevant_traces)
	return result

def get_ttl(ip, trace):
	for t in trace:
		if ip == t[0]:
			return t[1]

	return "NOT_FOUND"

def get_merged_trace(mda_trace, max_merge, print_dict=False):
    ttl_dict = OrderedDict()
    max_merge = int(max_merge)

    if max_merge == 0:
        skip_asterisk = False
    else:
        skip_asterisk = True

    done_once = False
    asterisk_removed = 0
    for ip, ttl in reversed(mda_trace):
        if skip_asterisk:
            if ip != '*':
                if done_once:
                    skip_asterisk = False
                if ttl in ttl_dict:
                    ttl_dict[ttl].append(ip)
                else:
                    ttl_dict[ttl] = [ip]
            else:
                done_once = True
                asterisk_removed += 1
                if asterisk_removed >= max_merge:
                    skip_asterisk = False
        else:
            if ttl in ttl_dict:
                ttl_dict[ttl].append(ip)
            else:
                ttl_dict[ttl] = [ip]

    new_trace = []
    reversed_dict = OrderedDict(sorted(ttl_dict.items()))
    if print_dict:
        print(mda_trace)
        print()
        print(ttl_dict)
        print()
        print(reversed_dict)

    current_ttl = 1
    for ttl, ips in reversed_dict.items():
        for ip in ips:
            new_trace.append([ip, current_ttl])
        current_ttl += 1

    merged_hops = len(mda_trace) - len(new_trace)

    return new_trace, merged_hops


def compare_step_ips(step, results_dict, traces, mda_traces):
	not_found_in_mda = []
	results = []

	step_str = "n"+str(step)
	too_short_traces = 0 
	sterik_servers = []

	dist_list = list()

	for simple_trace in traces:
		domain = simple_trace[0]
		# remove domain, source IP and srv IP from start of the list
		simple_trace = simple_trace[3:]
		dest_ip = simple_trace[-1]
	
		# print("On", domain, dest_ip, step_str)
		try:
			n_1_ip = simple_trace[step-1] # IP to check (checking for n-1 hop for now)
		
			if "*" in n_1_ip:
				sterik_servers.append(dest_ip)
				results_dict[domain][step_str+'_ip'] = "*"
				continue

			results_dict[domain][step_str+'_ip'] = n_1_ip

		except IndexError as e:
			#print("TCP trace is too short!",domain,dest_ip,n_1_ip)
			results_dict[domain][step_str+'_ip'] = "TRACE_TOO_SHORT"
			too_short_traces += 1
			continue
			

		distances = []
		n = 0
		print_trace = False

		# print("Number of complete MDA traces:", len(mda_traces[domain]))
		for src_ip, mda_trace in mda_traces[domain].items():
			# TTL of server
			srv_ttl = get_ttl(dest_ip, mda_trace)
			if srv_ttl == "NOT_FOUND":
				continue

			# TTL of test IP
			test_node_ttl = get_ttl(n_1_ip, mda_trace)

			if test_node_ttl == "NOT_FOUND":
				continue

			distance = abs(int(srv_ttl) - int(test_node_ttl))
			n += 1
			distances.append(distance)


		# inconclusive if last resp IP wasn't found in any good MDA traces

		if len(distances) == 0:
			results_dict[domain][step_str+"_distance"] = "NOT_FOUND"
			not_found_in_mda.append([dest_ip, n_1_ip, 0])
		else:
			avg_distance = float(sum(distances))/float(len(distances))
			min_distance = min(distances)
			max_distance = max(distances)
			results_dict[domain][step_str+"_distance"] = min_distance
			if '4' in step_str and min_distance == 0:
				print(str(domain))


			#print("Checked IP:",n_1_ip)
			#print("Found in MDA traces:",len(distances))
			#print(f"Avg dist:{avg_distance}\tMin dist:{min_distance}\tMax dist:{max_distance}\n\n")

			dist_list.append(min_distance)
				#dist_list.append(int(avg_distance))


	print(f"\nN{step} Analysis")
	print("Total Analyzed:", len(dist_list) + len(not_found_in_mda) + len(sterik_servers) + too_short_traces)
	print("Found:", len(dist_list))
	print("Not Found:", len(not_found_in_mda))
	print("Sterik:",len(sterik_servers))
	print("TCP Trace Too Short:", too_short_traces)

	return dist_list, sterik_servers, not_found_in_mda

def merged_analysis(simple_traces, mda_traces, results):
	merged_mda_traces = {}
	not_found_in_mda = []
	lri_not_found = []
	found_in_mda = []
	dist_list = []
	total_checked = []
	for simple_trace in simple_traces:
		domain = simple_trace[0]
		simple_trace = simple_trace[3:]
		dest_ip = simple_trace[-1]

		if results[domain]['n-1_ip'] != '*':
			continue

		lri, max_merge = get_lri(simple_trace)
		results[domain]['backtracked_ip'] = lri

		if lri == "LRI_NOT_FOUND":
			lri_not_found.append(dest_ip)
			continue

		total_checked.append(dest_ip)

		distances = []
		for src_ip, mda_trace in mda_traces[domain].items():
			merged_mda_trace, merged_hops = get_merged_trace(mda_trace, 25)

			srv_ttl = get_ttl(dest_ip, merged_mda_trace)
			lri_ttl = get_ttl(lri, merged_mda_trace)

			if srv_ttl == "NOT_FOUND":
				assert "SERVER TTL NOT FOUND"

			if lri_ttl == "NOT_FOUND":
				continue

			distance = abs(int(srv_ttl) - int(lri_ttl))
			distances.append(distance)

		if len(distances) == 0:
			results[domain]['backtracked_distance'] = "NOT_FOUND"
			not_found_in_mda.append([dest_ip, lri, max_merge])
		else:
			min_distance = min(distances)
			results[domain]['backtracked_distance'] = min_distance
			dist_list.append(min_distance)

	print("\nMerged MDA Trace Analysis")
	print("Total Analyzed:", len(total_checked))
	print("LRI not found:", len(lri_not_found))
	print("Found in MDA:", len(dist_list))
	print("Not found in MDA:", len(not_found_in_mda))

	return dist_list, not_found_in_mda

def make_plots(n_1_list, lri_list, output_name, title):
	sns.set()
	ecdf = ECDF(lri_list)
	plt.plot(ecdf.x, ecdf.y, label="Backtracked distances ECDF")

	ecdf = ECDF(n_1_list)
	plt.plot(ecdf.x, ecdf.y, label="N-1 distances ECDF")

	max_dist = max(max(lri_list), max(n_1_list))

	plt.title(title)
	plt.legend()
	x_ticks = range(0, max_dist+2, 1)
	plt.xticks(x_ticks)

	plt.savefig(output_name)
	plt.clf()
	plt.close()

def print_counts(title, dist_list):
	counts = Counter(dist_list)
	print(title)
	print(counts)

def write_to_file(ip_list, filename, fileheader):
	with open(filename, 'w') as f:
		f.write(fileheader)
		print("Writing", filename, len(ip_list))
		for dest, lri, max_merge in ip_list:
			f.write(dest+'\t'+lri+'\t'+str(max_merge)+'\n')


def make_not_found_files(n_1_not_found, lri_not_found):
	directory = 'ip_not_found_files/'
	if not os.path.exists(directory):
		os.mkdir(directory)

	print("N-1:", len(n_1_not_found))
	print("LRI:", len(lri_not_found))

	write_to_file(n_1_not_found, directory+'n-1_ip_not_found.txt', "Server_IP\tTest_IP\tMax_Merge\n")
	write_to_file(lri_not_found, directory+'backtracked_ip_not_found.txt', "Server_IP\tTest_IP\tMax_Merge\n")

def make_output_file(file, filename):
	directory = 'distances/'
	if not os.path.exists(directory):
		os.mkdir(directory)

	with open(directory+filename, 'w') as f:
		for distance in file:
			f.write(str(distance) + '\n')

def main():
	with open("resolved.txt", 'r') as fo:
		input_doms_ips_list = [line.strip().split(' ') for line in fo]

	mda_traces = get_mda_traces('../../mda_traces_asterisk.json')

	print("Total unique servers:", len(mda_traces['23.81.71.154']))
	simple_traces = get_traces_http('http-results.txt')
	print("Total HTTP traces done:", len(simple_traces))
	simple_traces = get_complete_simple_traces(simple_traces)
	print("Complete HTTP traces:", len(simple_traces))

	# Set up results dictionary
	results = {}
	complete_mda_traces_dict = {}
	for trace in simple_traces:
		domain = trace[0]
		srv_ip = trace[-1]

		if srv_ip == '*':
			print(domain, srv_ip)
			exit()

		results[domain] = {}
		results[domain]['dest_ip'] = srv_ip
		results[domain]['mda_not_complete'] = "N/A"
		results[domain]['n-1_ip'] = "N/A"
		results[domain]['n-1_distance'] = "N/A"
		results[domain]['backtracked_ip'] = "N/A"
		results[domain]['backtracked_distance'] = "N/A"

		relevant_mda_traces = {}
		# Get complete MDA traces for each domain
		for src_ip, traces in mda_traces.items():
			try:
				relevant_mda_traces[src_ip] = traces[srv_ip]
			except KeyError as e:
				mda_trace_not_done[src_ip] = srv_ip

		complete_mda_traces = {}
		for src_ip, trace in relevant_mda_traces.items():
			all_ips = [t[0] for t in trace]
			if srv_ip in all_ips:
				complete_mda_traces[src_ip] = trace

		complete_mda_traces_dict[domain] = complete_mda_traces
		if len(complete_mda_traces):
			results[domain]['mda_not_complete'] = False
		else:
			results[domain]['mda_not_complete'] = True

	simple_traces_mda_complete = []
	for trace in simple_traces:
		domain = trace[0]
		if not results[domain]['mda_not_complete']:
			simple_traces_mda_complete.append(trace)

	print("HTTP traces with at least one reference trace:", len(simple_traces_mda_complete))
	# Do analysis for n-1 IPs
	n_1_dist_list, sterik_servers, n_1_not_found_in_mda = compare_step_ips(-1, 
													results, simple_traces_mda_complete, 
													complete_mda_traces_dict)


	lri_dist_list, lri_not_found_in_mda = merged_analysis(simple_traces_mda_complete, 
													complete_mda_traces_dict, results)

	with open('from_control_results.json', 'w') as f:
		json.dump(results, f, indent=4)

	all_distances = n_1_dist_list + lri_dist_list
	print(len(all_distances))

	make_output_file(all_distances, "http_from_control.txt")
	make_output_file(n_1_dist_list, "n-1_from_control.txt")
	make_output_file(lri_dist_list, "backtracked_from_control.txt")
	# print("Total distances found:", len(n_1_dist_list)+len(lri_dist_list))
	# print("Total not found in MDA:", len(n_1_not_found_in_mda)+len(lri_not_found_in_mda))

	# make_plots(n_1_dist_list, lri_dist_list, 
	# 	"plots/merged_analysis_plot_from_control.png", "HTTP Plots From Control")
	# make_not_found_files(n_1_not_found_in_mda, lri_not_found_in_mda)
	print_counts("N-1 Counts:", n_1_dist_list)
	print_counts("Backtracked Counts:", lri_dist_list)


if __name__ == '__main__':
	main()