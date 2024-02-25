SPEED=$1
mkdir -p run_crawler_summary

# The set of unique domains which we need to run test on
python get_domains_left.py

# Remove old raw files
rm -rf run_crawler_raw_results
mkdir -p run_crawler_raw_results
FILE_SIZE="`cat domains_left.txt | wc -l`"
echo "Initial Input: "$FILE_SIZE > progress.txt
# Run crawler 2 hours at a time for increased efficiency
while [ $FILE_SIZE -gt 0 ]
do 
    timeout -s SIGINT 7200 python collection/load_webpages_threaded.py requests 30 domains_left.txt run_crawler_raw_results $SPEED &> run_crawler_summary/progress.clog
    python get_domains_left.py
    FILE_SIZE="`cat domains_left.txt | wc -l`"
    echo "Next Input: "$FILE_SIZE >> progress.txt
done

# Get the labels of our the crawled files
sleep 60
python summarize/summarize_csv.py run_crawler_raw_results &> run_crawler_summary/progress.sclog
tar -zcvf raw_results.tar.gz run_crawler_raw_results
rm -rf run_crawler_raw_results
