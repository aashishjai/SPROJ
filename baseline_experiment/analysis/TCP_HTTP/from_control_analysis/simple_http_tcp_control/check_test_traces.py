import json
from baseline_merged_analysis_http import get_mda_traces, get_merged_trace, get_ttl, make_plots, print_counts, get_traces_http, get_complete_simple_traces, make_output_file
from geoip import geolite2
import pandas as pd

def get_not_found_file(filename):
	with open(filename, 'r') as f:
		f.readline()
		dest_target = [line.strip().split('\t') for line in f]

	return dest_target

def find_in_mda(input_list, mda_traces, test_cdn_servers, control_cdn_servers, result):
	cdn_dist_list = []
	non_cdn_dist_list = []
	not_found_ips = []

	for domain, dest_ip, target_ip, max_merge in input_list:
		cdn_dest = False
		if dest_ip in test_cdn_servers:
			cdn_dest = True

		distances = {}
		for ref_ip, trace in mda_traces.items():
			cdn_ref = False
			if ref_ip in control_cdn_servers:
				cdn_ref = True

			if cdn_dest != cdn_ref:
				continue

			if not cdn_dest:
				ref_16 = '.'.join(ref_ip.split('.')[0:2])
				dest_16 = '.'.join(dest_ip.split('.')[0:2])
				if dest_16 != ref_16:
					continue
			
			merged_mda_trace, merged_hops = get_merged_trace(trace, max_merge)

			target_ttl = get_ttl(target_ip, merged_mda_trace)
			if target_ttl != "NOT_FOUND":
				server_ttl = get_ttl(ref_ip, merged_mda_trace)

				distance = abs(int(server_ttl) - int(target_ttl))
				distances[ref_ip] = distance

		srv_country = "N/A"
		lri_country = "N/A"

		if len(distances) == 0:
			not_found_ips.append(dest_ip)
			min_distance = -1
		else:
			min_key = min(distances, key=distances.get)
			# Get server location
			srv_country = "ERR"
			srv_rec = geolite2.lookup(dest_ip)
			if not(srv_rec == None) and not(srv_rec.country == None):
				srv_country = srv_rec.country
			
			# Get LRI location
			lri_country = "ERR"
			lri_rec = geolite2.lookup(target_ip)
			if not(lri_rec == None) and not(lri_rec.country == None):
				lri_country = lri_rec.country


			min_distance = distances[min_key]
			if cdn_dest:
				cdn_dist_list.append(min_distance)
			else:
				non_cdn_dist_list.append(min_distance)

		result[domain] = [
			dest_ip,
			srv_country,
			target_ip,
			lri_country,
			cdn_dest,
			min_distance
		]


	print("Total:", len(input_list))
	print("CDN IPs Found in MDA:", len(cdn_dist_list))
	print("Non-CDN IPs Found in MDA:", len(non_cdn_dist_list))
	print("Total IPs Found in MDA:", len(non_cdn_dist_list)+ len(cdn_dist_list))
	print("IPs not found in MDA:", len(not_found_ips))

	return cdn_dist_list, non_cdn_dist_list

def get_complete_mda_traces(mda_traces):
	complete_mda_traces = {}
	for dest_ip, trace in mda_traces.items():
		ips = [t[0] for t in trace]
		if dest_ip in ips:
			complete_mda_traces[dest_ip] = trace
	
	return complete_mda_traces

def get_lri(trace):
	srv_ip = trace[-1]
	num_asterisks = 0
	for ip in trace[::-1]:
		if ip != srv_ip:
			if ip == '*':
				num_asterisks += 1
				continue			
			return ip, num_asterisks

	return "LRI_NOT_FOUND", num_asterisks

def get_lri_max_merge(traces):
	n_1_trios = []
	backtracked_trios = []
	too_short = []
	not_found = []
	for trace in traces:
		domain = trace[0]
		# remove domain, source IP and srv IP from start of the list
		trace = trace[3:]
		dest_ip = trace[-1]
	
		# print("On", domain, dest_ip, step_str)
		try:
			lri = trace[-2] # IP to check (checking for n-1 hop for now)
			if "*" in lri:
				lri, max_merge = get_lri(trace)
				if lri != "LRI_NOT_FOUND":
					backtracked_trios.append([domain, dest_ip, lri, max_merge])
				else:
					not_found.append(domain)
			else:
				n_1_trios.append([domain, dest_ip, lri, 0])

		except IndexError as e:
			#print("TCP trace is too short!",domain,dest_ip,n_1_ip)
			too_short.append(domain)						

	print("Trace too short:", len(too_short))
	print("LRI Not Found:", len(not_found))
	return n_1_trios, backtracked_trios

def main():
	simple_traces = get_traces_http('http-results.txt')
	print("Total TCP traces done:", len(simple_traces))
	simple_traces = get_complete_simple_traces(simple_traces)
	print("Complete TCP traces:", len(simple_traces))

	print(len(simple_traces))
	n_1_trios, backtracked_trios = get_lri_max_merge(simple_traces)
	print("N-1:", len(n_1_trios))
	print("Backtracked:", len(backtracked_trios))

	# Get CDN servers for correct comparison
	with open('test_set_cdn_domains.txt', 'r') as f:
		test_cdn_domains = [line.strip() for line in f]
	with open('control_set_cdn_domains.txt', 'r') as f:
		control_cdn_domains = [line.strip() for line in f]

	with open('resolved.txt', 'r') as f:
		test_dom_ip = [line.strip().split(' ') for line in f]
	test_dom_to_ip = {t[0]:t[1] for t in test_dom_ip}
	with open('control_set.txt', 'r') as f:
		control_dom_ip = [line.strip().split(' ') for line in f]
	control_dom_to_ip = {t[0]:t[1] for t in control_dom_ip}

	test_cdn_servers = [test_dom_to_ip[dom] for dom in test_cdn_domains]
	control_cdn_servers = [control_dom_to_ip[dom] for dom in control_cdn_domains]

	print()
	mda_traces = get_mda_traces('../../PK_results/reference_traces_asterisk.json')
	print("Total MDA traces:", len(mda_traces))
	complete_mda_traces = get_complete_mda_traces(mda_traces)
	print("Complete MDA traces:", len(complete_mda_traces))

	result = {}

	print("N-1 Results")
	n_1_cdn_dist_list, n_1_non_cdn_dist_list = find_in_mda(n_1_trios, complete_mda_traces, 
								test_cdn_servers, control_cdn_servers, result)
	print()
	print("Backtracked Merged Results")
	backtracked_cdn_dist_list, backtracked_non_cdn_dist_list = find_in_mda(backtracked_trios, complete_mda_traces, 
								test_cdn_servers, control_cdn_servers, result)

	columns = [
	'domain',
	'server_ip',
	'server_country',
	'last_responding_ip',
	'last_responding_country',
	'cdn',
	'distance'
	]

	df = pd.DataFrame.from_dict(result, orient='index').reset_index()
	df.columns = columns

	df.to_csv('distances.csv', index=False)

	with open('from_test_results.json', 'w') as f:
		json.dump(result, f, indent=4)

	total = len(n_1_cdn_dist_list) + len(n_1_non_cdn_dist_list)
	total += len(backtracked_cdn_dist_list) + len(backtracked_non_cdn_dist_list)

	print()
	print("Total Not Found from control:", len(n_1_trios)+len(backtracked_trios))
	print("Total Coverage from test:", total)

	all_cdn = n_1_cdn_dist_list + backtracked_cdn_dist_list
	all_non_cdn = n_1_non_cdn_dist_list + backtracked_non_cdn_dist_list


	make_output_file(all_cdn, "http_from_test_cdn.txt")
	make_output_file(all_non_cdn, "http_from_test_non_cdn.txt")
	make_output_file(n_1_cdn_dist_list, "n-1_from_test_cdn.txt")
	make_output_file(n_1_non_cdn_dist_list, "n-1_from_test_non_cdn.txt")
	make_output_file(backtracked_cdn_dist_list, "backtracked_from_test_non_cdn.txt")
	make_output_file(backtracked_non_cdn_dist_list, "backtracked_from_test_cdn.txt")

	# make_plots(n_1_cdn_dist_list, backtracked_cdn_dist_list, 
	# 	"plots/cdn_merged_analysis_plot_from_test.png", "HTTP - CDN Plots From Test")
	# make_plots(n_1_non_cdn_dist_list, backtracked_non_cdn_dist_list, 
	# 	"plots/non_cdn_merged_analysis_plot_from_test.png", "HTTP - Non-CDN Plots From Test")

	print_counts("N-1 CDN Counts:", n_1_cdn_dist_list)
	print_counts("Backtracked CDN Counts:", backtracked_cdn_dist_list)
	print()
	print_counts("N-1 Non-CDN Counts:", n_1_non_cdn_dist_list)
	print_counts("Backtracked Non-CDN Counts:", backtracked_non_cdn_dist_list)



if __name__ == '__main__':
	main()