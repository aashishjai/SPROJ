Documentation for HTTP-Traceroute Data Collection Pipeline

The code works by sending an *HTTP_BUNDLE* to all the vantage points to run the data collection on those vantage points and send the data back to the Host machine running the experiment. 

## Prerequisites and assumptions

- The code assumes that you have root access to the machine, since at many places we use a custom resolver to resolve domains, which requires root access
- Python version > 3.7 for the data collection
- The set-up scripts (the zip file in the previous directory) to be installed in each of the vantage points. These scripts set up a local resolver on the remote machine and install all the required packages

## Data Collection

#### Step 1

**Commands to run:** 

- `python run_DNS_pipeline.py 0`: Carries out system-wide configurations for the default DNS resolver
- `python run_DNS_pipeline.py 1`: Any previous data in the same folder is deleted. The HTTP Bundle is transferred to each VP and the resolver tries to resolve the input set of domains and creates the *resolved_domains.txt* files.

#### Step 2

**Commands to run:** 

- `python run_DNS_pipeline.py 2`: The resolved domains are transferred back to the host machine. If the text files are empty, or do not get transferred back, it means the resolution process has not been completed yet and we need to wait.
- `python run_DNS_pipeline.py 3`: This takes the intersection of all the resolved domains to make sure we only test domains that can be resolved from each vantage point.
- `python run_DNS_pipeline.py 4`: The set of resolved domains are transferred to each VP and a crawler is run on them. This generates a three text files:
  - **_blocked_doms.txt*: All domains that were blocked via an explicit block-page
  - **_no_resp_doms.txt*: All domains that were blocked via a packet-drop
  - **_non_blocked_domains.txt*: All domains that were accessible

#### Step 3

**Commands to run:** 

- `python run_DNS_pipeline.py 5`: The domains blocked from each VP are transferred back to the host machine. The candidates for region-based blocking are generated for each VP. I.e. domains that are blocked in a VP, but unblocked in at least one other VP. If any of the blocked files are missing, it means the crawler is still running and we need to wait.
- `python run_DNS_pipeline.py 6`:  The candidates are transferred to each VP and are resolved to get their IP addresses.

#### Step 4

**Commands to run:** 

- `python run_DNS_pipeline.py 7`: The candidate domains as well as their IPs are transferred back from each VP. 
- `python run_DNS_pipeline.py 8`: The candidate domains and the reference domains, which were generated from the *non_blocked_domains.txt*, are sent to each VP and traceroutes are run on all of these domains.

#### Step 5

**Command to run:** 

- `python run_DNS_pipeline.py 9`: All the data required for analysis is sent back to the host machine.



