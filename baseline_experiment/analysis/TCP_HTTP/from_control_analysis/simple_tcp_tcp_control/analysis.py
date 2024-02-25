import pandas as pd 
import os

def get_mda_complete(df):
	mda_not_done = df[df['mda_not_done'] == True]
	mda_done = df[df['mda_not_done'] == False]

	print("MDA done:", len(mda_done))
	mda_not_complete = df[df['mda_not_complete'] == True]
	mda_complete = df[df['mda_not_complete'] == False]
	print("Mda complete:", len(mda_complete))

	return mda_complete, mda_not_complete

def get_error_categorization(x, step_str):
	if x[step_str+'_distance'].isdigit():
		return "NO_ERROR"
	elif x[step_str+'_distance'] == 'NOT_FOUND':
		return "IP_NOT_FOUND_IN_MDA"
	elif x[step_str+'_ip'] == '*':
		return "ASTERISK"
	elif x[step_str+'_ip'] == 'TRACE_TOO_SHORT':
		return "TRACE_TOO_SHORT"
	else:
		return "NOT_POSSIBLE"

def get_summary_numbers(df):
	for i in range(-1, -5, -1):
		step_str = 'n'+str(i)
		err_string = step_str+'_error_categorization'
		columns = [step_str+'_ip', step_str+'_location', step_str+'_distance']
		step_df = df[columns]
		df[err_string] = step_df.apply(get_error_categorization, axis=1, args=(step_str,))

	summary = {}
	summary['n-1_error_summary'] = df.groupby(['n-1_error_categorization', 'cdn'])['domains'].count()
	summary['n-2_error_summary'] = df.groupby(['n-2_error_categorization', 'cdn'])['domains'].count()
	summary['n-3_error_summary'] = df.groupby(['n-3_error_categorization', 'cdn'])['domains'].count()
	summary['n-4_error_summary'] = df.groupby(['n-4_error_categorization', 'cdn'])['domains'].count()

	summary_df = pd.DataFrame.from_dict(summary, orient='index')
	summary_df = summary_df.fillna(0)
	print(summary_df)

	return summary_df

def get_location_categorization(x, step_str):
	loc_str = step_str+'_location'
	if x[loc_str] == 'N/A':
		return "N/A"
	elif x[loc_str] == 'ERR' or x['dest_location'] == 'ERR':
		return "ERR"
	elif x[loc_str] == x['dest_location']:
		return "SAME_AS_SERVER"
	elif x[loc_str] == 'PK':
		return "TEST_COUNTRY"
	else:
		return "ELSEWHERE"


def not_found_analysis(df):
	summary = {}
	for i in range(-1, -5, -1):
		step_str = 'n'+str(i)
		loc_cat_str = step_str+'_location_categorization'
		df[loc_cat_str] = df.apply(get_location_categorization, axis=1, args=(step_str,))
		not_found_df = df[df[step_str+'_distance'] == 'NOT_FOUND']
		summary[step_str+'_loc_summary'] = not_found_df.groupby([loc_cat_str, 'cdn'])['domains'].count()

	summary_df = pd.DataFrame.from_dict(summary, orient='index')
	print(summary_df)

	return summary_df

def get_distribution(df):
	summary = {}
	for i in range(-1, -5, -1):
		step_str = 'n'+str(i)
		distance_str = step_str+'_distance'
		temp_df = df[df[distance_str].apply(lambda x: x.isdigit())]

		summary[distance_str] = temp_df.groupby(distance_str)['domains'].count()

	summary_df = pd.DataFrame.from_dict(summary).fillna(0).astype('int32')
	print(summary_df)

	return summary_df

def make_asterisk_files(df):
	asterisk_dir = 'asterisk_files/'
	if not os.path.exists(asterisk_dir):
		os.mkdir(asterisk_dir)

	n_1_asterisk = df[df['n-1_error_categorization'] == 'ASTERISK'][['domains','dest_ip']]
	print("n-1 asterisks:", len(n_1_asterisk))
	n_1_asterisk.to_csv(asterisk_dir+'n-1_asterisk.csv', index=False)

	n_2_asterisk = df[df['n-2_error_categorization'] == 'ASTERISK'][['domains','dest_ip']]
	print("n-2 asterisks:", len(n_2_asterisk))
	n_2_asterisk.to_csv(asterisk_dir+'n-2_asterisk.csv', index=False)

	n_3_asterisk = df[df['n-3_error_categorization'] == 'ASTERISK'][['domains','dest_ip']]
	print("n-3 asterisks:", len(n_3_asterisk))
	n_3_asterisk.to_csv(asterisk_dir+'n-3_asterisk.csv', index=False)

	n_4_asterisk = df[df['n-4_error_categorization'] == 'ASTERISK'][['domains','dest_ip']]
	print("n-4 asterisks:", len(n_4_asterisk))
	n_4_asterisk.to_csv(asterisk_dir+'n-4_asterisk.csv', index=False)

def make_ip_not_found_files(df):
	ip_not_found = 'ip_not_found_files/'
	if not os.path.exists(ip_not_found):
		os.mkdir(ip_not_found)

	n_1_ip_not_found = df[df['n-1_error_categorization'] == 'IP_NOT_FOUND_IN_MDA'][['domains','dest_ip']]
	print("n-1 ip_not_founds:", len(n_1_ip_not_found))
	n_1_ip_not_found.to_csv(ip_not_found+'n-1_ip_not_found.csv', index=False)

	n_2_ip_not_found = df[df['n-2_error_categorization'] == 'IP_NOT_FOUND_IN_MDA'][['domains','dest_ip']]
	print("n-2 ip_not_founds:", len(n_2_ip_not_found))
	n_2_ip_not_found.to_csv(ip_not_found+'n-2_ip_not_found.csv', index=False)

	n_3_ip_not_found = df[df['n-3_error_categorization'] == 'IP_NOT_FOUND_IN_MDA'][['domains','dest_ip']]
	print("n-3 ip_not_founds:", len(n_3_ip_not_found))
	n_3_ip_not_found.to_csv(ip_not_found+'n-3_ip_not_found.csv', index=False)

	n_4_ip_not_found = df[df['n-4_error_categorization'] == 'IP_NOT_FOUND_IN_MDA'][['domains','dest_ip']]
	print("n-4 ip_not_founds:", len(n_4_ip_not_found))
	n_4_ip_not_found.to_csv(ip_not_found+'n-4_ip_not_found.csv', index=False)



def main():
	df = pd.read_csv('results.csv', na_filter=False)
	df = df.rename(columns = {'Unnamed: 0': 'domains'})
	print("Total:", len(df))

	results_dir = 'results/'
	if not os.path.exists(results_dir):
		os.mkdir(results_dir)

	relevant_columns = ['domains', 
						'dest_ip', 
						'dest_location', 
						'cdn',
						'n-1_ip',
						'n-1_location',
						'n-1_distance',
						'n-2_ip',
						'n-2_location',
						'n-2_distance',
						'n-3_ip',
						'n-3_location',
						'n-3_distance',
						'n-4_ip',
						'n-4_location',
						'n-4_distance']

	df, mda_not_complete = get_mda_complete(df)
	df = df[relevant_columns]

	mda_not_complete[['domains', 'dest_ip', 'dest_location', 'cdn']].to_csv(results_dir+'mda_not_complete.csv')

	err_summary_df = get_summary_numbers(df)
	err_summary_df = err_summary_df.T
	err_summary_df.to_csv(results_dir+'error_summary.csv')
	
	loc_summary_df = not_found_analysis(df)
	loc_summary_df = loc_summary_df.T
	loc_summary_df.to_csv(results_dir+'location_summary.csv')

	n_1_cols = ['domains', 
				'dest_ip', 
				'dest_location', 
				'cdn',
				'n-1_ip',
				'n-1_location',
				'n-1_distance']

	not_found_same_server = df[(df['n-1_distance'] == 'NOT_FOUND') & (df['n-1_location_categorization'] == 'SAME_AS_SERVER')].sort_values('cdn')[n_1_cols]

	not_found_same_server.to_csv(results_dir+'n_1_not_found_same_server.csv')

	distribution = get_distribution(df)
	distribution.to_csv(results_dir+'distribution.csv')

	make_asterisk_files(df)
	make_ip_not_found_files(df)

if __name__ == '__main__':
	main()
