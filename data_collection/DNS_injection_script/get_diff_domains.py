pk_file = open("pk_resolved_domains.txt")
usa_file = open("usa_resolved_domains.txt")
doms_diff_ips = open("domains.txt",'w')


def domain_to_ip(text_file):
    domain_to_ip_dict = dict()
    for line in text_file:
        line = line.split(" ")
        domain = line[0]
        ips = line[1].strip().split(",")
        domain_to_ip_dict[domain] = ips
    return domain_to_ip_dict


def compairson(pk_domains, usa_domains):
    domains_different_ips = list() 

    for domain, ips in pk_domains.items():
        
        if domain not in usa_domains:
            continue
        
        pk_ips = sorted(ips)
        usa_ips = sorted(usa_domains[domain])

        if pk_ips != usa_ips:
            domains_different_ips.append(domain)

    for dom in domains_different_ips:
        doms_diff_ips.write(dom+"\n")

    print("Domains with different IPS:",len(domains_different_ips))


if __name__ == "__main__":
    pk_domains = domain_to_ip(pk_file)
    usa_domains = domain_to_ip(usa_file)
    compairson(pk_domains, usa_domains)


