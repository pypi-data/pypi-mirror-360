#!python
# Created by aaronkho, 14 Dec 2022

# This script allows the user to create an exfile from a JETTO
# run, specifically from its JSP and JST outputs.

# The exfile is saved in a specified target directory.

import sys
import os
import argparse
from pathlib import Path
from jetto_tools import output_to_input

def parse_opt(parents=[]):

    parser = argparse.ArgumentParser(parents=parents, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # REQUIRED ARGS
    # Name of exfile to be used.
    parser.add_argument("-o", "--outname", dest="new_exfile_name",
                        action="store", default=None,
                        help="Name of EXFILE to be written out to", required=True)

    # OPTIONAL ARGS
    # JSP path to be used. Optional, defaults to looking in the current directory
    parser.add_argument("-jsp", "--jsp", dest="jsp_path",
                        action="store", default=None,
                        help="Path to the jsp to make EXFILE from")
    # Time slices to be used. Optional, else uses the end time
    parser.add_argument("-t", "--times", dest="time_slices", nargs='*',
                        type=float, action="store", default=None,
                        help="Time slices from JSP to use profiles to make EXFILE")
    # Time range to be used. Optional, else uses the end time
    parser.add_argument("-r", "--range", dest="time_range", nargs=2,
                        type=float, action="store", default=None,
                        help="Time range from JSP to use profiles to make EXFILE")
    # Number of interpolated points in time range, incompatible with time slices. Optional, else uses the JSP time vector
    parser.add_argument("-n", "--npoints", dest="num_points",
                        type=int, action="store", default=None,
                        help="Number of evenly spaced interpolation points to use in specified time range to make EXFILE")
    # Path to directory where exfile will be written out. Optional, defaults to JINTRAC standard location
    loc = os.environ.get('JAMSOUT')
    sloc = loc.strip().split('/')
    while not sloc[-1]:
        del sloc[-1]
    sloc[-1] = 'exfile'
    exfile_output_path = '/'.join(sloc)
    parser.add_argument("-d", "--outdir", dest="exfile_path",
                        action="store", default=exfile_output_path,
                        help="Optional path to ouptput the EXFILE")
    # Path to conversion configuration file to be used. Optional, defaults to configuration file in repository
    default_exfile_temp_path = None
    parser.add_argument("-c", "--config", dest="user_config_path",
                         action="store", default=None,
                         help="Provide FULL path to configuration file to be used to generate new exfile.")
    # Path to template exfile to be used. Optional, defaults to None
    default_exfile_temp_path = None
    parser.add_argument("-b", "--template", dest="orig_exfile_path",
                         action="store", default=default_exfile_temp_path,
                         help="Provide FULL path to EXFILE to be used a template for new exfile.")
    # Set verbosity of procedure, useful for debugging. Optional, defaults to quiet
    parser.add_argument("-v", "--verbose", dest="verbosity",
                        type=int, action="store", default=0,
                        help="Set verbosity of scripts, useful for debugging")
    opts = parser.parse_args()
    return opts

def main():

    # Get command line options
    opts = parse_opt()
    if opts.jsp_path == None:
        opts.jsp_path = './' # jetto.jsp appended later on

    time_range = opts.time_range
    if time_range is not None:
        if time_range[0] < 0.0 and time_range[1] < 0.0:
            time_range = None
        elif time_range[0] < 0.0:
            time_range[0] = None
        elif time_range[1] < 0.0:
            time_range[1] = None
    time_slices = opts.time_slices
    if time_slices is not None:
        time_slices = [tt for tt in opts.time_slices if tt >= 0.0]

    exfile_write_status = output_to_input.convert_and_write(
        opts.exfile_path,
        opts.new_exfile_name,
        opts.jsp_path,
        time_range=time_range,
        time_slices=time_slices,
        num_points=opts.num_points,
        user_config_path=opts.user_config_path,
        orig_exfile_path=opts.orig_exfile_path,
        verbosity=opts.verbosity
    )

if __name__ == '__main__':
    main()

