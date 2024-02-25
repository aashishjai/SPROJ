VP_name=$1
COOL_DOWN=$2
SPEED=$3
INPUT_LIST=$4
echo "Starting step 2 - running crawl to resolved domains"

mkdir run1
mkdir run2
mkdir run3

echo "Starting run 1" > progress_logs.txt
date >> progress_logs.txt
# Get the blocked domains three times to make sure transient blocking is left behind
cd crawler_script
cat good_domains.txt >> resolved_domains.txt
bash run.sh $SPEED $INPUT_LIST
cd ..

# Move from crawler folder to run1 folder
mv crawler_script/resolved_domains.txt run1/resolved_domains.txt
mv crawler_script/http_blocked_doms.txt run1/http_blocked_doms.txt
mv crawler_script/http_no_resp_doms.txt run1/http_no_resp_doms.txt
mv crawler_script/http_non_blocked_doms.txt run1/http_non_blocked_doms.txt
mv crawler_script/run_crawler_raw_resultsall.csv run1/run_crawler_raw_resultsall.csv
mv crawler_script/raw_results.tar.gz run1/raw_results.tar.gz

# Copy relevant domains from run1 to crawler_script folder for rerun
cat run1/http_blocked_doms.txt | awk -F' ' '{print$1}' > crawler_script/resolved_domains.txt
cat run1/http_no_resp_doms.txt >> crawler_script/resolved_domains.txt

echo "Run 1 completed" >> progress_logs.txt
date >> progress_logs.txt
sleep $COOL_DOWN

echo "Starting run 2" >> progress_logs.txt
date >> progress_logs.txt

cd crawler_script
bash run.sh $SPEED
cd ..

# Move from crawler folder to run2 folder
mv crawler_script/resolved_domains.txt run2/resolved_domains.txt
mv crawler_script/http_blocked_doms.txt run2/http_blocked_doms.txt
mv crawler_script/http_no_resp_doms.txt run2/http_no_resp_doms.txt
mv crawler_script/http_non_blocked_doms.txt run2/http_non_blocked_doms.txt
mv crawler_script/run_crawler_raw_resultsall.csv run2/run_crawler_raw_resultsall.csv
mv crawler_script/raw_results.tar.gz run2/raw_results.tar.gz


# Copy relevant domains from run2 to crawler_script folder for rerun
cat run2/http_blocked_doms.txt | awk -F' ' '{print$1}' > crawler_script/resolved_domains.txt
cat run2/http_no_resp_doms.txt >> crawler_script/resolved_domains.txt

echo "Run 2 completed" >> progress_logs.txt
date >> progress_logs.txt
sleep $COOL_DOWN

echo "Starting run 3" >> progress_logs.txt
date >> progress_logs.txt

cd crawler_script
bash run.sh $SPEED
cd ..

# Move from crawler folder to run3 folder
mv crawler_script/resolved_domains.txt run3/resolved_domains.txt
mv crawler_script/http_blocked_doms.txt run3/http_blocked_doms.txt
mv crawler_script/http_no_resp_doms.txt run3/http_no_resp_doms.txt
mv crawler_script/http_non_blocked_doms.txt run3/http_non_blocked_doms.txt
mv crawler_script/run_crawler_raw_resultsall.csv run3/run_crawler_raw_resultsall.csv
mv crawler_script/raw_results.tar.gz run3/raw_results.tar.gz


echo "Run 3 completed" >> progress_logs.txt
echo data >> progress_logs.txt

BLOCKED_NAME="../"$VP_name"_http_blocked_doms.txt"
NO_RESP_NAME="../"$VP_name"_http_no_resp_doms.txt"
cp run3/http_blocked_doms.txt $BLOCKED_NAME
cp run3/http_no_resp_doms.txt $NO_RESP_NAME
cp run1/http_non_blocked_doms.txt ../http_non_blocked_doms.txt
