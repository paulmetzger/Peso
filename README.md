# Peso

This repository contains the Peso library that we used in the paper "Enforcing Deadlines for Skeleton-based Parallel Programming", Metzger P., Cole M., Fensch C., Aldinucci M., Bini E., in proc. of RTAS 2020.
The repository also contains scripts that we used to automate experiments. <br/>

## Directory structure

| Directory | Description |
|:---|:---|
|/peso\_workspace/measure_\*|Micro benchmark to measure inter-core communication latency|
|/peso\_workspace/peso       |Peso source code and benchmarks|
|/scripts                    |Scripts to automate experiments|
|/scripts/rt.db              |SQLite DB with collected data|

We used the XMOS xTIMEcomposer to edit and compile code in /peso\_workspace. xTIMEcomposer is available on xmos.com.

Contact: Paul Metzger, s1576303@sms.ed.ac.uk
