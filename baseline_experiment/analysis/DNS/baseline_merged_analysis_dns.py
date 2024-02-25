import os
import json
import glob
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.distributions.empirical_distribution import ECDF
from collections import Counter, OrderedDict


def get_mda_traces(file):
    with open(file, 'r') as f:
        full_dict = json.load(f)

    return full_dict


def get_simple_traces_dns(filenames, dom_to_ip):
    all_files = glob.glob(filenames)
    serv_traces = {}
    ip_to_dom = {}
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


def get_complete_simple_traces_dns(simple_traces, ip_to_dom):

    complete_traces = []
    for serv_ip, trace in simple_traces.items():
        # remove source IP and srv IP from start of the list
        if serv_ip in trace:
            complete_traces.append(trace)

    return complete_traces


def get_lri(trace):
    srv_ip = trace[-1]
    for ip in trace[::-1]:
        if ip != srv_ip and ip != '*':
            return ip

    return "LRI_NOT_FOUND"


def get_lris(simple_traces):
    result = {}
    relevant_traces = 0
    for trace in simple_traces:
        srv_ip = trace[-1]
        relevant_traces += 1
        result[srv_ip] = get_lri(trace)

    print("LRI Found for:", relevant_traces)
    return result


def get_ttl(ip, trace):
    for t in trace:
        if ip == t[0]:
            return t[1]

    return "NOT_FOUND"


def get_merged_trace(mda_trace, print_dict=False):

    ttl_dict = OrderedDict()

    add_asterisk = False
    done_once = False
    for ip, ttl in reversed(mda_trace):
        if not add_asterisk:
            if ip != '*':
                if done_once:
                    add_asterisk = True
                if ttl in ttl_dict:
                    ttl_dict[ttl].append(ip)
                else:
                    ttl_dict[ttl] = [ip]
            else:
                done_once = True
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

    return new_trace


def compare_step_ips(step, results_dict, traces, mda_traces, ip_to_dom):
    not_found_in_mda = []

    step_str = "n"+str(step)
    too_short_traces = 0
    sterik_servers = []

    bad_cases = []

    dist_list = list()

    for trace in traces:
        # remove source IP and srv IP from start of the list
        dest_ip = trace[-1]
        domain = ip_to_dom[dest_ip]

        # print("On", domain, dest_ip, step_str)
        try:
            # IP to check (checking for n-1 hop for now)
            n_1_ip = trace[step-1]

            if "*" in n_1_ip:
                sterik_servers.append(dest_ip)
                results_dict[domain][step_str+'_ip'] = "*"
                continue

            results_dict[domain][step_str+'_ip'] = n_1_ip

        except IndexError:
            #print("TCP trace is too short!",domain,dest_ip,n_1_ip)
            results_dict[domain][step_str+'_ip'] = "TRACE_TOO_SHORT"
            too_short_traces += 1
            continue

        distances = []
        n = 0
        print_trace = False

        # print("Number of complete MDA traces:", len(mda_traces[domain]))
        for src_ip, trace in mda_traces[domain].items():
            # TTL of server
            srv_ttl = get_ttl(dest_ip, trace)
            if srv_ttl == "NOT_FOUND":
                continue

            # TTL of test IP
            test_node_ttl = get_ttl(n_1_ip, trace)

            if test_node_ttl == "NOT_FOUND":
                continue

            distance = abs(int(srv_ttl) - int(test_node_ttl))
            n += 1
            distances.append(distance)

        # inconclusive if last resp IP wasn't found in any good MDA traces

        if len(distances) == 0:
            results_dict[domain][step_str+"_distance"] = "NOT_FOUND"
            not_found_in_mda.append([dest_ip, n_1_ip])
        else:
            min_distance = min(distances)
            if min_distance == 7:
                bad_cases.append((domain, dest_ip))
            results_dict[domain][step_str+"_distance"] = str(min_distance)
            if '4' in step_str and min_distance == 0:
                print(str(domain))

            #print("Checked IP:",n_1_ip)
            #print("Found in MDA traces:",len(distances))
            #print(f"Avg dist:{avg_distance}\tMin dist:{min_distance}\tMax dist:{max_distance}\n\n")

            dist_list.append(min_distance)
            # dist_list.append(int(avg_distance))

    print(f"\nN{step} Analysis")
    print("Total Analyzed:", len(dist_list) + len(not_found_in_mda) +
          len(sterik_servers) + too_short_traces)
    print("Found:", len(dist_list))
    print("Not Found:", len(not_found_in_mda))
    print("Sterik:", len(sterik_servers))
    print("TCP Trace Too Short:", too_short_traces)

    return dist_list, sterik_servers, not_found_in_mda, bad_cases


def merged_analysis(simple_traces, mda_traces, ip_to_dom, results):
    merged_mda_traces = {}
    not_found_in_mda = []
    lri_not_found = []
    found_in_mda = []
    dist_list = []
    total_checked = []
    for simple_trace in simple_traces:
        dest_ip = simple_trace[-1]
        domain = ip_to_dom[dest_ip]

        if results[domain]['n-1_ip'] != '*':
            continue

        lri = get_lri(simple_trace)
        results[domain]['backtracked_ip'] = lri

        if lri == "LRI_NOT_FOUND":
            lri_not_found.append(dest_ip)
            print(dest_ip)
            continue

        total_checked.append(dest_ip)

        distances = []
        for src_ip, mda_trace in mda_traces[domain].items():
            if dest_ip == '151.101.65.171':
                print(mda_trace)
            merged_mda_trace = get_merged_trace(mda_trace)
            if dest_ip == '151.101.65.171':
                print(merged_mda_trace)

            srv_ttl = get_ttl(dest_ip, merged_mda_trace)
            lri_ttl = get_ttl(lri, merged_mda_trace)

            if srv_ttl == "NOT_FOUND":
                assert "SERVER TTL NOT FOUND"

            if lri_ttl == "NOT_FOUND":
                continue

            distance = abs(int(srv_ttl) - int(lri_ttl))
            distances.append(distance)

        if len(distances) == 0:
            results[domain]['backtracked_distance'] = "NOT_FOUND"
            not_found_in_mda.append([dest_ip, lri])
        else:
            min_distance = min(distances)
            results[domain]['backtracked_distance'] = min_distance
            dist_list.append(min_distance)

    print("\nMerged MDA Trace Analysis")
    print("Total Analyzed:", len(total_checked))
    print("LRI not found:", len(lri_not_found))
    print("Found in MDA:", len(dist_list))
    print("Not found in MDA:", len(not_found_in_mda))

    return dist_list, not_found_in_mda


def ecdf(dist_list):
    """ Compute ECDF """
    data = np.array(dist_list)
    x = np.sort(data)
    n = x.size
    y = np.arange(1, n+1) / n
    return x, y


def make_plots(n_1_list, lri_list, output_name, title):
    sns.set()
    x, y = ecdf(lri_list)
    plt.plot(x, y, label="Backtracked distances ECDF")

    x, y = ecdf(n_1_list)
    plt.plot(x, y, label="N-1 distances ECDF")

    max_dist = max(max(lri_list), max(n_1_list))

    plt.title(title)
    plt.legend()
    x_ticks = range(0, max_dist+2, 1)
    plt.xticks(x_ticks)

    plt.savefig(output_name)
    plt.clf()
    plt.close()


def print_counts(title, dist_list):
    counts = Counter(dist_list)
    print(title)
    print(counts)


def write_to_file(ip_list, filename, fileheader):
    with open(filename, 'w') as f:
        f.write(fileheader)
        for dest, lri in ip_list:
            f.write(dest+'\t'+lri+'\n')


def make_not_found_files(n_1_not_found, lri_not_found):
    directory = 'ip_not_found_files/'
    if not os.path.exists(directory):
        os.mkdir(directory)

    print("N-1:", len(n_1_not_found))
    print("LRI:", len(lri_not_found))

    write_to_file(n_1_not_found, directory +
                  'n-1_ip_not_found.txt', "Server_IP\tTest_IP\n")
    write_to_file(lri_not_found, directory +
                  'backtracked_ip_not_found.txt', "Server_IP\tTest_IP\n")

def make_output_file(file, filename):
    directory = 'distances/'
    if not os.path.exists(directory):
        os.mkdir(directory)

    with open(directory+filename, 'w') as f:
        for distance in file:
            f.write(str(distance) + '\n')

def main():
    with open("domains_ns.txt", 'r') as f:
        input_doms_ips_list = [line.strip().split(' ') for line in f]
    dom_to_ip = {t[0]: t[1] for t in input_doms_ips_list}

    simple_traces, ip_to_dom = get_simple_traces_dns(
        'PK_results/step4_traceroute/*_dnstraceroute_.txt', dom_to_ip)
    print("Total Simple Traces (Unique Servers):", len(simple_traces))
    simple_traces = get_complete_simple_traces_dns(simple_traces, ip_to_dom)
    print("Complete Simple Traces:", len(simple_traces))

    print(len(ip_to_dom))

    mda_traces = get_mda_traces('./mda_traces_asterisk.json')
    print("Total unique servers:", len(
        mda_traces['23.81.71.154']), len(ip_to_dom))

    # Set up results dictionary
    results = {}
    complete_mda_traces_dict = {}
    for trace in simple_traces:
        srv_ip = trace[-1]
        domain = ip_to_dom[srv_ip]
        results[domain] = {}
        results[domain]['dest_ip'] = srv_ip
        results[domain]['mda_not_complete'] = "N/A"
        results[domain]['n-1_ip'] = "N/A"
        results[domain]['n-1_distance'] = "N/A"
        results[domain]['backtracked_ip'] = "N/A"
        results[domain]['backtracked_distance'] = "N/A"

        relevant_mda_traces = {}
        mda_trace_not_done = {}
        # Get complete MDA traces for each domain
        for src_ip, traces in mda_traces.items():
            try:
                relevant_mda_traces[src_ip] = traces[srv_ip]
            except KeyError as e:
                mda_trace_not_done[src_ip] = srv_ip

        complete_mda_traces = {}
        for src_ip, trace in relevant_mda_traces.items():
            all_ips = [t[0] for t in trace]
            if srv_ip in all_ips:
                complete_mda_traces[src_ip] = trace

        complete_mda_traces_dict[domain] = complete_mda_traces
        if len(complete_mda_traces):
            results[domain]['mda_not_complete'] = False
        else:
            results[domain]['mda_not_complete'] = True

    print("Total traces:", len(simple_traces))

    simple_traces_mda_complete = []
    for trace in simple_traces:
        domain = ip_to_dom[trace[-1]]
        if not results[domain]['mda_not_complete']:
            simple_traces_mda_complete.append(trace)

    print("Total traces with corresponding MDA trace:",
          len(simple_traces_mda_complete))

    # Do analysis for n-1 IPs
    n_1_dist_list, sterik_servers, n_1_not_found_in_mda, bad_cases = compare_step_ips(-1,
                                                                                      results, simple_traces_mda_complete,
                                                                                      complete_mda_traces_dict, ip_to_dom)

    lri_dist_list, lri_not_found_in_mda = merged_analysis(simple_traces_mda_complete,
                                                          complete_mda_traces_dict,
                                                          ip_to_dom, results)

    make_output_file(n_1_dist_list, "n-1_from_control.txt")
    make_output_file(lri_dist_list, "backtracked_from_control.txt")


    all_distances = n_1_dist_list + lri_dist_list
    make_output_file(all_distances, "dns_from_control.txt")

    with open('bad_cases.txt', 'w') as f:
        for domain, dest_ip in bad_cases:
            f.write(domain + '\t' + dest_ip + '\n')
    print()
    print("Total distances found:", len(n_1_dist_list))
    print("Total not found in MDA:", len(n_1_not_found_in_mda))

    # make_plots(n_1_dist_list, lri_dist_list,
    #            "plots/merged_analysis_plot_from_control.png", "DNS Plots From Control")
    make_not_found_files(n_1_not_found_in_mda, lri_not_found_in_mda)
    print_counts("N-1 Counts:", n_1_dist_list)
    print_counts("Backtracked Counts:", lri_dist_list)


if __name__ == '__main__':
    main()
