import seaborn as sns
import matplotlib.pyplot as plt

# Get input files
with open('MDA_TCP_OUTPUT_FIXED.txt', 'r') as f:
	all_lines = [line.strip() for line in f]

with open('resolved.txt', 'r') as f:
	dom_ip = [line.strip().split(' ') for line in f]
ip_to_dom = {t[1]:t[0] for t in dom_ip}

with open('../from_control_analysis/simple_tcp_tcp_control/results/mda_not_complete.csv') as f:
	f.readline()
	mda_not_complete_ips = [line.strip().split(',')[2] for line in f]

print("TOTAL INITIAL:", len(mda_not_complete_ips))

# Parse the input file
new_file = []
all_traces = []
problem_traces = []
trace_dict = {}
for line in all_lines:
	if 'tracelb' in line:
		prob_spot = line.find('tracelb')
		if prob_spot > 0:
			problem_traces.append(prior_trace)
			trace_line = line[:prob_spot]
			server_line = line[prob_spot:]
			if prior_trace not in trace_dict:
				trace_dict[prior_trace] = [trace_line]
			else:
				trace_dict[prior_trace].append(trace_line)

			prior_trace = server_line
			all_traces.append(server_line)

			new_file.append(trace_line)
			new_file.append(server_line)
		else:
			all_traces.append(line)
			prior_trace = line
			new_file.append(line)
	else:
		new_file.append(line)
		if prior_trace not in trace_dict:
			trace_dict[prior_trace] = [line]
		else:
			trace_dict[prior_trace].append(line)

print(len(all_traces))
# Get non-error servers
all_servers = set()
all_probe_server = []
for line in all_traces:
	server = line.split(' ')[4][:-1]
	if server not in mda_not_complete_ips:
		continue
	all_servers.add(server)
	num_probes = int(line.split(' ')[9])
	all_probe_server.append((server, num_probes))

# Get source-wise breakdown of NULL errors
total_null = set()
problem_probe_server = []
for trace in problem_traces:
	breakdown = trace.split(' ')
	src_ip = breakdown[2]
	dest_ip = breakdown[4][:-1]
	if dest_ip not in mda_not_complete_ips:
		continue
	total_null.add(dest_ip)
	
	num_probes = int(trace.split(' ')[9])
	problem_probe_server.append((server, num_probes))

# Overall categorization from traces
gap_limit_reached = set()
null_traces = set()
server_reached = set()
max_probed = set()
total = set()
for heading, trace in trace_dict.items():
	trace = ' '.join(trace).strip()
	heading_split = heading.split(' ')
	server = heading_split[4][:-1]
	if server not in mda_not_complete_ips:
		continue
	num_probes = int(heading_split[9])
	# if US_IP in heading:
	total.add(server)
	if (server in trace):
		server_reached.add(server)	
	elif '* -> * -> *' in trace[-11:]:
		gap_limit_reached.add(server)
	elif num_probes == 3000:
		max_probed.add(server)
	else:
		null_traces.add((server, trace, heading))
		# print(heading)
		# print(server, num_probes, heading)
		# print(trace)
		# print("====================")

unknown_err = set()
# Find discrepancy
for t in null_traces:
	server = t[0]
	trace = t[1]
	heading = t[2]
	if server not in total_null:
		unknown_err.add(server)

null_final = set()
for null in total_null:
	if (null in total) and (null not in max_probed):
		null_final.add(null)
		

print("Total MDA not complete:", len(total))
print("No Serv: Gap Limit Reached:", len(gap_limit_reached))
print("No Serv: Max Probes reached:", len(max_probed))
print("No Serv: Null Error:", len(null_final))
print("No Serv: Unknown:", len(unknown_err))

