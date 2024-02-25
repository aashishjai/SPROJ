import json
import sys
import glob

def get_traces(file):
	with open(file, 'r') as f:
		trace_dict = json.load(f)
	i = file.rfind('_')+1
	j = file.rfind('.')
	src_ip = file[i:j]

	return trace_dict, src_ip

def check_incomplete(trace_dict):
	incomplete = []
	complete = []
	for dest, ip_ttls in trace_dict.items():
		all_ips = [ip for ip, ttl in ip_ttls]
		if dest not in all_ips:
			incomplete.append(dest)
		else:
			complete.append(dest)

	return incomplete, complete


if __name__ == '__main__':

	files = glob.glob('*/ip_ttls_*.json')
	full_dict = {}
	for filename in files:
		trace_dict, src_ip = get_traces(filename)
		incomplete, complete = check_incomplete(trace_dict)

		full_dict[src_ip] = trace_dict

		print("For", src_ip)
		print("Total:", len(incomplete) + len(complete))
		print("Incomplete:", len(incomplete))
		print("Complete:", len(complete))

	with open("full_mda_traces.json", 'w') as f:
		json.dump(full_dict, f, indent=2)