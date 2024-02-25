import sys
with open("domains_ns.txt",'r') as file:
	data=file.read().split("\n")


def get_hex(domain):
	separate=domain.split(".")
	complete_hex=""
	for label in separate:
		length=hex(len(label))[2:]
		if len(length)==1:
			length="0"+length
		hex_of_label=''.join(str.encode(x).hex() for x in label)
		complete_hex=complete_hex+length+hex_of_label

	return "b77101200001000000000000"+complete_hex+"0000010001"
ip_seen=[]
with open("scamper_commands.txt",'w') as file:
	for one_domain_ip in data:
		if one_domain_ip=="":
			continue
		separate=one_domain_ip.split(" ")
		domain=separate[0]
		ip=separate[1]
		if ip in ip_seen:
			continue
		ip_seen.append(ip)


		domain_in_hex=get_hex(domain)
		new_command="tracelb -d 53 -p "+domain_in_hex+" -g 7 -H "+domain+" -P udp-sport "+ip

		file.write(new_command+"\n")

