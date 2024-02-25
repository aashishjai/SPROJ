import sys

file_type = sys.argv[1]
with open(file_type+'_cdn_domains_cname.txt', 'r') as f:
	cdn_cname = set([line.strip() for line in f])
with open(file_type+'_cdn_domains_asn.txt', 'r') as f:
	cdn_asn = set([line.strip() for line in f])

print("CDN Domains (cname):", len(cdn_cname))
print("CDN Domains (asn):", len(cdn_asn))

total = cdn_cname.union(cdn_asn)
print("Total CDN:", len(total))

with open(file_type+"_cdn_domains.txt", 'w') as f:
	for dom in total:
		f.write(dom+'\n')