import pandas as pd

def get_distance_counts(df):
	grouped = df.groupby('distance')['domain'].count()
	return grouped.reset_index()

print(1155 - 2 - 4 - 184 - 183)


df = pd.read_csv('distances.csv')
print("Total analyzed:", len(df))
df = df[df['distance'] != -1]
print("Distance found from test:", len(df))
cdn = df[df['cdn'] == True]
df = df[df['cdn'] == False]
print("CDN:", len(cdn))
print()
print("Non-CDN:", len(df))
non_error = df[df['last_responding_country'] != 'ERR']
geo_err = df[df['last_responding_country'] == 'ERR']
print("Non-ERR Geo:", len(non_error))

pk_lri = non_error[non_error['last_responding_country'] == 'PK']
non_pk_lri = non_error[non_error['last_responding_country'] != 'PK']

print("Total in Pak:", len(pk_lri))
print("Total not in Pak:", len(non_pk_lri))
print("Total GEO ERR:", len(geo_err))
total = len(df)
print("Total:", total)
pk_counts = get_distance_counts(pk_lri)
non_pk_counts = get_distance_counts(non_pk_lri)

print()
# Find false negatives for PK
false_neg = pk_counts[pk_counts['distance'] > 1]['domain'].sum()
print("False Negative:", false_neg)
false_neg_percentage = float(false_neg)/float(total)*100
print("False Negative %age:", false_neg_percentage)
print()
pk_correct = pk_counts[pk_counts['distance'] <= 1]['domain'].sum()
tp_pk_percentage = float(pk_correct)/float(total)*100
print("True Positive (PK):", pk_correct)
print("True Positive (PK) %age:", tp_pk_percentage)
print()
inconc = non_pk_counts[non_pk_counts['distance'] > 1]['domain'].sum() + len(geo_err)
inconc_percentage = float(inconc)/float(total)*100
print("Inconclusive:", inconc)
print("Inconclusive %age:", inconc_percentage)
print()
non_pk_correct = non_pk_counts[non_pk_counts['distance'] <= 1]['domain'].sum()
tp_non_pk_percentage = float(non_pk_correct)/float(total)*100
print("True Positive (Non-PK):", non_pk_correct)
print("True Positive (Non-PK) %age:", tp_non_pk_percentage)
print()

print("SUM:", false_neg_percentage+tp_pk_percentage+tp_non_pk_percentage+inconc_percentage)