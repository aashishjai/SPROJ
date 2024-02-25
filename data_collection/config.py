############################### GENERAL CONFIG ##############################
# The main directory after ~/ which will be used for the experiment on the server
MAIN_DIRECTORY = "three-run-debug/"

VANTAGES = [
    # "Asia,PK,Lahore,Nayatel,115.186.182.126",
    # "Asia,India,Mumbai,OneProvider,103.97.203.53",
    "NorthAmerica,US,Washington,OneProvider,15.204.166.135",
    # "Europe,Germany,Dusseldorf,OneProvider,89.163.131.83",
]

# The locations to the RSA keys on host machine for each vantage point
SERVER_RSA_KEY_PATHS = {

    # 'Cloud': '~/.ssh/stardust-lums',
    'OneProvider': '~/.ssh/id_rsa',
    # 'OneProvider': '~/.ssh/id_rsa_germany',
    # 'Host24': '~/.ssh/regionalism_key',
    # 'Institutional': '~/.ssh/root_key',
    # 'Germany1': '~/.ssh/heficed',

}

# The ports to connect to for each vantage point
SERVER_PORTS = {
    # 'Cloud': '22',
    # 'Nayatel': '22',
    'OneProvider': '22',
    # 'Institutional': '22',
    # 'Host24': '22',
    # 'Germany1': '22',
}

# The BIND Server is always running on 127.0.0.1
# If your server uses a private resolver, it could be hosted on different IP addresses
# Please check your vantage point to see on which port the local resolver is running on
DNS_RESOLVERS = {
    # 'Cloud': '127.0.0.1',
    'OneProvider': '8.8.8.8',
    # 'Institutional': '127.0.0.1',
    # 'Nayatel': '127.0.0.53',
    # 'Nayatel': '127.0.0.53', This is the local resolver
    # 'Host24': '127.0.0.1',
}

# IP Address of spoofing machine
SPOOFING_MACHINE_IP = '15.204.166.135'

# IP Address of spoofing machine
SPOOFING_MACHINE_PORT = '22'

# Path to RSA key of spoofing machine
SPOOFING_MACHINE_KEY_PATH = '~/.ssh/id_rsa'

# Name of RSA key of spoofing machine
# THIS SHOULD BE THE SAME AS THE ONE IN THE PATH ABOVE
SPOOFING_MACHINE_KEY = 'id_rsa'

##############################################################################
##############################################################################

############################### DNS CONFIG FILES ##############################
# Name of the DNS bundle
DNS_BUNDLE_NAME = "DNS_BUNDLE"

# Path to input domains
PATH_TO_INPUT_DOMAINS_DNS = "./sample_input_DNS.txt"

# Dir where all the resolved domains for each VP would be stored
PATH_TO_ACTIVE_DOMAINS = './active_domains_of_each_VP'

# Dir where all the blocked domains for each VP would be stored
PATH_TO_SERVER_SIDE_BLOCKED_CANDIDATES_DNS = './server_side_blocked_of_each_VP'

# Dir where summaries for checking progress of experiment would be stored
PATH_TO_DNS_SUMMARIES = './summary'

# Dir where data collected from each VP would be stored
PATH_TO_DATA_COLLECTION_DNS = './DNS_data_of_all_VPs'

# Number of retries for the DNS Simple traceroutes
DNS_RETRIES = str(3)

# Timeout value for the DNS Simple traceroutes 
# DNS_TIMEOUT = str(20)
DNS_TIMEOUT = str(40)

# Time to sleep after starting domain resolution
DOM_RESOLUTION_WAIT = 1000

# Time to sleep after starting DNS Traceroutes
DNS_TRACEROUTE_WAIT = 2160

# Time to sleep after starting MDA Traceroutes
MDA_TRACEROUTE_WAIT = 2160

# Time to sleep after starting path stitching command
PATH_STITCHING_WAIT = 2160
##############################################################################
##############################################################################

######################### INJECTION TESTCONFIG FILES #########################
# PATH_TO_INPUT_DOMAINS_INJECTION_TEST = "DNS_pipeline/DNS_data_of_all_VPs/\
# DNS_data_of_Asia_PK_Lahore_Nayatel_115.186.182.126/\
# DNS_pipeline_step_1/step1_resolve_here/resolved_domains.txt"

PATH_TO_INPUT_DOMAINS_INJECTION_TEST = "./DNS_pipeline/DNS_data_of_all_VPs/DNS_data_of_NorthAmerica_US_Washington_OneProvider_15.204.166.135/DNS_pipeline_step_1/step1_resolve_here/resolved_domains.txt"

TEST_VP_INDEX = 0 # changed from 1 to 0 and changed the path above

##############################################################################
##############################################################################

############################## HTTP CONFIG FILES #############################

# Name of the HTTP bundle
HTTP_BUNDLE_NAME = "HTTP_BUNDLE"

# Where the input file is stored, by default it would be in the "DNS_INJECTION_TEST" folder
PATH_TO_INPUT_DOMAINS_HTTP = './sample_input_HTTP_small.txt'

# This is where good domains are stored which are later used as a reference point to detect censorship
PATH_TO_GOOD_DOMAINS = './good_domains.txt'

# DIr where the resolved domains from each VP would be stored
PATH_TO_RESOLVED_DOMAINS_HTTP = './all_resolved'

# Dir where all the blocked domains of each VP would be stored
PATH_TO_BLOCKED_DOMAINS = './all_blocked'

# Dir where all the unresponsive domains of each VP would be stored
PATH_TO_UNRESPONSIVE_DOMAINS = './all_no_resp'

# Dir where each VP's candidate set would be stored
PATH_TO_CANDIDATES_HTTP = './all_candidate_sets'

# Dir where each VP's candidate set and their IPs would be stored
PATH_TO_CANDIDATE_IPS_HTTP = './all_candidate_set_IPs'

# Dir where summaries would be stored
PATH_TO_HTTP_SUMMARIES = './all_summaries'

# Dir where final data would be stored
PATH_TO_DATA_COLLECTION_HTTP = './TCP_HTTP_data'

# Time to wait in between each crawler run
COOL_DOWN = '60'

# Chunk size of the crawler, the greater the number, the slower the experiment.
# Minimum chunk size should not be less than 200
CHUNK_SIZE = 700

# Time to sleep after starting domain resolution
HTTP_DOM_RESOLUTION_WAIT = 5400

# Time to sleep when crawler is running
CRAWLER_WAIT = 5400

# Time to sleep when unresponsive domains are being resolved
RESOLVE_WAIT = 3600

# Time to wait when traceroutes are being run
HTTP_TRACEROUTE_WAIT = 28800

##############################################################################
##############################################################################
