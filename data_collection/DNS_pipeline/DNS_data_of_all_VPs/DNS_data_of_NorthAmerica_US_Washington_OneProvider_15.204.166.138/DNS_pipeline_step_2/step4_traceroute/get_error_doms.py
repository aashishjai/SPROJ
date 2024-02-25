import glob
import os


def check_traceroute(traceroute):
    all_responding_ips = [line[1] for line in traceroute]
    if len(set(all_responding_ips)) < len(all_responding_ips):
        dns_check = False
        for line in traceroute:
            if 'DNS' in line:
                dns_check = True
        if dns_check:
            return True
        else:
            return False
    else:
        return True


def get_domain_name(filename):
    i = filename.find('./') + len('./')
    j = filename.find('_dnstraceroute_')
    return filename[i:j]


# Get all the DNS files
all_dns_files = glob.glob('./*_dnstraceroute_.txt')

# Get the original input list to get the Nameserver
input_list = {}
with open('blocked_domains_with_ns.txt', 'r') as f:
    for line in f:
        split = line.strip().split()
        dom = split[0]
        ns = split[1]
        input_list[dom] = ns

count = 0
error_doms = []
for file in all_dns_files:
    with open(file, 'r') as f:
        traceroute = [line.strip().split(' ') for line in f]
        if not check_traceroute(traceroute):
            count += 1
            error_doms.append(get_domain_name(file))

# print(count)
# Make a new file to run with the version 2 of the traceroute script
with open('error_doms_with_ns.txt', 'w') as f:
    for dom in error_doms:
        ns = input_list[dom]
        f.write(dom + ' ' + ns + '\n')
