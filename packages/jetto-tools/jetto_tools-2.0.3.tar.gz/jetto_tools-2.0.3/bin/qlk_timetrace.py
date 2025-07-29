#!/usr/bin/env python
import os
from getpass import getuser
import numpy as np
from pathlib import Path
import copy
import argparse
import inspect

from jetto_tools import qualikiz

def main():
    """CLI description and implementation."""

    parser = argparse.ArgumentParser(description='Perform time-dependent analysis on JETTO-QuaLiKiz run using gamhistory flag.', \
                                     epilog='Developed by Aaron Ho at TUE - Technical University of Eindhoven. For questions or concerns, please email: a.ho@tue.nl')
    parser.add_argument('--username', dest='uname', default='', metavar='USERNAME', type=str, action='store', help='User ID for specifying JETTO input directory, only valid in JET computing cluster')
#    parser.add_argument('--catalogue', dest='fctg', default=False, action='store_true', help='Flag to toggle search inside JETTO catalogue directory, only valid in JET computing cluster')
    parser.add_argument('-o', '--outdir', dest='outdir', default='./', metavar='OUTPATH', type=str, action='store', help='Path to desired output directory')
    parser.add_argument('-s', '--timestart', dest='ti', default=None, type=float, action='store', help='Starting JETTO time for extracted data')
    parser.add_argument('-e', '--timeend', dest='tf', default=None, type=float, action='store', help='Ending JETTO time for extracted data')
    parser.add_argument('-w', '--window', dest='twindow', default=None, type=float, action='store', help='Specify the width of time window for averaging, toggles averaging process')
    parser.add_argument('-x', '--rho', dest='rho', default=11, type=float, action='store', help='Specify rho value to process if <= 1, or number of equally-spaced points from 0-1 if > 1')
    parser.add_argument('--nclass', dest='fnc', default=False, action='store_true', help='Toggles inclusion of neoclassical transport, sets time window to 0.05s by default')
    parser.add_argument('--eigenvalues', dest='feigen', default=False, action='store_true', help='Toggles printing of QuaLiKiz eigenvalue solutions, if provided in run directories')
    parser.add_argument('-a', '--analysis', dest='atype', default=None, type=str, choices=['n_peaking'], action='store', help='Specify which analysis routine to apply on the given run directory')
    parser.add_argument('rundirs', nargs='*', type=str, action='store', help='Name of JETTO run directory to serve as reference point for run generation')
    args = parser.parse_args()

    srcloc = Path(inspect.getsourcefile(qualikiz.perform_gamhistory_pipeline))
    print("Using jetto_tools definition from: %s" % (str(srcloc.resolve())))

    # Obtain user run directory in Heimdall cluster (should allow user to specify completely?)
    uid = args.uname if args.uname else getuser()
    bdir = '/common/cmg/' + uid + '/jetto/runs/' #if not args.fctg else '/home/' + uid + '/cmg/catalog/jetto/jet/'

    # Only allows single radii or equally spaced radial vectors (in normalized rho)
    radial_vector = np.linspace(0.0, 1.0, 11)
    if args.rho >= 0.0:
        radial_vector = np.array([args.rho]) if args.rho <= 1.0 else np.linspace(0.0, 1.0, int(args.rho))

    # Convert analysis type string into enumerated index using a dict
    atyperef = {
        "n_peaking": 1
    }
    atype = atyperef[args.atype] if args.atype is not None else 0

    odatalist = []
    oruntags = []
    edatalist = []
    eruntags = []
    # Performs the entire processing pipeline for each input run directory, in sequence
    for rdir in args.rundirs:
        rpath = Path(bdir+rdir)
        if rpath.is_dir():

            (odata, edata) = qualikiz.perform_gamhistory_pipeline(
                                 str(rpath.resolve()),
                                 time_start=args.ti,
                                 time_end=args.tf,
                                 time_window=args.twindow,
                                 radial_vector=radial_vector,
                                 nc_flag=args.fnc,
                                 include_eigenvalues=args.feigen,
                                 analysis_type=atype
                             )
            if odata is not None:
                odatalist.append(copy.deepcopy(odata))
                oruntags.append(rpath.stem)
            if edata is not None:
                edatalist.append(copy.deepcopy(edata))
                eruntags.append(rpath.stem)

    # This script is written in this segmented way to allow for expansions into standardize plotting routines

    # Generates one file per successfully flux-processed run directory
    if len(odatalist) > 0:

        opath = Path(args.outdir) if args.outdir is not None else Path("./")
        if not opath.exists():
            opath.mkdir(parents=True)
        if not opath.is_dir():
            raise IOError("Target output directory not found!")

        for ii in range(len(odatalist)):
            oname = oruntags[ii] + "_qlk_fluxes.csv"
            jpath = opath / oname
            #datalist[ii].to_json(str(jpath), indent=4)
            odatalist[ii].to_csv(str(jpath), index=False)
            print("Generated %s!" % str(jpath))

    # Generates one file per successfully eigenvalue-processed run directory
    if len(edatalist) > 0:

        opath = Path(args.outdir) if args.outdir is not None else Path("./")
        if not opath.exists():
            opath.mkdir(parents=True)
        if not opath.is_dir():
            raise IOError("Target output directory not found!")

        for ii in range(len(edatalist)):
            oname = eruntags[ii] + "_qlk_eigenvalues.csv"
            jpath = opath / oname
            #datalist[ii].to_json(str(jpath), indent=4)
            edatalist[ii].to_csv(str(jpath), index=False)
            print("Generated %s!" % str(jpath))

    print("Script completed!")


if __name__ == "__main__":
    main()
