## Detailed Breakdown of Script Functions

### Function: `set_up_configurations`
- **Purpose**: Modifies DNS resolver settings on a remote server (VP).
- **Commands**:
  - Uses `ssh` to connect to the remote server at `vp_ip` using the specified `SSH_KEY_PATH` and `port`.
  - Executes a `sed` command to modify the `/etc/resolv.conf` file on the remote server, replacing the existing `nameserver` entry with `resolver_ip`.
- **Expected Output**: The `/etc/resolv.conf` file on the remote server (`vp_ip`) is updated with the new DNS resolver IP.

### Function: `transfer_bundle_to_all_machines`
- **Purpose**: Transfers a data bundle to a remote server for DNS analysis.
- **Commands**:
  - First `ssh` command connects to `vp_ip` and creates the `main_dir` directory on the remote server.
  - Second `scp` command transfers the `vp_bundle_name` file from the local machine to the `main_dir` directory on the remote server at `vp_ip`.
- **Expected Output**: The data bundle (`vp_bundle_name`) is located in the `main_dir` directory on the remote server (`vp_ip`).

### Function: `start_crawler_on_all_machines`
- **Purpose**: Initiates a domain-resolving script on the remote server.
- **Command**:
  - An `ssh` command runs the `resolve_domains.sh` script located in the transferred bundle on the remote server at `vp_ip`.
- **Expected Output**: The script for domain resolution is executed on the remote server (`vp_ip`), and the process begins.

### Function: `get_active_domain_set`
- **Purpose**: Retrieves the set of active (resolved) domains from the remote server.
- **Commands**:
  - The first `scp` command copies the `resolved_domains.txt` file from the `vp_ip` remote server to the local machine's `config.PATH_TO_ACTIVE_DOMAINS` directory.
  - Subsequent commands process and store this data locally.
- **Expected Output**: A file containing resolved domains is transferred from the remote server (`vp_ip`) to the local machine.

### Function: `return_active_domain_set`
- **Purpose**: Sends the aggregated list of active domains back to the remote server.
- **Command**:
  - Uses `scp` to transfer `active_set.txt` from the local machine to the remote server at `vp_ip`.
- **Expected Output**: The `active_set.txt` file is copied to the specified location on the remote server (`vp_ip`).

### Function: `start_DNS_traceroute_spoofing_check`
- **Purpose**: Initiates a DNS traceroute process on the remote server.
- **Command**:
  - An `ssh` command is used to run the `run_traceroutes.sh` script on the remote server at `vp_ip`.
- **Expected Output**: DNS traceroute processes are started on the remote server (`vp_ip`).

### Function: `get_server_side_blocked`
- **Purpose**: Retrieves a list of potentially server-side blocked domains.
- **Commands**:
  - A `scp` command is used to copy `have_auth_no_ip_extended.common_three_runs.txt` from the remote server (`vp_ip`) to the local machine.
  - Further commands process and store this data locally.
- **Expected Output**: A file with server-side blocked domain candidates is transferred from the remote server (`vp_ip`) to the local machine.

### Function: `return_server_side_blocked`
- **Purpose**: Sends processed list of server-side blocked domains back to the remote server.
- **Command**:
  - Uses `scp` to transfer `have_auth_no_ip_extended.common_three_runs.txt` from the local machine to the remote server at `vp_ip`.
- **Expected Output**: The file with server-side blocked domains is sent back to the remote server (`vp_ip`).

### Function: `start_MDA_DNS`
- **Purpose**: Starts a detailed DNS analysis (MDA DNS) on the remote server.
- **Command**:
  - An `ssh` command is used to execute `proximity.sh` for DNS analysis on the remote server at `vp_ip`.
- **Expected Output**: An advanced DNS analysis process is initiated on the remote server (`vp_ip`).

### Function: `zip_and_get_back_collected_data`
- **Purpose**: Compresses and transfers collected DNS data from the remote server to the local machine.
- **Commands**:
  - First `ssh` command creates a zip file of DNS data directories on the remote server (`vp_ip`).
  - The `scp` command then transfers this zip file to the local machine.
- **Expected Output**: A zip file containing DNS data is received on the local machine from the remote server (`vp_ip`).

### Function: `start_get_summary`
- **Purpose**: Retrieves a summary of the DNS analysis from the remote server.
- **Commands**:
  - A series of commands run via `ssh` on the remote server (`vp_ip`) generate a statistical summary.
  - `scp` transfers this summary file to the local machine.
- **Expected Output**: A summary file containing DNS analysis statistics is received on the local machine from the remote server (`vp_ip`).


## Script Execution Breakdown (`if __name__ == "__main__":`)

### Directory Setup
- **Purpose**: Prepare local directories for data storage.
- **Process**:
  - Iterates through `directories_to_store_data`.
  - Creates each directory using `mkdir` if it doesn't exist.
- **Directories**:
  - `PATH_TO_ACTIVE_DOMAINS`: Stores active domain data.
  - `PATH_TO_DATA_COLLECTION_DNS`: Stores DNS data.
  - `PATH_TO_SERVER_SIDE_BLOCKED_CANDIDATES_DNS`: Stores server-side blocked domain candidates.
  - `PATH_TO_DNS_SUMMARIES`: Stores DNS operation summaries.

### Preparation for DNS Analysis
- **Purpose**: Configure remote servers (VPs) for DNS analysis.
- **Process**:
  - Fetches `vantage_array` and `main_dir` from `config`.
  - Determines `MODE` from command line argument.
  - Performs specific operations based on `MODE` on each VP.
- **Modes**:
  - Various `MODE` values trigger different operations (e.g., configuration setup, data bundle transfer, crawler initiation).
  - Functions corresponding to each `MODE` are executed for remote server operations.

### Data Aggregation and Cleanup
- **Purpose**: Aggregate data from VPs and clean directories.
- **Process**:
  - Executes directory cleaning and data aggregation based on `MODE`.
  - Uses Unix commands (`find`, `xargs`, `sort`, `awk`) for data processing.
  - `rm -rf` for directory cleanup.
- **Specifics**:
  - `MODE == 3, 5, 9`: Cleans directories for new data collection.
  - `MODE == 3`: Aggregates active domain data from all VPs.
  - `MODE == 5`: Aggregates server-side blocked domain candidates.
  - `MODE == 8`: Prepares DNS summaries directory.

### Second Loop for Data Distribution
- **Purpose**: Redistribute processed data to all VPs.
- **Process**:
  - Iterates through `vantage_array` again.
  - Depending on `MODE`, executes functions to send data back to VPs.
- **Functions**:
  - `return_active_domain_set` for `MODE == 3`.
  - `return_server_side_blocked` for `MODE == 5`.
- **Explanation**: Essential for two-step operations: initial data collection from VPs, followed by distribution of processed data back to them.

This script is a comprehensive tool for distributed DNS analysis, handling various stages of data collection, processing, and analysis across multiple remote servers. Each `MODE` represents a distinct stage in this workflow.


## `run_traceroutes.sh` Script Detailed Breakdown

### Overview
- **Purpose**: Integral to the DNS pipeline, focusing on resolving DNS queries, identifying server-side blocked domains, and performing DNS traceroutes for deeper analysis.

### Step-by-Step Process

1. **Parameters Initialization**
   - **Operation**: The script starts by initializing two parameters, `RETRIES` and `TIMEOUT`, which are passed as arguments.
   - **Purpose**: These parameters are likely used in subsequent DNS resolution or traceroute commands to define the retry count and timeout period for network requests.

2. **First DNS Resolution Run**
   - **Operation**:
     - Changes directory to `./step1_resolve_here`.
     - Executes `python get_server_side_blocked.py`, presumably to identify domains that are potentially blocked by the server.
     - Then, moves to `../step3_resolve_again_get_ns/` and runs `get_nameservers.py`.
     - Aggregates and filters results using `awk` and `cat` commands, focusing on domains without authoritative servers (`no_auth_no_ip.txt`) and those with authoritative servers but no IP addresses (`have_auth_no_ip.txt`).
   - **Purpose**: This step aims to categorize domains based on their resolution status and availability of authoritative DNS servers.

3. **Intermediary Logging and Waiting**
   - **Operation**: Logs progress in `progress_logs.txt` and introduces a sleep of 9 seconds.
   - **Purpose**: Provides a buffer time to ensure that all network operations and data processing have completed before proceeding.

4. **Second DNS Resolution Run**
   - **Operation**: Repeats the process of running `get_nameservers.py` and categorizing domains, similar to the first run.
   - **Purpose**: This step likely aims to verify the initial findings or to capture any changes in the DNS resolution status of the domains.

5. **Extended Waiting Period**
   - **Operation**: Logs progress and waits for a longer period (300 seconds).
   - **Purpose**: Ensures ample time for the second DNS resolution run to complete, especially important if network requests are delayed or queued.

6. **Third DNS Resolution Run**
   - **Operation**: Again repeats the DNS resolution process.
   - **Purpose**: This additional run might be to further verify the consistency of DNS resolution results or to capture any transient changes.

7. **Finalizing DNS Resolution Phase**
   - **Operation**: Logs the completion of DNS resolution steps and captures the public IP of the machine using `dig`. This is to check if VPNs were operational.
   - **Purpose**: To ensure that the data collected is accurate and the network environment (like VPNs) was stable during the data collection.

8. **Comparison Across Runs**
   - **Operation**: Executes `compare_across_three_runs.py` to analyze consistency across the three DNS resolution runs.
   - **Purpose**: To identify domains that consistently exhibit the same DNS resolution behavior, which is crucial for accurate analysis.

9. **Preparing for DNS Traceroute**
   - **Operation**: Copies the `have_auth_no_ip_extended.common_three_runs.txt` file to the `../DNS_pipeline_step_2/step3_resolve_again_get_ns/` directory and logs the transition to the next step.
   - **Purpose**: Sets the stage for the next part of the DNS analysis, which involves DNS traceroutes.

10. **Executing DNS Traceroutes**
    - **Operation**: Changes directory to `../DNS_pipeline_step_2/` and runs `run_traceroute.sh` with the previously set `RETRIES` and `TIMEOUT`.
    - **Purpose**: Performs traceroute operations on the identified domains to understand their routing paths and possibly identify points of network interference or blocking.

11. **Finalization and Logging**
    - **Operation**: Logs the final IP address of the machine post-traceroute execution, again to check for VPN consistency.
    - **Purpose**: Ensures the integrity and consistency of the network environment throughout the execution of the script.

### Conclusion
- **In Summary**: The `run_traceroutes.sh` script is a meticulously designed component of the DNS pipeline, executing multiple rounds of DNS resolution, categorizing domains based on their resolution status, and performing traceroutes. Each step is logged for transparency and to ensure the reliability of the analysis.


## `resolve_domains.sh` Script Detailed Breakdown

### Overview
- **Purpose**: This script is designed to resolve domain names using a BIND server and categorize the results into resolved and unresolved (potentially blocked) domains.

### Detailed Steps

1. **Parameter Initialization**
   - **Operation**: Receives `RESOLVER` as an argument, indicating the DNS resolver to use.
   - **Purpose**: To define which DNS resolver the BIND server should use for domain resolution.

2. **Restart BIND Service**
   - **Operation**: Executes `sudo service bind9 restart` to restart the BIND server.
   - **Purpose**: Ensures that the BIND server is running with the latest configuration or settings.

3. **Directory Creation for Runs**
   - **Operation**: Creates three directories: `run1`, `run2`, `run3`.
   - **Purpose**: These directories are likely used to store results from successive runs or phases of domain resolution.

4. **Logging Start of Domain Resolution**
   - **Operation**: Appends a log entry in `progress_logs.txt` indicating the start of domain resolution.
   - **Purpose**: To timestamp the initiation of the domain resolution process for tracking and record-keeping.

5. **Executing Domain Resolution Script**
   - **Operation**: Runs `python ./step1_resolve_here/my_bind.py $RESOLVER`.
   - **Purpose**: To execute the domain resolution process using the BIND server with the specified resolver.

6. **Categorizing Domains**
   - **Operation**:
     - Extracts failed domain resolutions from `step1_resolve_here/*fail*` and saves them to `blocked_domains.txt`.
     - Compiles successful resolutions from `step1_resolve_here/*success*` into `resolved_domains.txt`.
     - Removes temporary success and fail files.
   - **Purpose**: To categorize domains into two groups: those that could not be resolved (potentially blocked) and those that were successfully resolved.

7. **Logging Completion of Domain Resolution**
   - **Operation**: Appends a log entry indicating the completion of the BIND server's domain categorization process.
   - **Purpose**: To provide a timestamp for the completion of domain resolution, useful for tracking the duration of this process.

8. **Logging Machine's Public IP**
   - **Operation**: Uses `dig` to log the public IP of the machine, appending this information to `progress_logs.txt`.
   - **Purpose**: To verify the operational status of network configurations such as VPNs during the domain resolution process.

### Conclusion
- **In Summary**: `resolve_domains.sh` is a critical script in the DNS analysis pipeline, handling the resolution of domain names using BIND and categorizing them based on their resolution status. It includes meticulous logging for tracking the process and verifying the integrity of the network environment.


## `get_server_side_blocked.py` Script Detailed Breakdown

### Overview
- **Purpose**: To identify domains that are blocked on the server side by comparing lists of blocked and active domains.

### Detailed Process

1. **Reading Blocked Domains**
   - **Operation**: Opens and reads `blocked_domains.txt`.
   - **Details**: Reads each line into `blocked_domains`, trimming the last empty element.
   - **Purpose**: Loads the list of domains that failed to resolve, potentially indicating server-side blocking.

2. **Reading Active Domains**
   - **Operation**: Opens and reads `active_set.txt`.
   - **Details**: Reads each line into `active_domains`, excluding the last empty line.
   - **Purpose**: Gathers the list of successfully resolved (active) domains.

3. **Comparing Blocked and Active Domains**
   - **Operation**: Iterates through `blocked_domains` and compares with `active_domains`.
   - **Details**:
     - Extracts the domain part from `one_active_domain` (assumed format: `domain additional_info`).
     - Checks if `one_blocked_domain` matches `active_domain` and is non-empty.
     - Appends matching domains to `server_side_blocked.txt`.
   - **Purpose**: Identifies domains listed in both blocked and active lists, suggesting server-side blocking.

4. **Writing to Server-Side Blocked File**
   - **Operation**: Appends identified domains to `../step3_resolve_again_get_ns/server_side_blocked.txt`.
   - **Purpose**: Updates or creates a list of server-side blocked domains for subsequent analysis in the DNS pipeline.

### Conclusion
- **In Summary**: This script is key in the DNS analysis pipeline for flagging domains that appear in both the blocked and active lists, indicative of server-side blocking. It aids in pinpointing domains requiring further investigation or alternative resolution strategies.


## `get_name_servers.py` Script Detailed Breakdown

### Overview
- **Purpose**: To perform DNS queries on a list of domains, particularly those identified as server-side blocked, using parallel processing for efficiency.

### Detailed Steps

1. **Environment Setup**
   - **Operation**: Changes the working directory to the script's directory (`os.chdir(os.path.dirname(sys.argv[0]))`).
   - **Purpose**: Ensures that file operations are executed in the same directory as the script for consistency.

2. **Function: `spread_work`**
   - **Operation**: Accepts a list of domains (`domain_list`) and an index (`count`), iterating over the domains to perform DNS queries using `mydig.alias`.
   - **Purpose**: Modularizes the process of DNS resolution for a subset of domains.
   - **Details**: Skips empty domain entries to avoid unnecessary processing.

3. **Main Execution**
   - **Operation**: Reads `server_side_blocked.txt` to obtain a list of domains for resolution.
   - **Multithreading Setup**:
     - Sets `N_THREADS` to 60, defining the number of parallel processes.
     - Calculates `THREAD_WORKLOAD` to evenly distribute domains across threads.
   - **Parallel Resolution**:
     - Iterates in chunks of `THREAD_WORKLOAD`.
     - For each chunk, creates a `Process` targeting `spread_work` with the chunk and an index.
     - Starts each process, effectively parallelizing the resolution of domains.

### Conclusion
- **In Summary**: `get_name_servers.py` employs multi-threading to efficiently resolve DNS queries for a list of server-side blocked domains. It reads the domains from `server_side_blocked.txt`, distributes them across multiple processes, and uses the `mydig` module to perform DNS queries. This approach significantly enhances the efficiency of the resolution process in the DNS analysis pipeline.
