python get_cdns.py TCP_HTTP_data/Asia_PK_Lahore_Nayatel_58.65.173.14_output/resolved.txt
python combine_cdn_doms.py

python combine_mda_files.py dns_outputs/
python combine_mda_files.py tcp_http_outputs/

python dns_find_lris.py DNS_data_of_all_VPs/DNS_data_of_Asia_PK_Lahore_Nayatel_58.65.173.14
python http_find_lris.py tcp TCP_HTTP_data/Asia_PK_Lahore_Nayatel_58.65.173.14_output/ Asia_PK_Lahore_Nayatel_58.65.173.14_results/tcp_http_results

python dns_get_distances.py Asia_PK_Lahore_Nayatel_58.65.173.14_results/dns_results
python http_get_distances_test.py tcp Asia_PK_Lahore_Nayatel_58.65.173.14_results/tcp_http_results tcp_http_outputs/full_mda_traces.json
python http_get_distances_control.py tcp Asia_PK_Lahore_Nayatel_58.65.173.14_results/tcp_http_results tcp_http_outputs/full_mda_traces.json

python compile_results.py TCP_HTTP_DATA/Asia_PK_Lahore_Nayatel_58.65.173.14_output/ Asia_PK_Lahore_Nayatel_58.65.173.14_results/