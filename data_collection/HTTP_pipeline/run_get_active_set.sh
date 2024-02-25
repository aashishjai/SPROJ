python get_active_set.py
mv active_doms.txt get_ips/step1_resolve_here
cd get_ips
bash run_bind_server.sh
cd ..
awk '{print $1}' active_set.txt > active_doms.txt
awk '{print $2}' active_set.txt > active_ips.txt
awk -F "," '{print $1}' active_ips.txt > active_ip.txt
paste -d " " active_doms.txt active_ip.txt > active_set.txt 
rm active_ip.txt active_doms.txt active_ips.txt