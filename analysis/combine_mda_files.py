import json
import sys
import glob

def get_traces(file):
	with open(file, 'r') as f:
		trace_dict = json.load(f)
	i = file.rfind('_')+1
	j = file.rfind('.')
	src_ip = file[i:j]
	print(src_ip)
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

def add_asterisks(mda_traces):
	new_traces = {}
	for src_ip, traces in mda_traces.items():
		new_traces[src_ip] = {}
		for dest_ip, trace in traces.items():
			new_trace = []
			for ip, current_ttl in trace:
				if current_ttl == 1:
					new_trace.append([ip, current_ttl])
				else:
					while current_ttl - prior_ttl > 1:
						prior_ttl += 1
						new_trace.append(['*', prior_ttl])

					new_trace.append([ip, current_ttl])
				prior_ttl = current_ttl

			new_traces[src_ip][dest_ip] = new_trace

	return new_traces

if __name__ == '__main__':

	main_dir = sys.argv[1]
	files = glob.glob(main_dir+'/ip_ttls_*.json')
	full_dict = {}
	for filename in files:
		trace_dict, src_ip = get_traces(filename)
		incomplete, complete = check_incomplete(trace_dict)

		full_dict[src_ip] = trace_dict

		print("For", src_ip)
		print("Total:", len(incomplete) + len(complete))
		print("Incomplete:", len(incomplete))
		print("Complete:", len(complete))

	with_asterisks = add_asterisks(full_dict)

	with open(main_dir+"/full_mda_traces.json", 'w') as f:
		json.dump(with_asterisks, f, indent=2)
