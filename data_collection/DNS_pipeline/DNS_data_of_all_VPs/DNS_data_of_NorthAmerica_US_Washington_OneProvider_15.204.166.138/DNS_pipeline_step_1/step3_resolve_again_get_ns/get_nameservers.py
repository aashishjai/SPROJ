import time
import mydig
import os
import sys
from multiprocessing import Process
os.chdir(os.path.dirname(sys.argv[0]))


def spread_work(domain_list, count):
    for domain in domain_list:
        if domain == "":
            continue
        mydig.alias([count, domain, "A"])


if __name__ == "__main__":
    domain_list = []
    with open("server_side_blocked.txt", 'r') as file:
        domain_list = file.read().split("\n")

    N_THREADS = 60
    THREAD_WORKLOAD = int(max(len(domain_list) / N_THREADS, 1))

    count = 0
    for thread_start_index in range(0, len(domain_list), THREAD_WORKLOAD):
        thread_chunk = domain_list[thread_start_index:
                                   thread_start_index + THREAD_WORKLOAD]
        p = Process(target=spread_work, args=(thread_chunk, count,))
        count = count + 1
        p.start()
