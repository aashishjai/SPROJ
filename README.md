# regionalism2020

Repo for submission of regionalism work to IMC 2020. There are two pipelines that can be run one after the other. While the paper contains the theoretical details of the algorithm, the code is split up into two repositories: **Analysis** and **Data_Collection**.

## Introduction

The project aims to use _traceroutes_ from a set _vantage-point_ to a _server_ and compare these traceroutes to deduce whether a website hosted on that server is blocked by the server, or is rather censored by some third party. There is already a plethora of research conducted on censorship, so this research focuses purely on server-side blocking of domains.

## Key terms

**Vantage points:** These are simply remote servers spread out across the world. In all cases these vantage points are machines running root Server, and are used to gather a variety of traceroutes. The more vantage points we have, the more accurate our analysis can be.

**Traceroutes:** Given a source and a destination, these are simply all the routers and other network devices we touch before we reach the server. In our context, we use this to figure out where blocking took place.

## Prerequisites and assumptions

- The code assumes that you have root access to the machine, since at many places we use a custom resolver to resolve domains, which requires root access
- Python version > 3.7 for the data collection
- The set-up scripts provided in the repo are to be installed in each of the vantage points. These scripts set up a local resolver on the remote machine and install all the required packages to run the traceroutes

## Vantage Points Setup

There are some prerequisites for setting up a new remote server to conduct the experiments. The first is that you must have root access to the server, this is because the data collection requires the use of a local bind server, which requires root access. The second is that the remote server must have an RSA public/private key pair rather than password access. The path to this RSA key on the host machine will be given in the config.py file. Please follow the following instructions to set up your remote server

- Enable root access to the server

- Generate a private/public pair of RSA keys to enable public key based authentication to your server. [This guide](https://kb.iu.edu/d/aews) will help you do that

- Test the connection by trying to ssh to the server using the local private key

- zip the **setup_scripts** directory and transfer it to the remote server

- Unzip it on the remote server and run the following command:

  ```
  bash setup.sh
  ```

- Go to the **config.py** file in the **data_collection/** directory. The first variable is a list of vantage points containing comma-separated strings. The naming convention for a vantage point is:  CONTINENT,COUNTRY,CITY,VP_TYPE,IP_ADDRESS. The VP Type can be a random name you give to a set of servers (each VP type would be associated with one RSA key)

- Open **config.py** and fill in the SERVER_RSA_KEY_PATHS dictionary where the key is a VP_type and the value is the path to the RSA key on your host computer. 

## How can I run the code?

First, make sure you have run the set_scripts on the correct servers and set up the vantages in the **config.py** file. Both of these things are described right above.

Depending on whether you want to start the data collection, or whether you want to run the analysis scripts, you can navigate to the appropriate folder to have a look at how to run the correct script.

###################
# DNS Pipeline
### Mode 0
- Initiates connection to server using SSH
- sed command is used to modify the /etc/resolv.conf file on the remote server. 
- This file is typically used to specify the DNS resolvers that the system should use.
- ie means to edit the /etc/resolv.conf in place
  
### Mode 1 
- Function designed to transfer a data bundle to a remote machine, and then unzip the bundle on the remote machine
- creates a directory mentioned in main_dir in the virtual machine
- uses scp to transfer the file from local to remote server 
- removes the older version of the folder and unzips the new folder on the remote machine and places it in the specified directory

### Mode 2 
- Commands ran in  screen session which runs even after the SSH ends
- cd's into the specified directory
- runs the bash file resolve_domains.sh
  - resolve_domains.sh
    - takes 8.8.8.8 as argument
    - restarts bind9, which is a dns server
    - makes 3 folders: run123
    - runs my_bind.py(8.8.8.8)
    - creates blocked and resolved txt files

