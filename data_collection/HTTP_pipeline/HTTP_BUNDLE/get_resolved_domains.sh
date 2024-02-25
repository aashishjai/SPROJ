VP_name=$1
RESOLVER=$2
echo "Getting resolved domains using bind server"
cd step_1
bash run_bind_server.sh $RESOLVER
cd ..
RESOLVED_NAME=$VP_name"_resolved_domains.txt"
awk '{print $1}' step_1/step1_resolve_here/resolved_domains.txt > $RESOLVED_NAME