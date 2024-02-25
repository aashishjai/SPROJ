from sc_warts import WartsReader
import glob
import os
import json

def read_warts(input_file, output_dir):
	w = WartsReader(input_file, verbose=False)
	dsts = set()
	c = 1
	traces = {}
	skipped = 0
	while True:
		(flags, wartsObj) = w.next()
		if flags == False: break
		c += 1

		dest = flags['dstaddr']
		src = flags['srcaddr']

		# print "Got: %s from %s" % (dest, src)
		first_ip = "NONE"
		for node in wartsObj.nodes:
			if 'addr' in node:
				first_ip = node['addr']
				break
		if first_ip == "NONE":
			print "SKIPPING %s" % dest
			skipped += 1
			continue

		traces[dest] = {}
		traces[dest][first_ip] = 1
		for i, link in enumerate(wartsObj.links):
			for probe_set in link['probe_sets']:
				for probe in probe_set:
					ttl = probe['probe']['ttl']
					for reply in probe['replies']:
						ip = reply['from']
						if ip == first_ip:
							continue
						traces[dest][ip] = ttl

	final_trace_dict = {}
	for dest_ip, ip_ttl in traces.items():
		# print "For destination:", dest_ip
		tupls = sorted([(ip,ttl) for ip, ttl in ip_ttl.items()], key=lambda x: x[1])
		final_trace_dict[dest_ip] = tupls

	print("Total probes sent:", c)
	print("Total traces:", len(final_trace_dict))
	print("Total skipped:", skipped)
	with open(output_dir+'/ip_ttls_'+src+'.json', 'w') as f:
		json.dump(final_trace_dict, f, indent=4)

		
if __name__ == '__main__':
	# Read all the DNS files and store them
	all_dns_mda = glob.glob('./DNS_data_of_all_VPs/*/DNS_pipeline_step_4/ip_ttls_*')
	dns_outputs = 'dns_outputs/'
	if not os.path.exists(dns_outputs):
		os.mkdir(dns_outputs)

	for mda_file in all_dns_mda:
		new_file_name = dns_outputs+mda_file.split(os.sep)[-1]
		os.system('cp '+ mda_file + ' ' + new_file_name)

	# Read all the TCP files and store them
	all_tcp_mda = glob.glob('./TCP_HTTP_data/*/TCP-MDA/MDA_TCP_OUTPUT.warts')
	tcp_http_outputs = 'tcp_http_outputs/'
	if not os.path.exists(tcp_http_outputs):
		os.mkdir(tcp_http_outputs)

	for mda_file in all_tcp_mda:
		print mda_file
		read_warts(mda_file, tcp_http_outputs)