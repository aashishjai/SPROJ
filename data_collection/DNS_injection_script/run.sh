# this script needs to be run as sudo
# domains to check for DNS injection are to be placed in 'domains.txt'
# domains receiving false responses will be saved in 'censored_domains.txt'
# domains found affected by DNS injection will be saved in 'dns_injected_domains.txt '
echo "Installing required packages" >> custom_progress_logs.txt
sudo apt install inetutils-traceroute
pip install python-geoip
pip install python-geoip-geolite2
pip install python-geoip-python3
echo "********************************************************************" >> custom_progress_logs.txt

echo "Finding domains that receive false responses..."
sudo python false_response.py
echo "Affected domains are saved in 'false_resp_domains.txt"
echo "********************************************************************" >> custom_progress_logs.txt

echo "Finding border routers..." >> custom_progress_logs.txt
sudo python ./get_border_routers.py
echo "IPs for border routers are saved in 'border_routers.txt" >> custom_progress_logs.txt
echo "********************************************************************" >> custom_progress_logs.txt

echo "Resolving domains from border routers..." >> custom_progress_logs.txt
sudo python ./resolve_from_border.py
cat ./*_fail.txt > ./not_resolved.txt
rm ./*_fail.txt
cat ./*_success.txt > ./dns_injected_domains.txt
rm ./*_success.txt
echo "DNS Injection Test Complete." >> custom_progress_logs.txt
echo "Affected domains are saved in 'dns_injected_domains.txt '" >> custom_progress_logs.txt