import pandas as pd 

def label_transform(x):
	if 'Censorship' in x:
		return 'Middlebox'
	return x.split('-')[1]

def get_val(x):
	if x == 'INTERESTING FINDING':
		return 'CORRECT'
	elif x == 'INTERESTING VAGUE':
		return 'VAGUE'
	else:
		return x

df = pd.read_csv('validation.csv')
df['label'] = df['final_label'].apply(label_transform)
df['manual'] = df['validation'].apply(get_val)

df = df[['domain', 'label', 'manual']]

grouped = df.groupby(['label', 'manual'])['domain'].count()
print(grouped)