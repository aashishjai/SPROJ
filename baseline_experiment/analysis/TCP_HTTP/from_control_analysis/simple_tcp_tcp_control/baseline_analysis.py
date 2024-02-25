from geoip import geolite2
import pandas as pd
import json 
from statsmodels.distributions.empirical_distribution import ECDF
import matplotlib.pyplot as plt
import numpy as np
import matplotlib

def get_mda_traces(file):
	with open(file, 'r') as f:
		full_dict = json.load(f)

	return full_dict

def get_ttl(ip, trace):
	for t in trace:
		if ip == t[0]:
			return t[1]

	return "NOT_FOUND"

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


def get_complete_traces(all_traces, ip_to_dom, cdn_domains):
	cdn_traces = list()
	normal_traces = list()

	for tr in all_traces:
		source_ip = tr[0]
		serv_ip = tr[1]
		
		# remove source IP and srv IP from start of the list
		trace = tr[0:0]
		trace.extend(tr[2:])

		# ignore the failed traces
		if trace[-1] != serv_ip:
			continue

		if ip_to_dom[serv_ip] in cdn_domains:
			cdn_traces.append(tr)
		else:
			normal_traces.append(tr)

	return normal_traces, cdn_traces

def compare_step_ips(step, results_dict, traces, mda_traces, ip_to_dom):
	inconc_trios = []
	results = []

	step_str = "n"+str(step)

	#trace_type = "normal"
	#step = -1
	too_short_traces = 0 
	sterik_traces = 0

	dist_list = list()

	for tr in traces:
		# remove source IP and srv IP from start of the list
		trace = tr[0:0]
		trace.extend(tr[2:])
		domain = ip_to_dom[trace[-1]]
		test_srv_ip = trace[-1]
	
		try:
			test_last_resp_ip = trace[step-1] # IP to check (checking for n-1 hop for now)
		
			if "*" in test_last_resp_ip:
				sterik_traces += 1
				results_dict[domain][step_str+'_ip'] = "*"
				continue

			# if last rep IP is source IP
			if test_last_resp_ip == tr[0]:
				results_dict[domain][step_str+'_ip'] = "TRACE_TOO_SHORT"
				continue
			results_dict[domain][step_str+'_ip'] = test_last_resp_ip

			# Get test ip location
			lri_country = "ERR"
			lri_rec = geolite2.lookup(test_last_resp_ip)
			if not(lri_rec == None) and not(lri_rec.country == None):
				lri_country = lri_rec.country

			results_dict[domain][step_str+"_location"] = lri_country
		
		except IndexError as e:
			#print("TCP trace is too short!",domain,test_srv_ip,test_last_resp_ip)
			results_dict[domain][step_str+'_ip'] = "TRACE_TOO_SHORT"
			too_short_traces += 1
			continue
			
		# print("On", domain, test_srv_ip, step_str)

		distances = []
		n = 0
		print_trace = False

		# print("Number of complete MDA traces:", len(complete_mda_traces))
		for src_ip, trace in mda_traces[domain].items():
			# TTL of server
			srv_ttl = get_ttl(test_srv_ip, trace)
			if srv_ttl == "NOT_FOUND":
				continue

			# TTL of test IP
			test_node_ttl = get_ttl(test_last_resp_ip, trace)

			if test_node_ttl == "NOT_FOUND":
				continue

			distance = abs(int(srv_ttl) - int(test_node_ttl))
			n += 1
			distances.append(distance)


		# inconclusive if last resp IP wasn't found in any good MDA traces

		if len(distances) == 0:
			results_dict[domain][step_str+"_distance"] = "NOT_FOUND"
			inconc_trios.append(domain)
		else:
			avg_distance = float(sum(distances))/float(len(distances))
			min_distance = min(distances)
			max_distance = max(distances)
			results_dict[domain][step_str+"_distance"] = min_distance
			if '4' in step_str and min_distance == 0:
				print(str(domain))


			#print("Checked IP:",test_last_resp_ip)
			#print("Found in MDA traces:",len(distances))
			#print(f"Avg dist:{avg_distance}\tMin dist:{min_distance}\tMax dist:{max_distance}\n\n")

			dist_list.append(min_distance)
				#dist_list.append(int(avg_distance))


	print(f"\nStep: N{step}")
	print("Found:", len(dist_list))
	print("Not Found:", len(inconc_trios))
	print("Sterik:",sterik_traces)
	print("TCP Trace Too Short:", too_short_traces)
	print("SUM:", len(dist_list) + len(inconc_trios) + sterik_traces + too_short_traces)

	return dist_list

def main():
	# Get the input files
	with open("resolved.txt", 'r') as fo:
		input_doms_list = [line.strip().split(' ')[0] for line in fo]
	with open("resolved.txt", 'r') as fo:
		input_doms_ips_list = [line.strip().split(' ')[1] for line in fo]
	with open('test_set_cdn_domains.txt', 'r') as f:
		cdn_check = [line.strip() for line in f]

	print("All input domains:", len(set(input_doms_ips_list)))
	ip_to_dom = dict(zip(input_doms_ips_list, input_doms_list))
	print("All unique servers:", len(set(input_doms_ips_list)))

	# Get all simple traces
	all_traces = get_traces_tcp("nonhttp-results.txt")
	print("All Simple traces:", len(all_traces))


	# Filter traces
	normal_traces, cdn_traces = get_complete_traces(all_traces, ip_to_dom, [])
	print("Simple Complete traces:", len(normal_traces) + len(cdn_traces))

	# Get reference traces
	all_mda_traces = get_mda_traces("../../full_mda_traces.json")

	# normal_traces = normal_traces[:10]
	traces = normal_traces

	complete_mda_traces_dict = {}
	relevant_mda_traces = {}
	mda_trace_not_done = {}

	results_dict = {}
	for trace in traces:
		domain = ip_to_dom[trace[-1]]
		srv_ip = trace[-1]

		# Set up initial dictionary
		results_dict[domain] = {}
		results_dict[domain]['dest_ip'] = srv_ip
		results_dict[domain]['dest_location'] = "N/A"
		results_dict[domain]['mda_not_done'] = "N/A"
		results_dict[domain]['mda_not_complete'] = "N/A"
		results_dict[domain]['cdn'] = str(domain in cdn_check)
		results_dict[domain]['n-1_ip'] = "N/A"
		results_dict[domain]['n-1_location'] = "N/A"
		results_dict[domain]['n-1_distance'] = "N/A"
		results_dict[domain]['n-2_ip'] = "N/A"
		results_dict[domain]['n-2_location'] = "N/A"
		results_dict[domain]['n-2_distance'] = "N/A"
		results_dict[domain]['n-3_ip'] = "N/A"
		results_dict[domain]['n-3_location'] = "N/A"
		results_dict[domain]['n-3_distance'] = "N/A"
		results_dict[domain]['n-4_ip'] = "N/A"
		results_dict[domain]['n-4_location'] = "N/A"
		results_dict[domain]['n-4_distance'] = "N/A"

		# Get complete MDA traces for each domain
		for src_ip, trace_dict in all_mda_traces.items():
			try:
				relevant_mda_traces[src_ip] = trace_dict[srv_ip]
			except KeyError as e:
				mda_trace_not_done[src_ip] = srv_ip


		if len(relevant_mda_traces):
			results_dict[domain]['mda_not_done'] = "FALSE"
		else:
			results_dict[domain]['mda_not_done'] = "TRUE"
			continue

		complete_mda_traces = {}
		for src_ip, trace in relevant_mda_traces.items():
			all_ips = [t[0] for t in trace]
			if srv_ip in all_ips:
				complete_mda_traces[src_ip] = trace

		complete_mda_traces_dict[domain] = complete_mda_traces
		if len(complete_mda_traces):
			results_dict[domain]['mda_not_complete'] = "FALSE"
		else:
			results_dict[domain]['mda_not_complete'] = "TRUE"
			continue

		srv_country = "ERR"
		srv_rec = geolite2.lookup(srv_ip)
		if not(srv_rec == None) and not(srv_rec.country == None):
			srv_country = srv_rec.country
		results_dict[domain]['dest_location'] = srv_country

	gs1 = plt.GridSpec(nrows=2, ncols=2, hspace=0.75, wspace=0.5)
	plt.suptitle('Control Analysis')

	for step in range(-1, -5, -1):
		print("At step:", step)
		path_differences = compare_step_ips(step, results_dict, normal_traces, complete_mda_traces_dict, ip_to_dom)
		print(f"Min: {min(path_differences)}, Max: {max(path_differences)}")
		import collections
		counter=collections.Counter(path_differences)
		print(counter)
		ecdf = ECDF(path_differences)

		plt.subplot(gs1[-step - 1])
		plt.plot(ecdf.x, ecdf.y)
		plt.title(f"{str(-step)} Hop(s) Away From Server")
		plt.xlabel("Minimum Path Difference")
		x_ticks = range(0, int(max(path_differences))+2, 1)
		y_ticks = np.arange(0, 1.25, 0.25)
		plt.xticks(x_ticks)
		plt.yticks(y_ticks)

	df = pd.DataFrame.from_dict(results_dict, orient='index')
	df.to_csv('results.csv')

	fig = matplotlib.pyplot.gcf()
	fig.set_size_inches(10, 7)
	fig.savefig('Baseline_Normal.png', dpi=150)


if __name__ == '__main__':
	main()