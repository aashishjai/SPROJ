import os
import json 
import pandas as pd 

# READ ALL ASTERISK FILES AND GET DEST IPS FROM THERE
def get_asterisk_ips(filename):
	with open(filename, 'r') as f:
		f.readline()
		dom_ips = [line.strip().split(',') for line in f]

	ips = [t[1] for t in dom_ips]
	ip_to_dom = {t[1]:t[0] for t in dom_ips}

	return ips, ip_to_dom

def get_mda_traces(file):
	with open(file, 'r') as f:
		full_dict = json.load(f)

	return full_dict

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

def get_lris(dest_ips, simple_traces):
	result = {}
	relevant_traces = 0
	for trace in simple_traces:
		srv_ip = trace[-1]

		if srv_ip in dest_ips:
			relevant_traces += 1
			for ip in trace[::-1]:
				if ip != srv_ip and ip != '*':
					result[srv_ip] = ip
					break

	return result

def get_ttl(ip, trace):
	for t in trace:
		if ip == t[0]:
			return t[1]

	return "NOT_FOUND"

def check_mda(lri_dict, mda_traces):
	result = {}
	for src_ip, traces in mda_traces.items():
		result[src_ip] = {}
		for dest_ip, lri in lri_dict.items():
			trace = traces[dest_ip]
			all_trace_ips = [t[0] for t in trace]
			if dest_ip not in all_trace_ips:
				continue
			if lri in all_trace_ips:
				srv_ttl = get_ttl(dest_ip, trace)
				# print("Dest:", dest_ip)
				# print("Server TTL:", srv_ttl)
				# print("LRI:", lri)
				lri_ttl = 9999999
				not_consistent = False
				for ref_ip, ttl in trace:
					if lri == ref_ip:
						lri_ttl = ttl
					# If we find an IP of ttl greater than LRI TTL that isn't server
					if ttl > lri_ttl and ttl != srv_ttl and ref_ip != '*':
						not_consistent = True

				if not_consistent:
					result[src_ip][dest_ip] = "MDA_LRI_NOT_CONSISTENT"
					# print("LRI TTL:", lri_ttl)
					print("Server IP:", dest_ip)
					print("Server TTL:", srv_ttl)
					print("Last Responding IP:", lri)
					print("LRI TTL:", lri_ttl)
					print(trace)
					print("=============")
				else:
					result[src_ip][dest_ip] = "MDA_LRI_CONSISTENT"
					# print("CONSISTENT:", lri_ttl)
				# print(trace)
			else:
				# LRI was not found
				result[src_ip][dest_ip] = "MDA_LRI_NOT_CONSISTENT"

			# print("===============")
	result_df = pd.DataFrame.from_dict(result).reset_index()
	groupby_cols = [col for col in result_df.columns if col != 'index']
	summary = {}
	for col in groupby_cols:
		grouped = result_df.groupby(col)['index'].count()
		summary[col] = grouped

	summary_df = pd.DataFrame.from_dict(summary)

	return summary_df

def main():	
	n_1_dest_ips, _ = get_asterisk_ips('asterisk_files/n-1_asterisk.csv')
	simple_traces = get_traces_tcp("nonhttp-results.txt")
	mda_traces = get_mda_traces('../../mda_traces_asterisk.json')
	print(len(n_1_dest_ips))
	lri_dict = get_lris(n_1_dest_ips, simple_traces)

	summary_df = check_mda(lri_dict, mda_traces)
	print(summary_df)
	summary_df.to_csv('asterisk_results/n-1_lri_in_mda_summary.csv')

if __name__ == '__main__':
	main()