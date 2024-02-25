import json
import sys

input_file = sys.argv[1]
output_file = sys.argv[2]
with open(input_file, 'r') as f:
	mda_traces = json.load(f)

new_traces = {}
for dest_ip, trace in mda_traces.items():
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

	new_traces[dest_ip] = new_trace

with open(output_file, 'w') as f:
	json.dump(new_traces, f, indent=4)