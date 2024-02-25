import sys
from geoip import geolite2
import pandas as pd
import os
''' This file gets the labels at each stage of the analysis '''

def get_crawler_block_type(trios, http_block_file, no_resp_file,  crawler_results_file):
	with open(http_block_file, 'r') as f:
		http_blocked_doms = [line.strip().split(' ')[0] for line in f]
	
	with open(no_resp_file, 'r') as f:
		http_no_resp_doms = [line.strip() for line in f]

	# To further check for RST injection by looking at "Connection Reset" cases
	with open(crawler_results_file, 'r') as f:
		crawler_results = [line.strip().split('\t') for line in f]

	connection_reset_doms = []
	unblocked = []
	for t in crawler_results:
		if len(t) == 2:
			if 'connection reset' in t[1].lower():
				connection_reset_doms.append(t[0])
			elif 'surf safely' in t[1].lower():
				http_blocked_doms.append(t[0])
		else:
			if '200-nonblock' in t[2].lower():
				unblocked.append(t[0])

	candidates = [trio[0] for trio in trios]
	
	block_labels = {}
	http_rst = 0
	http_bp = 0
	http_pd = 0
	num_unblocked = 0

	for dom in candidates:
		if dom in connection_reset_doms:
			http_rst += 1
			block_labels[dom] = 'RST'
		elif dom in http_blocked_doms:
			http_bp += 1
			block_labels[dom] = 'Blockpage'
		elif dom in http_no_resp_doms:
			http_pd += 1
			block_labels[dom] = 'NoResponse'
		else:
			if dom in unblocked:
				num_unblocked += 1
			else:
				unblocked.append(dom)
				num_unblocked += 1
			# print(dom)
			# print("Block Type Error Should not happen")

	print("HTTP-RST:", http_rst)
	print("HTTP-BlockPage:", http_bp)
	print("HTTP-NoResponse:", http_pd)
	print("Unblocked:", num_unblocked)
	print("Total Block Labels:", len(block_labels))
	
	return block_labels, unblocked

def get_traceroute_block_type(trios, tcp_blocktype_file, http_blocktype_file, ip_to_dom):
	with open(tcp_blocktype_file, 'r') as f:
		tcp_block = [line.strip().split(' ') for line in f]
	tcp_dict = {t[0]: t[1] for t in tcp_block}

	with open(http_blocktype_file, 'r') as f:
		http_block = [line.strip().split(' ') for line in f]
	http_dict = {t[0]: t[1] for t in http_block}

	# block_types = {}
	# for trio in trios:
	# 	dom = trio[0]
	# 	ip = trio[2]
	# 	if ip in tcp_dict:
	# 		block_types[dom] = tcp_dict[ip]
	# 	elif dom in http_dict:
	# 		block_types[dom] = http_dict[dom]
	# 	else:
	# 		block_types[dom] = 'TracerouteComplete'

	return tcp_dict, http_dict


def get_geo_locations(candidates):

	geo_labels = {}

	for dom_ips in candidates:
		dom = dom_ips[0]
		lri = dom_ips[1]
		srv_ip = dom_ips[2]

		lri_country = "ERR"
		lri_rec = geolite2.lookup(lri)
		if not(lri_rec == None) and not(lri_rec.country == None):
			lri_country = lri_rec.country

		srv_country = "ERR"
		srv_rec = geolite2.lookup(srv_ip)
		if not(srv_rec == None) and not(srv_rec.country == None):
			srv_country = srv_rec.country

		geo_labels[dom] = (lri_country, srv_country)

	print("Total Geo Labels:", len(geo_labels))

	return geo_labels

def get_ttls_from_control(serverside_results_file):
	with open(serverside_results_file, 'r') as f:
		f.readline()
		tuples = [line.strip().split('\t') for line in f]
	
	ttls_from_control = {t[0]:t[1:] for t in tuples}

	print("Domains with LRI in Control:", len(ttls_from_control))

	return ttls_from_control


def get_ttls_from_test(good_traces_results_file):
	with open(good_traces_results_file, 'r') as f:
		f.readline()
		tuples = [line.strip().split('\t') for line in f]

	ttls_from_test = {t[0]: t[1:] for t in tuples}

	print("Domains with LRI in Good Traces:", len(ttls_from_test))

	return ttls_from_test

def get_block_code(candidates, block_code_file):

	relevant_lines = []
	with open(block_code_file, 'r') as f:
		for line in f:
			dom = line.strip().split('\t')[0]
			if dom in candidates:
				relevant_lines.append(line.strip().split('\t'))
		
	print("Status Codes:", len(relevant_lines))

	block_codes = {}
	for line in relevant_lines:
		if len(line) == 4:
			block_codes[line[0]] = line[2]
		else:
			block_codes[line[0]] = "N/A"
	
	return block_codes


def transform_final_label(x):
	if 'inconclusive' in x.lower():
		return 'Inconclusive'
	else:
		return x
		
if __name__ == "__main__":

	INPUT_DIR = sys.argv[1]
	OUTPUT_DIR = sys.argv[2]
	RESULTS_DIR = OUTPUT_DIR + 'final_results_2/'
	if not os.path.exists(RESULTS_DIR):
		os.mkdir(RESULTS_DIR)

	TEST_LOCATION = "N/A"
	if "PK" in INPUT_DIR:
		TEST_LOCATION = "PK"
	elif "US" in INPUT_DIR:
		TEST_LOCATION = "US"
	elif "Germany" in INPUT_DIR:
		TEST_LOCATION = "DE"
	else:
		print("THIS LOCATION MISSING")
		exit()

	DNS_THRESHOLD = 3

	TCP_CONTROL_THRESHOLD = 3
	HTTP_CONTROL_THRESHOLD = 3
	
	TCP_TEST_CDN_THRESHOLD = 1
	HTTP_TEST_CDN_THRESHOLD = 1

	TCP_TEST_NON_CDN_THRESHOLD = 1
	HTTP_TEST_NON_CDN_THRESHOLD = 1


	# Step 1 - Get all the Trio files (Dom + LRR + SRV) - Convert to Dict
	http_trio_file = OUTPUT_DIR+'tcp_http_results/results_http/last_resp_ip.txt'
	with open(http_trio_file, 'r') as f:
		http_trios = [line.strip().split('\t') for line in f]
	http_trios = {t[0]: (t[1], t[2]) for t in http_trios}


	tcp_trio_file = OUTPUT_DIR+'tcp_http_results/results_tcp/last_resp_ip.txt'
	with open(tcp_trio_file, 'r') as f:
		tcp_trios = [line.strip().split('\t') for line in f]
	tcp_trios = {t[0]: (t[1], t[2]) for t in tcp_trios if t[0]}

	# Step 2 - Get Results file for TCP and HTTP
	# Step 2a - Get Results for LRI in Control - TCP
	tcp_serverside_results_file = OUTPUT_DIR + \
		'tcp_http_results/results_tcp/from_control_results.tsv'
	tcp_ttls_from_control = get_ttls_from_control(tcp_serverside_results_file)

	# Step 2b - Get Results for LRI in Good Traces from test - TCP
	tcp_good_traces_results = OUTPUT_DIR + \
		'tcp_http_results/results_tcp/from_test_results.tsv'
	tcp_ttls_from_test = get_ttls_from_test(tcp_good_traces_results)
	# Step 2c - Get Results for LRI in Control - HTTP
	http_serverside_results_file = OUTPUT_DIR+'tcp_http_results/results_http/from_control_results.tsv'
	http_ttls_from_control = get_ttls_from_control(http_serverside_results_file)

	# Step 2d - Get Results for LRI in Good Traces from test - HTTP
	http_good_traces_results = OUTPUT_DIR + \
		'tcp_http_results/results_http/from_test_results.tsv'
	http_ttls_from_test = get_ttls_from_test(http_good_traces_results)


	# Step 3 - Combine Trios
	tcp_doms = list(tcp_ttls_from_control.keys()) + list(tcp_ttls_from_test.keys())
	http_doms = list(http_ttls_from_control.keys()) + list(http_ttls_from_test.keys())

	print(len(http_trios) + len(tcp_trios))

	all_trios = []
	for dom in tcp_trios:
		all_trios.append([dom, tcp_trios[dom][0], tcp_trios[dom][1]])

	print(len(all_trios))
	num_in_tcp = 0
	for dom, http_tuple in http_trios.items():
		if dom not in tcp_doms:
			all_trios.append([dom, http_tuple[0], http_tuple[1]])
		else:
			num_in_tcp += 1
	print("NUM IN TCP:", num_in_tcp)

	# Find out how many "no traceroute" domains were left out
	with open(OUTPUT_DIR+'tcp_http_results/results_http/not_found.txt') as f:
		http_not_found = [line.strip().split('\t')[0] for line in f]

	with open(OUTPUT_DIR+'tcp_http_results/results_tcp/not_found.txt') as f:
		tcp_not_found = [line.strip().split('\t')[0] for line in f]
	
	with open(OUTPUT_DIR+'tcp_http_results/results_http/inconclusive_parse.txt', 'r') as f:
		f.readline()
		http_no_traceroute = [line.strip().split('\t')[0] for line in f]
	
	candidates = [trio[0] for trio in all_trios]

	http_no_traceroute_filtered = [dom for dom in http_no_traceroute if dom not in candidates]
	total_results = len(http_ttls_from_control) + len(http_ttls_from_test) + len(tcp_ttls_from_control) + len(tcp_ttls_from_test)
	print("TCP Analyzed:", len(tcp_trios))
	print("TCP Results:", len(tcp_doms))
	print("TCP Inconclusive:", len(tcp_not_found))
	print("HTTP Input:", len(http_trios))
	print("HTTP Analyzed:", len(http_trios))
	# print("Num in tcp:", num_in_tcp)
	print("HTTP No Traceroute:", len(http_no_traceroute_filtered))
	print("Inconclusive:", len(http_not_found))

	print("HTTP Results:", len(http_doms))
	print("Total Results:", total_results)
	print("Full Input:", len(all_trios))

	tcp_rst_file = OUTPUT_DIR + 'tcp_http_results/results_tcp/rst_doms.txt'
	tcp_no_resp_file = OUTPUT_DIR + 'tcp_http_results/results_tcp/packet_drops.txt'

	http_block_file = INPUT_DIR+'http_blocked_doms.txt'
	no_resp_file = INPUT_DIR+'http_no_resp_doms.txt'
	http_rst_file = INPUT_DIR+'tcp_http_results/results_http/duplicate_packet_domains.txt'

	crawler_results_file = INPUT_DIR+'run_crawler_raw_resultsall.csv'

	# Get Block Types for TCP/HTTP from crawler
	crawler_blocking_types, unblocked_domains = get_crawler_block_type(all_trios, http_block_file, no_resp_file, crawler_results_file)

	tcp_blocktype_file = OUTPUT_DIR + \
		'tcp_http_results/results_tcp/traceroute_blocktype_tcp.txt'
	http_blocktype_file = OUTPUT_DIR + \
		'tcp_http_results/results_http/traceroute_blocktype_http.txt'

	ip_to_dom = {}
	for trio in all_trios:
		ip = trio[2]
		dom = trio[0]
		if ip not in ip_to_dom:
			ip_to_dom[ip] = [dom]
		else:
			ip_to_dom[ip].append(dom)


	# Get Block Types for TCP/HTTP from traceroutes
	traceroute_tcp_block_type, traceroute_http_block_type = get_traceroute_block_type(all_trios, tcp_blocktype_file, http_blocktype_file, ip_to_dom)


	# Get Block Codes for TCP/HTTP
	block_code_file = INPUT_DIR + 'run_crawler_raw_resultsall.csv'
	block_codes = get_block_code(candidates, block_code_file)
	
	# Get Geo Locations for TCP/HTTPf
	geo_locations = get_geo_locations(all_trios)

	# Get CDN domains
	with open('cdn_results/cdn_domains.txt', 'r') as f:
		cdn_domains = set([line.strip() for line in f])

	print("Number of cdn domains:", len(cdn_domains))
	dns_trios = []
	# Get DNS results
	DNS_DIR = OUTPUT_DIR+'dns_results/'
	dns_trio_file = 'last_responding_ips.tsv'
	dns_results_file = 'dns_serverside_results.tsv'

	dns_ttls = get_ttls_from_control(DNS_DIR+dns_results_file)
	with open(DNS_DIR+dns_trio_file, 'r') as f:
		f.readline()
		dns_trios = [line.strip().split('\t') for line in f]

	dns_locations = get_geo_locations(dns_trios)

	false_resp_doms = []
	try:
		# Get DNS Injection Results
		with open(DNS_DIR+'/false_resp_domains.txt', 'r') as f:
			false_resp_doms = [line.strip().split('\t')[0] for line in f]
	except FileNotFoundError:
		print("File not found error")

	print("Before:", len(all_trios))
	all_trios = [t for t in all_trios if t[0] not in unblocked_domains]
	print("After:", len(all_trios))

	# Make Dataframe
	big_dictionary = {}

	for dom in false_resp_doms:
		lri = "N/A"
		srv_ip = "N/A"
		block_level = "DNS"
		crawler_block_type = "DNS-FalseResponse"
		traceroute_block_type = "DNS-FalseResponse"
		block_code = "N/A"
		lri_country = "N/A"
		srv_ip_country = "N/A"
		lri_location_category = "N/A"
		lri_comparison = "N/A"
		lri_distance = "N/A"
		merged_hops = "N/A"
		min_diff = -1
		ref_ip = "N/A"
		cdn_str = "N/A"
		final_label = "DNS-False-Response"

		big_dictionary[dom] = [lri, srv_ip, 
					block_level, crawler_block_type, traceroute_block_type, block_code, 
					lri_country, srv_ip_country, lri_location_category, 
					lri_comparison, lri_distance, merged_hops,
					min_diff, ref_ip, cdn_str, final_label]



	for trio in dns_trios:
		dom = trio[0]
		lri = trio[1]
		srv_ip = trio[2]
		block_level = "DNS"
		crawler_block_type = "DNS-Unresolved"
		traceroute_block_type = "DNS-Unresolved"
		block_code = "N/A"

		lri_country = dns_locations[dom][0]
		srv_ip_country = dns_locations[dom][1]

		lri_location_category = "ELSEWHERE"
		if lri_country == TEST_LOCATION:
			lri_location_category = "IN_COUNTRY_OF_REQUEST"
		elif lri_country == "ERR":
			lri_location_category = "ERR"
		elif lri_country == srv_ip_country:
			lri_location_category = "SAME_AS_SERVER"

		lri_comparison = "FROM_CONTROL"

		if dom in dns_ttls:
			min_diff = dns_ttls[dom][0]
			merged_hops = dns_ttls[dom][1]

			if int(min_diff) <= DNS_THRESHOLD:
				lri_distance = "CLOSE_TO_SERVER"
			else: 
				lri_distance = "FAR_FROM_SERVER"
		else:
			continue

		if lri_distance == "CLOSE_TO_SERVER":
			final_label = "DNS-Serverside-Blocking"
		else:
			if lri_country == TEST_LOCATION:
				final_label = "DNS-Censorship"
			else:
				final_label = "DNS-Middlebox-Blocking-Other"
		ref_ip = "N/A"
		cdn_str = "N/A"

		big_dictionary[dom] = [lri, srv_ip, 
                        block_level, crawler_block_type, traceroute_block_type, block_code,
						lri_country, srv_ip_country, lri_location_category, 
						lri_comparison, lri_distance, merged_hops,
                        int(min_diff), ref_ip, cdn_str, final_label]

	tcp_from_control = 0
	http_from_control = 0
	tcp_from_test = 0
	http_from_test = 0
	none = 0
	for t in all_trios:
		dom = t[0]
		lri = t[1]
		srv_ip = t[2]


		crawler_block_type = crawler_blocking_types[dom]
		if dom in tcp_doms:
			block_level = "TCP"
			if srv_ip in traceroute_tcp_block_type:
				traceroute_block_type = traceroute_tcp_block_type[srv_ip]
			else:
				traceroute_block_type = "TCP-TracerouteComplete"
		else:
			if dom in traceroute_http_block_type:
				traceroute_block_type = traceroute_http_block_type[dom]
			else:
				traceroute_block_type = "HTTP-TracerouteComplete"
			block_level = "HTTP"

		block_code = block_codes[dom]
		lri_country = geo_locations[dom][0]
		srv_ip_country = geo_locations[dom][1]

		lri_location_category = "ELSEWHERE"
		if lri_country == "PK":
			lri_location_category = "IN_COUNTRY_OF_REQUEST"
		elif lri_country == "ERR":
			lri_location_category = "ERR"
		elif lri_country == srv_ip_country:
			lri_location_category = "SAME_AS_SERVER"

		lri_comparison = "LRI_NOT_FOUND_ANYWHERE"
		final_label = "Inconclusive"
		lri_distance = "N/A"
		merged_hops = "N/A"
		min_diff = -1
		cdn_str = "N/A"
		ref_ip = "N/A"

		if dom in cdn_domains:
			cdn_str = 'CDN_True'
		else:
			cdn_str = 'CDN_False'

	# SPLIT TEST INTO CDN AND NON-CDN
	# USE THRESHOLD OF 1 FOR NON-CDN
	# IF PK AND <= 1, SERVERSIDE BLOCKING
	# IF PK AND > 1, CENSORSHIP
	# IF NON-PK AND <= 1, SERVERSIDE
	# IF NON-PK AND > 1, INCONCLUSIVE

		if dom in tcp_ttls_from_control:
			lri_comparison = "FROM_CONTROL"
			min_diff = tcp_ttls_from_control[dom][0]
			merged_hops = tcp_ttls_from_control[dom][1]

			if int(min_diff) <= TCP_CONTROL_THRESHOLD:
				lri_distance = "CLOSE_TO_SERVER"
				if int(merged_hops) > TCP_CONTROL_THRESHOLD and traceroute_block_type == 'TCP-PacketDrop':
					final_label = "Inconclusive"
				else:
					final_label = "TCP-Serverside-Blocking"
			else: 
				lri_distance = "FAR_FROM_SERVER"
				if lri_country == TEST_LOCATION:
					final_label = "TCP-Censorship"
				else:
					final_label = "TCP-Middlebox-Blocking-Other"

			tcp_from_control += 1		
		elif dom in tcp_ttls_from_test:
			lri_comparison = "FROM_TEST"
			ttls = tcp_ttls_from_test[dom]
			min_diff = ttls[0]
			merged_hops = ttls[1]
			ref_ip = ttls[2]

			if cdn_str == 'CDN_True':
				if int(min_diff) <= TCP_TEST_CDN_THRESHOLD:
					lri_distance = "CLOSE_TO_SERVER"
					if int(merged_hops) > TCP_TEST_CDN_THRESHOLD and traceroute_block_type == 'TCP-PacketDrop':
						final_label = "Inconclusive"
					else:
						final_label = "TCP-Serverside-Blocking"
				else: 
					lri_distance = "FAR_FROM_SERVER"
					if lri_country == TEST_LOCATION:
						final_label = "TCP-Censorship"
					else:
						final_label = "TCP-Middlebox-Blocking-Other"
			else:
				if lri_country == TEST_LOCATION:
					if int(min_diff) <= TCP_TEST_NON_CDN_THRESHOLD:
						lri_distance = "CLOSE_TO_SERVER"
						final_label = "TCP-Serverside-Blocking"
					else:
						lri_distance = "FAR_FROM_SERVER"
						final_label = "TCP-Censorship"
				elif lri_country == "ERR":
					final_label = "Inconclusive"
				else:
					if int(min_diff) <= TCP_TEST_NON_CDN_THRESHOLD:
						lri_distance = "CLOSE_TO_SERVER"
						final_label = "TCP-Serverside-Blocking"
					else:
						final_label = "Inconclusive"
			tcp_from_test += 1		

		elif dom in http_ttls_from_control:
			lri_comparison = "FROM_CONTROL"
			min_diff = http_ttls_from_control[dom][0]
			merged_hops = http_ttls_from_control[dom][1]

			if int(min_diff) <= HTTP_CONTROL_THRESHOLD:
				lri_distance = "CLOSE_TO_SERVER"
				if int(merged_hops) > HTTP_CONTROL_THRESHOLD and traceroute_block_type == 'HTTP-PacketDrop':
					final_label = "Inconclusive"
				else:
					final_label = "HTTP-Serverside-Blocking"
			else: 
				lri_distance = "FAR_FROM_SERVER"
				if lri_country == TEST_LOCATION:
					final_label = "HTTP-Censorship"
				else:
					final_label = "HTTP-Middlebox-Blocking-Other"
			http_from_control += 1
		elif dom in http_ttls_from_test:
			lri_comparison = "FROM_TEST"
			ttls = http_ttls_from_test[dom]
			min_diff = ttls[0]
			merged_hops = ttls[1]
			ref_ip = ttls[2]

			if cdn_str == 'CDN_True':
				if int(min_diff) <= HTTP_TEST_CDN_THRESHOLD:
					lri_distance = "CLOSE_TO_SERVER"
					if int(merged_hops) > HTTP_TEST_CDN_THRESHOLD and traceroute_block_type == 'HTTP-PacketDrop':
						final_label = "Inconclusive"
					else:
						final_label = "HTTP-Serverside-Blocking"
				else:
					lri_distance = "FAR_FROM_SERVER"
					if lri_country == TEST_LOCATION:
						final_label = "HTTP-Censorship"
					else:
						final_label = "HTTP-Middlebox-Blocking-Other"
			else:
				if lri_country == TEST_LOCATION:
					if int(min_diff) <= HTTP_TEST_NON_CDN_THRESHOLD:
						lri_distance = "CLOSE_TO_SERVER"
						final_label = "HTTP-Serverside-Blocking"
					else:
						lri_distance = "FAR_FROM_SERVER"
						final_label = "HTTP-Censorship"
				elif lri_country == "ERR":
					final_label = "Inconclusive"
				else:
					if int(min_diff) <= HTTP_TEST_NON_CDN_THRESHOLD:
						lri_distance = "CLOSE_TO_SERVER"
						final_label = "HTTP-Serverside-Blocking"
					else:
						final_label = "Inconclusive"

			http_from_test += 1
		else:
			none += 1

		big_dictionary[dom] = [lri, srv_ip, 
							block_level, crawler_block_type, traceroute_block_type, block_code, 
							lri_country, srv_ip_country, lri_location_category, 
							lri_comparison, lri_distance, merged_hops,
							int(min_diff), ref_ip, cdn_str, final_label]


	columns = ['domain', 'last_responding_IP', 'server_ip', 
				'block_level', 'crawler_block_type', 'traceroute_block_type', 'block_status_code', 
				'lri_country', 'srv_country', 'lri_location_category', 
				'lri_comparison', 'lri_distance', 'merged_hops',
				'min_diff', 'ref_ip', 'cdn_str', 'final_label']

	relevant = ['domain', 'last_responding_IP', 'server_ip',
             'block_level', 'crawler_block_type', 'traceroute_block_type', 'block_status_code',
	             'lri_comparison', 'lri_distance', 'final_label']


	df = pd.DataFrame.from_dict(big_dictionary, orient='index').reset_index()
	df.columns = columns

	# inconclusive_non_cdn = df[df['final_label'] == 'Inconclusive-Non-CDN-Test']
	# inconclusive_non_cdn = inconclusive_non_cdn[['domain', 'last_responding_IP', 'lri_country', 'server_ip', 'srv_country', 'min_diff', 'ref_ip']]
	# inconclusive_non_cdn = inconclusive_non_cdn.sort_values(['lri_country', 'min_diff', 'srv_country', 'last_responding_IP', 'server_ip'])
	# inconclusive_non_cdn.to_csv(RESULTS_DIR+'inconclusive_non_cdn.tsv', sep='\t')
	# print("Inconclusive non CDN:", len(inconclusive_non_cdn))

	# 	print(df)
	label_file = 'final_labels.tsv'
	df.to_csv(RESULTS_DIR+label_file, index=False, sep='\t')

	
	# df['final_label_2'] = df['final_label'].apply(transform_final_label)
	grouped = df.groupby(['block_level','traceroute_block_type', 'final_label'])['domain'].count()
	print(grouped)

	grouped_file = 'grouped_numbers.tsv'    	

	grouped.to_csv(RESULTS_DIR+grouped_file, sep='\t')
