# regionalism2020

Repo for submission of regionalism work to IMC 2020. There are two pipelines that can be run one after the other. While the paper contains the theoretical details of the algorithm, the code is split up into two repositories: **Analysis** and **Data_Collection**. This section deals with how to run the **Analysis** scripts

### Analysis

1. After the DNS Data Collection has completed, copy all these files into the data_collection directory

3. Run using Python 2

   ```
   python read_all_mda_py2.py
   ```
4. Check the default folders in run_analysis.sh and change them to the names used in your data collection
5. Run with Python 3 set as default
   ```
   bash run_analysis.sh
   ```
