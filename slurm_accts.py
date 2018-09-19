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
RESULTS_DIR = "./logs"


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
    parser.add_argument("-d", "--debug", help="enable debug logging",
                        action="store_true")
    parser.add_argument("-f", "--fields", help="accounting fields",
                        default=ACCT_FIELDS)
    parser.add_argument('-o', '--output', type=argparse.FileType('w'),
                        default=sys.stdout)
    parser.add_argument('-p', '--partition', help="limit query to specific partition(s)",
                        default=None)
    parser.add_argument('-r', '--results', help="destination directory for results",
                        default=RESULTS_DIR)
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

    # check if end date may not be the actual end of a given end month (28 or later)
    # if not, adjust it
    if int(args.endday) >= 28 and int(args.endday) != calendar.monthrange(int(args.endyear), int(args.endmonth))[1]:
        eday = str(calendar.monthrange(
            int(args.endyear), int(args.endmonth))[1]).zfill(2)
        logging.debug(
            "Auto adjusting end day from {} to {}".format(args.endday, eday))
    else:
        eday = str(args.endday).zfill(2)

    # pad with zeros our start/end numbers
    sday = str(args.startday).zfill(2)
    smonth = str(args.startmonth).zfill(2)
    syear = str(args.startyear).zfill(4)
    emonth = str(args.endmonth).zfill(2)
    eyear = str(args.endyear).zfill(4)

    # construct start and end fields
    start_str = "-S {0}-{1}-{2}".format(syear, smonth, sday)
    end_str = "-E {0}-{1}-{2}T23:59:59".format(eyear, emonth, eday)

    # do we have partitions?
    if args.partition:
        partition = "r " + args.partition
    else:
        partition = ""

    # # construct sacct account
    sacct_cmd = ("echo sacct -aLo {0} {1} {2} -XTp{3} &> {4}/{5}-{6}-HPC-slurm-all.txt".format(
        args.fields, start_str, end_str, partition, args.results, eyear, emonth))

    # construct sacct account
    # sacct_cmd = ("echo sacct -aLo {0} {1} {2} -XTp{3}".format(
    #     args.fields, start_str, end_str, partition, args.results, eyear, emonth))
    # construct sacct account
    # sacct_cmd = ("ls -la")

    logging.debug("Command: {}".format(sacct_cmd))
    # print sacct command
    # print(sacct_cmd)

    # if args.execute:
    #     logging.debug("Executing: {}".format(sacct_cmd))
    #     subprocess.call([sacct_cmd])
    # else:
    #     print("\n" + sacct_cmd + "\n")

    if args.execute:
        logging.debug("Executing: {}".format(sacct_cmd))
        command = shlex.split(sacct_cmd)
        subprocess.call([sacct_cmd])
        try:
            # output = subprocess.check_output(sacct_cmd, stderr=sys.stdout).decode()
            output = subprocess.check_output(sacct_cmd, stderr=sys.stdout).decode()
            # success = True
        except subprocess.CalledProcessError as e:
            # output = e.output.decode()
            logging.error(e.output.decode())
            # success = False
    else:
        print("\n" + sacct_cmd + "\n")


# Execute main() function
if __name__ == '__main__':
    main()
