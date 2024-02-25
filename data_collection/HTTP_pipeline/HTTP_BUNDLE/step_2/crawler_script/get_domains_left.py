import glob

all_files = glob.glob('run_crawler_raw_results/*')

with open('resolved_domains.txt', 'r') as f:
    input_doms = [line.strip() for line in f]

input_doms = set(input_doms)

doms_done = set()
for one_file in all_files:
    i = one_file.rfind('/') + len('/')
    j = one_file.find('.json')
    doms_done.add(one_file[i:j])

doms_left = input_doms.difference(doms_done)

with open('domains_left.txt', 'w') as f:
    for dom in doms_left:
        f.write(dom +'\n')