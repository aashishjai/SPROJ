import subprocess
from geoip import geolite2
import socket
from requests import get
from multiprocessing import Process
import os
import json

# clear previous files
open("tracert_output.txt", 'w').close()

# get public IP and country
response = get('https://ipinfo.io/json', verify = True).json()
my_ip = response['ip']
print('\nMy Public IP address:', my_ip)
my_country = geolite2.lookup(my_ip).country
print('My country:', my_country, "\n")

ip_to_dom = dict()
# domains to traceroute to for obtaining the router at the edge
# tracert_domains = [
#     'hostafrica.co.za',
#     'apnic.net',
#     # 'digitalpacific.com.au']
#     # 'hetzner.com' ]
#     'swissns.ch']
tracert_domains = [
    'google.com',
    'amazon.com',
    # 'gogoanime.io',
    'bing.com',
    'facebook.com',
    'pornhub.com',
    'instagram.com']
    # 'digitalpacific.com.au']
    # 'hetzner.com' ]


def get_server_ip(domain):
    output = subprocess.check_output(["dig", "+short", "A", domain])
    output = output.decode("utf-8").strip().split("\n")[0]
    return output


def get_nameserver(ip):
    done = False
    try:
        output = subprocess.check_output(
            ["inetutils-traceroute", "-M", "icmp", ip])
        ns_to_check = open("border_routers.txt", 'a')
        output = output.decode("utf-8")
        output_list = output.split("\n")
        tracert_outputs = open("tracert_output.txt", 'a')
        tracert_outputs.write(ip_to_dom[ip] + "\n" + str(output))
        tracert_outputs.close()

        for i, line in enumerate(output_list):
            print(i)
            if i == 0:
                continue

            if len(line) >= 2:
                hop_ip = ""
                for hop in line.split()[1:]:
                    if '*' not in hop:
                        hop_ip = hop
                        break

                if not hop_ip:
                    continue

                hop_ip = hop_ip.strip()
                match = geolite2.lookup(hop_ip)
                country = ""

                if match:
                    country = match.country

                    if country != my_country and done == False:
                        ns_to_check.write(hop_ip + "\n")
                        done = True

        ns_to_check.close()
    except subprocess.CalledProcessError as e:
        print(f"Error running traceroute for IP {ip}: {e}")
    


if __name__ == '__main__':
    open('border_routers.txt', 'w')

    domain_list = []
    for dom in tracert_domains:
        ips = get_server_ip(dom)
        domain_list.append(ips)
        ip_to_dom[ips] = dom

    print("here")
    N_THREADS = 100
    THREAD_WORKLOAD = int(max(len(domain_list) / N_THREADS, 1))
    count = 0

    for thread_start_index in range(0, len(domain_list), THREAD_WORKLOAD):
        print("here2")
        thread_chunk = domain_list[thread_start_index:
                                   thread_start_index + THREAD_WORKLOAD]
        p = Process(target=get_nameserver, args=(thread_chunk))
        count = count + 1
        p.start()
