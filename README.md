# slurm_acct

SLURM sacct constructor

## slurm_acct.py

Simple tool for constructing sacct command to run various accounting reports in the format expected by our business office. Its main goal is to calculate the last day of a given month, and automating the task of running reports for a previous month.


### Features

* Defaults are calculated to produce last month's accounting
* Defaults are shown in `--help`
* Business office output (uses specific queue & filename combinations)
* Automatically calculate last day of the month
* Execute constructed commands
* Python 2.7 & 3 compatible, using commonly available modules


### Examples

* Show how to run last month's aggregate report for all users and clusters:

	```
	 ./slurm_accts.py                                                                                                                                                                  
	```
   output:

	```
	sacct -XTp -a -L  -S 2018-08-01 -E 2018-08-31T23:59:59  -o JobID,User,Account,cluster,Partition,NodeList,NNodes,AllocCPUS,start,end,CPUTime,CPUTimeRAW,Elapsed,ElapsedRaw > ./results/2018-08-HPC-slurm-all.txt
	```

* Run last month's aggregate report for all users and clusters, split into multiple files for business office:

	```
	./slurm_accts.py -b -x
	```

* Run reports from beginning of February until June 15th, and save them in a filename with 'custom' suffix

	```
	./slurm_accts.py -sm 2 -em 6 -ed 15 -s custom -x
	```
### Defaults

`slurm_acct` defaults to the following:

* time range is first day through last day of a previous month
* there is no limit to which clusters, partitions or users areused

### Command line arguments

```
usage: slurm_accts.py [-h] [-sd STARTDAY] [-sm STARTMONTH] [-sy STARTYEAR]
                      [-ed ENDDAY] [-em ENDMONTH] [-ey ENDYEAR] [-a ACCOUNT]
                      [-b] [-c CLUSTER] [-d] [-f FIELDS] [-o OUTPUT]
                      [-p PARTITION] [-r RESULTDIR] [-s SUFFIX] [-u USER] [-x]

Simple tool to construct sacct command to output accounting data in a
predefined format. Default date range is: 2018/8/1-31.

optional arguments:
  -h, --help            show this help message and exit
  -sd STARTDAY, --startday STARTDAY
                        accounting start day (default: 1)
  -sm STARTMONTH, --startmonth STARTMONTH
                        accounting start month (default: 8)
  -sy STARTYEAR, --startyear STARTYEAR
                        accounting start year (default: 2018)
  -ed ENDDAY, --endday ENDDAY
                        accounting end day (default: 31)
  -em ENDMONTH, --endmonth ENDMONTH
                        accounting end month (default: 8)
  -ey ENDYEAR, --endyear ENDYEAR
                        accounting end year (default: 2018)
  -a ACCOUNT, --account ACCOUNT
                        limit query to specific account(s) (default: None)
  -b, --business        business office setup (default: False)
  -c CLUSTER, --cluster CLUSTER
                        limit query to specific cluster(s) (default: None)
  -d, --debug           enable debug logging (default: False)
  -f FIELDS, --fields FIELDS
                        accounting fields (default: JobID,User,Account,cluster
                        ,Partition,NodeList,NNodes,AllocCPUS,start,end,CPUTime
                        ,CPUTimeRAW,Elapsed,ElapsedRaw)
  -o OUTPUT, --output OUTPUT
  -p PARTITION, --partition PARTITION
                        limit query to specific partition(s) (default: None)
  -r RESULTDIR, --resultdir RESULTDIR
                        destination directory for results (default: ./results)
  -s SUFFIX, --suffix SUFFIX
                        custom filename suffix (default: all)
  -u USER, --user USER  limit query to specific user(s) (default: None)
  -x, --execute         execute constructed command (default: False)
```

### Defining custom business report

For the purpose of our business office we have to filter sacct based on combinations of various partitions and save them to various files. This is stored as a key/value dictionary inside the script. In this example we have `gpu_q` partition being saved to a file with 'gpu' in its name, while all three `pegasus_q`, `discovery_q` and `haswell_q` get stored in a file with 'std' suffix.

```
# business output: partitions + file suffixes
BUSINESS_OUTPUT = {'pegasus_q,discovery_q,haswell_q': 'std',
                   'smp_q':  'smp',
                   'gpu_q': 'gpu',
                   'orion_q': 'orion',
                   None: 'all'
                   }
```