import os
import sys
# os.chdir(os.path.dirname(sys.argv[0]))
from subprocess import check_output
import subprocess
import re

domains_file = sys.argv[1]
pcap_file = sys.argv[2]

with open(domains_file,'r') as file:
	inputs = [line.strip().split(' ') for line in file]

for dom_ip in inputs:

	domain=dom_ip[0]
	ip=dom_ip[1]

	os.system("tshark -r "+pcap_file+" -w"+" ./traces/"+ip+".pcap -F pcap ip.addr=="+ip)

