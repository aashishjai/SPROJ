import os
import sys

MAIN_DIR = sys.argv[1]

with open(MAIN_DIR + '/resolved.txt', 'r') as f:
	resolved_dom_ips = [line.strip().split(' ') for line in f]

ip_to_dom = {}
for dom, ip in resolved_dom_ips:
	if ip in ip_to_dom:
		ip_to_dom[ip].append(dom)
	else:
		ip_to_dom[ip] = [dom]

CDN_RESULTS = './cdn_results/'
if not os.path.exists(CDN_RESULTS):
	os.mkdir(CDN_RESULTS)

with open(MAIN_DIR+'/resolved_ips.txt', 'w') as f:
	f.write('begin\n')
	for line in resolved_dom_ips:
		f.write(line[1]+'\n')
	f.write('end\n')

os.system('netcat whois.cymru.com 43 < '+MAIN_DIR+'/resolved_ips.txt | \
	sort -n > '+MAIN_DIR+'/ip_to_asn.txt')

with open(MAIN_DIR+'/ip_to_asn.txt', 'r') as f:
	f.readline()
	all_asn_lines = [line.strip().split('|') for line in f]

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
cdn_ips = set()
for line in all_asn_lines:
	asn_number = line[0].strip()
	ip_address = line[1].strip()
	asn_name = line[2].strip().lower()

	if asn_number in ASN_TO_CDN:
		dom_cdn = ASN_TO_CDN[asn_number]
		doms = ip_to_dom[ip_address]
		cdn_ips.add(ip_address)
		for dom in doms: 
			dom_to_cdn[dom] = dom_cdn

print(len(dom_to_cdn))
print(len(cdn_ips))

print(MAIN_DIR+'/cdn_domains_asn.txt')
with open(CDN_RESULTS+'/cdn_domains_asn.txt', 'w') as f:
	for dom, cdn in dom_to_cdn.items():
		f.write(dom + '\n')

with open(CDN_RESULTS+'/cdn_ips.txt', 'w') as f:
	for ip in cdn_ips:
		f.write(ip + '\n')