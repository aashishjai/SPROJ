import json


def get_domains_dict(results):
	domains = []
	for domain, inner_dict in results.items():
		if isinstance(inner_dict['n-1_distance'], int) \
		or isinstance(inner_dict['backtracked_distance'], int):
			domains.append(domain)

	return set(domains)

def get_domains_list(results):
	domains = []
	for domain, inner_list in results.items():
		if inner_list[-1] != -1:
			domains.append(domain)

	return set(domains)


with open('from_control_results.json', 'r') as f:
	from_control = json.load(f)

with open('from_test_results.json', 'r') as f:\
	from_test = json.load(f)

control_domains = get_domains_dict(from_control)
test_domains = get_domains_list(from_test)

print(len(control_domains))
print(len(test_domains))
all_domains = test_domains.union(control_domains)

total = 1500
done = len(all_domains)

coverage = (float(done) / float(total)) * 100

print("HTTP: "+str(done)+"/"+str(total)+" = "+str(coverage)+'%')