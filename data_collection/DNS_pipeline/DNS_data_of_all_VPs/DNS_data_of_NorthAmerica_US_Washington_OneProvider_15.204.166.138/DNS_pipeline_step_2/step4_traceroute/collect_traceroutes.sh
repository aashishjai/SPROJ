RETRIES=$1
TIMEOUT=$2
python collect_traceroute.py blocked_domains_with_ns.txt $RETRIES $TIMEOUT
python get_error_doms.py
python collect_traceroute_v2.py error_doms_with_ns.txt
