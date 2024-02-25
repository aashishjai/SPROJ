import sys
import json

def get_mda_traces(file):
	with open(file, 'r') as f:
		full_dict = json.load(f)

	return full_dict

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

def main():
	mda_file = sys.argv[1]
	mda_traces = get_mda_traces(mda_file)
	asterisk_traces = add_asterisks(mda_traces)
	



if __name__ == '__main__':
	main()