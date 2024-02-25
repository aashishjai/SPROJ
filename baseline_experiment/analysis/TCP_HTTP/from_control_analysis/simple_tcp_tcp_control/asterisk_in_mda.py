import os
import json
import pandas as pd

# READ ALL ASTERISK FILES AND GET DEST IPS FROM THERE
def get_asterisk_ips(filename):
	with open(filename, 'r') as f:
		f.readline()
		dom_ips = [line.strip().split(',') for line in f]

	ips = [t[1] for t in dom_ips]
	ip_to_dom = {t[1]:t[0] for t in dom_ips}

	return ips, ip_to_dom

def get_mda_traces(file):
	with open(file, 'r') as f:
		full_dict = json.load(f)

	return full_dict

def do_asterisk_analysis(ips, step, mda_traces):
	results = {}
	for src_ip, traces in mda_traces.items():
		results[src_ip] = {}
		for dest_ip in ips:
			trace = traces[dest_ip]
			all_ips = [t[0] for t in trace]
			if dest_ip in all_ips:
				max_ttl = trace[-1][1]
				relevant_ttl = max_ttl + step
				relevant_ips = [ip for ip, ttl in trace if ttl == relevant_ttl]
				if len(relevant_ips) == 1 and relevant_ips[0] == '*':
					results[src_ip][dest_ip] = "MDA_ASTERISK"
				else:
					results[src_ip][dest_ip] = "MDA_NON_ASTERISK"
			else:
				results[src_ip][dest_ip] = "MDA_NOT_COMPLETE"

	return results

def summary_categorization_by_source(df):
	groupby_cols = [col for col in df.columns if col != 'index']
	result = {}
	for col_name in groupby_cols:
		grouped = df.groupby(col_name)['index'].count()
		result[col_name] = grouped

	result_df = pd.DataFrame.from_dict(result, orient='index')
	return result_df

def get_consistency_val(x):
	for col in x:
		if 'MDA_NON_ASTERISK' in col:
			return 'MDA_INCONSISTENT'

	return 'MDA_CONSISTENT'

def summary_categorization_overall(df):
	df['consistency'] = df.apply(get_consistency_val, axis=1)

	grouped = df.groupby('consistency')['index'].count()
	return grouped

def main():
	results_dir = 'asterisk_results/'
	if not os.path.exists(results_dir):
		os.mkdir(results_dir)

	for step in range(-1, -5, -1):
		step_str = 'n'+str(step)
		print(step_str)
		filename = 'asterisk_files/'+step_str+'_asterisk.csv'
		asterisk_ips, ip_to_dom = get_asterisk_ips(filename)
		print("Total:", len(asterisk_ips))
		mda_traces = get_mda_traces('../../mda_traces_asterisk.json')
		asterisk_results = do_asterisk_analysis(asterisk_ips, step, mda_traces)
		df = pd.DataFrame.from_dict(asterisk_results).reset_index()
		by_source_summary = summary_categorization_by_source(df)
		consistency_summary = summary_categorization_overall(df)
		by_source_summary.to_csv(results_dir+step_str+'_by_source.csv')
		consistency_summary.to_csv(results_dir+step_str+'_consistency.csv')



if __name__ == '__main__':
	main()
