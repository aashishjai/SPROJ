import glob
import os
import time
import sys
sys.path.insert(1, '../')
import config as config  # NOQA

def set_up_configrations(vp_ip, vp_name, SSH_KEY_PATH, port, resolver_ip):
    '''
    This carries out all the necessary system configurations required to run the HTTP Pipeline
    '''
    print("Starting system-wide configurations on VP whose name is:", vp_name)
    os.system("""ssh -p """+port+""" -i """+SSH_KEY_PATH+""" root@""" + vp_ip + """ \
              "sed -ie 's/nameserver.*/nameserver """ + resolver_ip + """/' /etc/resolv.conf;" """)


# sed -ie 's/nameserver.*/nameserver 127.0.0.1/' /etc/resolv.conf

def transfer_bundle_and_get_resolved_domains(vp_ip, vp_name, bundle_name, main_dir, SSH_KEY_PATH, port, resolver_ip):
    '''
    This function is used to send the zipped HTTP bundle to the remote machines to run the required
    experiment. After the bundle is sent, we unzip it and run the command to get the resolve domains
    Please note we first delete pre existing bundle data with rm -rf command. This is to ensure that
    when script starts we always have the data which is obtained by running script. without rm -rf,
    its possible that script gets struck and we end up thinking that old data was collected by the
    script we ran.
    '''
    print("Starting data collection for VP whose name is:", vp_name)
    os.system("""ssh -p """+port+""" -i """+SSH_KEY_PATH+""" root@""" + vp_ip + """ \
              mkdir -p """ + main_dir + """; """)

    # Transferring bundle to VP (change directory here)
    os.system("scp -P " + port + " -i " + SSH_KEY_PATH + " -r ./" + bundle_name + " root@"
              + vp_ip + ":~/" + main_dir)

    # Here we are unzipping the bundles on remote machine before starting run.sh.
    os.system("""ssh -p """ + port + """ -i """ + SSH_KEY_PATH + """ root@""" + vp_ip + """ "screen -m -d bash -c 'echo "Bind server is about to start!!";\
        cd """ + main_dir + """;\
        rm -rf """ + bundle_name[:-4] + """;\
        sleep 10;\
        unzip """ + bundle_name+"""; \
        cd """ + bundle_name[:-4]+""";\
        bash get_resolved_domains.sh """+vp_name+" "+resolver_ip+""";'" """)


def transfer_back_resolved_domains(vp_ip, vp_name, bundle_name, main_dir, SSH_KEY_PATH, port):
    '''
    This function transfers the list of resolved domains from a given vantage point to the
    machine controlling the experiments
    '''

    print("Getting resolved domains for vp whose name is:", vp_name)

    # Get the domains that were resolved from this VP
    os.system("scp -P " + port + " -i " + SSH_KEY_PATH + " -r root@" + vp_ip + ":~/" + main_dir
              + bundle_name[:-4] + "/" + vp_name + "_resolved_domains.txt " + config.PATH_TO_RESOLVED_DOMAINS_HTTP)


def get_intersection(dir, filename):
    '''
    This takes the intersection of all the resolved domains. The only domains that will
    form a part of the candidate set are the domains that can be resolved in each and
    every single one of the vantage points
    '''
    all_files = glob.glob(dir+'/*_'+filename)
    all_dom_lists = []
    for file in all_files:
        doms = []
        with open(file, 'r') as f:
            doms = [dom.strip() for dom in f]

        all_dom_lists.append(doms)

    intersection = set(all_dom_lists[0])
    for dom_list in all_dom_lists:
        intersection.intersection_update(dom_list)

    with open('resolved_domains.txt', 'w') as f:
        for dom in intersection:
            f.write(dom+'\n')


def transfer_resolved_domains_get_blocked_domains(vp_ip, vp_name, bundle_name, main_dir, SSH_KEY_PATH, port):
    '''
    The domains resolved from all vantage points are transferred to a vantage point "vp_name" and
    we start to crawl these domains. After this step, we have a list of domains that fall into one of
    three categories, "blocked", "no_response" and "unblocked".
    '''
    print("Starting crawler on resolve domains on vp whose name is:", vp_name)

    # Transferring resolved to VP (change directory here)
    os.system("scp -P " + port + " -i " + SSH_KEY_PATH + " -r ./resolved_domains.txt root@"
              + vp_ip + ":~/" + main_dir + bundle_name[:-4] + "/step_2/crawler_script/")

    # Running the crawler to get the blocked domains in each VP
    os.system("""ssh -p """ + port + """ -i """ + SSH_KEY_PATH + """ root@""" + vp_ip + """ "screen -m -d bash -c 'echo "Get ready! Crawler is about to start!";\
        cd """ + main_dir + """;\
        cd """ + bundle_name[:-4]+"""/step_2/;\
        bash get_blocked_domains.sh """+vp_name+" "+config.COOL_DOWN+" "+str(config.CHUNK_SIZE)+""" resolved_domains.txt;'" """)


def transfer_back_blocked_domains(vp_ip, vp_name, bundle_name, main_dir, SSH_KEY_PATH, port):
    '''
    This function transfers back the blocked domains and the domains that gave no response
    the given vantage point.
    '''
    print("Getting the blocked domains for VP whose name is:", vp_name)

    # Get the domains whose HTTP response showed they were blocked from this VP
    os.system("scp -P " + port + " -i " + SSH_KEY_PATH + " -r root@" + vp_ip + ":~/" + main_dir
              + bundle_name[:-4] + "/" + vp_name + "_http_blocked_doms.txt "+config.PATH_TO_BLOCKED_DOMAINS)

    # Get the domains that did not respond at all from this VP
    os.system("scp -P " + port + " -i " + SSH_KEY_PATH + " -r root@" + vp_ip + ":~/" + main_dir
              + bundle_name[:-4] + "/" + vp_name + "_http_no_resp_doms.txt "+config.PATH_TO_UNRESPONSIVE_DOMAINS)


def get_candidate(dirs, filenames):
    '''
    This generates the "candidate set", the set of domains on which we run the traceroutes.
    From here onwards, all domains that did not respond, or the ones that are blocked, will both
    be referred to as "blocked". The candidate set is the set of all domains that are blocked in
    one VP and unblocked in at least one other VP.
    '''

    # Gets the domains that are blocked in one VP and store them in a dict
    # The key is the VP, the value is a list of domains that are blocked in that VP
    dom_dict = {}
    for directory, filename in zip(dirs, filenames):
        all_files = glob.glob(directory+'/*_'+filename)
        for file in all_files:
            vp_name = file[file.rfind('/')+1:file.find('_'+filename)]
            with open(file, 'r') as f:
                doms = [dom.strip().split(' ')[0] for dom in f]
            if vp_name in dom_dict:
                dom_dict[vp_name] += doms
            else:
                dom_dict[vp_name] = doms

    candidate_sets = {}
    for vp_name in dom_dict.keys():
        candidate_sets[vp_name] = set()

    # For each domain, check if this domain is resolved anywhere else
    for curr_VP, curr_doms in dom_dict.items():
        for dom in curr_doms:
            for other_VP, other_doms in dom_dict.items():
                if curr_VP != other_VP:
                    if dom not in other_doms:
                        candidate_sets[curr_VP].add(dom)

    return candidate_sets


def transfer_candidate_domains(vp_ip, vp_name, bundle_name, main_dir, SSH_KEY_PATH, port):
    '''
    This functions transfers the active set to the target vantage point
    It then runs the custom resolver
    '''

    print("Transferring active set to test VP whose name is:", vp_name)

    os.system("scp -P " + port + " -i " + SSH_KEY_PATH + " " + config.PATH_TO_CANDIDATES_HTTP+"/"+vp_name+"_candidate_set.txt root@" +
              vp_ip + ":~/" + main_dir + bundle_name[:-4] + "/get_ips/step1_resolve_here/active_doms.txt")


def resolve_candidate_set(vp_ip, vp_name, bundle_name, main_dir, SSH_KEY_PATH, port, resolver_ip):
    '''
        This function gets the IP address for all the candidate set domains.
        This is only run in the "Test" country to make sure that the
                destination IPs are the same for each vantage point
    '''
    # Running the crawler to get the blocked domains in each VP
    print("Resolving active set on test VP whose name is:", vp_name)

    os.system("""ssh -p """ + port + """ -i """ + SSH_KEY_PATH + """ root@""" + vp_ip + """ "screen -m -d bash -c 'echo "Resolving Domains using bind server!";\
        cd """ + main_dir + """;\
        cd """ + bundle_name[:-4]+"""/get_ips/;\
        bash run_bind_server.sh """+resolver_ip+""";'" """)


def transfer_back_candidate_IPs(vp_ip, vp_name, bundle_name, main_dir, SSH_KEY_PATH, port):

    print("Transferring back active set IPs on test VP whose name is:", vp_name)

    # Get the IPs from the active set that was resolved previously
    os.system("scp -P " + port + " -i " + SSH_KEY_PATH + " -r root@" + vp_ip + ":~/" + main_dir
              + bundle_name[:-4] + "/active_set_IPs.txt ./"+config.PATH_TO_CANDIDATE_IPS_HTTP+'/'+vp_name+'_candidate_set_IPs.txt')


def generate_full_candidate_set(filename):
    files = glob.glob(config.PATH_TO_CANDIDATE_IPS_HTTP+'/*_'+filename)
    full_set = set()
    for file in files:
        with open(file, 'r') as f:
            for line in f:
                dom = line.split(' ')[0]
                ip = line.split(' ')[1].split(',')[0]
                full_line = dom + ' ' + ip
                full_set.add(full_line)

    return full_set


def transfer_candidate_set_run_traceroutes(vp_ip, vp_name, bundle_name, main_dir, SSH_KEY_PATH, port):
    '''
    This will transfer the "candidate set" to the vantage point, a text file of domains and
    their server IPs, for traceroutes to be run on them
    '''
    print("Transferring active set IP and running traceroutes on VP whose name is:", vp_name)

    # Transfer active set into all vantage points
    os.system("scp -P " + port + " -i " + SSH_KEY_PATH + " ./candidate_set_IPs.txt root@" +
              vp_ip + ":~/" + main_dir + bundle_name[:-4] + "/step_3_scamper/MDA_traceroute_input.txt")

    os.system("""ssh -p """ + port + """ -i """ + SSH_KEY_PATH + """ root@""" + vp_ip + """ "screen -m -d bash -c 'echo "Resolving Domains using bind server!";\
        cd """ + main_dir + """;\
        cd """ + bundle_name[:-4]+"""/step_3_scamper/;\
        bash run.sh;'" """)

def transfer_data_back(vp_ip, vp_name, bundle_name, main_dir, SSH_KEY_PATH, port):
    '''
    After the traceroutes have completed, this will send the folder containing the results back
    to this host machine
    '''
    print("Transferring the final data back to this machine")
    os.system("""ssh -p """ + port + """ -i """ + SSH_KEY_PATH + """ root@""" + vp_ip + """ "screen -m -d bash -c 'echo "Transferring data back!";\
        cd """ + main_dir + """;\
        cd """ + bundle_name[:-4]+""";\
        mkdir -v results/
        cd step_3_scamper/http-scamper_v0.9.3/scamper/custom-files/;\
        cp -r ./* ../../../../results/;\
        cd ../../../../;\
        cd step_2/run1/;\
        cp http_no_resp_doms.txt http_blocked_doms.txt run_crawler_raw_resultsall.csv ../../results/;\
        cd ../../results;\
        zip -r """+vp_name+"""_output.zip ./* ;'" """)

    print("Waiting 30 seconds while zip file is created")
    time.sleep(30)

    os.system("scp -P " + port + " -i " + SSH_KEY_PATH + " -r root@" + vp_ip + ":~/" + main_dir
              + bundle_name[:-4] + "/results/" + vp_name + """_output.zip ./"""+config.PATH_TO_DATA_COLLECTION_HTTP)


def get_summary(vp_ip, vp_name, bundle_name, main_dir, SSH_KEY_PATH, port):
    print("Getting summary")
    os.system("""ssh -p """ + port + """ -i """ + SSH_KEY_PATH + """ root@""" + vp_ip + """ "screen -m -d bash -c 'echo "Gathering summary and sending back!";\
        cd """ + main_dir + """;\
        cd """ + bundle_name[:-4]+""";\
        cat """ + vp_name + """_resolved_domains.txt | wc -l > stats;\
        cat step_2/run1/http_blocked_doms.txt | wc -l >> stats;\
        cat step_2/run1/http_no_resp_doms.txt | wc -l >> stats;\
        cat step_2/run2/http_blocked_doms.txt | wc -l >> stats;\
        cat step_2/run2/http_no_resp_doms.txt | wc -l >> stats;\
        cat step_2/run2/http_no_resp_doms.txt | wc -l >> stats;\
        cat """ + vp_name + """_http_blocked_doms.txt | wc -l >> stats;\
        cat """ + vp_name + """_http_no_resp_doms.txt | wc -l >> stats;\
        cat active_set_IPs.txt | wc -l >> stats;\'" 
        cat step_3_scamper/status.txt >> stats;\'" """)

    os.system("scp -P " + port + " -i " + SSH_KEY_PATH + " -r root@" + vp_ip + ":~/" + main_dir
              + bundle_name[:-4] + "/stats " + config.PATH_TO_HTTP_SUMMARIES)


    
if __name__ == "__main__":
    directories_to_store_data = [config.PATH_TO_RESOLVED_DOMAINS_HTTP, config.PATH_TO_BLOCKED_DOMAINS,
                                 config.PATH_TO_UNRESPONSIVE_DOMAINS, config.PATH_TO_DATA_COLLECTION_HTTP,
                                 config.PATH_TO_CANDIDATES_HTTP, config.PATH_TO_CANDIDATE_IPS_HTTP]
    for one_dir in directories_to_store_data:
        if one_dir[2:] not in os.listdir("."):
            os.system("mkdir "+one_dir)

    vantage_array = config.VANTAGES
    bundle_name = config.HTTP_BUNDLE_NAME+".zip"
    main_dir = config.MAIN_DIRECTORY

    mode = int(sys.argv[1])

    if mode == 3:
        get_intersection(config.PATH_TO_RESOLVED_DOMAINS_HTTP,
                         "resolved_domains.txt")

    for one_vp in vantage_array:
        if one_vp != "":
            one_vp_array = one_vp.split(",")
            vp_ip = one_vp_array[-1:][0]
            vp_type = one_vp_array[-2]

            vp_name = "_".join(one_vp_array)
            bundle_name = config.HTTP_BUNDLE_NAME+".zip"
            main_dir = config.MAIN_DIRECTORY

            if mode == 0:
                set_up_configrations(
                    vp_ip, vp_name, config.SERVER_RSA_KEY_PATHS[vp_type], config.SERVER_PORTS[vp_type], config.DNS_RESOLVERS[vp_type])
            elif mode == 1:
                transfer_bundle_and_get_resolved_domains(
                    vp_ip, vp_name, bundle_name, main_dir, config.SERVER_RSA_KEY_PATHS[vp_type], config.SERVER_PORTS[vp_type], config.DNS_RESOLVERS[vp_type])
            elif mode == 2:
                transfer_back_resolved_domains(
                    vp_ip, vp_name, bundle_name, main_dir, config.SERVER_RSA_KEY_PATHS[vp_type], config.SERVER_PORTS[vp_type])
            elif mode == 4:
                transfer_resolved_domains_get_blocked_domains(
                    vp_ip, vp_name, bundle_name, main_dir, config.SERVER_RSA_KEY_PATHS[vp_type], config.SERVER_PORTS[vp_type])
            elif mode == 5:
                transfer_back_blocked_domains(
                    vp_ip, vp_name, bundle_name, main_dir, config.SERVER_RSA_KEY_PATHS[vp_type], config.SERVER_PORTS[vp_type])
            elif mode == 6:
                transfer_candidate_domains(
                    vp_ip, vp_name, bundle_name, main_dir, config.SERVER_RSA_KEY_PATHS[vp_type], config.SERVER_PORTS[vp_type])
                resolve_candidate_set(
                    vp_ip, vp_name, bundle_name, main_dir, config.SERVER_RSA_KEY_PATHS[vp_type], config.SERVER_PORTS[vp_type], config.DNS_RESOLVERS[vp_type])
            elif mode == 7:
                transfer_back_candidate_IPs(vp_ip, vp_name, bundle_name,
                                            main_dir, config.SERVER_RSA_KEY_PATHS[vp_type], config.SERVER_PORTS[vp_type])
            elif mode == 8:
                transfer_candidate_set_run_traceroutes(
                    vp_ip, vp_name, bundle_name, main_dir, config.SERVER_RSA_KEY_PATHS[vp_type], config.SERVER_PORTS[vp_type])
            elif mode == 9:
                transfer_data_back(
                    vp_ip, vp_name, bundle_name, main_dir, config.SERVER_RSA_KEY_PATHS[vp_type], config.SERVER_PORTS[vp_type])
    if mode == 5:
        candidate_sets = get_candidate([config.PATH_TO_BLOCKED_DOMAINS, config.PATH_TO_UNRESPONSIVE_DOMAINS],
                                       ['http_blocked_doms.txt', 'http_no_resp_doms.txt'])

        for vp_name, candidate_set in candidate_sets.items():
            with open(config.PATH_TO_CANDIDATES_HTTP+'/'+vp_name+'_candidate_set.txt', 'w') as f:
                for dom in candidate_set:
                    f.write(dom+'\n')

    if mode == 7:
        full_cand_set = generate_full_candidate_set('candidate_set_IPs.txt')
        with open('candidate_set_IPs.txt', 'w') as f:
            for candidate_ip in full_cand_set:
                f.write(candidate_ip.strip() + '\n')
