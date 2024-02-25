import sys
import os
from utils import get_mda_traces, get_merged_trace, get_ttl

if __name__ == "__main__":
	# Get packet type
	packet_type = sys.argv[1]
	MAIN_DIR = sys.argv[2]
	log_file = sys.argv[3]
	RESULTS_DIR = MAIN_DIR + "/results_"+packet_type.lower()+'/'
	if not os.path.exists(RESULTS_DIR):
		os.mkdir(RESULTS_DIR)

	# Get the trios
	with open(RESULTS_DIR+'last_resp_ip.txt', 'r') as f:
		all_trios=[line.strip().split('\t') for line in f]

	print("For", packet_type, "input size:", len(all_trios))
	# Get the MDA file
	mda_traces = get_mda_traces(log_file)

	# Carry out distance analysis
	results = {}
	min_dist_counts = {}
	for domain, lri, dest_ip, max_merge in all_trios:
		distances = []
		for src_ip, traces in mda_traces.items():
			# To make sure we do not check the same VP
			distance = -1
			if src_ip not in MAIN_DIR:
				if dest_ip in traces:
					mda_trace = traces[dest_ip]
					merged_hops = 0
					mda_trace, merged_hops = get_merged_trace(mda_trace, max_merge)

					lri_ttl = get_ttl(lri, mda_trace)
					dest_ttl = get_ttl(dest_ip, mda_trace)

					if dest_ttl != "NOT_FOUND" and lri_ttl != "NOT_FOUND":
						distance = abs(int(dest_ttl) - int(lri_ttl))

					if distance != -1:
						distances.append((distance, merged_hops))

		if len(distances):
			min_distance = min(distances, key=lambda x: x[0])
			results[domain] = min_distance
			if min_distance[0] in min_dist_counts:
				min_dist_counts[min_distance[0]] += 1
			else:
				min_dist_counts[min_distance[0]] = 1
	
	for min_dist, count in min_dist_counts.items():
		print(min_dist, count)

	print("LRI Found for:", len(results))
	print("LRI Not-Found for:", len(all_trios) - len(results))
	with open(RESULTS_DIR+"from_test_input.txt", 'w') as f:
		for domain, lri, dest_ip, max_merge in all_trios:
			if domain not in results:
				f.write(domain + '\t' + lri + '\t' + dest_ip + '\t' + str(max_merge) + '\n')

	with open(RESULTS_DIR + '/from_control_results.tsv', 'w') as f:
		f.write("DOMAIN\tMIN_DISTANCE\tMERGED_HOPS\n")
		for domain, min_distance in results.items():
			f.write(domain + '\t' +
			        str(min_distance[0]) + '\t' + str(min_distance[1])+'\n')
