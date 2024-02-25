import re
import os
import sys
from scapy.all import *
from sc_warts import WartsReader
import json

def get_last_nodes(dest, dummy_ip_where_packet_drop):
		last_nodes_dict={}
		query_id_ttl={}
		query_id=[]
		ttl=[]
		server_flow_array=[]
		server_flow_ttl=[]

		file_path="./traces/"+dest+".pcap"
		packets = rdpcap(file_path)
		past_packet=["",""]

		for packet in packets:
			past_packet[0]=past_packet[1]
			past_packet[1]=packet
			if (packet.proto) == 17:
				source_ip=packet.payload.src
				server_ip=packet.payload
				server_udp=server_ip.payload
				query_id.append(server_udp.payload.id)
				ttl.append(server_ip.ttl)

				'''
				So algorithm here is that we first pick any packet which is a UDP packet as its visible for proto==17 check
				Then we see if the packet was sent by server as its visible in below condition. if thats the case
				we pick server's flow identifier and add it in server flow array.
				'''
				if packet.payload.src in dest:
					 
					
					copy_query_id=list(query_id)
					copy_ttl=list(ttl)
					copy_query_id.reverse()
					copy_ttl.reverse()
					one_flow_set=set()
					 
					one_flow_set.add(server_ip.src)
					one_flow_set.add(server_ip.dst)
					 
					one_flow_set.add(server_udp.sport)
					one_flow_set.add(server_udp.dport)
					server_query_id=server_udp.payload.id

					if not one_flow_set in server_flow_array:
						server_flow_array.append(one_flow_set)
						server_flow_ttl.append([])

					'''
					Now as we have server flow, we see one packet behind that if it was a UDP packet, if it was then
					we check if it was the query to which server had responded. we do this by doing id check.
					Then for that particular flow, we keep a ttl field which is minimum
					'''			

					if server_udp.sport==53 and past_packet[0].payload.proto==17 and server_udp.payload.id==past_packet[0].payload.payload.payload.id:
						relevant_index=server_flow_array.index(one_flow_set)
						server_flow_ttl[relevant_index].append(past_packet[0].payload.ttl)
						server_flow_ttl[relevant_index]=[min(server_flow_ttl[relevant_index])]
						 
			if (packet.proto) == 1:
				if packet.payload.src in dummy_ip_where_packet_drop:
					source_ip=packet.payload.src

					one_flow_set=set()
					icmp_ip=packet.payload.payload.payload
					if icmp_ip.proto==1:
						continue
					one_flow_set.add(icmp_ip.src)
					one_flow_set.add(icmp_ip.dst)

					icmp_udp=packet.payload.payload.payload.payload
					one_flow_set.add(icmp_udp.sport)
					one_flow_set.add(icmp_udp.dport)

					if source_ip in last_nodes_dict:
						last_nodes_dict[source_ip].append(one_flow_set)
					else:
						last_nodes_dict[source_ip]=[one_flow_set]

		for second_last_ip in list(last_nodes_dict.keys()):
			all_flows=last_nodes_dict[second_last_ip]
			ttl_arr=[]
				 
			for one_flow_of_second_last_ip in all_flows:
				if one_flow_of_second_last_ip in server_flow_array:
					relevant_index=server_flow_array.index(one_flow_of_second_last_ip)
					ttl_arr.append(server_flow_ttl[relevant_index])

			dummy_arr=[]
			final_ttl_arr=sum(ttl_arr,dummy_arr) # concat
			if len(final_ttl_arr)>0:
				server_ttl_value=min(final_ttl_arr)
				return server_ttl_value

		return -1

if __name__ == '__main__':
	assert len(sys.argv) == 3

	input_file = sys.argv[1]
	output_dir = sys.argv[2]

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

		print "Got: %s from %s" % (dest, src)
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
	incomplete = []
	complete = []
	for dest_ip, ip_ttl in traces.items():
		print "For destination:", dest_ip
		tupls = sorted([(ip,ttl) for ip, ttl in ip_ttl.items()], key=lambda x: x[1])
		all_ttls = [t[1] for t in tupls]
		max_ttl = max(all_ttls)

		possible_packet_drop = [ip for ip, ttl in tupls if ttl == max_ttl]

		server_ttl = get_last_nodes(dest_ip, possible_packet_drop)
		if server_ttl == -1:
			incomplete.append(dest_ip)
		else:
			tupls.append((dest_ip, server_ttl))
			complete.append(dest_ip)

		final_trace_dict[dest_ip] = tupls



	print("Total probes sent:", c)
	print("Total traces:", len(final_trace_dict))
	print("Total complete:", len(complete))
	print("Total incomplete:", len(incomplete))
	print("Total skipped:", skipped)
	with open(output_dir+'/ip_ttls_'+src+'.json', 'w') as f:
		json.dump(final_trace_dict, f, indent=4)