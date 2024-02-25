import glob
import json
from collections import OrderedDict

def get_simple_traces_dns(filenames, dom_to_ip):
    all_files = glob.glob(filenames)
    serv_traces = {}
    ip_to_dom = {}
    print("Total files:", len(all_files))
    for file in all_files:
        i = file.rfind('/')+1
        j = file.find('_dnstraceroute_')
        domain = file[i:j]

        dest_ip = dom_to_ip[domain]
        if dest_ip in serv_traces:
            continue

        ip_to_dom[dest_ip] = domain

        trace = []
        ttl = 1
        prev_ttl = 0
        with open(file, 'r') as f:
            for line in f:
                line = line.strip().split(' ')
                ip = line[1]
                ttl = line[0]
                for _ in range(int(prev_ttl)+1, int(ttl)):
                    trace.append('*')
                if ip not in trace:
                    trace.append(ip)
                    prev_ttl = ttl
                    if line[-1] == 'DNS':
                        prev_ttl = 0
                        break
                elif line[-1] == 'DNS':
                    prev_ttl = 0
                    new_trace = [
                        trace_ip for trace_ip in trace if trace_ip != ip]
                    trace = new_trace
                    trace.append(ip)
                    break

        serv_traces[dest_ip] = trace
    return serv_traces, ip_to_dom

def get_mda_traces(file):
    with open(file, 'r') as f:
        full_dict = json.load(f)

    return full_dict

def get_merged_trace(mda_trace, max_merge, print_dict=False):
    ttl_dict = OrderedDict()
    max_merge = int(max_merge)

    if max_merge == 0:
        skip_asterisk = False
    else:
        skip_asterisk = True

    done_once = False
    asterisk_removed = 0
    for ip, ttl in reversed(mda_trace):
        if skip_asterisk:
            if ip != '*':
                if done_once:
                    skip_asterisk = False
                if ttl in ttl_dict:
                    ttl_dict[ttl].append(ip)
                else:
                    ttl_dict[ttl] = [ip]
            else:
                done_once = True
                asterisk_removed += 1
                if asterisk_removed >= max_merge:
                    skip_asterisk = False
        else:
            if ttl in ttl_dict:
                ttl_dict[ttl].append(ip)
            else:
                ttl_dict[ttl] = [ip]

    new_trace = []
    reversed_dict = OrderedDict(sorted(ttl_dict.items()))
    if print_dict:
        print(mda_trace)
        print()
        print(ttl_dict)
        print()
        print(reversed_dict)

    current_ttl = 1
    for ttl, ips in reversed_dict.items():
        for ip in ips:
            new_trace.append([ip, current_ttl])
        current_ttl += 1

    merged_hops = len(mda_trace) - len(new_trace)

    return new_trace, merged_hops

def get_ttl(ip, trace):
    for t in trace:
        if ip == t[0]:
            return t[1]

    return "NOT_FOUND"
