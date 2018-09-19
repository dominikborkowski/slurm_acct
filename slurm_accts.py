#!/usr/bin/env python
# small script to construct sacct command for our monthly billing
#
# originally written for python3, looks like it runs on python2 also
#
import time             # calculate time
import argparse         # parse command line arguments
import logging          # use for normal and verbose modes, includes stdout/stderr
import sys              # adds ability to exit the program
import calendar         # calendar and stuff
import datetime         # get current dates/etc
import subprocess       # because we want to execute shell commands
import shlex            # and because subprocess is stupid on python and takes only arrays


# some constants
ACCT_FIELDS = "JobID,User,Account,cluster,CPUTime,NNodes,NodeList,Partition,Elapsed,AllocCPUS,start,end"
RESULT_DIR = "./logs"

# business output: partitions + file suffixes
BUSINESS_OUTPUT = {'pegasus_q,discovery_q,haswell_q': 'std',
                   'smp_q':  'smp',
                   'gpu_q': 'gpu',
                   'orion_q': 'orion',
                   None: ''
                   }


def get_default_date():
    """Provide default dates, for LAST month (from today)
    Returns:
        dictionary: year of that month, last month, last day of said month
    """
    # initialize our defaults, using current year and previous month
    default_date = {'year': datetime.date.today().year,
                    'month':  datetime.date.today().month - 1 or 12,
                    'day': None
                    }

    # if our calculated month is december, then we should rewind to previous year
    if default_date['month'] == 12:
        default_date['year'] = datetime.date.today().year - 1

    # finally, find the number of days in that month
    default_date['day'] = calendar.monthrange(
        default_date['year'], default_date['month'])[1]

    return (default_date)


def get_sacct_cmd(sday, smonth, syear, eday, emonth, eyear, fields, partition):
    """Construct sacct command. If end day is > 28 then adjust to last day of that month.
    Arguments:
        sday {int} -- accounting start day of the month
        smonth {int} -- accounting start month
        syear {int} -- accounting start year
        eday {int} -- accounting end day
        emonth {int} -- accounting end month
        eyear {int} -- accounting end year
        fields {string} -- sacct fields
        partition {string} -- list of partitions
    Returns:
        string: full sacct command
    """

    # check if end date may not be the actual end of a given end month (28 or later)
    # if not, adjust it
    if eday >= 28 and eday != calendar.monthrange(eyear, emonth)[1]:
        logging.debug("Auto adjusting end day from {}".format(eday))
        eday = str(calendar.monthrange(eyear, emonth)[1]).zfill(2)
        logging.debug("Auto adjusting end day to {}".format(eday))
    else:
        eday = str(eday).zfill(2)

    # pad with zeros our start/end numbers
    sday = str(sday).zfill(2)
    smonth = str(smonth).zfill(2)
    syear = str(syear).zfill(4)
    emonth = str(emonth).zfill(2)
    eyear = str(eyear).zfill(4)

    # construct start and end fields
    start_str = "-S {0}-{1}-{2}".format(syear, smonth, sday)
    end_str = "-E {0}-{1}-{2}T23:59:59".format(eyear, emonth, eday)

    # do we have partitions?
    if partition:
        partition = "r " + partition
    else:
        partition = ""

    # final command
    command = (
        "sacct -aLo {0} {1} {2} -XTp{3}".format(fields, start_str, end_str, partition))
    logging.debug("Command: {}".format(command))
    return (command)


def exec_sacct_cmd(command, emonth, eyear, suffix, resultdir, execute):
    """Execute sacct command
    Arguments:
        command {string} -- full sacct command
        eyear {int} -- accounting end year
        resultdir {string} -- location of output file
        execute {boolean} -- if set, execute. otherwise just print
    Returns:
        string: -- output of the command
    """
    # construct command with stdout redirection
    emonth = str(emonth).zfill(2)
    eyear = str(eyear).zfill(4)
    command = command + \
        (" &> {0}/{1}-{2}-HPC-slurm-{3}.txt".format(resultdir, eyear, emonth, suffix))

    if execute:
        logging.debug("Executing: {}".format(command))
        subprocess.call([command])
    else:
        # print("\n" + command + "\n")
        print(command)

    # if args.execute:
    #     logging.debug("Executing: {}".format(sacct_cmd))
    #     command = shlex.split(sacct_cmd)
    #     subprocess.call([sacct_cmd])
    #     try:
    #         # output = subprocess.check_output(sacct_cmd, stderr=sys.stdout).decode()
    #         output = subprocess.check_output(sacct_cmd, stderr=sys.stdout).decode()
    #         # success = True
    #     except subprocess.CalledProcessError as e:
    #         # output = e.output.decode()
    #         logging.error(e.output.decode())
    #         # success = False
    # else:
    #     print("\n" + sacct_cmd + "\n")


def get_business_output(args):
    """Get business output
    Arguments:
        args {reference} -- full arguments
    """
    # construct command with stdout redirection
    logging.debug("Business output")

    for key in BUSINESS_OUTPUT:
        partition = key
        suffix = BUSINESS_OUTPUT[key]
        # get a command
        sacct_cmd = get_sacct_cmd(int(args.startday), int(args.startmonth), int(args.startyear),
            int(args.endday), int(args.endmonth), int(args.endyear), args.fields, partition)
        # execute or print it
        exec_sacct_cmd(sacct_cmd, int(args.endmonth), int(args.endyear), suffix, args.resultdir, args.execute)


def parse_input():
    """Parse command line input to retrieve transfer options
    Returns:
      reference - object with all the arguments as attributes
    """

    # get the default dates
    defaults = get_default_date()

    # show default date range
    dflt_range = str(defaults['year']) + "/" + \
        str(defaults['month']) + "/1-" + str(defaults['day'])

    parser = argparse.ArgumentParser(
        description='Simple tool to construct sacct command to output accounting data in a predefined format.\
            Default date range is: {}.'.format(dflt_range),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("-sd", "--startday", help="accounting start day",
                        default=1)
    parser.add_argument("-sm", "--startmonth", help="accounting start month",
                        default=defaults['month'])
    parser.add_argument("-sy", "--startyear", help="accounting start year",
                        default=defaults['year'])
    parser.add_argument("-ed", "--endday", help="accounting end day",
                        default=defaults['day'])
    parser.add_argument("-em", "--endmonth", help="accounting end month",
                        default=defaults['month'])
    parser.add_argument("-ey", "--endyear", help="accounting end year",
                        default=defaults['year'])
    parser.add_argument("-b", "--business", help="business office setup",
                        action="store_true")
    parser.add_argument("-d", "--debug", help="enable debug logging",
                        action="store_true")
    parser.add_argument("-f", "--fields", help="accounting fields",
                        default=ACCT_FIELDS)
    parser.add_argument('-o', '--output', type=argparse.FileType('w'),
                        default=sys.stdout)
    parser.add_argument('-p', '--partition', help="limit query to specific partition(s)",
                        default=None)
    parser.add_argument('-r', '--resultdir', help="destination directory for results",
                        default=RESULT_DIR)
    parser.add_argument("-x", "--execute", help="execute constructed command",
                        action="store_true")

    args = parser.parse_args()

    # enable verbose logging if debug is enabled
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    # print(args.transfer_mode)
    return(args)


def main():
    # parse input
    args = parse_input()

    if args.business:
        # print("business")
        get_business_output(args)
    else:
        # get a command
        sacct_cmd = get_sacct_cmd(int(args.startday), int(args.startmonth), int(args.startyear),
                                  int(args.endday), int(args.endmonth), int(args.endyear), args.fields, args.partition)
        # execute or print it
        exec_sacct_cmd(sacct_cmd, int(args.endmonth), int(
            args.endyear), "all", args.resultdir, args.execute)



# Execute main() function
if __name__ == '__main__':
    main()
