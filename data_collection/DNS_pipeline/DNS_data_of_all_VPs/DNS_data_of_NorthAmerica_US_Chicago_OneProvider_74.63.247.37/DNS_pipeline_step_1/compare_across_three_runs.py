import os
from functools import reduce

BASE_DIR = os.getcwd() 
runs = ["run1", "run2", "run3"]


def prep_data():
	for run in runs:
		with open(run+'/blocked_domain_ns_info.txt', 'r') as f:
			have_auth_tuples = []
			no_auth_tuples = []
			for line in f:
				if "The" in line.strip().split(' ')[0] or "root" in line.strip().split(' ')[0]:
					with open("error.txt", 'w') as f:
						f.write(line)
				else:
					split_line = line.strip().split('  ')
					if len(split_line) > 1:
						cname = split_line[-1]
						domain_and_records = split_line[:-1]
						records = []
						for i, domain_record in enumerate(domain_and_records):
							if i == 0:
								domain_name = domain_record.split(' ')[0]
								domain_record = ' '.join(domain_record.split(' ')[1:])

							records.append(domain_record)
						sorted_records = sorted(records)
						auth_ip = sorted_records[0].split(' ')[4]

						have_auth_tuples.append([domain_name, auth_ip, cname])
					else:
						no_auth_tuples.append(split_line[0].split(' '))
			with open(run+'/have_auth_no_ip_extended.txt', 'w') as f:
				for tupl in have_auth_tuples:
					f.write(tupl[0] + ' ' + tupl[1] + ' ' + tupl[2] + '\n')

			with open(run+'/no_auth_no_ip_extended.txt', 'w') as f:
				for tupl in no_auth_tuples:
					f.write(tupl[0] + ' ' + tupl[1] + '\n')


def compare_across_runs():
	os.chdir(BASE_DIR)
	no_auth_no_ip = dict()
	have_auth_no_ip = dict()

	for run in runs:
		no_auth_no_ip[run] = set()
		have_auth_no_ip[run] = set()

		with open(os.path.join(BASE_DIR, run, "no_auth_no_ip_extended.txt")) as f:
			no_auth_no_ip[run] = set([line.strip() for line in f.readlines()])

		with open(os.path.join(BASE_DIR, run, "have_auth_no_ip_extended.txt")) as f:
			have_auth_no_ip[run] = set([line.strip() for line in f.readlines()])

	no_auth_no_ip_common = reduce(
		lambda x, y: x & y, list(no_auth_no_ip.values()))
	have_auth_no_ip_common = reduce(
		lambda x, y: x & y, list(have_auth_no_ip.values()))

	with open("no_auth_no_ip_extended.common_three_runs.txt", "w") as wf:
		wf.write("\n".join(no_auth_no_ip_common))

	with open("have_auth_no_ip_extended.common_three_runs.txt", "w") as wf:
		wf.write("\n".join(have_auth_no_ip_common))

	with open("blocked_stats.txt", "w") as wf:
		wf.write("\n".join(["No auth: " + str(len(no_auth_no_ip_common)),
                      "Have auth: " + str(len(have_auth_no_ip_common))]))


if __name__ == "__main__":
	prep_data()
	compare_across_runs()
