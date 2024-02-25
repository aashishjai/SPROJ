if __name__ == "__main__":
	try:
		# If the "active_set_IPs.txt" file exists, it will use that
		dom_ips = []
		with open("../active_set_IPs.txt", 'r') as f:
			for line in f:
				dom = line.split(' ')[0].strip()
				ip = line.split(' ')[1].strip().split(',')[0]
				dom_ips.append(dom + ' ' + ip + '\n')

		with open("simple_traceroute_input.txt", "w") as f:
			for dom_ip in dom_ips:
				f.write(dom_ip)
	except:
		# Otherwise it will create an empty text file to prevent code from crashing
		with open("simple_traceroute_input.txt", "w") as f:
			f.write('\n')
