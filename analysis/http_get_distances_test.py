import sys
import os
from utils import get_mda_traces, get_merged_trace, get_ttl

def get_complete_mda_traces(all_trios, mda_traces, main_dir):
	complete_mda_traces = {}
	for src_ip, traces in mda_traces.items():
		if src_ip in main_dir:
			for dest_ip, trace in traces.items():
				all_ips = [t[0] for t in trace]
				if dest_ip in all_ips:
					complete_mda_traces[dest_ip] = trace

	return complete_mda_traces

if __name__ == "__main__":
	# Get packet type
	packet_type = sys.argv[1]
	MAIN_DIR = sys.argv[2]
	log_file = sys.argv[3]
	RESULTS_DIR = MAIN_DIR + "/results_"+packet_type.lower()+'/'
	if not os.path.exists(RESULTS_DIR):
		os.mkdir(RESULTS_DIR)

	MDA_INPUT_DIR = '_'.join(MAIN_DIR.split(os.sep)[0].split('_')[:-1])+'_output'

	# Get the trios
	with open(RESULTS_DIR+'from_test_input.txt', 'r') as f:
		all_trios=[line.strip().split('\t') for line in f]

	print("For", packet_type, "input size:", len(all_trios))

	# Get the MDA file
	mda_traces = get_mda_traces(log_file)
	with open('TCP_HTTP_data/'+MDA_INPUT_DIR+'/TCP-MDA/resolved.txt', 'r') as f:
		dom_ips = [line.strip().split(' ') for line in f]

	ip_to_dom = {t[1]:t[0] for t in dom_ips}

	# Get all relevant, complete traces
	relevant_traces_dict = get_complete_mda_traces(all_trios, mda_traces, MAIN_DIR)
	print(len(relevant_traces_dict))

	# Get the CDN domains
	with open('cdn_results/cdn_domains.txt', 'r') as f:
		cdn_domains = [line.strip() for line in f]

	with open('cdn_results/cdn_ips.txt', 'r') as f:
		cdn_ips = [line.strip() for line in f]

	# Carry out distance analysis
	results = {}
	min_dist_counts = {}

	print(all_trios[0])

	for domain, lri, dest_ip, max_merge in all_trios:
		distances = []
		test_cdn = domain in cdn_domains
		print(domain, lri, dest_ip, test_cdn)
		for ref_ip, trace in relevant_traces_dict.items():
			distance = -1
			all_ips = [t[0] for t in trace]

			ref_cdn = (ip_to_dom[ref_ip] in cdn_domains) or (ref_ip in cdn_ips)

			if test_cdn != ref_cdn:
				continue

			trace, merged_hops = get_merged_trace(trace, max_merge)

			if lri in all_ips:
				lri_ttl = get_ttl(lri, trace)
				if lri_ttl == "NOT_FOUND":
					print("Should not happen")
					exit()
				else:
					srv_ttl = get_ttl(ref_ip, trace)
					if srv_ttl != "NOT_FOUND":
						distance = abs(int(srv_ttl) - int(lri_ttl))
						distances.append((distance, merged_hops, ref_ip))

		if len(distances):
			min_distance = min(distances, key=lambda x: x[0])
			results[domain] = min_distance
			print(min_distance)
			if min_distance[0] in min_dist_counts:
				min_dist_counts[min_distance[0]] += 1
			else:
				min_dist_counts[min_distance[0]] = 1

	for min_dist, count in min_dist_counts.items():
		print(min_dist, count)

	print("LRI Found for:", len(results))
	print("LRI Not-Found for:", len(all_trios) - len(results))
	with open(RESULTS_DIR+"not_found.txt", 'w') as f:
		for domain, lri, dest_ip, max_merge in all_trios:
			if domain not in results:
				f.write(domain + '\t' + lri + '\t' + dest_ip + '\n')

	with open(RESULTS_DIR + '/from_test_results.tsv', 'w') as f:
		f.write("DOMAIN\tMIN_DISTANCE\tMERGED_HOPS\tREF_IP\n")
		for domain, min_distance in results.items():
			f.write(domain + '\t' +
			        str(min_distance[0]) + '\t' + str(min_distance[1])+'\t'+str(min_distance[2])+'\n')
