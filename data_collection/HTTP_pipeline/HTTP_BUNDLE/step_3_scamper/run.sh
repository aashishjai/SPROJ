python make_candidate_input.py
cp MDA_traceroute_input.txt full_candidate_set.txt
head -n 250 ../http_non_blocked_doms.txt >> MDA_traceroute_input.txt

# Run simple traceroute on full candidate set
cat full_candidate_set.txt > ./http-scamper_v0.9.3/scamper/custom-files/HTTP-TCP-Traceroute/resolved.txt
echo "Simple Traceroute on Candidate Set Started" > status.txt
date >> status.txt
cd ./http-scamper_v0.9.3/scamper/custom-files/HTTP-TCP-Traceroute
echo "I am in the following directory"
pwd
date
bash run.sh
cd ../
cp -r HTTP-TCP-Traceroute full_candidate_traceroutes
echo 'First task done'
cd ../../../
echo "Simple Traceroute Finished" >> status.txt
date >> status.txt


# Run simple traceroute on VP candidate set
cat simple_traceroute_input.txt > ./http-scamper_v0.9.3/scamper/custom-files/HTTP-TCP-Traceroute/resolved.txt
echo "Simple Traceroute on VP Set Started" >> status.txt
date >> status.txt
cd ./http-scamper_v0.9.3/scamper/custom-files/HTTP-TCP-Traceroute
echo "I am in the following directory"
pwd
date
bash run.sh
echo 'Second task done'
cd ../../../../
echo "Simple Traceroute Finished" >> status.txt
date >> status.txt

# Run MDA traceroute on full candidate set
cat MDA_traceroute_input.txt > ./http-scamper_v0.9.3/scamper/custom-files/TCP-MDA/resolved.txt
cd ./http-scamper_v0.9.3/scamper/custom-files/TCP-MDA/
echo "MDA Traceroute Started" >> ../../../../status.txt
date >> ../../../../status.txt
bash run.sh
echo 'Third task done'
echo "MDA Traceroute Finished" >> ../../../../status.txt
date >> ../../../../status.txt
echo "Task complete"
date
