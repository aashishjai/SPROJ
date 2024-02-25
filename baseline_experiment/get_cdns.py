import os
import sys

# Either "test_set" or "control_set"
file_type = sys.argv[1]

with open('input_sets/'+file_type+'.txt', 'r') as f:
	resolved_dom_ips = [line.strip().split(' ') for line in f]

ip_to_dom = {t[1]:t[0] for t in resolved_dom_ips}

CDN_RESULTS = 'cdn_results/'
if not os.path.exists(CDN_RESULTS):
	os.mkdir(CDN_RESULTS)

with open('input_sets/'+file_type+'_ips.txt', 'w') as f:
	f.write('begin\n')
	for line in resolved_dom_ips:
		f.write(line[1]+'\n')
	f.write('end\n')

os.system('netcat whois.cymru.com 43 < input_sets/'+file_type+'_ips.txt | \
	sort -n > cdn_results/'+file_type+'_ip_to_asn.txt')

with open('cdn_results/'+file_type+'_ip_to_asn.txt', 'r') as f:
	f.readline()
	all_asn_lines = [line.strip().split('|') for line in f]

CDN_LIST = [
	'cloudflare',
	'edgecast',
	'verizon',
	'akamai',
	'stackpath',
	'limelight',
	'fastly',
]

ASN_TO_CDN = {
	'13335':'cloudflare',
	'15133':'edgecase',
	'16625':'akamai',
	'20940':'akamai',
	'20446':'stackpath',
	'22822':'limelight',
	'54113':'fastly',
	'14618': 'amazon',
	'16509': 'amazon',
	'15169': 'google',
	'19527': 'google',
}


dom_to_cdn = {}
for line in all_asn_lines:
	asn_number = line[0].strip()
	ip_address = line[1].strip()
	asn_name = line[2].strip().lower()

	dom = ip_to_dom[ip_address]
	if asn_number in ASN_TO_CDN:
		dom_cdn = ASN_TO_CDN[asn_number]
		dom_to_cdn[dom] = dom_cdn

with open('cdn_results/'+file_type+'_cdn_domains_asn.txt', 'w') as f:
	for dom, cdn in dom_to_cdn.items():
		f.write(dom + '\n')