import config as config
import sys
import os
import time
from datetime import datetime
import zipfile

def run_DNS(config):
    '''
            This function runs the entire DNS pipeline from start to finish
            It achieves this by calling another python file called 
            "run_DNS_pipeline.py", which is a file that is
            designed to run the experiment on multiple vantage points simultaneously.

            These vantage points are instances of Amazon EC2 or One Provider machines 
    '''
    os.system("cp "+config.PATH_TO_INPUT_DOMAINS_DNS +
              " ./DNS_pipeline/"+config.DNS_BUNDLE_NAME+"/DNS_pipeline_step_1/step1_resolve_here/input.txt")
    os.chdir('./DNS_pipeline/')
    os.system("zip -r "+config.DNS_BUNDLE_NAME+".zip "+config.DNS_BUNDLE_NAME)

    # To carry out all system-wide configurations for the data collection
    os.system("python run_DNS_pipeline.py 0")
    
    print("We are now periodically running all the steps for data collection")

    # The first step is to transfer all the DNS bundles to all the machines
    os.system("python run_DNS_pipeline.py 1")

    # After the bundles have been transferred, the domain resolution begins
    # This is done by a custom resolver which is run on each vantage point by the following command
    os.system("python run_DNS_pipeline.py 2")

    # Since the domain resolution is taking place via "screen" on the remote servers
    # There are to be a wait time before the next script can be run
    print("\nStep 1 has started - now waiting for",
          config.DOM_RESOLUTION_WAIT, "seconds")
    print("Time now:", datetime.now())
    time.sleep(config.DOM_RESOLUTION_WAIT)

    # Two things are happening in this command:
    #		The resolved domains are being transferred back to this machine, and a union is taken of these domains
    # 		This union is sent to all vantage points so server-side blocking candidates can be generated
    os.system("python run_DNS_pipeline.py 3")

    # The DNS-traceroutes are to be run on these candidate domains on each VP
    os.system("python run_DNS_pipeline.py 4")

    # DNS traceroutes also take a fair amount of time ro run. ~6-8 hours
    print("\nStep 2 has started - now waiting for",
          config.DNS_TRACEROUTE_WAIT, "seconds")
    print("Time now:", datetime.now())
    time.sleep(config.DNS_TRACEROUTE_WAIT)

    # The server-side blocked candidate domains are transferered back to this machine, and a union is taken of these domains
    # This union is sent back to all the vantage points so an MDA traceroute can be run on these machines for us to carry out the analysis
    os.system("python run_DNS_pipeline.py 5")

    # This command runs the MDA DNS Traceroutes
    os.system("python run_DNS_pipeline.py 6")

    # Wait until the MDA Traceroutes are complete, ~6-8 hours:
    print("\nStep 3 has started - now waiting for",
          config.MDA_TRACEROUTE_WAIT, "seconds")
    print("Time now:", datetime.now())
    time.sleep(config.MDA_TRACEROUTE_WAIT)

    # Transfer all the data back:
    print("Transferring all the data back")
    os.system("python run_DNS_pipeline.py 7")


def run_injection_test(config):
    
    # resolved_domains_path = config.PATH_TO_INPUT_DOMAINS_INJECTION_TEST
    # parts = resolved_domains_path.split("/")
    # print(parts)
    
    # # Assuming the structure is consistent and the zip file is in the same directory
    # zip_folder_name = os.path.splitext(parts[3])[0]
    # print(zip_folder_name)
    # zip_file_path_full = os.path.join("/".join(parts[:3]), zip_folder_name + ".zip")
    # print(zip_file_path_full)
    # # Unzipping the file
    # with zipfile.ZipFile(zip_file_path_full, 'r') as zip_ref:
    #     zip_ref.extractall(os.path.dirname(resolved_domains_path))

    input_domains = []
    os.system('cp '+config.PATH_TO_INPUT_DOMAINS_INJECTION_TEST+' DNS_injection_script/domains.txt')

    vantage_array = config.VANTAGES
    test_vp = vantage_array[config.TEST_VP_INDEX]

    test_vp_array = test_vp.split(",")
    test_vp_ip = test_vp_array[-1:][0]
    test_vp_type = test_vp_array[-2]

    SSH_KEY_PATH = config.SERVER_RSA_KEY_PATHS[test_vp_type]
    port = config.SERVER_PORTS[test_vp_type]

    USERNAME = "root"
    main_dir = config.MAIN_DIRECTORY

    os.system("zip -r DNS_injection_script.zip DNS_injection_script/")

    os.system("scp -P " + port + " -i " + SSH_KEY_PATH +
                " ./DNS_injection_script.zip root@"
                + test_vp_ip + ":~/" + main_dir)

    os.system("""ssh -p """+port+""" -i """+SSH_KEY_PATH+""" """+USERNAME+"""@""" + test_vp_ip + """ \
            "screen -m -d bash -c 'echo "Get ready! Injection Test is about to start!";\
            cd ~/""" + main_dir + """;\
            rm -rf DNS_injection_script/;\
            unzip DNS_injection_script.zip;\
            cd DNS_injection_script/;\
            bash run.sh'" """)


def get_injection_test_results(config):
    # vantage_array = vantages.read().split("\n")
    vantage_array = config.VANTAGES

    test_vp = vantage_array[config.TEST_VP_INDEX]

    test_vp_array = test_vp.split(",")
    test_vp_ip = test_vp_array[-1:][0]
    test_vp_type = test_vp_array[-2]

    SSH_KEY_PATH = config.SERVER_RSA_KEY_PATHS[test_vp_type]
    port = config.SERVER_PORTS[test_vp_type]

    main_dir = config.MAIN_DIRECTORY

    os.system("scp -P " + port + " -i " + SSH_KEY_PATH +
                " root@" + test_vp_ip + ":~/" + main_dir + "DNS_injection_script/" +
                "not_resolved.txt ./DNS_injection_script")

    domains = set()
    with open("DNS_injection_script/not_resolved.txt", 'r') as f:
        for line in f:
            domain = line.strip().split(" ")[0]
            if domain != "The":
                domains.add(domain)

    with open("not_DNS_injected.txt", 'w') as f:
        for dom in domains:
            f.write(dom+'\n')


def run_HTTP(config):
    '''
            This function runs the entire HTTP pipeline from start to finish
            It achieves this by calling another python file called 
            "run_HTTP_pipeline.py", which is a file that is
            designed to run the experiment on multiple vantage points simultaneously.

            These vantage points are instances of Amazon EC2 or One Provider machines 
    '''

    # Copy the input file to the appropriate place in the HTTP Bundle
    os.system("cp " + config.PATH_TO_INPUT_DOMAINS_HTTP +
              " HTTP_pipeline/"+config.HTTP_BUNDLE_NAME+"/step_1/step1_resolve_here/input.txt")

    os.system("cp " + config.PATH_TO_GOOD_DOMAINS +
              " HTTP_pipeline/"+config.HTTP_BUNDLE_NAME+"/step_2/crawler_script/good_domains.txt")

    os.chdir('./HTTP_pipeline/')

    # Zip the HTTP_BUNDLE so it can be sent over SCP
    os.system("zip -r "+config.HTTP_BUNDLE_NAME+".zip "+config.HTTP_BUNDLE_NAME)

    print("We are now periodically running all the steps for data collection")
    
    # This does the system configurations for all the VPs
    os.system("python run_HTTP_pipeline.py 0")

    # This command will transfer the HTTP bundle to the vantage points
    # After unzipping the bundle, it also starts the domain resolution
    os.system("python run_HTTP_pipeline.py 1")

    # Wait till the domain resolution is complete
    os.system(f"echo waiting for {config.HTTP_DOM_RESOLUTION_WAIT}")
    time.sleep(config.HTTP_DOM_RESOLUTION_WAIT)

    # Transfers the resolved domains back to the host machine
    os.system("python run_HTTP_pipeline.py 2")

    # Gets the intersection of the domains resolved from each vantage point
    # This ensures only the domains resolved everywhere are checked in this pipeline
    os.system("python run_HTTP_pipeline.py 3")

    # Transfer the resolved domains to each VP and start the crawler
    os.system("python run_HTTP_pipeline.py 4")

    # Wait till crawler has run
    os.system(f"echo waiting for {config.CRAWLER_WAIT}")
    time.sleep(config.CRAWLER_WAIT)

    # Transfer back the Blocked and the Unresponsive domains to host machine
    # This also generates the candidate set and transfers it too all the VPs
    os.system("python run_HTTP_pipeline.py 5")

    # This resolves the IPs from the candidate set ONLY in the test vantage point
    os.system("python run_HTTP_pipeline.py 6")

    # Wait till domain resolution is complete
    os.system(f"echo waiting for {config.RESOLVE_WAIT}")
    time.sleep(config.RESOLVE_WAIT)

    # This function transfers the domains and IPs from the test vantage point
    # to the host machine
    os.system("python run_HTTP_pipeline.py 7")

    # Transfer the candidate set to each VP and run the traceroutes
    os.system("python run_HTTP_pipeline.py 8")
    
    # Wait until the traceroutes have completed
    os.system(f"echo waiting for {config.HTTP_TRACEROUTE_WAIT}")
    time.sleep(config.HTTP_TRACEROUTE_WAIT)
    
    # Transfer result back to host machine
    os.system("python run_HTTP_pipeline.py 9")

if __name__ == '__main__':
    MODE = sys.argv[1]

    if MODE == "DNS":
        print("Calling run_DNS")
        run_DNS(config)
    elif MODE == "HTTP":
        print("Calling run_HTTP")
        run_HTTP(config)
    elif MODE == "injection_test":
        print("Calling run_injection_test")
        run_injection_test(config)
    elif MODE == "injection_test_result":
        get_injection_test_results(config)
    else:
        print("================= ERROR =================\n")
        print("You haven't specified which pipeline to run")
        print("You can use the following arguments:")
        print("\t\'DNS\' to run the DNS Pipeline")
        print("\t\'HTTP\' to run the HTTP Pipeline")
        print("\t\'injection_test\' to run the DNS Injection Test")
        print("\t\'injection_test_result\' to get results from the DNS Injection Test")
