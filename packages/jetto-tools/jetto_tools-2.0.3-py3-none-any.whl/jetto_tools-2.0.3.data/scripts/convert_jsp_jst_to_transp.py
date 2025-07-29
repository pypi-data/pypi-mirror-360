#!python
# Required imports
import sys
import argparse
import jetto_tools.transp

def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="JETTO output conversion to TRANSP netCDF-3 format")

    parser.add_argument('machinename', type=str, nargs='?',
                        help="Machine name for TRANSP folder output", default=None)
    parser.add_argument('shotnumber', type=int, nargs='?',
                        help="Shot number for TRANSP folder output", default=None)
    parser.add_argument('sequencenumber', type=int, nargs='?',
                        help="Sequence number (2-digit) for TRANSP folder output", default=None)
    parser.add_argument('-p','--jspfilepath',default='jetto.jsp',
                        help="Path to jetto.jsp file to be converted"
                             "(default: jetto.jsp in current directory)")
    parser.add_argument('-t','--jstfilepath',default='jetto.jst',
                        help="Path to jetto.jst file to be converted"
                             "(default: jetto.jst in current directory)")
    parser.add_argument('--no-legacy', action="store_true", dset="no_legacy",
        help=("Save bin boundary and bin centred radial profiles on different"
            "size radial grids. Note this file will not be readable with "
            "JETDSP")
    )

    args = parser.parse_args()

    ier = jetto_tools.transp.convert_jsp_jst_to_netcdf(
        args.machinename, args.shotnumber, args.sequencenumber,
        args.jspfilepath, args.jstfilepath, legacy=not args.no_legacy)

    if ier == 0:
        print("TRANSP CDF generation script completed!")


#-----------------------------------------------------------------
if __name__ == "__main__":
    main()
