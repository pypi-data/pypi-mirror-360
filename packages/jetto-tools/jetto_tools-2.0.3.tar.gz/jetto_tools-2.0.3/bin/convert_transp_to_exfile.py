#!/usr/bin/env python
# Created by aaronkho, 07 Aug 2020

# This script allows the user to create an exfile used by JETTO
# from the output netCDF file of a TRANSP run.

# The exfile is saved in a specified target directory.

import sys
import argparse
import jetto_tools.transp

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description='Generate JETTO ex-file from TRANSP CDF file.\n\nExamples:\n  python3 ./transp_to_exfile.py --runid H05 --time_zero 40.0 JET 94980\n  python3 ./transp_to_exfile.py --cdf ./94980H05.CDF --time_zero 40.0 JET 94980\n  python3 ./transp_to_exfile.py -o ./custom.ex --runid H05 --time_zero 40.0 JET 94980', \
                                     epilog='Developed by Aaron Ho at DIFFER - Dutch Institute of Fundamental Energy Research.\nFor questions or concerns, please email: a.ho@differ.nl')
    parser.add_argument('--runid', dest='runid', default=None, type=str, action='store', help='Run ID within pulse number of device to access')
    parser.add_argument('--cdf', dest='inpath', default=None, type=str, action='store', help='Optional path including filename for input CDF file, TRANSP run directory takes precedence')
    parser.add_argument('-o', dest='opath', default=None, type=str, action='store', help='Optional path including filename for created ex-file, otherwise uses CDF filename in current working directory')
    parser.add_argument('--time_zero', dest='tzero', default=None, type=float, action='store', help='Used to shift time axis back to experimental time since TRANSP runs always start at t=0')
    parser.add_argument('device', nargs=1, type=str, action='store', help='Name of device within TRANSP shared run directory')
    parser.add_argument('pulseno', nargs=1, type=int, action='store', help='Pulse number within device to access')
    parser.add_argument('times', nargs='*', type=float, action='store', help='Start and end times in TRANSP run for data to be converted, set negative for simulation start and end value')
    args = parser.parse_args()   # Default grabs from sys.argv

    if args.runid is None and args.inpath is None:
        raise ValueError("CDF file specification not provided to script! Aborting!")
    tbeg = None
    tend = None
    if len(args.times) > 0:
        if len(args.times) >= 1 and args.times[0] >= 0.0:
            tbeg = float(args.times[0])
        if len(args.times) >= 2 and args.times[1] >= 0.0:
            tend = float(args.times[1])
    if tbeg is not None and tend is not None and tend < tbeg:
        tend = None

    tstart = args.tzero
    # SPECIFIC TO JET - hard-coded here to prevent user error, but not good general practice
    if tstart is None and args.device == 'JET':
        tstart = 40.0

    ier = 0
    customflag = True if args.inpath is not None else False
    if customflag:
        try:
            ier = jetto_tools.transp.convert_cdf_to_exfile(args.device[0], args.pulseno[0], 'none', args.opath, tbeg=tbeg, tend=tend, inpath=args.inpath, tstart=tstart)
        except Exception as e:
            ier = 1
            print(repr(e))
            if args.runid is not None:
                print("Retrying with data flags passed to script...")
                customflag = False
    if not customflag:
        ier = jetto_tools.transp.convert_cdf_to_exfile(args.device[0], args.pulseno[0], args.runid, args.opath, tbeg=tbeg, tend=tend, tstart=tstart)

    if ier == 0:
        print("Ex-file generation script completed!")

if __name__ == "__main__":
    main()
