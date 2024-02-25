# Datasets
This contains the various datasets we used for our experiments.

### Alexa 100k

The Alexa 100k dataset is in the file alexa_100k.txt and contains the top 100,000 websites globally.

### Institution 100k

This dataset consists of the domains most frequently requested by the users. We collect our dataset from a mirrored stream of live network traffic that passes through the edge router connecting the institution to the Internet. We use a desktop machine connected to the edge router to capture and process the mirrored network stream. We deploy Zeek IDS[b] (formerly known as Bro) on our desktop machine for capturing the raw packet stream and generating high-level summaries of the network traces. Instead of conventional packet capture tools, we use Zeek as it allows us to safely capture high-volume network traffic from the edge router while conserving storage space for long-term data collection. From the captured traces, Zeek
produces detailed network logs and summaries that we preprocess to extract DNS “A” record queries in order to find the most requested domains. To ensure the anonymity of the Zeek logs, we install a capture filter at our desktop machine which allows it to only capture the inbound and outbound DNS packets from the mirrored network stream. Our Zeek logs thus only contain DNS-level summaries that do not expose any Personally Identifiable Information (PII).

### Available Sites

This directory contains a file available_sites.txt from which we sample the input to the baseline experiment. The section below explains how the input set was generated. 

##### Methodology

We generate available_sites set for a particular test country in three steps,

- We run our crawler in a test and compare country to collect HTTP data for Alexa's top 100k websites.  

- Then, we pick the sites that get labeled as 200-UNBLOCK in the test country and add them in an unblocked set. 

- For each website in an unblocked set, we compute the fuzzy hashes of the HTML we got for that site in test and compare country and then compare those hashes. if the similarity score of hashes is greater than 80, we add that site in available_sites set. (Two hashes can have a similarity score from 0 to 100)

