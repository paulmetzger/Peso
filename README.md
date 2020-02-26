# Peso

This repository contains the Peso library that we used in the paper "Enforcing Deadlines for Skeleton-based Parallel Programming", Metzger P., Cole M., Fensch C., Aldinucci M., Bini E., in proc. of RTAS 2020.
The repository also contains scripts that we used to automate experiments. <br/>

## Directory structure

/peso\_workspace/measure_\* - Micro benchmark to measure inter-core communication latency <br/> 
/peso\_workspace/peso - Peso source code and benchmarks <br/>
/scripts - scripts to automate experiments <br/>
/scripts/rt.db - SQLite DB with collected data <br/>

We used the XMOS xTIMEcomposer to edit and compile the code in /peso\_workspace. The xTIMEcomposer is available on xmos.com.

Contact: Paul Metzger, s1576303@sms.ed.ac.uk
