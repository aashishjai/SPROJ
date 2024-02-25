## Prerequisites and assumptions

- The code assumes that you have root access to the machine, since at many places we use a custom resolver to resolve domains, which requires root access
- Python version > 3.7 for the data collection
- The set-up scripts (the zip file in the previous directory) to be installed in each of the vantage points. These scripts set up a local resolver on the remote machine and install all the required packages

## Code Overview

In both the DNS Pipeline and the HTTP Pipeline, the code works by sending the appropriate _Bundle_ that contains the data collection code to all vantage points which are specified in the **_config.py_** file. 

The data collection is organized in three folders, *DNS_pipeline*, *HTTP_pipeline*, and *DNS_injection_script*. 

#### ./DNS_pipeline/

- ***run_DNS_pipeline.py*** contains the wrapper code for running the data collection across all vantage points
- The **DNS_bundle** contains all the code that will be zipped and transferred to the vantage points

#### ./HTTP_pipeline/

- ***run_HTTP_pipeline.py*** contains the wrapper code for running the data collection across all vantage points
- The **HTTP_bundle** contains all the code that will be zipped and transferred to the vantage points

### Configuration

The ***config.py*** file contains all the important configurations for running an end-to-end experiment. The most important variables in this file are:

- `VANTAGES`: This is a list of comma-separate strings in the format *CONTINENT, COUNTRY, CITY, SERVICE-PROVIDER, IP-ADDRESS*
- `SERVER_RSA_KEY_PATHS`: A dictionary in which a service-provider is mapped to the location of the relevant SSH key
- `DNS_RESOLVERS`: This specifies which resolver to use for the experiment. The BIND server is always running on 127.0.0.1, the local resolver will be different on every machine.
- `PATH_TO_INPUT_DOMAINS_*`: These specify the path to the input for the relevant pipeline
- `*_WAIT`: These specify how long the code waits before moving on to the next step

## Running the code

If you wish to spare yourself the details and just start running the code, you just need to run the following commands.

To run the DNS pipeline:

```
python run_all.py DNS
```

To run the DNS injection test:

```
python run_all.py injection_test
```

To get the DNS injection rest result:

```
python run_all.py injection_test_result
```

To run the HTTP pipeline:

```
python run_all.py HTTP
```

This runs the HTTP pipeline

Opening the file will let you know some details as to how the code is running, but keep in mind that each pipeline will take ~18 hours to run from start to finish for 100k domains.
