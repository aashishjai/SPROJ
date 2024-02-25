#!/usr/bin/env python
#
# Program:      $Id: $ 
# Author:       Robert Beverly <rbeverly@nps.edu>
# Description:  Example use of sc_warts library.  
#               Counts the number of different destinations probed
#
import sys
from sc_warts import WartsReader
import json

def get_json_dump(obj, output_dir):
	dict_obj = {}
	dict_obj['flags'] = wartsObj.flags
	dict_obj['nodes'] = wartsObj.nodes
	dict_obj['links'] = wartsObj.links

	with open(output_dir+'sample_obj.json', 'w') as f:
		json.dump(dict_obj, f, indent=2)


if __name__ == "__main__":
	assert len(sys.argv) == 3

	input_file = sys.argv[1]
	output_dir = sys.argv[2]

	w = WartsReader(input_file, verbose=False)
	dsts = set()
	c = 1
	traces = {}
	skipped = 0
	while True:
		# print "===================="
		# print "Traceroute number:", c
		(flags, wartsObj) = w.next()
		if flags == False: break
		c += 1

		# print "Flags:"
		# print wartsObj.flags
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
		# print "\n"
		# print "Nodes:"
		# for node in wartsObj.nodes:
		# 	print node
		# print "\n"
		# print "Links:"
		# print "Each link has 2 keys, probe_sets and link"

		traces[dest] = {}
		traces[dest][first_ip] = 1
		for i, link in enumerate(wartsObj.links):
			# print "Link", i+1
			# print "link:", link['link']
			# print "Probe Sets:"
			for probe_set in link['probe_sets']:
				# print "\nPrinting probes in set:"
				for probe in probe_set:
					ttl = probe['probe']['ttl']
					for reply in probe['replies']:
						ip = reply['from']
						if ip == first_ip:
							continue
						traces[dest][ip] = ttl
					# print probe
			# print "\n"
		# print "===================="

	final_trace_dict = {}
	for dest_ip, ip_ttl in traces.items():
		print "For destination:", dest_ip
		tupls = sorted([(ip,ttl) for ip, ttl in ip_ttl.items()], key=lambda x: x[1])
		final_trace_dict[dest_ip] = tupls

	print("Total probes sent:", c)
	print("Total traces:", len(final_trace_dict))
	print("Total skipped:", skipped)
	with open(output_dir+'/ip_ttls_'+src+'.json', 'w') as f:
		json.dump(final_trace_dict, f, indent=4)