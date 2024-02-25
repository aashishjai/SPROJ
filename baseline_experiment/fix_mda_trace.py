with open('./MDA_TCP_OUTPUT_FIXED.txt', 'r') as f:
	all_lines = [line.strip() for line in f]

new_file = []
for line in all_lines:
	if 'tracelb' in line:
		prob_spot = line.find('tracelb')
		if prob_spot > 0:
			line1 = line[:prob_spot]
			line2 = line[prob_spot:]
			new_file.append(line1)
			new_file.append(line2)
		else:
			new_file.append(line)
	else:
		new_file.append(line)

with open('./MDA_TCP_NEWLINE_FIXED.txt', 'w') as f:
	for line in new_file:
		f.write(line + '\n')