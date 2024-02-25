
# cp domains_ns.txt ./process_parser/
# cp MDA_DNS_tcpdump_logs.pcap ./process_parser/
echo "We are now going to extract pcap trace for each website from large pcap trace. Time below shows when this process began" > process_parser/progress_logs.txt
cd process_parser
date >> progress_logs.txt
python get_tashark_logs.py ../domains_ns.txt ../MDA_DNS_tcpdump_logs.pcap
date >> progress_logs.txt
echo "Time above shows when breakdown of large pcap finished. We have traces now. Time below shows start of path stitching process." >> progress_logs.txt
date >> progress_logs.txt
python parse_scamper_warts.py ../MDA_DNS_OUTPUT.warts ../
echo "Path stitching process finished!" >> progress_logs.txt
date >> progress_logs.txt
cd ../

