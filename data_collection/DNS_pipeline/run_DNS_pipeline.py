import os
import time
import sys
sys.path.insert(1, '../')
import config as config


def set_up_configrations(vp_ip, vp_name, SSH_KEY_PATH, port, resolver_ip):
    # Configure VP to run the DNS pipeline.
    print("Starting system-wide configurations on VP named ", vp_name)
    print("Starting pipeline 0 got stuff: ", vp_ip, vp_name, SSH_KEY_PATH, port, resolver_ip)
    os.system(
        """ssh -p """ +
        port +
        """ -i """ +
        SSH_KEY_PATH +
        """ root@""" +
        vp_ip +
        """ \
              "sed -ie 's/nameserver.*/nameserver """ +
        resolver_ip +
        """/' /etc/resolv.conf;" """)


def transfer_bundle_to_all_machines(
        vp_ip,
        vp_bundle_name,
        main_dir,
        SSH_KEY_PATH,
        USERNAME,
        vp_name,
        port):

    print("Starting data transfer for VP named ", vp_name)

    # Transfer bundle to relevant EC2 machines and clean old directories.
    os.system(
        """ssh -p """ +
        port +
        """ -i """ +
        SSH_KEY_PATH +
        """ """ +
        USERNAME +
        """@""" +
        vp_ip +
        """ \
	       	  mkdir -p """ +
        main_dir +
        """; """)

    os.system(
        "scp -P " +
        port +
        " -i " +
        SSH_KEY_PATH +
        " -r " +
        vp_bundle_name +
        " " +
        USERNAME +
        "@" +
        vp_ip +
        ":~/" +
        main_dir)

    # Unzip the bundles on remote machines.
    os.system("""ssh -p """ + port + """ -i """ + SSH_KEY_PATH +
              """ """ + USERNAME + """@""" + vp_ip + """ \
		  "screen -m -d bash -c 'echo "Get ready! Crawler is about to start!";\
          cd """ + main_dir + """;\
		  rm -rf """ + vp_bundle_name[:-4] + """;\
		  unzip """ + vp_bundle_name + """;\
          echo """ + vp_country + """ > ~/country.txt;'" """)


def start_crawler_on_all_machines(
        vp_ip,
        vp_bundle_name,
        main_dir,
        SSH_KEY_PATH,
        USERNAME,
        vp_name,
        port,
        vp_type):

    print(
        "Starting process of resolving domain through BIND server for VP named ",
        vp_name)

    '''
	Here we are unzipping the bundles on remote machine before starting "run.sh". Please note that we first
	delete pre-existing bundle data with "rm -rf" command. This is to ensure that when the script starts,
	we always have the new data.
	'''

    os.system("""ssh -p """ + port + """ -i """ + SSH_KEY_PATH +
              """ """ + USERNAME + """@""" + vp_ip + """ \
		  "screen -m -d bash -c 'echo "Get ready! Crawler is about to start!";\
		  cd ~/""" + main_dir + vp_bundle_name[:-4] + """/DNS_pipeline_step_1/;\
		  bash resolve_domains.sh """ + config.DNS_RESOLVERS[vp_type] + """;'" """)


def get_active_domain_set(
        vp_ip,
        vp_bundle_name,
        main_dir,
        SSH_KEY_PATH,
        USERNAME,
        vp_name,
        port):

    print("Getting active set for VP named ", vp_name)

    os.system("scp -P " +
              port +
              " -i " +
              SSH_KEY_PATH +
              " " +
              USERNAME +
              "@" +
              vp_ip +
              ":~/" +
              main_dir +
              vp_bundle_name[:-
                             4] +
              "/DNS_pipeline_step_1/step1_resolve_here/resolved_domains.txt " +
              config.PATH_TO_ACTIVE_DOMAINS +
              "/")

    os.system(
        "cat " +
        config.PATH_TO_ACTIVE_DOMAINS +
        "/resolved_domains.txt > " +
        config.PATH_TO_ACTIVE_DOMAINS +
        "/" +
        vp_name +
        "_active_set")
    os.system(
        "rm -rf " +
        config.PATH_TO_ACTIVE_DOMAINS +
        "/resolved_domains.txt")


def return_active_domain_set(
        vp_ip,
        vp_bundle_name,
        main_dir,
        SSH_KEY_PATH,
        USERNAME,
        vp_name,
        port):

    print("Transfering active set back to VP named ", vp_name)

    os.system("scp -P " +
              port +
              " -i " +
              SSH_KEY_PATH +
              " -r " +
              config.PATH_TO_ACTIVE_DOMAINS +
              "/active_set.txt " +
              USERNAME +
              "@" +
              vp_ip +
              ":~/" +
              main_dir +
              vp_bundle_name[:-
                             4] +
              "/DNS_pipeline_step_1/step1_resolve_here/")


def start_DNS_traceroute_spoofing_check(
        vp_ip,
        vp_bundle_name,
        main_dir,
        SSH_KEY_PATH,
        USERNAME,
        vp_name,
        port):

    print("Starting DNS traceroute for VP named ", vp_name)

    '''
	Here we are starting the DNS traceroute on server_side_blocked set.
	'''
    os.system("""ssh -p """ +
              port +
              """ -i """ +
              SSH_KEY_PATH +
              """ """ +
              USERNAME +
              """@""" +
              vp_ip +
              """ \
          "screen -m -d bash -c 'echo "Get ready! Crawler is about to start!";\
          cd ~/""" +
              main_dir +
              vp_bundle_name[:-
                             4] +
              """/DNS_pipeline_step_1/;\
          bash run_traceroutes.sh """ +
              config.DNS_RETRIES +
              " " +
              config.DNS_TIMEOUT +
              """;'" """)


def get_server_side_blocked(
        vp_ip,
        vp_bundle_name,
        main_dir,
        SSH_KEY_PATH,
        USERNAME,
        vp_name,
        port):

    print("Getting server side blocked domains for VP named ", vp_name)

    os.system("scp -P " +
              port +
              " -i " +
              SSH_KEY_PATH +
              " " +
              USERNAME +
              "@" +
              vp_ip +
              ":~/" +
              main_dir +
              vp_bundle_name[:-
                             4] +
              "/DNS_pipeline_step_1/have_auth_no_ip_extended.common_three_runs.txt " +
              config.PATH_TO_SERVER_SIDE_BLOCKED_CANDIDATES_DNS +
              "/")

    os.system(
        "cat " +
        config.PATH_TO_SERVER_SIDE_BLOCKED_CANDIDATES_DNS +
        "/have_auth_no_ip_extended.common_three_runs.txt > " +
        config.PATH_TO_SERVER_SIDE_BLOCKED_CANDIDATES_DNS +
        "/" +
        vp_name +
        "_have_auth_no_ip_extended.common_three_runs.txt")


def return_server_side_blocked(
        vp_ip,
        vp_bundle_name,
        main_dir,
        SSH_KEY_PATH,
        USERNAME,
        vp_name,
        port):

    print("Returning server side blocked domains for VP named ", vp_name)

    os.system("scp -P " +
              port +
              " -i " +
              SSH_KEY_PATH +
              " -r " +
              config.PATH_TO_SERVER_SIDE_BLOCKED_CANDIDATES_DNS +
              "/have_auth_no_ip_extended.common_three_runs.txt " +
              USERNAME +
              "@" +
              vp_ip +
              ":~/" +
              main_dir +
              vp_bundle_name[:-
                             4] +
              "/DNS_pipeline_step_3/")


def start_MDA_DNS(
        vp_ip,
        vp_bundle_name,
        main_dir,
        SSH_KEY_PATH,
        USERNAME,
        vp_name,
        port):

    print("Starting MDA DNS for VP named ", vp_name)

    os.system("""ssh -p """ + port + """ -i """ + SSH_KEY_PATH +
              """ """ + USERNAME + """@""" + vp_ip + """ \
		  "screen -m -d bash -c 'echo "Get ready! Crawler is about to start!";\
		  cd ~/""" + main_dir + vp_bundle_name[:-4] + """/DNS_pipeline_step_3/;\
		  bash proximity.sh;'" """)

def zip_and_get_back_collected_data(
        vp_ip,
        vp_bundle_name,
        main_dir,
        SSH_KEY_PATH,
        USERNAME,
        vp_name,
        port):

    print(
        "Starting compression and data transfer back to local machine for VP named ",
        vp_name)

    os.system("""ssh -p """ + port + """ -i """ + SSH_KEY_PATH + """ """ + USERNAME + """@""" + vp_ip + """ \
		  "echo "Get ready! Crawler is about to start!";\
		  cd ~/""" + main_dir + vp_bundle_name[:-4] + """/;\
		  zip -r DNS_data_of_""" + vp_name +
              """.zip ./DNS_pipeline_step_1 ./DNS_pipeline_step_2/step4_traceroute ./DNS_pipeline_step_3" """)

    os.system("scp -P " +
              port +
              " -i " +
              SSH_KEY_PATH +
              " -r " +
              USERNAME +
              "@" +
              vp_ip +
              ":~/" +
              main_dir +
              vp_bundle_name[:-
                             4] +
              "/DNS_data_of_" +
              vp_name +
              ".zip " +
              config.PATH_TO_DATA_COLLECTION_DNS +
              "/")


def start_get_summary(
        vp_ip,
        vp_bundle_name,
        main_dir,
        SSH_KEY_PATH,
        USERNAME,
        vp_name,
        port):

    print("Getting summary for VP named ", vp_name)

    os.system(
        """ssh -p """ + port + """ -i """ + SSH_KEY_PATH + """ """ + USERNAME + """@""" + vp_ip + """ \
		  "screen -m -d bash -c 'cd ~/""" + main_dir + vp_bundle_name[:-4] + """/;\
		  rm -rf stats;\
		  echo """ + vp_name + """ >> stats;\
		  cat ./DNS_pipeline_step_1/step1_resolve_here/resolved_domains.txt | wc -l >> stats;\
		  cat ./DNS_pipeline_step_1/step1_resolve_here/blocked_domains.txt | wc -l >> stats;\
		  cat ./DNS_pipeline_step_1/have_auth_no_ip_extended.common_three_runs.txt | wc -l >> stats;\
		  ls ./DNS_pipeline_step_2/step4_traceroute/ | grep dnst | wc -l >> stats;\
		  cd DNS_pipeline_step_3/;\
		  bash remove_null_chr.sh;\
		  cd ..;\
		  cat ./DNS_pipeline_step_3/MDA_DNS_scamper_output_temp.txt | grep nodes | wc -l >> stats ;\
		  cat ./DNS_pipeline_step_3/process_parser/complete_stitched_paths/final_log | grep nodes | wc -l >> stats;\
		  dig +retry=5 +short myip.opendns.com @resolver1.opendns.com >> stats;'" """)

    time.sleep(25)

    os.system("scp -P " +
              port +
              " -i " +
              SSH_KEY_PATH +
              " " +
              USERNAME +
              "@" +
              vp_ip +
              ":~/" +
              main_dir +
              vp_bundle_name[:-
                             4] +
              "/stats " +
              config.PATH_TO_DNS_SUMMARIES +
              "/")

    os.system(
        " cat " +
        config.PATH_TO_DNS_SUMMARIES +
        "/stats | xargs | sed -e \'s/ /,/g\' > " +
        config.PATH_TO_DNS_SUMMARIES +
        "/" +
        vp_name +
        "_stats.txt")


if __name__ == "__main__":
    directories_to_store_data = [
        config.PATH_TO_ACTIVE_DOMAINS,
        config.PATH_TO_DATA_COLLECTION_DNS,
        config.PATH_TO_SERVER_SIDE_BLOCKED_CANDIDATES_DNS,
        config.PATH_TO_DNS_SUMMARIES]

    for one_dir in directories_to_store_data:
        if one_dir[2:] not in os.listdir("."):
            os.system("mkdir " + one_dir)

    vantage_array = config.VANTAGES

    main_dir = config.MAIN_DIRECTORY

    MODE = int(sys.argv[1])

    '''
	Mode 3, 5 and 9 get data from all VPs and store them in relevant directories. So, we need to clean directories with "rm -rf" command
	before we get the data for the current run. This is to ensure we do not end up using data collected from an old run.
	'''

    if MODE == 1:
        print("************************** Warning **************************")
        print("The mode you chose deletes old data with rm -rf. if you don't\n\
			   intend to delete old data, please kill the process with CTRL+C")
        print("**************************************************************")
        time.sleep(5)

    elif MODE == 3:
        os.system("rm -rf " + config.PATH_TO_ACTIVE_DOMAINS + "/**")

    elif MODE == 5:
        os.system(
            "rm -rf " +
            config.PATH_TO_SERVER_SIDE_BLOCKED_CANDIDATES_DNS +
            "/**")

    elif MODE == 8:
        os.system("rm -rf " + config.PATH_TO_DATA_COLLECTION_DNS + "/**")

    elif MODE == 9:
        os.system("rm -rf " + config.PATH_TO_DNS_SUMMARIES + "/**")

    for one_vp in vantage_array:
        if one_vp != "":
            one_vp_array = one_vp.split(",")
            vp_ip = one_vp_array[-1:][0]
            vp_name = "_".join(one_vp_array)
            vp_type = one_vp_array[-2]
            vp_country = one_vp_array[1]
            vp_bundle_name = config.DNS_BUNDLE_NAME + ".zip"

            '''
			As we use one key to SSH into EC2 machines and the other to SSH into One provider machines, we made two separate functions
			to start scripts in EC2 and One provider machines.
			'''

            print(config.SERVER_PORTS[vp_type])

            if MODE == 0:
                set_up_configrations(
                    vp_ip,
                    vp_name,
                    config.SERVER_RSA_KEY_PATHS[vp_type],
                    config.SERVER_PORTS[vp_type],
                    config.DNS_RESOLVERS[vp_type])

            elif MODE == 1:
                transfer_bundle_to_all_machines(
                    vp_ip,
                    vp_bundle_name,
                    main_dir,
                    config.SERVER_RSA_KEY_PATHS[vp_type],
                    "root",
                    vp_name,
                    config.SERVER_PORTS[vp_type])

            elif MODE == 2:
                start_crawler_on_all_machines(
                    vp_ip,
                    vp_bundle_name,
                    main_dir,
                    config.SERVER_RSA_KEY_PATHS[vp_type],
                    "root",
                    vp_name,
                    config.SERVER_PORTS[vp_type],
                    vp_type)

            elif MODE == 3:
                get_active_domain_set(
                    vp_ip,
                    vp_bundle_name,
                    main_dir,
                    config.SERVER_RSA_KEY_PATHS[vp_type],
                    "root",
                    vp_name,
                    config.SERVER_PORTS[vp_type])

            elif MODE == 4:
                start_DNS_traceroute_spoofing_check(
                    vp_ip,
                    vp_bundle_name,
                    main_dir,
                    config.SERVER_RSA_KEY_PATHS[vp_type],
                    "root",
                    vp_name,
                    config.SERVER_PORTS[vp_type])

            elif MODE == 5:
                get_server_side_blocked(
                    vp_ip,
                    vp_bundle_name,
                    main_dir,
                    config.SERVER_RSA_KEY_PATHS[vp_type],
                    "root",
                    vp_name,
                    config.SERVER_PORTS[vp_type])

            elif MODE == 6:
                start_MDA_DNS(
                    vp_ip,
                    vp_bundle_name,
                    main_dir,
                    config.SERVER_RSA_KEY_PATHS[vp_type],
                    "root",
                    vp_name,
                    config.SERVER_PORTS[vp_type])

            elif MODE == 7:
                zip_and_get_back_collected_data(
                    vp_ip,
                    vp_bundle_name,
                    main_dir,
                    config.SERVER_RSA_KEY_PATHS[vp_type],
                    "root",
                    vp_name,
                    config.SERVER_PORTS[vp_type])

            elif MODE == 8:
                start_get_summary(
                    vp_ip,
                    vp_bundle_name,
                    main_dir,
                    config.SERVER_RSA_KEY_PATHS[vp_type],
                    "root",
                    vp_name,
                    config.SERVER_PORTS[vp_type])

    '''
	Please note that the following commands are used to concatenate data collected from all VPs into one VP:
		i)   "find" lists down all relevant files.
		ii)  "xargs" concatenate files into one file with one '\n' between data of each file.
		iii) "sort" only keeps unique lines.
		iv)  "awk" removes extra spaces.
	'''

    if MODE == 3:
        os.system(
            "find " +
            config.PATH_TO_ACTIVE_DOMAINS +
            "/*_active_set* | xargs -I{} sh -c \"cat {}; echo \'\'\" | sort -u -k1,1 | awk \' {if($1!=\"\")print} \'> " +
            config.PATH_TO_ACTIVE_DOMAINS +
            "/active_set.txt")

    elif MODE == 5:
        os.system(
            "find " +
            config.PATH_TO_SERVER_SIDE_BLOCKED_CANDIDATES_DNS +
            "/*_have_auth* | xargs -I{} sh -c \"cat {}; echo \'\'\"   | sort -u -k2,2 | awk \' {if($1!=\"\")print} \'> " +
            config.PATH_TO_SERVER_SIDE_BLOCKED_CANDIDATES_DNS +
            "/have_auth_no_ip_extended.common_three_runs.txt")

    elif MODE == 8:
        os.system("rm -rf " + config.PATH_TO_DNS_SUMMARIES + "/stats.csv")
        os.system(
            "echo \"VP name,Resolved domains,Unresolved domains, Blocked domains,DNS traceroutes done ,MDA DNS done, Path stitched, Public IP of machine,Fake spoofed packets, Actual spoofed packets \" >> " +
            config.PATH_TO_DNS_SUMMARIES +
            "/stats.csv")
        os.system(
            "find " +
            config.PATH_TO_DNS_SUMMARIES +
            "/*_stats* | xargs -I{} sh -c \"cat {}; echo \'\'\" | sort -u -k1,1 | awk \' {if($1!=\"\")print} \'>> " +
            config.PATH_TO_DNS_SUMMARIES +
            "/stats.csv")
        os.system("rm -rf " + config.PATH_TO_DNS_SUMMARIES +
                  "/*.txt* " + config.PATH_TO_DNS_SUMMARIES + "/stats")

    '''
		The reason for having the second loop is that some commands have to perform two tasks. They have to collect data
		from all VPs initially in the first loop. Then they have to process that data and then distribute to
		all the VPs in second task. That's why we need second loop.
	'''

    for one_vp in vantage_array:
        if one_vp != "":
            one_vp_array = one_vp.split(",")
            vp_ip = one_vp_array[-1:][0]
            vp_name = "_".join(one_vp_array)
            vp_type = one_vp_array[-2]
            vp_country = one_vp_array[1]
            vp_bundle_name = config.DNS_BUNDLE_NAME + ".zip"

            if MODE == 3:
                return_active_domain_set(
                    vp_ip,
                    vp_bundle_name,
                    main_dir,
                    config.SERVER_RSA_KEY_PATHS[vp_type],
                    "root",
                    vp_name,
                    config.SERVER_PORTS[vp_type])

            elif MODE == 5:
                return_server_side_blocked(
                    vp_ip,
                    vp_bundle_name,
                    main_dir,
                    config.SERVER_RSA_KEY_PATHS[vp_type],
                    "root",
                    vp_name,
                    config.SERVER_PORTS[vp_type])
