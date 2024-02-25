import time
from multiprocessing import Process
import dns.resolver
from dns.resolver import NoAnswer
from dns.resolver import NXDOMAIN
from dns.resolver import NoNameservers
import os
import sys
sys.path.insert(0, '/root')
os.chdir(os.path.dirname(sys.argv[0]))


def one_fun(my_list, num):
    res = dns.resolver.Resolver(configure=False)
    num = str(num)
    start = time.time()
    resolver = sys.argv[1]
    res.nameservers = [resolver]

    domain_list = my_list
    fail_domain = []

    count = 0
    for i in range(2):
        fail_str = ""
        for domain in domain_list:
            count = count+1

            try:
                resultDNS = res.query(domain, 'a')
                one_line = domain+" "

                for i in resultDNS:
                    one_line = one_line+str(i)+","
                one_line_without_trailing_comma = one_line[0:-1]

                with open(num+"_success.txt", 'a') as file1:
                    file1.write(one_line_without_trailing_comma+"\n")

            except Exception as e:
                fail_str = fail_str+domain+" "+str(e)+"\n"
                fail_domain.append(domain)

        domain_list = fail_domain
        fail_domain = []
    with open(num+"_fail.txt", 'w') as file1:
        file1.write(fail_str)

    with open("time.txt", 'a') as file5:
        file5.write("Thread : "+num+" Time taken "+str(time.time() -
                                                       start)+" failures "+str(len(fail_domain))+"\n")


N_THREADS = 100

domain_list = []


with open("active_doms.txt", 'r') as file:
    domain_list = file.read().split("\n")
THREAD_WORKLOAD = int(max(len(domain_list) / N_THREADS, 1))
count = 0
for thread_start_index in range(0, len(domain_list), THREAD_WORKLOAD):
    thread_chunk = domain_list[thread_start_index:
                               thread_start_index + THREAD_WORKLOAD]
    p = Process(target=one_fun, args=(thread_chunk, count,))
    count = count+1
    p.start()
