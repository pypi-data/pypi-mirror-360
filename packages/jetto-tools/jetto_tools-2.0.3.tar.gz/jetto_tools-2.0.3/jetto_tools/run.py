# Script with functions to automatically generate JETTO runs, given a template or base case

# Required imports
import os
import sys
from getpass import getuser
import shutil
import re
import copy
import argparse
import datetime
import subprocess

import numpy as np


def make_jetto_run(refrundir,exfilename,runname=None,username=None,foverwrite=False,runnumber=1,runflag=False):

    basename = 'run'
    rname = 'gen'
    uname = getuser()
    if isinstance(runname,str) and runname.strip() and not re.search('/',runname):
        rname = runname.strip()
    if isinstance(username,str) and username.strip() and not re.search('/',username):
        uname = username.strip()
    rundir = '/common/cmg/' + uname + '/jetto/runs/'

    refdir = None
    if isinstance(refrundir,str) and os.path.isdir(rundir+refrundir):
        refdir = rundir + refrundir
        if not refdir.endswith('/'):
            refdir = refdir + '/'

    status = 1
    exname = None
    extname = None
    if refdir is not None:
        if isinstance(exfilename,str):
            exdir = '/u/'+uname+'/cmg/jams/data/exfile/'
            exfile = exfilename
            extfile = exfilename
            if not exfile.endswith('.ex'):
                exfile = exfile + '.ex'
                extfile = extfile + '.ext'
            else:
                extfile = extfile + 't'

            if os.path.isfile(exdir+exfile):
                exname = exdir + exfile
            elif os.path.isfile(exfile):
                plist = exfile.split('/')
                if os.path.isfile(exdir+plist[-1]) and not foverwrite:
                    raise IOError('Ex-file %s already exists in %s. Aborting.' % (plist[-1],exdir))
                    sys.exit(1)
                shutil.copy2(exfile,exdir+plist[-1])
                exname = exdir + plist[-1]

            if os.path.isfile(exdir+extfile):
                extname = exdir + extfile
            elif os.path.isfile(extfile):
                plist = extfile.split('/')
                if os.path.isfile(exdir+plist[-1]) and not foverwrite:
                    raise IOError('Ext-file %s already exists in %s. Aborting.' % (plist[-1],exdir))
                    sys.exit(1)
                shutil.copy2(extfile,exdir+plist[-1])
                extname = exdir + plist[-1]
    else:
        print("Reference run directory %s not found. Run script produced nothing." % (refrundir))

    if refdir is not None and exname is not None:
        ii = int(runnumber) if isinstance(runnumber,(int,float)) else 1
        nn = "%03d" % (ii)
        runname = basename + rname + nn
        if not foverwrite:
            while os.path.isdir(rundir+runname):
                ii = ii + 1
                nn = "%03d" % (ii)
                runname = basename + rname + nn

        if not os.path.isdir(rundir+runname):
            os.makedirs(rundir+runname)
        if os.path.isfile(refdir+'jetto.in') and os.path.isfile(refdir+'.llcmd'):
            now = datetime.datetime.now()
            with open(refdir+'jetto.in','r') as origfile:
                with open(rundir+runname+'/jetto.in','w') as newfile:
                    for line in origfile:
                        if re.search(r'^Date\s+:',line):
                            newfile.write("%-30s : %s\n" % ("Date",now.strftime("%d/%m/%Y")))
                        elif re.search(r'^Time\s+:',line):
                            newfile.write("%-30s : %s\n" % ("Time",now.strftime("%H:%M:%S")))
                        else:
                            newfile.write(line)

            with open(refdir+'.llcmd','r') as origfile:
                with open(rundir+runname+'/.llcmd','w') as newfile:
                    for line in origfile:
                        if re.search(r'\s+job_name\s+=',line):
                            newfile.write("# @ %-12s = %s\n" % ("job_name",'jetto.'+runname))
                        elif re.search(r'\s+arguments\s+=',line):
                            newfile.write("# @ %-12s =  " % ("arguments"))
                            mm = re.search(r'=\s+(.+)$',line)
                            sline = mm.group(1).split()
                            sline[-2] = runname
                            for ii in np.arange(0,len(sline)):
                                newfile.write("%s " % (sline[ii]))
                            newfile.write("\n")
                        elif re.search(r'\s+initialdir\s+=',line):
                            newfile.write("# @ %-12s = %s\n" % ("initialdir",rundir+runname))
                        else:
                            newfile.write(line)

            with open(refdir+'jetto.jset','r') as origfile:
                with open(rundir+runname+'/jetto.jset','w') as newfile:
                    for line in origfile:
                        if re.search(r'^Creation Name\s+:',line):
                            newfile.write("%-58s : %s\n" % ("Creation Name",rundir+runname+'/jetto.jset'))
                        elif re.search(r'^Creation Date\s+:',line):
                            newfile.write("%-58s : %s\n" % ("Creation Date",now.strftime("%d/%m/%Y")))
                        elif re.search(r'^Creation Time\s+:',line):
                            newfile.write("%-58s : %s\n" % ("Creation Time",now.strftime("%H:%M:%S")))
                        elif re.search(r'^JobProcessingPanel\.runDirNumber\s+:',line):
                            newfile.write("%-58s : %s\n" % ("JobProcessingPanel.runDirNumber",rname+nn))
                        elif re.search(r'^SetUpPanel\.exFileName\s+:',line):
                            newfile.write("%-58s : %s\n" % ("SetUpPanel.exFileName",exdir+exfile))
                        else:
                            newfile.write(line)

            shutil.copy2(exname,rundir+runname+'/jetto.ex')
            if extname is not None:
                shutil.copy2(extname,rundir+runname+'/jetto.ext')

            status = 0
    else:
        print("Ex-file %s not found. Run script produced nothing." % (exfilename))

    if refdir is not None and exname is not None and runflag and os.path.isfile(rundir+runname+'/.llcmd'):
        cwd = os.getcwd()
        os.chdir(rundir+runname)
        subprocess.run(['llsubmit','.llcmd'])
        os.chdir(cwd)

    return status

