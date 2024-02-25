import os
import sys
import json
import socket


def get_key_by_val(val, dic):
	val_doms = []
	for dom, ip in dic.items():
		if ip == val:
			val_doms.append(dom)
	return val_doms


def find_mutliple_ips(components):
	ips = []
	for comp in components:
		try:
			# check if IP is valid
			socket.inet_pton(socket.AF_INET, comp)
			ips.append(comp)
		except socket.error:
			continue
	ips = list(set(ips))
	return ips


duplicate_packet_domains = []


def get_traces_http(input_log_fn, traceroute_name):
	all_traces = []

	no_trace = []
	packet_drop = []
	rst = []

	with open(input_log_fn, 'r') as input_log_obj:
		new_trace = []
		for line in input_log_obj:
			components = line.strip().split(' ')
			if traceroute_name == components[0]:
				domain = components[-1]
				new_trace = list(filter(None, new_trace))
				all_traces.append(new_trace)
				# The case where the traceroute did not even start
				if len(new_trace) == 3:
					no_trace.append(serv_ip)
				# First trace would be empty
				elif (len(new_trace)):
					# Case of packet drop we do not reach server
					if new_trace[-1] != serv_ip:
						packet_drop.append(serv_ip)

				new_trace = []
				my_ip = components[2]
				serv_ip = components[-2]
				new_trace.append(domain)
				new_trace.append(my_ip)
				new_trace.append(serv_ip)
			else:
				# if the length is longer than usual
				if len(components) > 7:

					# find IPs (packets) present in the line of the trace
					ips = find_mutliple_ips(components)

					# if multiple IPs found, spoofed IP one of them, and TCP RST packet is present
					if len(ips) > 1 and serv_ip in ips and "[TCP, RST]" in line:
						print(domain)

						# select the IP apart from server IP as the last responding IP
						for ip in ips:
							if ip != serv_ip:
								last_responding_ip = ip

						# append the last responding IP to the trace
						new_trace.append(last_responding_ip)
						duplicate_packet_domains.append(domain)
						rst.append(serv_ip)

						continue

				new_trace.append(components[2])
				if 'RST]' in components:
					rst.append(serv_ip)

		if new_trace[-1] != serv_ip:
			packet_drop.append(serv_ip)

		all_traces.append(new_trace)
		all_traces = list(filter(None, all_traces))
		return all_traces, set(no_trace), set(packet_drop), set(rst)


def get_traces_tcp(input_log_fn, traceroute_name):
	packet_drop_servers = []
	rst_servers = []
	syn_ack_servers = []

	all_traces = []
	with open(input_log_fn, 'r') as input_log_obj:
		new_trace = []
		for line in input_log_obj:
			components = line.strip().split(' ')
			if traceroute_name == components[0]:
				new_trace = list(filter(None, new_trace))
				all_traces.append(new_trace)
				if len(new_trace):
					if new_trace[-1] != serv_ip:
						packet_drop_servers.append(serv_ip)
				new_trace = []
				my_ip = components[2]
				serv_ip = components[-1]
				new_trace.append(my_ip)
				new_trace.append(serv_ip)
			else:
				new_trace.append(components[2])
				if '[SYN-ACK]' in components:
					syn_ack_servers.append(serv_ip)
				elif 'RST]' in components:
					rst_servers.append(serv_ip)

		all_traces.append(new_trace)
		all_traces = list(filter(None, all_traces))
		return all_traces, packet_drop_servers, rst_servers, syn_ack_servers


def get_filtered(dead_domains, input_doms):
	for dom in dead_domains:
		input_doms.pop(dom, None)
	return input_doms


def get_HTTP_LRR(all_traces, fil_dom_dict, RESULTS_DIR):
	pres_doms = []
	no_lri = []
	duplicates_ips = open(RESULTS_DIR+'/duplicate_packet_domains.txt', 'w')
	last_resp_ip = open(RESULTS_DIR+'/last_resp_ip.txt', 'w')
	for trace in all_traces:
		domain = trace[0]
		serv_ip = trace[2]

		if serv_ip in fil_dom_dict.values():
			rel_doms = get_key_by_val(serv_ip, fil_dom_dict)
			for dom in rel_doms:
				if dom not in pres_doms:
					pres_doms.append(dom)
					fil_trace = trace[3:]

					num_asterisks = 0
					# If Server IP is in file trace, pick up IP right before the server IP
					if len(fil_trace):
						# If Server IP is in file trace, pick up IP right before the server IP that isn't an '*'
						if serv_ip == fil_trace[-1]:
							if len(fil_trace) >= 2:
								for ip in reversed(fil_trace[:-1]):
									if ip != '*':
										last_responding_ip = ip
										break
									else:
										num_asterisks += 1
							else:
								last_responding_ip = None
						# Else pick up the last IP in the trace that isn't an '*'
						else:
							for ip in reversed(fil_trace):
								if ip != '*':
									last_responding_ip = ip
									break
					else:
						last_responding_ip = None

					# save spoofed domains in a separate text file
					if str(last_responding_ip) != "None":
						if domain in duplicate_packet_domains:
							duplicates_ips.write(
								dom + '\t' + str(last_responding_ip) + '\t' + serv_ip + '\n')
						last_resp_ip.write(
							dom + '\t' + str(last_responding_ip) + '\t' + serv_ip + '\t' + str(num_asterisks) + '\n')

		else:
			pass
			# print("Server IP:", serv_ip)
			# print("Trace:", trace)
			# print("Trace[1]:", trace[1])
			# print(fil_dom_dict)
			# break
	not_pres = list(set(fil_dom_dict.keys()).difference(set(pres_doms)))
	no_lri = list(set(no_lri))

	inconc_count = 0
	with open(RESULTS_DIR+'inconclusive_parse.txt', 'w') as file_obj:
		file_obj.write("domain\treason_for_inconclusivity\n")
		for ech in not_pres:
			file_obj.write(ech + '\t' +
                            'Private IP\n'
                  )
			inconc_count += 1
		for ech in no_lri:
			file_obj.write(ech + '\t' +
                            'No Traceroute\n'
                  )
			inconc_count += 1

	print("Number of traces:", len(all_traces))
	print("Pres Doms Length:", len(pres_doms))
	print("inconclusive:", inconc_count)


def get_TCP_LRR(all_traces, fil_dom_dict, packet_drop_servers, rst_servers, syn_ack_servers, RESULTS_DIR):
	tcp_doms = []
	no_lri = []
	last_resp_ip = open(RESULTS_DIR+'/last_resp_ip.txt', 'w')
	packet_drop_doms = []
	rst_doms = []
	for trace in all_traces:
		serv_ip = trace[1]
		# On the TCP level we only want to check packet drop and RST cases
		if serv_ip in rst_servers or serv_ip in packet_drop_servers:
			if serv_ip in fil_dom_dict.values():
				rel_doms = get_key_by_val(serv_ip, fil_dom_dict)
				for dom in rel_doms:
					if dom not in tcp_doms:
						# To know which doms are from TCP-RST set and which ones are packet drop
						if serv_ip in rst_servers:
							rst_doms.append(dom)
						else:
							packet_drop_doms.append(dom)
						tcp_doms.append(dom)
						fil_trace = trace[2:]
						num_asterisks = 0
						if len(fil_trace):
							# If Server IP is in file trace, pick up IP right before the server IP that isn't an '*'
							if serv_ip == fil_trace[-1]:
								if len(fil_trace) >= 2:
									for ip in reversed(fil_trace[:-1]):
										if ip != '*':
											last_responding_ip = ip
											break
										else:
											num_asterisks += 1
								else:
									last_responding_ip = None
							# Else pick up the last IP in the trace that isn't an '*'
							else:
								for ip in reversed(fil_trace):
									if ip != '*':
										last_responding_ip = ip
										break
						else:
							last_responding_ip = None

						if last_responding_ip == None:
							no_lri.append(dom)
						if str(last_responding_ip) != "None":
							last_resp_ip.write(
								dom + '\t' + str(last_responding_ip) + '\t' + serv_ip + '\t' + str(num_asterisks) + '\n')

			else:
				pass
				# print("Server IP:", serv_ip)
				# print("Trace:", trace)
				# print("Trace[1]:", trace[1])
				# print(fil_dom_dict)
				# break

	with open(RESULTS_DIR+'rst_doms.txt', 'w') as f:
		for dom in rst_doms:
			f.write(dom + '\n')

	with open(RESULTS_DIR+'packet_drops.txt', 'w') as f:
		for dom in packet_drop_doms:
			f.write(dom + '\n')
	print("Packet Drop Doms:", len(packet_drop_doms))
	print("RST Doms:", len(rst_doms))

	no_lri = list(set(no_lri))

	print("Number of traces:", len(all_traces))
	print("TCP-Blocked Doms:", len(tcp_doms))
	print("No LRI:", len(no_lri))


if __name__ == '__main__':
	packet_type = sys.argv[1]
	INPUT_DIR = sys.argv[2]
	MAIN_DIR = sys.argv[3]
	RESULTS_DIR = MAIN_DIR + "/results_"+packet_type.lower()+'/'
	if not os.path.exists(RESULTS_DIR):
		os.mkdir(RESULTS_DIR)

	if packet_type == "TCP":
		tr_path = INPUT_DIR+"HTTP-TCP-Traceroute/TCP/nonhttp-results.txt"
	elif packet_type == "HTTP":
		tr_path = INPUT_DIR+"HTTP-TCP-Traceroute/HTTP/http-results.txt"
	else:
		print("Please select TCP or HTTP as an argument")

	with open(INPUT_DIR+"HTTP-TCP-Traceroute/resolved_tool_filtered.txt", 'r') as fo:
		input_doms_list = [line.strip().split(' ')[0] for line in fo]

	with open(INPUT_DIR+"HTTP-TCP-Traceroute/resolved_tool_filtered.txt", 'r') as fo:
		input_doms_ips_list = [line.strip().split(' ')[1] for line in fo]

	traceroute_name = packet_type.lower() + '-traceroute'

	input_doms = dict(zip(input_doms_list, input_doms_ips_list))
	ip_to_dom = dict(zip(input_doms_ips_list, input_doms_list))

	print(len(input_doms_list))
	fil_dom_dict = input_doms

	if packet_type == "TCP":
		all_traces, packet_drop_servers, rst_servers, syn_ack_servers = get_traces_tcp(
			tr_path, traceroute_name)
		get_TCP_LRR(all_traces, fil_dom_dict, packet_drop_servers,
		            rst_servers, syn_ack_servers, RESULTS_DIR)

		with open(RESULTS_DIR+"traceroute_blocktype_tcp.txt", 'w') as f:
			for serv_ip in packet_drop_servers:
				if serv_ip in ip_to_dom:
					f.write(serv_ip + ' ' + "TCP-PacketDrop\n")
			for serv_ip in rst_servers:
				if serv_ip in ip_to_dom:
					f.write(serv_ip + ' ' + "TCP-RST\n")

	elif packet_type == "HTTP":
		all_traces, no_trace, packet_drop, rst = get_traces_http(
			tr_path, traceroute_name)
		get_HTTP_LRR(all_traces, fil_dom_dict, RESULTS_DIR)

		with open(RESULTS_DIR+"traceroute_blocktype_http.txt", 'w') as f:
			for serv_ip in no_trace:
				if serv_ip in ip_to_dom:
					f.write(ip_to_dom[serv_ip] + ' ' + "HTTP-NoTrace\n")
			for serv_ip in packet_drop:
				if serv_ip in ip_to_dom:
					f.write(ip_to_dom[serv_ip] + ' ' + "HTTP-PacketDrop\n")
			for serv_ip in rst:
				if serv_ip in ip_to_dom:
					f.write(ip_to_dom[serv_ip] + ' ' + "HTTP-RST\n")
	else:
		print("Incorrect packet type. Exiting")
		exit()
