import sys
from utils import get_mda_traces, get_merged_trace, get_ttl

if __name__ == "__main__":
	# Get simple traces
	MAIN_DIR = sys.argv[1]
	with open(MAIN_DIR + '/last_responding_ips.tsv', 'r') as f:
		f.readline()
		dns_trios = [line.strip().split('\t') for line in f]
	
	print("Total Input:", len(dns_trios))
	# Get MDA traces
	mda_traces = get_mda_traces('dns_outputs/full_mda_traces.json')

	# Carry out distance analysis
	results = {}
	for domain, lri, dest_ip, max_merge in dns_trios:
		distances = []
		for src_ip, traces in mda_traces.items():
			# To make sure we do not check the same VP
			distance = -1
			if src_ip not in MAIN_DIR:
				if dest_ip in traces:
					mda_trace = traces[dest_ip]
					merged_hops = 0
					if int(max_merge) != 0:
						mda_trace, merged_hops = get_merged_trace(mda_trace, int(max_merge))

					lri_ttl = get_ttl(lri, mda_trace)
					dest_ttl = get_ttl(dest_ip, mda_trace)

					if dest_ttl != "NOT_FOUND" and lri_ttl != "NOT_FOUND":
						distance = abs(int(dest_ttl) - int(lri_ttl))
					
					if distance != -1:
						distances.append((distance, merged_hops))
		if len(distances):
			min_distance = min(distances, key=lambda x: x[0])
			results[domain] = min_distance


	print("Total results:", len(results))
	with open(MAIN_DIR + '/dns_lri_not_found.txt', 'w') as f:
		for domain, _, _, _ in dns_trios:
			if domain not in results:
				f.write(domain + '\n')
		
	with open(MAIN_DIR + '/dns_serverside_results.tsv', 'w') as f:
		f.write("DOMAIN\tMIN_DISTANCE\tMERGED_HOPS\n")
		for domain, min_distance in results.items():
			f.write(domain + '\t' + str(min_distance[0]) + '\t' + str(min_distance[1])+'\n')