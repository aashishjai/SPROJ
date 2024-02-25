import subprocess
from requests import get
from multiprocessing import Process
import json
import os
import ipaddress

def do_whois(ip, dom):
    log_path = "./logs/"+dom+"_whois_resp.txt"
    if not os.path.isfile(log_path):
        open(log_path,'w').close()

    whois_resp = open("./logs/"+dom+"_whois_resp.txt",'a')
    whois_resp.write("\n\n\n"+"-"*10+"\t"+str(ip)+"\t"+str(dom)+"\t"+"-"*10+"\n")
    
    whois = subprocess.run(["whois", ip], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode('utf-8')
    whois = whois.split("\n")
    descr = ""
    for line in whois:
        whois_resp.write(line+"\n")
        line = line.lower()
        if "org" in line and "name" in line:
            line = line.split(":")
            org = line[1].lstrip().strip().lower()
            return org
        elif "descr" in line and not descr:
            try:
                line = line = line.split(":")
                descr = line[1].lstrip().strip().lower()
            except:
                continue
    return descr


def check_false_resp(domains, my_ip, my_isp, upstream_isps):
    result_file = open("domains_no_false_resp.txt",'a')
    false_resp_doms = open("false_resp_domains.txt",'a')
    
    # checking in file that also contains IPs
    for dom_string in domains:
        dom_string = dom_string.split()
        dom = dom_string[0].strip()
        ips = []
        if len(dom_string) >1:
            ips = dom_string[1].strip()
            ips = [ip.strip() for ip in ips.split(",")]
        else:
            full_domain = "www."+dom
        
        dig_log_path = "./logs/"+dom+"_dig_resp.txt"
        if not os.path.isfile(dig_log_path):
            open(dig_log_path,'w').close()

        # if file don't contain IPs
        if not ips:
            dig_resp = open(dig_log_path,'a')
            output = subprocess.check_output(["dig", "A", dom])
            output = output.decode("utf-8")
            output = output.split("\n")
            dig_resp.write("\n"+"-"*10+"\t"+full_domain+"-"*10+"\n")
            ips = []
            answer_section = False
            for line in output:
                dig_resp.write(line+"\n")
                
                if answer_section and "IN" in line and "CNAME" not in line:
                    if not line:
                        answer_section = False
                        continue
                    returned_ip = line.split()[-1]
                    ips.append(returned_ip)
                
                if "ANSWER SECTION" in line:
                    answer_section = True
                
        if not ips:
            result_file.write(dom+"\t"+"NO-IPs-FOUND"+"\n")
            continue
        
        false_response = False
        org = ""
        orgs_dict = dict()
        org_found = False
        for ip in ips:
            if ipaddress.ip_address(ip).is_private:
                false_response = True
                org_found = True
                orgs_dict[ip] = "PRIVATE-IP"
                break
            
            org = do_whois(ip, dom)
            
            if org:
                org_found = True
            else:
                org = "NOT-FOUND"
            
            orgs_dict[ip] = org
            
            if org in upstream_isps or org == my_isp:
                false_response = True
                break
        
        if not org_found:
            orgs_dict["ALL-IPs"] = "NO-ORG-FOUND"
        
        if false_response == False:
            result_file.write(dom+"\t"+str(orgs_dict)+"\n")
        else:
            false_resp_doms.write(dom+"\t"+str(orgs_dict)+"\n")
        

if __name__ == '__main__':
    response = get('https://ipinfo.io/json', verify = True).json()
    my_ip = response['ip']
    
    my_isp = do_whois(my_ip, "MY_ISP")
    print('\nMy Public IP address:', my_ip,"\nMy ISP: ", my_isp)
    
    upstream_isps = ["transworld associates (pvt) limited","pakistan telecommuication company limited", "nayatel (pvt) ltd"]

    # clear output files
    open("domains_no_false_resp.txt", 'w').close()
    open("false_resp_domains.txt", 'w').close()

    domains_file = open("domains.txt")
    domain_list = []
    for dom in domains_file:
        domain_list.append(dom)
        
    N_THREADS = 100
    THREAD_WORKLOAD = int(max(len(domain_list) / N_THREADS, 1))
    count = 0

    for thread_start_index in range(0, len(domain_list), THREAD_WORKLOAD):
        thread_chunk = domain_list[thread_start_index:
                                   thread_start_index + THREAD_WORKLOAD]
        p = Process(target=check_false_resp, args=[thread_chunk, my_ip, my_isp, upstream_isps])
        count = count + 1
        p.start()
    