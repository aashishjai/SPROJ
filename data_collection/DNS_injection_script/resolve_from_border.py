from multiprocessing import Process
import dns.resolver
from dns.resolver import NoAnswer
from dns.resolver import NXDOMAIN
from dns.resolver import NoNameservers
import os
import sys
import time


def dns_query(my_list, num, nameservers):
    res = dns.resolver.Resolver(configure=False) 
    res.timeout = 15
    res.lifetime = 15
    num = str(num)
    start = time.time()

    # res.nameservers = nameservers
    res.nameservers = [nameservers]
    domain_list = my_list
    fail_domain = []

    retry = 0
    count = 0
    for i in range(1):
        fail_str = ""
        for domain in domain_list:
            count = count + 1

            try:
                print("here")
                resultDNS = res.resolve(domain, 'a') # changed by aash
                # resultDNS = res.resolve("1.1.1.1", 'a') # changed by aash
                one_line = domain + " "
                print("here2")

                for i in resultDNS:
                    one_line = one_line + str(i) + ","

                one_line_without_trailing_comma = one_line[0:-1]
                answer = ''
                with open(nameservers + "_" + num + "_success.txt", 'a') as file1:
                    file1.write(one_line_without_trailing_comma + "\n")

            except Exception as e:
                fail_str = fail_str + domain + " " + str(e) + "\n"
                chunk_string = domain + " " + str(e) + "\n"
                with open(nameservers + "_" + num + "_fail.txt", 'a') as file1:
                    file1.write(chunk_string)
                fail_domain.append(domain)
        domain_list = fail_domain
        fail_domain = []

    with open("time.txt", 'a') as file5:
        file5.write("Thread : " +
                    num +
                    " Time taken " +
                    str(time.time() -
                        start) +
                    " failures " +
                    str(len(fail_domain)) +
                    "\n")


def main(nameserver):
    N_THREADS = 100
    domain_list = []

    with open("domains_no_false_resp.txt", 'r') as file:
        domain_list = file.read().split("\n")
        domain_list = [d.split()[0] for d in domain_list if d]

    THREAD_WORKLOAD = int(max(len(domain_list) / N_THREADS, 1))
    count = 0
    for thread_start_index in range(0, len(domain_list), THREAD_WORKLOAD):
        thread_chunk = domain_list[thread_start_index:
                                   thread_start_index + THREAD_WORKLOAD]
        p = Process(target=dns_query, args=(thread_chunk, count, nameserver))
        count = count + 1
        p.start()


if __name__ == '__main__':
    nameservers = open("border_routers.txt", 'r').readlines()
    nameservers = [ns.strip() for ns in nameservers]
    nameservers = list(set(nameservers))
    domain_list = nameservers
    if not nameservers:
        print("No border router found! Exiting...")
        exit() # added by aash

    N_THREADS = 100

    THREAD_WORKLOAD = int(max(len(domain_list) / N_THREADS, 1))
    count = 0
    for thread_start_index in range(0, len(domain_list), THREAD_WORKLOAD):
        thread_chunk = domain_list[thread_start_index:
                                   thread_start_index + THREAD_WORKLOAD]
        p = Process(target=main, args=(thread_chunk))
        count = count + 1
        p.start()

######################################################################

