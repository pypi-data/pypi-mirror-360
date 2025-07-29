# Imports

import argparse
import sys
import os
import datetime
import filecmp
import shutil
import copy
from jetto_tools import binary
import numpy as np
import math
from scipy import interpolate
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import re

###############################################################################

# Check command line arguments

def checkInputs(fileDonor, fileCoconut, outputDir):
    # File listing JETTO donor run
    if (not os.path.isfile(fileDonor)):
        print("Specified JETTO input file not found: " + fileDonor)
        sys.exit(1)
    # File listing COCONUT runs
    if (not os.path.isfile(fileCoconut)):
        print("Specified COCONUT input file not found: " + fileCoconut)
        sys.exit(2)
    return

###############################################################################

# Read input file listing JETTO donor run
#   Lines beginning with "#" to be ignored as comments
#   All other lines to be treated as a path to a catalogue directory

def getJettoInputDir(inputFile):
    dirList = []
    print("\nParsing input file: ", inputFile)
    with open(inputFile) as openFileObject:
        for fileLine in openFileObject:
            fileLine = fileLine[:-1]   # Remove trailing newline
            if (fileLine[0] == "#"):
                print("  Ignoring comment line: ", fileLine)
            else:
                if (not os.path.exists(fileLine)):
                    print("  Input directory ", fileLine, " does not exist")
                    sys.exit(3)
                dirList.append(fileLine) 
                print("  Input directory: ", fileLine)
    if (len(dirList) < 1):
        print("No JETTO donor directory listed in input file", inputFile)
        sys.exit(4)
    if (len(dirList) > 1):
        print("Multiple JETTO donor directories listed in input file",        \
              inputFile, ". Taking first given: ", dirList[0])
    
    print("JETTO donor file parsed.", len(dirList),                           \
          "input directories added.")
    return(dirList[0])

###############################################################################

# Read input file listing COCONUT runs
#   Lines beginning with "#" to be ignored as comments
#   All other lines to be treated as a path to a catalogue directory

def getCoconutInputDirs(inputFile):
    dirList = []
    tOffsetList = []
    print("\nParsing input file: ", inputFile)
    with open(inputFile) as openFileObject:
        for fileLine in openFileObject:
            fileLine = fileLine[:-1]   # Remove trailing newline
            if (fileLine[0] == "#"):
                print("  Ignoring comment line: ", fileLine)
            else:
                splitFileLine = fileLine.split()
                if (len(splitFileLine) == 1):
                    dirLine = fileLine
                    tOffset = 0.0
                else:
                    dirLine = splitFileLine[0]
                    tOffset = float(splitFileLine[1])
                if (not os.path.exists(dirLine)):
                    print("  Input directory ", dirLine, " does not exist")
                    sys.exit(5)
                dirList.append(dirLine)
                tOffsetList.append(tOffset)
                print("  Input directory: " + dirLine +                       \
                      " with time offset " + str(tOffset) + " seconds")

    print("COCONUT list file parsed.", len(dirList),                          \
          "input directories added.\n")
    return(dirList, tOffsetList)

###############################################################################

# Read input file for plotting listing JETTO output runs
#   Lines beginning with "#" to be ignored as comments
#   All other lines to be treated as a path to a directory

def getJettoOutputDirs(inputFile):
    dirList = []
    labelList = []
    print("\nParsing input file: ", inputFile)
    with open(inputFile) as openFileObject:
        for fileLine in openFileObject:
            fileLine = fileLine[:-1]   # Remove trailing newline
            if (fileLine[0] == "#"):
                print("  Ignoring comment line: ", fileLine)
            else:
                splitFileLine = fileLine.split(maxsplit=1)
                if (len(splitFileLine) == 1):
                    dirLine = fileLine
                    dirJetto = dirLine.split("/")
                    labelLine = dirJetto[-1]
                else:
                    dirLine = splitFileLine[0]
                    labelLine = splitFileLine[1]
                if (not os.path.exists(dirLine)):
                    print("  Input directory ", dirLine, " does not exist")
                    sys.exit(5)
                dirList.append(dirLine)
                labelList.append(labelLine)
                print("  JETTO output plot directory: " + dirLine)
    print("JETTO output plot list file parsed.", len(dirList),                \
          "output plot directories added.\n")
    return(dirList, labelList)

###############################################################################

# Extract setting/value pairs from the settings file in the JETTO donor
# directory

def extractJettoSettings(dir):
    setFile = "jetto.jset"
    settingList = []
    valueList = []
    with open(dir+"/"+setFile) as openFileObject:
        for fileLine in openFileObject:
            colonInd = fileLine.find(":")
            if (colonInd != -1):
                lStr = fileLine[0:colonInd-1]
                lStr = lStr.strip()
                rStr = fileLine[colonInd+1:-1]
                rStr = rStr.strip()
                settingList.append(lStr)
                valueList.append(rStr)
    return(settingList, valueList)

###############################################################################

# Extract setting/value pairs from the settings file in each directory
# Creates lists of lists; 1st index: #dir, 2nd index: setting/value

def extractCoconutSettings(dirList):
    settingLists = []
    valueLists = []
    setFile = "edge2d.coset"
    for i, dir in enumerate(dirList):
        settingList = []
        valueList = []
        with open(dir+"/"+setFile) as openFileObject:
            for fileLine in openFileObject:
                colonInd = fileLine.find(":")
                if (colonInd != -1):
                    lStr = fileLine[0:colonInd-1]
                    lStr = lStr.strip()
                    rStr = fileLine[colonInd+1:-1]
                    rStr = rStr.strip()
                    settingList.append(lStr)
                    valueList.append(rStr)
        settingLists.append(settingList)
        valueLists.append(valueList)
    return(settingLists, valueLists) 

###############################################################################

# Check that specified input files are consistent
# Then copy over to the output directory, overwriting as needed

def compareAndCopyInputFiles(fileList, dirList, printLabel, outFileName):

    # Compare input files
    print("Comparing " + printLabel + " input files")
    previousDirIndex = -1
    for i, dir in enumerate(dirList):
        inputFiles = [dir + "/" + inputFile for inputFile in fileList]
        notFoundFiles = {f for f in inputFiles if not os.path.isfile(f)}
        if (len(notFoundFiles) == len(inputFiles)):
            print("Directory " + dir + " contains no " + printLabel +         \
                  " input files - skipping...")
        elif (len(notFoundFiles) == 0):
            if (previousDirIndex != -1):
                for j, File in enumerate(inputFiles):
                    oldFile = dirList[previousDirIndex]+"/"+fileList[j]
                    fileComp = filecmp.cmp(oldFile, File, shallow=False)
                    if (not fileComp):
                        print(printLabel + " input files " + oldFile +        \
                              " and " + File + " differ")
#                        sys.exit(101)
            previousDirIndex = i
        else:
            print("Directory " + dir + " contains an incomplete set of " +    \
                  printLabel + " input files")
            sys.exit(102)
    print(printLabel + " input files consistent between COCONUT runs")

    # Copy over files to output directory
    for i, File in enumerate(inputFiles):
        shutil.copy(File, outFileName[i])
    
    return

###############################################################################

# Handle ex-file

def exFile(dirList, datDir, fileCoconut, outputDir):
    exFile = ["jetto.ex"]
    exDir = datDir + "/exfile"
    if (not os.path.exists(exDir)):
        os.mkdir(exDir)
    outFileName = [exDir + "/" +                                              \
                  (fileCoconut[::-1].split(".",1))[-1][::-1] + ".ex"]
    print("Writing Ex-File for JETTO input " + f"{outFileName}...")
    compareAndCopyInputFiles(exFile, dirList, "Ex-File", outFileName)
    modifyJsetValue(outputDir, "SetUpPanel.exFileName", outFileName[0], False)
    modifyJsetValue(outputDir, "SetUpPanel.exFilePrvDir", exDir, False)
    modifyJsetValue(outputDir, "SetUpPanel.exFileSource", "Private", False)
    print()
    return(outFileName)

###############################################################################

# Modify ex-file to reflect initial conditions

# Run is fully predictive, so only need initial time point

# Adapted from Ziga Stancar's set-exfile-profiles.py

def modifyExFile(dirCoconut, newExFile, ECRHflag):
    exFile = dirCoconut + "/jetto.ex"
    jspFile = dirCoconut + "/jetto.jsp"

    vars_remove = ["XRHO","R","XVEC1","TVEC1","RA","SPSI","PSI","RHO"]
    ecrhVarsRemove = ["QECE", "JZEC"]
    if (ECRHflag):
        for ecrhVarRemove in ecrhVarsRemove:
            vars_remove.append([ecrhVarRemove])

    exData_allvars = []
    exData = binary.read_binary_file(exFile)
    exData["variables"] = [var for var in exData]
    info_index = exData["variables"].index("DDA NAME")
    exData_allvars.extend(exData["variables"][info_index+1:-1])
    exData_allvars =  list(set(exData_allvars))

    for i in vars_remove:
        if i in exData_allvars:
            exData_allvars.remove(i)

    exData_allvars_nonzero = np.zeros(len(exData_allvars), dtype=int)
    jsp = {}
    jspRead = binary.read_binary_file(jspFile)
    for i, var in enumerate(exData_allvars):
        if exData[var].any():
            exData_allvars_nonzero[i] = int(1)
        if exData_allvars_nonzero[i].any():
            var_tmp = interpolate.interp1d(
                    jspRead["XVEC1"][0,:], jspRead[var][0,:], 
                    kind="linear", fill_value="extrapolate")
            for t in range(len(exData["TVEC1"])):
                exData[var][t] = var_tmp(exData["XVEC1"][0,:])

    tmp_exData = exData
    del tmp_exData["variables"]
    binary.write_binary_exfile(tmp_exData, newExFile)
    
    return

###############################################################################

# Handle boundary file

def boundaryFile(dirList, datDir, fileCoconut, outputDir):
    boundaryFile = ["jetto.bnd"]
    bndDir = datDir + "/boundary"
    if (not os.path.exists(bndDir)):
        os.mkdir(bndDir)
    outFileName = [bndDir + "/" +                                             \
                  (fileCoconut[::-1].split(".",1))[-1][::-1] + ".bnd"]
    print("Writing boundary file for JETTO input " + f"{outFileName}...")
    compareAndCopyInputFiles(boundaryFile, dirList, "boundary",outFileName)
    modifyJsetValue(outputDir, "EquilEscoRefPanel.bndFileName",               \
                    outFileName[0], False)
    modifyJsetValue(outputDir, "EquilEscoRefPanel.bndFilePrvDir",             \
                    bndDir, False)
    modifyJsetValue(outputDir, "EquilEscoRefPanel.bndFileSource",             \
                    "Private", False)
    print()
    return

###############################################################################

# Handle GRAY input files

# Having demonstrated consistency between files, check that graybeam.data is
# up to date. If not, use the updated version.

def grayInputFiles(dirList, datDir, fileCoconut, outputDir, graybeamFlag):
    grayInputFiles = ["gray.data", "graybeam.data"]
    ecrhDir = datDir + "/ecrh"
    if (not os.path.exists(ecrhDir)):
        os.mkdir(ecrhDir)
    filePrefix = (fileCoconut[::-1].split(".",1))[-1][::-1] + "_"
    outFileName = [ecrhDir + "/" + filePrefix + x for x in grayInputFiles]
    print("Writing GRAY files for JETTO input " + f"{outFileName}...")
    compareAndCopyInputFiles(grayInputFiles, dirList, "GRAY", outFileName)
    # Compare to 2023 updated graybeam.data
    refUpdateFile = "/home/dtaylor/cmg/jams/data/ecrh/graybeam_updated.data"
    fileComp = filecmp.cmp(outFileName[1], refUpdateFile, shallow=False)
    if (not fileComp):
        print("WARNING: used input file " + outFileName[1] +                  \
              " differs from updated reference version " + refUpdateFile + ".")
    if (graybeamFlag):
        print("Using updated reference version instead.")
        shutil.copy(refUpdateFile, outFileName[1])
    modifyJsetValue(outputDir, "ECRHPanel.GRAYFileName", outFileName[0], False)
    modifyJsetValue(outputDir, "ECRHPanel.GRAYPrvDir", ecrhDir, False)
    modifyJsetValue(outputDir, "ECRHPanel.GRAYSource", "Private", False)
    modifyJsetValue(outputDir, "ECRHPanel.GRAYBeamFileName", outFileName[1],  \
                    False)
    modifyJsetValue(outputDir, "ECRHPanel.GRAYBeamPrvDir", ecrhDir, False)
    modifyJsetValue(outputDir, "ECRHPanel.GRAYBeamSource", "Private", False)
    print()
    return

###############################################################################

# Verify and read all JST files

def readJstFiles(dirList):
    print("Reading in JST files from directories")
    jstRead = []
    for i, dir in enumerate(dirList):
        print("  Directory " + str(i+1) + " of " + str(len(dirList)))
        jstFile = dir + "/jetto.jst"
        if (not os.path.exists(jstFile)):
            print("Directory " + dir + " does not contain JST file")
            sys.exit(202)
        jstTmp = binary.read_binary_file(jstFile)
        jstRead.append(jstTmp)
    print("All JST files read\n")
    return(jstRead)

###############################################################################

# Verify and read all JSP files

def readJspFiles(dirList):
    print("Reading in JSP files from directories")
    jspRead = []
    for i, dir in enumerate(dirList):
        print("  Directory " + str(i+1) + " of " + str(len(dirList)))
        jspFile = dir + "/jetto.jsp"
        if (not os.path.exists(jspFile)):
            print("Directory " + dir + " does not contain JSP file")
            sys.exit(201)
        jspTmp = binary.read_binary_file(jspFile)
        jspRead.append(jspTmp)
    print("All JSP files read\n")
    return(jspRead)

###############################################################################

# Savitzky-Golay smoothing filter

def savitzky_golay(y, window_size, order, deriv=0, rate=1):
    window_size = np.abs(int(window_size))
    order = np.abs(int(order))
    order_range = range(order + 1)
    half_window = (window_size - 1) // 2
    # precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in                          \
                range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * math.factorial(deriv)
    # pad the signal at the extremes with values taken from the signal itself
    firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve( m[::-1], y, mode="valid")

###############################################################################

# Modify an entry in jetto.jset in the output directory

def modifyJsetValue(outputDir, key, value, quiet):
    fileJset = outputDir + "/jetto.jset"
    # Escape control chars in key
    modifiedKey = re.sub(r"\.", r"\.", key)  # escaping both strings is correct
    modifiedKey = re.sub(r"\[", r"\[", modifiedKey)
    modifiedKey = re.sub(r"\]", r"\]", modifiedKey)
    modifiedKey = re.sub(r"\s", r"\\s", modifiedKey)
    modifiedKey = re.sub(r"\(", r"\(", modifiedKey)
    modifiedKey = re.sub(r"\)", r"\)", modifiedKey)
    modifiedKey = re.sub(r"\+", r"\+", modifiedKey)
    # Read existing jset
    file = open(fileJset, "r+")
    text = file.readlines()
    file.close()
    # Parse file
    # First look for the key and modify it if found
    lineRegex = r"(^" + modifiedKey + r"\s*:\s*)[A-Za-z0-9\+-_./\s,()]*\n"
    keyMatch     = False
    settingMatch = False
    for i, line in enumerate(text):
        # Note the end of the settings block in case we need to manipulate it
        if (settingMatch):
            setEndMatch = re.search(r"^\*", line)
            if (setEndMatch):
                indEndSetting = i
        # Note the start of the settings block in case we need to manipulate it
        setMatch = re.search(r"^\*Settings", line)
        if (setMatch):
            settingMatch = True
            indSetting = i
        match = re.search(lineRegex, line)
        # Matching key?
        if (match):
            if (not quiet):
                print("    Modifying key " + key + " in file " + fileJset +   \
                      ": " + value)
            keyMatch = True
            modifiedLine = match.groups(0)[0] + value + "\n"
            text[i] = re.sub(lineRegex, modifiedLine, line)
    # If not found, add it to the settings block, and alphabetise the block
    if (not keyMatch):
        if (not quiet):
            print("    Adding key " + key + " to file " + fileJset + ": " +   \
                  value)
        nCharBeforeColon = 60
        lenWhitespace = nCharBeforeColon - len(key)
        wspace = " " * lenWhitespace
        newLine = key + wspace + ": " + value + "\n"
        text.insert(indSetting+1, newLine)
        text[indSetting+1:indEndSetting] =                                    \
                               sorted(text[indSetting+1:indEndSetting])
    # Write the file back
    with open(fileJset, "w") as file:
        file.writelines(text)
    return

###############################################################################

# Tidy up the Extra Namelist section of jetto.jset in the output directory

# Only the first n=32 array listings are actually read. The rest are ignored.
# Take any listings within the first n that are turned off and delete them.
# Also delete any beyond the first n, and any in the old three-line format.

def tidyExtraNamelist(outputDir, settingListJetto, valueListJetto):
    # Find currently defined length of extra namelist
    keyRows = "OutputExtraNamelist.selItems.rows"
    nRows = getValueFromCoconutList(settingListJetto, valueListJetto, keyRows)
    nRows = int(nRows)
    # Read existing jset
    fileJset = outputDir + "/jetto.jset"
    file = open(fileJset, "r+")
    text = file.readlines()
    file.close()
    # Remove existing extra namelist items above currently specified size of
    # extra namelist array
    # Search through file for extra namelist items and remove as needed
    # Use index 3 - will find all newer four-line format entries
    key3 = r"^OutputExtraNamelist\.selItems\.cell\[([0-9]+)\]\[3\]\s*:" +     \
           r"\s*([a-zA-Z0-9]+)\s*$"
    key2 = r"^OutputExtraNamelist\.selItems\.cell\[([0-9]+)\]\[2\]\s*:" +     \
           r"\s*[a-zA-Z0-9]*\s*$"
    match3PrevInd = -1
    for i in range(len(text)-1, -1, -1):
        line = text[i]
        # Match index 3 to find four-line format entries
        match3 = re.search(key3, line)
        if (match3):
            match3PrevInd = i
            match3Ind = int(match3.groups(0)[0])
            if (match3Ind >= nRows):
                # Remove this line and previous 3
                for j in range(0, 4):
                    text.pop(i-j)
                i = i - 4
        # Match index 2 if previous line didn't match index 3
        match2 = re.search(key2, line)
        if (match2):
            match2Ind = int(match2.groups(0)[0])
            if (match3PrevInd - i != 1 and match2Ind >= nRows):
                # Remove this line and previous 2
                for j in range(0, 3):
                    text.pop(i-j)
                i = i - 3

    # Write the file back
    with open(fileJset, "w") as file:
        file.writelines(text)

    # Pass through again to deduce largest new index
    indexMax = -1
    for i, line in enumerate(text):
        match3 = re.search(key3, line)
        if (match3):
            keyIndex = int(match3.groups(0)[0])
            if (keyIndex > indexMax):
                indexMax = keyIndex
    modifyJsetValue(outputDir, "OutputExtraNamelist.selItems.rows",           \
                    str(indexMax), True)

    return

###############################################################################

# Modify an Extra Namelist entry in jetto.jset in the output directory

def modifyExtraNamelist(outputDir, key, value, turnOn, quiet):
    nPossibleExtraNamelist = 32    # Indices from this up are ignored by JAMS
    
    fileJset = outputDir + "/jetto.jset"
    # Read existing jset
    file = open(fileJset, "r+")
    text = file.readlines()
    file.close()

    # First determine the largest current Extra Namelist index
    modifiedKey =                                                             \
           r"^OutputExtraNamelist\.selItems\.cell\[([0-9]+)\]\[0\]\s*:\s*"    \
             + key + r"\s*$"
    indexKey = r"^OutputExtraNamelist\.selItems\.cell\[([0-9]+)\]"
    indexMax = -1
    for i, line in enumerate(text):
        indexMatch = re.search(indexKey, line)
        if (indexMatch):
            indexInd = int(indexMatch.groups(0)[0])
            if (indexInd > indexMax):
                indexMax = indexInd
    # Then determine which indices up to that are already in use
    # Note if we find our variable
    varOn = np.zeros([indexMax+1]).astype("bool")
    keyMatch = False
    for i, line in enumerate(text):
        match = re.search(modifiedKey, line)
        indexMatch = re.search(indexKey, line)
        if (match):
            keyIndex = match.groups(0)[0]
            keyMatch = True
        if (indexMatch):
            indexInd = int(indexMatch.groups(0)[0])
            varOn[indexInd] = True
    # Modify .jset
    if (turnOn):
        turnOnStr = "true"
    else:
        turnOnStr = "false"
    keyPrefix = "OutputExtraNamelist.selItems.cell["
    if (keyMatch):
        modifyJsetValue(outputDir, keyPrefix+str(keyIndex)+"][1]", key,   \
                        quiet)
        modifyJsetValue(outputDir, keyPrefix+str(keyIndex)+"][1]", "",    \
                        quiet)
        modifyJsetValue(outputDir, keyPrefix+str(keyIndex)+"][2]", value, \
                        quiet)
        modifyJsetValue(outputDir, keyPrefix+str(keyIndex)+"][3]",        \
                        turnOnStr,quiet)
    else:
        newInd = np.where(varOn == False)
        try:
            newInd = newInd[0][0]
        except:
            newInd = len(varOn)
        if (newInd >= nPossibleExtraNamelist):
            modifyJsetValue(outputDir, "OutputExtraNamelist.selItems.rows",   \
                            str(newInd+1), True)
        modifyJsetValue(outputDir, keyPrefix+str(newInd)+"][0]", key, quiet)
        modifyJsetValue(outputDir, keyPrefix+str(newInd)+"][1]", "", quiet)
        modifyJsetValue(outputDir, keyPrefix+str(newInd)+"][2]", value, quiet)
        modifyJsetValue(outputDir, keyPrefix+str(newInd)+"][3]", turnOnStr,   \
                        quiet)
    return

###############################################################################

# Erase Jset settings for a panel

# Assumes key name starts with supplied name string

def eraseJsetPanel(outputDir, name):
    fileJset = outputDir + "/jetto.jset"
    # Read existing jset
    file = open(fileJset, "r+")
    text = file.readlines()
    file.close()
    # List panel entries in existing jset
    key = r"(^" + name +                                                      \
          r"[A-Za-z0-9.\[\]\(\)-+\s]*[A-Za-z0-9.\[\]\(\)-+])\s+:"
    for i, line in enumerate(text):
        match = re.search(key, line)
        if (match):
            modifyJsetValue(outputDir, match.groups(0)[0], " ", True)
    return

###############################################################################

# Set Jset transport panel settings from COCONUT sequence

def setCoconutJsetTransportPanel(outputDir, settingLists, valueLists,         \
                                 dirCoconutList, tOffsetList, t0List, t1List):
    
    # Get H-mode onset time from COCONUT runs
    lhKey = "TransportETBPanel.LHTransition"
    keyVals = getValueFromCoconutLists(settingLists, valueLists, lhKey)
    tLHs = np.array([])
    for i, keyVal in enumerate(keyVals):
        tLHs = np.append(tLHs, float(keyVal) + tOffsetList[i])
    if not allSame(keyVals):
        print("Variation in LH transition time between COCONUT runs:")
        print(tLHs)
        tLH = tLHs[-1]
        print("Setting LH transition time to " + str(tLH) + " seconds")
#        sys.exit(301)

    # Take the latest COCONUT run, and, provided that it is later than the
    # LH transition time, copy the transport panel settings from that run.
    #     NB This may need reworking later, if the sequence goes all the way
    #        through into the ramp-down phase.
    # Exclude:
    #    TransportAndELMSPanel - in COCONUT-specific settings
    #    TransportELMSPanel    - found under MHD panel - duplicate anyhow?
    # Don't exclude:
    #    TransportERdPanel     - seems to be obsolete? Possible check with FK.
    t0 = str(t0List[-1])
    t1 = str(t1List[-1])
    if (float(t1) < tLH):
        print("Final COCONUT run in the sequence before LH transition")
#        sys.exit(302)
    print("    Copying transport panel settings from COCONUT run " +          \
          dirCoconutList[-1] + ", which covers the time period from "         \
          + t0 + " to " + t1 + " seconds")
    panelRegex = r"^Transport(?!AndELMSPanel)(?!ELMSPanel)"
    for i, key in enumerate(settingLists[-1]):
        match = re.search(panelRegex, key)
        if (match):
            modifyJsetValue(outputDir, key, valueLists[-1][i], True)
    # Reset LH transition adjusted for run time offset
    # This needs to be after the above full-panel write
    modifyJsetValue(outputDir, lhKey, str(tLH), True)
    print("Transport panel copied to jetto.jset")

    return

###############################################################################

# Set Jset ELM panel settings from COCONUT sequence

def setCoconutJsetElmPanel(outputDir, settingLists, valueLists,               \
                                 dirCoconutList, tOffsetList, t0List, t1List):
    
    # Take the latest COCONUT run, copy the ELM panel settings from that run.
    #     NB This may need reworking later, if the sequence goes all the way
    #        through into the ramp-down phase.
    # Include:
    #    ELM*               - various subheadings within main ELMs panel
    #    TransportELMSPanel - found under MHD panel - duplicate anyhow?
    t0 = str(t0List[-1])
    t1 = str(t1List[-1])
    print("    Copying ELM panel settings from COCONUT run " +                \
          dirCoconutList[-1] + ", which covers the time period from "         \
          + t0 + " to " + t1 + " seconds")
    panelRegex = r"^ELM"
    for i, key in enumerate(settingLists[-1]):
        match = re.search(panelRegex, key)
        if (match):
            modifyJsetValue(outputDir, key, valueLists[-1][i], True)
    panelRegex = r"^TransportELMSPanel"
    for i, key in enumerate(settingLists[-1]):
        match = re.search(panelRegex, key)
        if (match):
            modifyJsetValue(outputDir, key, valueLists[-1][i], True)
    print("ELM panel copied to jetto.jset")

    return

###############################################################################

# Set Jset Sawteeth panel settings from COCONUT sequence

def setCoconutJsetSawteethPanel(outputDir, settingLists, valueLists,          \
                                dirCoconutList, tOffsetList, t0List, t1List):
    
    # Take the latest COCONUT run that uses sawtooth settings, and copy the
    # panel settings from that run.
    #     NB This may need reworking later, if the sequence goes all the way
    #        through into the ramp-down phase.
    # Include:
    #    Sawteeth Panel - main sawteeth panel
    #    KdSawPanel     - Kadomtsev options subpanel
    key = "SawteethPanel.select"
    keyVals = getValueFromCoconutLists(settingLists, valueLists, key)
    findSawteeth = False
    for i, val in enumerate(keyVals):
        if (val == "true"):
            findSawteeth = True
            maxSawteethRun = i
    if (findSawteeth):          
        t0 = str(t0List[maxSawteethRun])
        t1 = str(t1List[maxSawteethRun])
        print("    Copying Sawteeth panel settings from COCONUT run " +       \
              dirCoconutList[maxSawteethRun] +                                \
              ", which covers the time period from "                          \
              + t0 + " to " + t1 + " seconds")
        panelRegex = r"^Sawteeth"
        for i, key in enumerate(settingLists[maxSawteethRun]):
            match = re.search(panelRegex, key)
            if (match):
                modifyJsetValue(outputDir, key,                               \
                                valueLists[maxSawteethRun][i], True)
        panelRegex = r"^Kdsaw"
        for i, key in enumerate(settingLists[maxSawteethRun]):
            match = re.search(panelRegex, key)
            if (match):
                modifyJsetValue(outputDir, key,                               \
                                valueLists[maxSawteethRun][i], True)
        print("Sawteeth panel copied to jetto.jset")
    else:
        modifyJsetValue(outputDir, key, "false", True)
        print("Sawteeth not found in COCONUT; panel switched off")

    return

###############################################################################

# Set Jset Neutrals panel settings from COCONUT sequence

def setCoconutJsetNeutralsPanel(outputDir, settingLists, valueLists,          \
                                dirCoconutList, tOffsetList, t0List, t1List):
    
    # Take the latest COCONUT run that uses neutrals settings, and copy the
    # panel settings from that run.
    #     NB This may need reworking later, if the sequence goes all the way
    #        through into the ramp-down phase.
    # Include:
    #    NeutralSourcePanel - main neutrals panel
    #    NeutEireneDialog   - EIRENE pop-out
    #    FranticPanel       - Frantic pop-out

    key = "NeutralSourcePanel.select"
    keyVals = getValueFromCoconutLists(settingLists, valueLists, key)
    findNeutrals = False
    for i, val in enumerate(keyVals):
        if (val == "true"):
            findNeutrals = True
            maxNeutralsRun = i
    if (findNeutrals):          
        t0 = str(t0List[maxNeutralsRun])
        t1 = str(t1List[maxNeutralsRun])
        print("    Copying Neutrals panel settings from COCONUT run " +       \
              dirCoconutList[maxNeutralsRun] +                                \
              ", which covers the time period from "                          \
              + t0 + " to " + t1 + " seconds")
        panelRegex = r"^NeutralSource"
        for i, key in enumerate(settingLists[maxNeutralsRun]):
            match = re.search(panelRegex, key)
            if (match):
                modifyJsetValue(outputDir, key,                               \
                                valueLists[maxNeutralsRun][i], True)
        panelRegex = r"^NeutEirene"
        for i, key in enumerate(settingLists[maxNeutralsRun]):
            match = re.search(panelRegex, key)
            if (match):
                modifyJsetValue(outputDir, key,                               \
                                valueLists[maxNeutralsRun][i], True)
        panelRegex = r"^Frantic"
        for i, key in enumerate(settingLists[maxNeutralsRun]):
            match = re.search(panelRegex, key)
            if (match):
                modifyJsetValue(outputDir, key,                               \
                                valueLists[maxNeutralsRun][i], True)
        print("Neutrals panel copied to jetto.jset")
    else:
        modifyJsetValue(outputDir, key, "false", True)
        print("Neutrals not found in COCONUT; panel switched off")

    return

###############################################################################

# L-H transition power threshold settings

def lhTransition(outputDir, settingLists, valueLists):
    # Is model on?
    # Note that IPWDEP appears multiple times in some edge2d.cosets, e.g.
    # /home/gcor/cmg/catalog/edge2d/iter/53298X/aug1422/seq#1/edge2d.coset
    # Assume this is a bug? Reported to Francis Casson. The first will be
    # detected here.
    ipwdepInds, ipwdepArr, ipwdepNames, ipwdepVals, ipwdepOns =               \
          findExtraNamelist(settingLists, valueLists, "IPWDEP")
    fpwdepInds, fpwdepArr, fpwdepNames, fpwdepVals, fpwdepOns =               \
          findExtraNamelist(settingLists, valueLists, "FPWDEP")
    tpwdepInds, tpwdepArr, tpwdepNames, tpwdepVals, tpwdepOns =               \
          findExtraNamelist(settingLists, valueLists, "TPWDEP")
    rpwdepInds, rpwdepArr, rpwdepNames, rpwdepVals, rpwdepOns =               \
          findExtraNamelist(settingLists, valueLists, "RPWDEP")
    # Find latest run with model on and whether parameters are used.
    lhFound = False
    fFound = False
    fpwdepArr = np.array([])
    tpwdepArr = np.array([])
    rpwdepArr = np.array([])
    fpwdepDefault = 1.0
    tpwdepDefault = 0.0
    rpwdepDefault = 0.0
    for i, run in enumerate(settingLists):
        if (ipwdepOns[i]):
            lhFound = True
            maxIpwdepOn = i
            if (fpwdepOns[i]):
                fpwdepArr = np.append(fpwdepArr, float(fpwdepVals[i]))
            else:
                fpwdepArr = np.append(fpwdepArr, fpwdepDefault)
            if (tpwdepOns[i]):
                tpwdepArr = np.append(tpwdepArr, float(tpwdepVals[i]))
            else:
                tpwdepArr = np.append(tpwdepArr, tpwdepDefault)
            if (rpwdepOns[i]):
                rpwdepArr = np.append(rpwdepArr, float(rpwdepVals[i]))
            else:
                rpwdepArr = np.append(rpwdepArr, rpwdepDefault)
        else:
            fpwdepArr = np.append(fpwdepArr, "Not found")
            tpwdepArr = np.append(tpwdepArr, "Not found")
            rpwdepArr = np.append(rpwdepArr, "Not found")
    # Is there variation between COCONUT runs?
    if (not allSame(ipwdepVals)):
        print("    Variation in IPWDEP between COCONUT runs;  taking " +      \
              "latest run: " + dirCoconutList[maxIpwdepOn] +                  \
              ", which covers the time period from "                          \
              + t0 + " to " + t1 + " seconds")
    # Modfy .jset
    if (lhFound):
        modifyExtraNamelist(outputDir, "IPWDEP", ipwdepVals[maxIpwdepOn],     \
                            True, True)
        """
        modifyExtraNamelist(outputDir, "FPWDEP", fpwdepVals[maxIpwdepOn],     \
                            True, True)
        modifyExtraNamelist(outputDir, "TPWDEP", tpwdepVals[maxIpwdepOn],     \
                            True, True)
        modifyExtraNamelist(outputDir, "RPWDEP", rpwdepVals[maxIpwdepOn],     \
                            True, True)
        """
    else:
        print("    IPWDEP not found - turning off setting")
        modifyExtraNamelist(outputDir, "IPWDEP", 0, False, True)
    return

###############################################################################

# Are all values of a list identical?

def allSame(list):
    return all(x == list[0] for x in list)

###############################################################################

# Get sequence of values for a .jset key from the COCONUT sequence

def getValueFromCoconutLists(settingLists, valueLists, key):
    keyVals = np.array([])
    for i, settingList in enumerate(settingLists):
        ind = settingList.index(key)
        keyVals = np.append(keyVals, valueLists[i][ind])
    return(keyVals)

###############################################################################

# Get value for a .jset key from a single COCONUT run

def getValueFromCoconutList(settingList, valueList, key):
    ind = settingList.index(key)
    keyVal = valueList[ind]
    return(keyVal)

###############################################################################

# Smooth the given boundary condition data from JSP, and write it out to a
# JETTO input boundary condition file

# Modified from Ziga Stancar's time-dependent-boundary-condition.py

def smoothAndWriteBoundaryCondition(jsRead, type, boundDir, outputDir,        \
                                    fileCoconut, tOffsetList,                 \
                                    tLabel, dLabel, mult, foSuffix,           \
                                    dispLabel, dispUnits, plot):
    # Collate the data
    dat = {}
    datBoundary = np.array([])
    time = np.array([])
    for i, js in enumerate(jsRead):
        if (type == "T"):    # JST
            datBoundary = np.append(datBoundary, js[dLabel])
            jsTime = js[tLabel][:,0] + tOffsetList[i]
        elif (type == "P"):  # JSP
            dat = js[dLabel]
            datBoundary = np.append(datBoundary, dat[:,-1])
            jsTime = js[tLabel][:,0,0] + tOffsetList[i]
        time = np.append(time, jsTime)
    timeSort = np.argsort(time)
    datBoundary = datBoundary[timeSort] * mult
    time = time[timeSort]

    # Divide up data by any time gaps within it
    dtGap = 0.2
    tGapInd = np.where(time[1:]-time[:-1] > dtGap)
    tGapInd = np.append(-1, tGapInd)
    tGapInd = np.append(tGapInd, -1)

    # Set up parameters for the Savitzky-Gokay smoothing
    dtSmWind = 0.05     # Time duration of Savitzky-Golay smoothing window
    smWind = math.ceil(dtSmWind * len(time) / (np.max(time)-np.min(time)))
    sgOrd = 3           # Savitzky-Golay order
    dtInterp = 0.5      # Equidistant time grid for boundary file interpolation

    # Smooth each range
    tInterp = np.array([])
    datInterp = np.array([])
    for i, gap in enumerate(tGapInd):
        if (i > 0):
            timeRange = time[tGapInd[i-1]+1:tGapInd[i]]
            datRange = datBoundary[tGapInd[i-1]+1:tGapInd[i]]
            # Apply the Savitzky-Golay filter to the data
            interpStepNum = math.ceil( (np.max(timeRange)-np.min(timeRange))  \
                                       / dtInterp )
            sgWinSize = int(len(timeRange) / smWind)
            interp = interpolate.interp1d(timeRange,                          \
                                     savitzky_golay(datRange,sgWinSize,sgOrd),\
                                                    fill_value="extrapolate")
            interpTime = np.linspace(np.min(timeRange),np.max(timeRange),    \
                                     num=interpStepNum, endpoint=True)
            interpArray = interp(interpTime)
            tInterp = np.append(tInterp, interpTime)
            datInterp = np.append(datInterp, interpArray)

    # Write out the JETTO input file to data/boundcond
    # Take the name as that of the COCONUT input file, without the final ".dat"
    outFileName = boundDir + "/" +                                            \
                  (fileCoconut[::-1].split(".",1))[-1][::-1] + "." + foSuffix
    out = open(outFileName, "w")
    for j in range(len(tInterp)):
        out.write(f"{tInterp[j]:.3f},{datInterp[j]:.3f}\n")
    out.close()
    print("  " + dispLabel + " boundary condition JETTO input file " +        \
          outFileName + " written")

    # Make plots if desired
    if plot:
        plt.figure()
        plt.plot(time, datBoundary, color="r",                                \
          label="COCONUT simulation sequence")
        plt.plot(tInterp, datInterp, color="g",                               \
          label=f"Savitzky-Golay smoothing")
        plt.xlabel("Time [s]")
        plt.ylabel(dispLabel + " [" + dispUnits + "]")
        plt.legend()

    return(outFileName)

###############################################################################

# Create JETTO Ip boundary condition input file from COCONUT PPF output

def makeIpBoundaryConditionFile(jstRead, boundDir, fileCoconut, outputDir,    \
                                tOffsetList, plot):
    type      = "T"
    tVar      = "TVEC1"
    dVar      = "CUR"
    foSuffix  = "cup"
    dispLabel = "Ip"
    dispUnits = "A"
    mult      = 1
    outFileName = smoothAndWriteBoundaryCondition(jstRead, type,              \
                                    boundDir, outputDir, fileCoconut,         \
                                    tOffsetList,                              \
                                    tVar, dVar, mult, foSuffix,               \
                                    dispLabel, dispUnits, plot)
    modifyJsetValue(outputDir, "EquationsPanel.current.usage",                \
                    "Predictive", False)
    modifyJsetValue(outputDir, "BoundCondPanel.current.fileName",             \
                    outFileName, False)
    modifyJsetValue(outputDir, "BoundCondPanel.current.filePrvDir",           \
                    boundDir, False)
    modifyJsetValue(outputDir, "BoundCondPanel.current.fileSource",           \
                    "Private", False)
    modifyJsetValue(outputDir, "BoundCondPanel.current.option",               \
                    "From File", False)
    return

###############################################################################

# Create JETTO Te boundary condition input file from COCONUT PPF output

def makeTeBoundaryConditionFile(jspRead, boundDir, fileCoconut, outputDir,    \
                                tOffsetList, plot):
    type      = "P"
    tVar      = "TIME"
    dVar      = "TE"
    foSuffix  = "tep"
    dispLabel = "Te"
    dispUnits = "eV"
    mult      = 1
    outFileName = smoothAndWriteBoundaryCondition(jspRead, type,              \
                                    boundDir, outputDir, fileCoconut,         \
                                    tOffsetList,                              \
                                    tVar, dVar, mult, foSuffix,               \
                                    dispLabel, dispUnits, plot)
    modifyJsetValue(outputDir, "EquationsPanel.eleTemp.usage",                \
                    "Predictive", False)
    modifyJsetValue(outputDir, "BoundCondPanel.eleTemp.fileName",             \
                    outFileName, False)
    modifyJsetValue(outputDir, "BoundCondPanel.eleTemp.filePrvDir",           \
                    boundDir, False)
    modifyJsetValue(outputDir, "BoundCondPanel.eleTemp.fileSource",           \
                    "Private", False)
    modifyJsetValue(outputDir, "BoundCondPanel.eleTemp.option",               \
                    "From File", False)
    return

###############################################################################

# Create JETTO Ti boundary condition input file from COCONUT PPF output

def makeTiBoundaryConditionFile(jspRead, boundDir, fileCoconut, outputDir,    \
                                tOffsetList, plot):
    type      = "P"
    tVar      = "TIME"
    dVar      = "TI"
    foSuffix  = "tip"
    dispLabel = "Ti"
    dispUnits = "eV"
    mult      = 1
    outFileName = smoothAndWriteBoundaryCondition(jspRead, type,              \
                                    boundDir, outputDir, fileCoconut,         \
                                    tOffsetList,                              \
                                    tVar, dVar, mult, foSuffix,               \
                                    dispLabel, dispUnits, plot)
    modifyJsetValue(outputDir, "EquationsPanel.ionTemp.usage",                \
                    "Predictive", False)
    modifyJsetValue(outputDir, "BoundCondPanel.ionTemp.fileName",             \
                    outFileName, False)
    modifyJsetValue(outputDir, "BoundCondPanel.ionTemp.filePrvDir",           \
                    boundDir, False)
    modifyJsetValue(outputDir, "BoundCondPanel.ionTemp.fileSource",           \
                    "Private", False)
    modifyJsetValue(outputDir, "BoundCondPanel.ionTemp.option",               \
                    "From File", False)
    return

###############################################################################

# Create JETTO Ni(1) and Ni(2) boundary condition input files from COCONUT PPF
# output

# NB Only hydrogenic species are handled

def makeNiBoundaryConditionFiles(jspRead, boundDir, fileCoconut, outputDir,   \
                                 tOffsetList, settingLists, valueLists,       \
                                 settingListJetto, valueListJetto, plot):

    mult = 1e-6    # JSP has m^-3; .ni1p and .ni2p need cm^-3
    
    # Which ions are in the reference run series, and in which proportions?
    # Assume ion 1 is turned on - makes no sense otherwise
    i1MassVals = getValueFromCoconutLists(settingLists, valueLists,           \
                                          "EquationsPanel.ionDens[0].mass")
    # Is ion 2 turned on?
    i2On = getValueFromCoconutLists(settingLists, valueLists,                 \
                                    "EquationsPanel.ionDens[1].usage")
    i2MassVals = getValueFromCoconutLists(settingLists, valueLists,           \
                                          "EquationsPanel.ionDens[1].mass")

    # COCONUT ion density
    i1Boundary = np.array([])
    i2Boundary = np.array([])
    time       = np.array([])
    for i, jsp in enumerate(jspRead):
        # Ion 1
        if (float(i1MassVals[i]) == 1.0):
            dat = jsp["NIH"]
        elif (float(i1MassVals[i]) == 2.0):
            dat = jsp["NID"]
        elif (float(i1MassVals[i]) == 3.0):
            dat = jsp["NIT"]
        else:
            print("Unknown ion(1) mass: " + i1MassVals[i])
            sys.exit(801)
        i1Boundary = np.append(i1Boundary, dat[:,-1])
        # Ion 2
        if (i2On[i] != "Off"):
            if (float(i2MassVals[i]) == 1.0):
                dat = jsp["NIH"]
            elif (float(i2MassVals[i]) == 2.0):
                dat = jsp["NID"]
            elif (float(i2MassVals[i]) == 3.0):
                dat = jsp["NIT"]
            else:
                print("Unknown ion(2) mass: " + i2MassVals[i])
                sys.exit(802)
            i2Boundary = np.append(i2Boundary, dat[:,-1])
        else:
            i2Boundary = np.append(i2Boundary, dat[:,-1]*0.0)
        # Time
        jspTime = jsp["TIME"][:,0,0] + tOffsetList[i]
        time = np.append(time, jspTime)
    timeSort = np.argsort(time)
    # Total density
    niBoundary = i1Boundary + i2Boundary
    niBoundary = niBoundary[timeSort] * mult
    time = time[timeSort]

    # Divide up data by any time gaps within it
    dtGap = 0.2
    tGapInd = np.where(time[1:]-time[:-1] > dtGap)
    tGapInd = np.append(-1, tGapInd)
    tGapInd = np.append(tGapInd, -1)

    # Set up parameters for the Savitzky-Gokay smoothing
    dtSmWind = 0.05      # Time duration of Savitzky-Golay smoothing window
    smWind = math.ceil(dtSmWind * len(time) / (np.max(time)-np.min(time)))
    sgOrd = 3           # Savitzky-Golay order
    dtInterp = 0.5      # Equidistant time grid for boundary file interpolation

    # Smooth each range
    tInterp = np.array([])
    niInterp = np.array([])
    for i, gap in enumerate(tGapInd):
        if (i > 0):
            timeRange = time[tGapInd[i-1]+1:tGapInd[i]]
            niRange = niBoundary[tGapInd[i-1]+1:tGapInd[i]]
            if (i > 1):
                # If this range begins lower than the last one ended, set
                # values to the previous range end value until they exceed it
                if (True):
                    niPrevEnd = niBoundary[tGapInd[i-1]]
                    j = 0
                    while (niRange[j] < niPrevEnd):
                        niRange[j] = niPrevEnd
                        j = j + 1
                # If this range begins lower than the last one, add the
                # difference to it
                if (False):
                    niPrevEnd = niBoundary[tGapInd[i-1]]
                    niThisStart = niBoundary[tGapInd[i-1]+1]
                    dNi = niPrevEnd - niThisStart
                    for j in range(0, len(niRange)):
                        niRange[j] = niRange[j] + dNi
            
            # Apply the Savitzky-Golay filter to the data
            interpStepNum = math.ceil( (np.max(timeRange)-np.min(timeRange))  \
                                       / dtInterp )
            sgWinSize = int(len(timeRange) / smWind)
            interp = interpolate.interp1d(timeRange,                          \
                                     savitzky_golay(niRange,sgWinSize,sgOrd), \
                                                    fill_value="extrapolate")
            interpTime = np.linspace(np.min(timeRange),np.max(timeRange),     \
                                     num=interpStepNum, endpoint=True)
            interpArray = interp(interpTime)
            tInterp = np.append(tInterp, interpTime)
            niInterp = np.append(niInterp, interpArray)            

    # Take the desired ion fractions from the donor run
    i1MassOut = getValueFromCoconutList(settingListJetto, valueListJetto,     \
                                        "EquationsPanel.ionDens[0].mass")
    i1FracOut = getValueFromCoconutList(settingListJetto, valueListJetto,     \
                                        "EquationsPanel.ionDens[0].fraction")
    # Is ion 2 turned on?
    i2OnOut = getValueFromCoconutList(settingListJetto, valueListJetto,       \
                                        "EquationsPanel.ionDens[1].usage")
    i2MassOut = getValueFromCoconutList(settingListJetto, valueListJetto,     \
                                        "EquationsPanel.ionDens[1].mass")
    i2FracOut = getValueFromCoconutList(settingListJetto, valueListJetto,     \
                                        "EquationsPanel.ionDens[1].fraction")

    # Write out the JETTO input files to data/boundcond
    # Take the name as that of the COCONUT input file, without the final ".dat"
    # Ion 1
    i1FracOut = float(i1FracOut)
    outFileName = boundDir + "/" +                                            \
                  (fileCoconut[::-1].split(".",1))[-1][::-1] + ".ni1p"
    out = open(outFileName, "w")
    for j in range(len(tInterp)):
        out.write(f"{tInterp[j]:.3f},{niInterp[j]*i1FracOut:.3f}\n")
    out.close()
    print("  Ni(1) boundary condition JETTO input file " +        \
          outFileName + " written")
    modifyJsetValue(outputDir, "EquationsPanel.ionDens[0].usage",             \
                    "Predictive", False)
    modifyJsetValue(outputDir, "BoundCondPanel.ionDens[0].fileName",          \
                    outFileName, False)
    modifyJsetValue(outputDir, "BoundCondPanel.ionDens[0].filePrvDir",        \
                    boundDir, False)
    modifyJsetValue(outputDir, "BoundCondPanel.ionDens[0].fileSource",        \
                    "Private", False)
    modifyJsetValue(outputDir, "BoundCondPanel.ionDens[0].option",            \
                    "From File", False)
    # Ion 2
    if (i2OnOut != "Off"):
        i2FracOut = float(i2FracOut)
        outFileName = boundDir + "/" +                                        \
                      (fileCoconut[::-1].split(".",1))[-1][::-1] + ".ni2p"
        out = open(outFileName, "w")
        for j in range(len(tInterp)):
            out.write(f"{tInterp[j]:.3f},{niInterp[j]*i2FracOut:.3f}\n")
        out.close()
        print("  Ni(2) boundary condition JETTO input file " +    \
              outFileName + " written")        
        modifyJsetValue(outputDir, "EquationsPanel.ionDens[1].usage",         \
                        "Predictive", False)
        modifyJsetValue(outputDir, "BoundCondPanel.ionDens[1].fileName",      \
                        outFileName, False)
        modifyJsetValue(outputDir, "BoundCondPanel.ionDens[1].filePrvDir",    \
                        boundDir, False)
        modifyJsetValue(outputDir, "BoundCondPanel.ionDens[1].fileSource",    \
                        "Private", False)
        modifyJsetValue(outputDir, "BoundCondPanel.ionDens[1].option",        \
                        "From File", False)

    # Make plots if desired
    if plot:
        plt.figure()
        plt.plot(time, niBoundary, color="r",                                 \
                 label="COCONUT simulation sequence")
        plt.plot(tInterp, niInterp, color="yellow",                           \
                 label=f"Total ni smoothed")
        plt.plot(tInterp, niInterp*i1FracOut, color="g",                      \
                 label=f"Species 1")
        if (i2OnOut != "Off"):
            plt.plot(tInterp, niInterp*i2FracOut, color="b",                  \
                     label=f"Species 2")
        plt.xlabel("Time [s]")
        plt.ylabel("ni [cm$^-3$]")
        plt.legend()

    return

###############################################################################

# Create JETTO vtor boundary condition input file from COCONUT PPF output

def makeVtorBoundaryConditionFile(jspRead, boundDir, fileCoconut, outputDir,  \
                                  tOffsetList, plot):
    type      = "P"
    tVar      = "TIME"
    dVar      = "VTOR"
    foSuffix  = "evp"
    dispLabel = "vtor"
    dispUnits = "cm/s"
    mult      = 1e2     # JSP has m/s; .evp needs cm/s
    outFileName = smoothAndWriteBoundaryCondition(jspRead, type,              \
                                    boundDir, outputDir, fileCoconut,         \
                                    tOffsetList,                              \
                                    tVar, dVar, mult, foSuffix,               \
                                    dispLabel, dispUnits, plot)
    modifyJsetValue(outputDir, "BoundCondPanel.edgeVel.fileName",             \
                    outFileName, False)
    modifyJsetValue(outputDir, "BoundCondPanel.edgeVel.filePrvDir",           \
                    boundDir, False)
    modifyJsetValue(outputDir, "BoundCondPanel.edgeVel.fileSource",           \
                    "Private", False)
    modifyJsetValue(outputDir, "BoundCondPanel.edgeVel.option",               \
                    "From File", False)
    return

###############################################################################

# Return start and end times list for given sequence

def timeStartEnd(jstRead, tOffsets):
    t0 = np.array([])
    t1 = np.array([])
    for i in range(0, len(tOffsets)):
        tArr = jstRead[i]["TVEC1"][:,0] + tOffsets[i]
        t0 = np.append(t0, np.min(tArr))
        t1 = np.append(t1, np.max(tArr))
    return(t0, t1)

###############################################################################

# Remove duplicate points from time polygons
# Can take single or multiple value numpy array arguments in addition to the
# numpy time array

def simplifyTimePolygon(timeIn, *argsIn):
    time = copy.copy(timeIn)
    args = list(argsIn)

    # Error checking
    #  Non-matching arrays
    argLens = np.array([len(time)])
    for ar in args:
        argLens = np.append(argLens, len(ar))
    if (not allSame(argLens)):
        print("Time and data have different array lengths")
        return
    #  No changes possible
    if (len(time) < 3):
        return

    # Check for more than two successive identical sets of values. Remove
    # middle time points. Work backwards in array to avoid indexing problems
    count = 1
    lastVal = np.array([])
    for ar in args:
        lastVal = np.append(lastVal, ar[-1])
    for i in range(len(time)-2, -1, -1):
        matchVals = True
        for j, ar in enumerate(args):
            if (ar[i] != lastVal[j]):
                matchVals = False
        if (matchVals):
            count = count + 1
        else:
            if (count > 2):
                time = np.delete(time, list(range(i+2,i+count)))
                for j, ar in enumerate(args):
                    ar = np.delete(ar, list(range(i+2,i+count)))
                    args[j] = ar
            count = 1
            lastVal = np.array([])
            for ar in args:
                lastVal = np.append(lastVal, ar[i])
    if (count > 2):
        time = np.delete(time, list(range(1,count-1)))
        for j, ar in enumerate(args):
            ar = np.delete(ar, list(range(i+2,i+count)))
            args[j] = ar
    argsOut = tuple(args)
    
    return(time, *argsOut)

###############################################################################

# Combine ECRH heating waveforms from COCONUT sequence

def makeEcrh(settingLists, valueLists, outputDir, tOffsets, ecrhOns,          \
             t0overall, t1overall, t0List, t1List, dirCoconutList, plot):

    eps = 1e-5

    # Check consistency of source
    # Can potentially handle multiple sources, but leave for now as more
    #  complicated and not yet needed.
    ecrhSrcs = getValueFromCoconutLists(settingLists, valueLists,             \
                                       "ECRHPanel.source")
    for i in range(len(settingLists)-1, -1, -1):
        if (not ecrhOns[i]):
            ecrhSrcs = np.delete(ecrhSrcs, i)
    if (not allSame(ecrhSrcs)):
        print("Differing ECRH sources between COCONUT runs in sequence:")
        print(ecrhSrcs)
        sys.exit(401)
    ecrhSrc = ecrhSrcs[0]
    modifyJsetValue(outputDir, "ECRHPanel.source", ecrhSrc, True)

    # Different sources
    if (ecrhSrc == "GRAY"):
        if (plot):
            ecrhFig, ecrhAx = plt.subplots(nrows=3, ncols=1, figsize=(10,10), \
                                           sharex=True, sharey=False)
            ecrhLegend = np.array([])

        # Definitions
        nLauncher = 20
        # Better generic way to list these?
        launcherList = list(map(str, list(range(1,1+nLauncher,1))))
        launcherList = ["Beam " + s for s in launcherList]

        # When are launchers turned on?
        launcherOn = [False] * len(launcherList)
        launcherOnList =                                                      \
                np.zeros([len(launcherList), len(settingLists)]).astype("bool")
        for i, launcher in enumerate(launcherList):
            keyPrefix = "ECRHPanel.ECRHGray[" + str(i) + "]."
            key = keyPrefix + "selectBeam"
            launcherOnRuns = getValueFromCoconutLists(settingLists,           \
                                                         valueLists, key)
            for j, settingList in enumerate(settingLists):
                if (ecrhOns[j]):
                    if (launcherOnRuns[j] == "false"):
                        launcherOnList[i, j] = False
                    elif (launcherOnRuns[j] == "true"):
                        launcherOnList[i, j] = True
            if (any(launcherOnList[i])):
                # Set normalisation values for time polygon
                launcherOn[i] = True
                modifyJsetValue(outputDir, key, "true", True)
                modifyJsetValue(outputDir, keyPrefix+"selectInputPower",      \
                                "true", True)
                modifyJsetValue(outputDir, keyPrefix+"selectPolInj",          \
                                "true", True)
                modifyJsetValue(outputDir, keyPrefix+"selectTorInj",          \
                                "true", True)
                modifyJsetValue(outputDir, keyPrefix+"powec", "1.0", True)
                modifyJsetValue(outputDir, keyPrefix+"angpec", "0.0", True)
                modifyJsetValue(outputDir, keyPrefix+"angtec", "0.0", True)
            else:
                modifyJsetValue(outputDir, key, "false", True)
        # Turn off Beam 10: EL_BOT_XM for specific runs where it was
        # accidentally left on, but had low absorption. This can cause problems
        # when our new JETTO regime has better absorption.
        noBeam10List = [
            "/home/stholer/cmg/catalog/edge2d/iter/53298X/dec2022/seq#1",
            "/home/stholer/cmg/catalog/edge2d/iter/53298X/mar0223/seq#2",
            "/home/stholer/cmg/catalog/edge2d/iter/53298X/mar0423/seq#2",
            "/home/stholer/cmg/catalog/edge2d/iter/53298X/mar0923/seq#1",
            "/home/stholer/cmg/catalog/edge2d/iter/53298X/mar1323/seq#1",
            "/home/stholer/cmg/catalog/edge2d/iter/53298X/mar1723/seq#2",
            "/home/stholer/cmg/catalog/edge2d/iter/53298X/mar2023/seq#1",
            "/home/stholer/cmg/catalog/edge2d/iter/53298X/mar2323/seq#1",
            "/home/stholer/cmg/catalog/edge2d/iter/53298X/mar2723/seq#1",
            "/home/stholer/cmg/catalog/edge2d/iter/53298X/mar3023/seq#1",
            "/home/stholer/cmg/catalog/edge2d/iter/53298X/apr0223/seq#1",
            "/home/stholer/cmg/catalog/edge2d/iter/53298X/apr0623/seq#1",
            "/home/stholer/cmg/catalog/edge2d/iter/53298X/apr0923/seq#1",
            "/home/stholer/cmg/catalog/edge2d/iter/53298X/apr1223/seq#1",
            "/home/stholer/cmg/catalog/edge2d/iter/53298X/apr1723/seq#1",
            "/home/stholer/cmg/catalog/edge2d/iter/53298X/apr2023/seq#1",
            "/home/stholer/cmg/catalog/edge2d/iter/53298X/apr2723/seq#1",
            "/home/stholer/cmg/catalog/edge2d/iter/53298X/may0723/seq#1",
            "/home/stholer/cmg/catalog/edge2d/iter/53298X/may1223/seq#2",
            "/home/stholer/cmg/catalog/edge2d/iter/53298X/may1623/seq#1",
            "/home/stholer/cmg/catalog/edge2d/iter/53298X/may2023/seq#1",
            "/home/stholer/cmg/catalog/edge2d/iter/53298X/jun2223/seq#1",
            "/home/stholer/cmg/catalog/edge2d/iter/53298X/jul0523/seq#1",
            "/home/stholer/cmg/catalog/edge2d/iter/53298X/jul0923/seq#1",
            "/home/stholer/cmg/catalog/edge2d/iter/53298X/jul1523/seq#1"]
        for i, run1 in enumerate(dirCoconutList):
            for j, run2 in enumerate(noBeam10List):
                if (run1 == run2):
                    launcherOnList[9,i] = False

        # These fields need to match between COCONUT runs
        # 'CAll' seems to be correct, despite 'Call' clearly being intended
        matchValues = ["GRAYCAllInterval"]
        # Do the above fields match across the COCONUT sequence?
        for i, matchValue in enumerate(matchValues):
            key = "ECRHPanel." + matchValue
            matchVals = getValueFromCoconutLists(settingLists, valueLists, key)
            valsOn = []
            for j, settingList in enumerate(settingLists):
                if (ecrhOns[j]):
                    valsOn.append(matchVals[j])
            if (not allSame(valsOn)):
                print("    Differing values in .jset key " + key + ":")
                print("    ", valsOn)
                if (matchValue == "GRAYCAllInterval"):
                    minCallInterval = 0.1
                    vals = np.array(list(map(float, valsOn)))
                    valMin = np.min(vals)
                    if (valMin < minCallInterval):
                        print("    Setting GRAYCallInterval to " +            \
                              str(minCallInterval) + " seconds")
                        valMin = minCallInterval
                    else:
                        print("    Setting GRAYCallInterval to minimum " +    \
                              "value: " + str(valMin))
                modifyJsetValue(outputDir, key, str(valMin), True)
#                sys.exit(403)
            else:
                modifyJsetValue(outputDir, key, valsOn[0], True)

        # Cross-check launcher labels for all launchers, even if not on
        nameBeamRef = []
        for i, launcher in enumerate(launcherList):
            nameBeam = []
            keyPrefix = "ECRHPanel.ECRHGray[" + str(i) + "]."
            for j, settingList in enumerate(settingLists):
                # Get normalisation and multipliers
                flag = getValueFromCoconutList(                       \
                               settingList, valueLists[j], keyPrefix+"beam")
                nameBeam.append(flag)
            if (not allSame(nameBeam)):
                print("Differing ECRH launcher labels in Beam " + str(i) + ":")
                sys.exit(404)
            nameBeamRef.append(nameBeam[0])
            modifyJsetValue(outputDir, keyPrefix+"beam", nameBeam[0], True)

        # For launchers that are on, build time polygons
        tPolyQuants = ["powec",                                               \
                       "angpec",                                              \
                       "angtec"]
        for i, launcher in enumerate(launcherList):
            if (launcherOn[i]):
                # Initialise time polygons
                tPowPoly = np.array([])
                powPoly = np.array([])
                tPolPoly = np.array([])
                polPoly = np.array([])
                tTorPoly = np.array([])
                torPoly = np.array([])

                # Loop through run sequence, building time polygons
                keyPrefix = "ECRHPanel.ECRHGray[" + str(i) + "]."
                t0 = -1e-10
                t1 = -1e-10
                for j, settingList in enumerate(settingLists):
                    t0 = t0List[j]
                    if (t0 < t1):   # Remove run overlap
                        t0 = t1
                    t1 = t1List[j]
                    # Only consider if this COCONUT had this launcher on
                    if (launcherOnList[i,j]):
                        # Get normalisation and multipliers

                        powMult = float(getValueFromCoconutList(              \
                                       settingList, valueLists[j],            \
                                       keyPrefix+"powec"))
                        polAdd = float(getValueFromCoconutList(               \
                                       settingList, valueLists[j],            \
                                       keyPrefix+"angpec"))
                        torAdd = float(getValueFromCoconutList(               \
                                       settingList, valueLists[j],            \
                                       keyPrefix+"angtec"))
                        # Are there time polygons?
                        for k, quant in enumerate(tPolyQuants):
                            if (quant == "powec"):
                                keyEnd = "selectInputPower"
                            elif (quant == "angpec"):
                                keyEnd = "selectPolInj"
                            elif (quant == "angtec"):
                                keyend = "selectTorInj"
                            else:
                                sys.exit(405)
                            tPolySelS = getValueFromCoconutList(              \
                                                  settingList, valueLists[j], \
                                                  keyPrefix+keyEnd)
                            tPolyTemp = np.array([])
                            valPolyTemp = np.array([])
                            if (tPolySelS == "true"):
                                # Retrieve data
                                nPoly = 0
                                nInd  = -1
                                while True:
                                    nInd = nInd + 1
                                    try:
                                        polyFlag = getValueFromCoconutList(   \
                                                   settingList, valueLists[j],\
                                                   keyPrefix+quant+           \
                                                           ".tpoly.select["+  \
                                                           str(nInd)+"]")
                                        if (polyFlag == "true"):
                                            nPoly = nPoly + 1
                                            tPolyTemp = np.append(            \
                                                  tPolyTemp, float(     \
                                                  getValueFromCoconutList(    \
                                                   settingList, valueLists[j],\
                                                   keyPrefix+quant+           \
                                                        ".tpoly.time["+       \
                                                         str(nInd)+"]") ))
                                            if (quant == "powec"):
                                                valPolyTemp = np.append(      \
                                                  valPolyTemp,                \
                                                    powMult*float(            \
                                                 getValueFromCoconutList(     \
                                                   settingList, valueLists[j],\
                                                   keyPrefix+quant+           \
                                                        ".tpoly.value["+      \
                                                         str(nInd)+"][0]") ))
                                            elif (quant == "angpec"):
                                                valPolyTemp = np.append(      \
                                                  valPolyTemp,                \
                                                    polAdd+float(             \
                                                 getValueFromCoconutList(     \
                                                   settingList, valueLists[j],\
                                                   keyPrefix+quant+           \
                                                        ".tpoly.value["+      \
                                                         str(nInd)+"][0]") ))
                                            elif (quant == "angtec"):
                                                valPolyTemp = np.append(      \
                                                  valPolyTemp,                \
                                                    polAdd+float(             \
                                                 getValueFromCoconutList(     \
                                                   settingList, valueLists[j],\
                                                   keyPrefix+quant+           \
                                                        ".tpoly.value["+      \
                                                         str(nInd)+"][0]") ))
                                            else:
                                                sys.exit(405)
                                    except:
                                        break
                                    
                                # Sort time points
                                sortInd = np.argsort(tPolyTemp)
                                tPolyTemp = tPolyTemp[sortInd]
                                valPolyTemp = valPolyTemp[sortInd]
                                # Add time offset
                                tPolyTemp = tPolyTemp + tOffsets[j]
                                if (len(tPolyTemp) > 0):
                                    # Are time points before this run?
                                    if (tPolyTemp[0] < t0):
                                        tBefInd = np.where(tPolyTemp < t0)
                                        prevInd = np.max(tBefInd)
                                        if (tPolyTemp[prevInd+1] > t0):
                                            tPolyTemp[prevInd] = t0
                                            if (prevInd > 0):
                                                tBefInd = np.delete(tBefInd,  \
                                                                    prevInd)
                                                tPolyTemp = np.delete(        \
                                                         tPolyTemp, tBefInd)
                                                valPolyTemp = np.delete(      \
                                                       valPolyTemp, tBefInd)
                                        else:
                                            tPolyTemp = np.delete(        \
                                                         tPolyTemp, tBefInd)
                                            valPolyTemp = np.delete(      \
                                                       valPolyTemp, tBefInd)
                                    # Are time points after this run?
                                    if (tPolyTemp[-1] > t1):
                                        tAftInd = np.where(tPolyTemp >= t1)
                                        nextInd = np.min(tAftInd)
                                        tPolyTemp = np.delete(tPolyTemp,      \
                                                                tAftInd)
                                        valPolyTemp = np.delete(valPolyTemp,  \
                                                                tAftInd)
                                # Add remaining time points to the overall
                                # time polygon
                                if (quant == "powec"):
                                    tPowPoly = np.append(tPowPoly,   tPolyTemp)
                                    powPoly  = np.append( powPoly, valPolyTemp)
                                elif (quant == "angpec"):
                                    tPolPoly = np.append(tPolPoly,   tPolyTemp)
                                    polPoly  = np.append( polPoly, valPolyTemp)
                                elif (quant == "angtec"):
                                    tTorPoly = np.append(tTorPoly,   tPolyTemp)
                                    torPoly  = np.append( torPoly, valPolyTemp)
                                else:
                                    sys.exit(405)
                                
                            else:
                                if (quant == "powec"):
                                    tPowPoly = np.append(tPowPoly, t0)
                                    powPoly  = np.append(powPoly, powMult)
                                elif (quant == "angpec"):
                                    tPolPoly = np.append(tPolPoly, t0)
                                    polPoly  = np.append(polPoly, polAdd)
                                elif (quant == "angtec"):
                                    tTorPoly = np.append(tTorPoly, t0)
                                    torPoly  = np.append(torPoly, torAdd)
                                else:
                                    sys.exit(405)
                    else:
                        # Launcher is off - check it wasn't previously left on
                        if (j > 0):
                            if (launcherOnList[i,j-1] == True):
                                # Set to zero from this time
                                tPowPoly = np.append(tPowPoly,                \
                                                    [t0List[j]-eps, t0List[j]])
                                powPoly  = np.append( powPoly,                \
                                                      [powPoly[-1], 0.0])
                        
                # Check that we have found some nonzero power
                # Else turn the launcher off again
                if (len(powPoly) > 0):
                    if (np.max(powPoly) > 0):
                        # Add points at start to zero the waveforms
                        # We can account for eps edge cases later
                        # if we need to
                        if (tPowPoly[0]-eps > t0overall):
                            tPowPoly = np.insert(tPowPoly, 0,                 \
                                                 [t0overall,tPowPoly[0]-eps])
                            powPoly = np.insert(powPoly, 0, [0.0,0.0])
                        if (tPolPoly[0]-eps > t0overall):
                            tPolPoly = np.insert(tPolPoly, 0,                 \
                                                 [t0overall,tPolPoly[0]-eps])
                            polPoly = np.insert(polPoly, 0, [0.0,0.0])
                        if (tTorPoly[0]-eps > t0overall):
                            tTorPoly = np.insert(tTorPoly, 0,                 \
                                                 [t0overall,tTorPoly[0]-eps])
                            torPoly = np.insert(torPoly, 0, [0.0,0.0])

                        # Add points at end to zero the waveform
                        if (tPowPoly[-1]+eps < t1overall):
                            tPowPoly = np.append(tPowPoly,                \
                                                 [t1overall,t1overall+eps])
                            powPoly = np.append(powPoly, [powPoly[-1],0.0])
                        if (tPolPoly[-1]+eps < t1overall):
                            tPolPoly = np.append(tPolPoly,                \
                                                 [t1overall,t1overall+eps])
                            polPoly = np.append(polPoly, [polPoly[-1],0.0])
                        if (tTorPoly[-1]+eps < t1overall):
                            tTorPoly = np.append(tTorPoly,                \
                                                 [t1overall,t1overall+eps])
                            torPoly = np.append(torPoly, [torPoly[-1],0.0])

                        # Simplify the time polygons
                        tPowPoly, powPoly =                                   \
                                  simplifyTimePolygon(tPowPoly, powPoly)
                        tPolPoly, polPoly =                                   \
                                  simplifyTimePolygon(tPolPoly, polPoly)
                        tTorPoly, torPoly =                                   \
                                  simplifyTimePolygon(tTorPoly, torPoly)

                        # Write out the time polygons
                        for j in range(0, len(tPowPoly)):
                            modifyJsetValue(outputDir,                    \
                                 keyPrefix+"powec.tpoly.select["+str(j)+"]",  \
                                 "true", True)
                            modifyJsetValue(outputDir,                    \
                                 keyPrefix+"powec.tpoly.time["+str(j)+"]",    \
                                 str(tPowPoly[j]), True)
                            modifyJsetValue(outputDir,                    \
                                 keyPrefix+"powec.tpoly.value["+str(j)+"][0]",\
                                 str(powPoly[j]), True)
                        for j in range(0, len(tPolPoly)):
                            modifyJsetValue(outputDir,                    \
                                 keyPrefix+"angpec.tpoly.select["+str(j)+"]", \
                                 "true", True)
                            modifyJsetValue(outputDir,                    \
                                 keyPrefix+"angpec.tpoly.time["+str(j)+"]",   \
                                 str(tPolPoly[j]), True)
                            modifyJsetValue(outputDir,                    \
                                 keyPrefix+"angpec.tpoly.value["+str(j)+      \
                                            "][0]", str(polPoly[j]), True)
                        for j in range(0, len(tTorPoly)):
                            modifyJsetValue(outputDir,                    \
                                 keyPrefix+"angtec.tpoly.select["+str(j)+"]", \
                                 "true", True)
                            modifyJsetValue(outputDir,                    \
                                 keyPrefix+"angtec.tpoly.time["+str(j)+"]",   \
                                 str(tTorPoly[j]), True)
                            modifyJsetValue(outputDir,                    \
                                 keyPrefix+"angtec.tpoly.value["+str(j)+      \
                                            "][0]", str(torPoly[j]), True)

                        # Plot
                        if (plot):
                            ecrhAx[0].plot(tPowPoly, powPoly)
                            ecrhAx[1].plot(tPolPoly, polPoly)
                            ecrhAx[2].plot(tTorPoly, torPoly)
                            ecrhLegend = np.append(ecrhLegend,                \
                                    launcherList[i]+" ("+nameBeamRef[i]+")")

                    else:
                            modifyJsetValue(outputDir,                       \
                                  keyPrefix+ "selectBeam", "false", True)
                else:
                    modifyJsetValue(outputDir,                           \
                              keyPrefix+ "selectBeam", "false", True)
        if (plot):
            ecrhAx[0].title.set_text("Combined ECRH time polygons")
            ecrhAx[0].set_ylabel("Power [W]")
            ecrhAx[1].set_ylabel("Poloidal angle [deg]")
            ecrhAx[2].set_ylabel("Toroidal angle [deg]")
            ecrhAx[2].set_xlabel("Time [s]")
            ecrhAx[0].legend(ecrhLegend)

    else:
        print("ECRH source '" + ecrhSrc + "' not yet handled")
        sys.exit(402)

    return

###############################################################################

# Combine NBI heating waveforms from COCONUT sequence

def makeNbi(settingLists, valueLists, outputDir, tOffsets, nbiOns,            \
            t0overall, t1overall, t0List, t1List, dirCoconutList, plot):

    eps = 1e-5

    # Check consistency of source
    # Can potentially handle multiple sources, but leave for now as more
    #  complicated and not yet needed.
    nbiSrcs = getValueFromCoconutLists(settingLists, valueLists,              \
                                       "NBIPanel.source")
    for i in range(len(settingLists)-1, -1, -1):
        if (not nbiOns[i]):
            nbiSrcs = np.delete(nbiSrcs, i)
    if (not allSame(nbiSrcs)):
        print("Differing NBI sources between COCONUT runs in sequence:")
        print(nbiSrcs)
        sys.exit(501)
    nbiSrc = nbiSrcs[0]
    modifyJsetValue(outputDir, "NBIPanel.source", nbiSrc, True)

    # Different sources
    if (nbiSrc == "Pencil"):

        if (plot):
            nbiFig, nbiAx = plt.subplots(nrows=4, ncols=1, figsize=(10,10), \
                                           sharex=True, sharey=False)
            nbiLegend = np.array([])

        nbiPencilSrcs = getValueFromCoconutLists(settingLists, valueLists,    \
                                                     "NBIPencilRef.source")
        if (not allSame(nbiPencilSrcs)):
            print("Differing NBI sources between COCONUT runs in seq:")
            print(nbiSrcs)
            sys.exit(503)
        nbiPencilSrc = nbiPencilSrcs[0]
        modifyJsetValue(outputDir, "NBIPencilRef.source", nbiPencilSrc, True)
        if (nbiPencilSrc == "Beam Boxes"):

            # Definitions
            octList = ["4", "8", "H"]  # Better generic way to list these?
            nPini = 12                 # Seems hardcoded into JINTRAC?
            piniList = [" "] * nPini   # Empty string doesn't work?
            for i, pini in enumerate(piniList):  # To match .jset defs
                if (i < 8):
                    piniList[i] = "pini[" + str(i) + "]"
                else:
                    piniList[i] = "pini1[" + str(i-8) + "]"
                
            # When are octants turned on?
            octOn = [False] * len(octList)
            octOnList =                                                       \
                np.zeros([len(octList), len(settingLists)]).astype("bool")
            for i, octant in enumerate(octList):
                key = "NBIPencilBoxRef.selectBeamBox[" + str(i) + "]"
                octOnRuns = getValueFromCoconutLists(settingLists,            \
                                                         valueLists, key)
                for j, settingList in enumerate(settingLists):
                    if (octOnRuns[j] == "false"):
                        octOnList[i, j] = False
                    elif (octOnRuns[j] == "true"):
                        octOnList[i, j] = True
                if (any(octOnList[i])):
                    octOn[i] = True
                    modifyJsetValue(outputDir, key, "true", True)
                else:
                    modifyJsetValue(outputDir, key, "false", True)
            # Turn off Octant H for specific runs where it was
            # accidentally turned on
            noOctHList = [
                "/home/lgarzot/cmg/catalog/edge2d/iter/53298X/jun1723/seq#1"]
            for i, run1 in enumerate(dirCoconutList):
                for j, run2 in enumerate(noOctHList):
                    if (run1 == run2):
                        octOnList[2,i] = False
    
            # These fields need to match between COCONUT runs
            # 'mass' not used
            matchValues = ["beamFraction[0]",                                 \
                           "beamFraction[1]",                                 \
                           "beamFraction[2]",                                 \
                           "boxType",                                         \
                           "ionEnergy",                                       \
                           "ionMass",]
            # Do the above fields match when the octant is on?
            for i, octant in enumerate(octList):
                if (octOn[i]):
                    for j, matchValue in enumerate(matchValues):
                        key = "NBIPencilBoxDialog["+str(i)+"]." + matchValue
                        matchVals = getValueFromCoconutLists(settingLists,    \
                                                               valueLists, key)
                        valsOn = []
                        for k, settingList in enumerate(settingLists):
                            if (octOnList[i, k]):
                                valsOn.append(matchVals[k])
                        if (not allSame(valsOn)):
                            print("Differing values in .jset key " + key + ":")
                            print(valsOn)
                            sys.exit(505)
                        modifyJsetValue(outputDir, key, valsOn[0], True)
            
            # Which PINIs are on?
            piniOn = np.zeros([len(octList), nPini]).astype("bool")
            for i, octant in enumerate(octList):
                if (octOn[i]):
                    for j, pini in enumerate(piniList):
                        key = "NBIPencilBoxDialog[" + str(i) + "]." + pini
                        piniOnList = getValueFromCoconutLists(                \
                                                 settingLists, valueLists, key)
                        piniOns = np.zeros([len(octList), nPini,              \
                                             len(settingLists)]).astype("bool")
                        for k, piniSett in enumerate(piniOnList):
                            if (piniSett == "true"):
                                piniOns[i, j, k] = True
                                piniOn[i, j] = True
                        if (piniOn[i, j] == True):
                            modifyJsetValue(outputDir, key, "true", True)
                        else:
                            modifyJsetValue(outputDir, key, "false", True)

            # For octants that are on, build a time polygon
            t0 = -1e-10
            t1 = -1e-10
            for i, octant in enumerate(octList):
                if (octOn[i]):
                    # Initialise time polygons
                    timePoly = np.array([])
                    powerPoly = np.array([])
                    srcPoly = np.array([])
                    currentPoly = np.array([])
                    torquePoly = np.array([])
                    # Set time polygon options
                    keyPrefix = "NBIPencilBoxDialog[" + str(i) + "]."
                    key = keyPrefix + "optionTpoly"
                    modifyJsetValue(outputDir, key, "Dialog", True)
                    key = keyPrefix + "selectTpoly"
                    modifyJsetValue(outputDir, key, "true", True)
                    # Loop through run sequence, building time polygons
                    for j, settingList in enumerate(settingLists):
                        t0 = t0List[j]
                        if (t0 < t1):   # Remove run overlap
                            t0 = t1
                        t1 = t1List[j]
                        # Only consider if this COCONUT  had this octant on
                        if (nbiOns[j] and octOnList[i, j]):
                            # Get normalisation and multipliers
                            multFlag = []
                            multVal  = []
                            for k in range(0, 4):
                                flag = getValueFromCoconutList(               \
                                           settingList, valueLists[j],        \
                                           keyPrefix+"selectValue["+str(k)+"]")
                                if (flag == "true"):
                                    multFlag.append(True)
                                    val = float(getValueFromCoconutList(      \
                                                settingList, valueLists[j],\
                                                keyPrefix+"value["+str(k)+"]"))
                                    multVal.append(val)
                                else:
                                    multFlag.append(False)
                                    multVal.append(1.0)
                            # Is there a time polygon?
                            tPolySelS = getValueFromCoconutList(              \
                                                  settingList, valueLists[j], \
                                                  keyPrefix+"selectTpoly")
                            timePolyTemp = np.array([])
                            powerPolyTemp = np.array([])
                            srcPolyTemp = np.array([])
                            currentPolyTemp = np.array([])
                            torquePolyTemp = np.array([])
                            if (tPolySelS == "true"):
                                # Retrieve data
                                nPoly = 0
                                nInd  = -1
                                while True:
                                    nInd = nInd + 1
                                    try:
                                        polyFlag = getValueFromCoconutList(   \
                                                   settingList, valueLists[j],\
                                                   keyPrefix+"tpoly.select["  \
                                                             +str(nInd)+"]")
                                        if (polyFlag == "true"):
                                            nPoly = nPoly + 1
                                            timePolyTemp = np.append(         \
                                                  timePolyTemp, float(        \
                                                  getValueFromCoconutList(    \
                                                   settingList, valueLists[j],\
                                                   keyPrefix+"tpoly.time["    \
                                                         +str(nInd)+"]") )) 
                                            powerPolyTemp = np.append(        \
                                                  powerPolyTemp,              \
                                                    multVal[0]*float(         \
                                                 getValueFromCoconutList(     \
                                                   settingList, valueLists[j],\
                                                   keyPrefix+"tpoly.value["   \
                                                         +str(nInd)+"][0]") ))
                                            srcPolyTemp = np.append(          \
                                                  srcPolyTemp,                \
                                                    multVal[1]*float(         \
                                                 getValueFromCoconutList(     \
                                                   settingList, valueLists[j],\
                                                   keyPrefix+"tpoly.value["   \
                                                         +str(nInd)+"][1]") ))
                                            currentPolyTemp = np.append(      \
                                                  currentPolyTemp,            \
                                                    multVal[2]*float(         \
                                                 getValueFromCoconutList(     \
                                                   settingList, valueLists[j],\
                                                   keyPrefix+"tpoly.value["   \
                                                         +str(nInd)+"][2]") ))
                                            torquePolyTemp = np.append(       \
                                                  torquePolyTemp,             \
                                                    multVal[3]*float(         \
                                                 getValueFromCoconutList(     \
                                                   settingList, valueLists[j],\
                                                   keyPrefix+"tpoly.value["   \
                                                         +str(nInd)+"][3]") ))
                                    except:
                                        break
                                # Sort time points
                                sortInd = np.argsort(timePolyTemp)
                                timePolyTemp = timePolyTemp[sortInd]
                                powerPolyTemp = powerPolyTemp[sortInd]
                                srcPolyTemp = srcPolyTemp[sortInd]
                                currentPolyTemp = currentPolyTemp[sortInd]
                                torquePolyTemp = torquePolyTemp[sortInd]
                                # Add time offset
                                timePolyTemp = timePolyTemp + tOffsets[j]
                                # Are time points before this run?
                                if (timePolyTemp[0] < t0):
                                    tBefInd = np.where(timePolyTemp < t0)
                                    prevInd = np.max(tBefInd)
                                    if (timePolyTemp[prevInd+1] > t0):
                                        timePolyTemp[prevInd] = t0
                                        if (prevInd > 0):
                                            tBefInd = np.delete(tBefInd,      \
                                                                prevInd)
                                            timePolyTemp = np.delete(         \
                                                      timePolyTemp, tBefInd)
                                            powerPolyTemp = np.delete(        \
                                                      powerPolyTemp, tBefInd)
                                            srcPolyTemp = np.delete(          \
                                                      srcPolyTemp, tBefInd)
                                            currentPolyTemp = np.delete(      \
                                                      currentPolyTemp, tBefInd)
                                            torquePolyTemp = np.delete(       \
                                                      torquePolyTemp, tBefInd)
                                    else:
                                        timePolyTemp = np.delete(             \
                                                  timePolyTemp, tBefInd)
                                        powerPolyTemp = np.delete(            \
                                                  powerPolyTemp, tBefInd)
                                        srcPolyTemp = np.delete(              \
                                                  srcPolyTemp, tBefInd)
                                        currentPolyTemp = np.delete(         \
                                                  currentPolyTemp, tBefInd)
                                        torquePolyTemp = np.delete(          \
                                                  torquePolyTemp, tBefInd)
                                # Are time points after this run?
                                if (timePolyTemp[-1] > t1):
                                    tAftInd = np.where(timePolyTemp >= t1)
                                    nextInd = np.min(tAftInd)
                                    timePolyTemp = np.delete(                 \
                                              timePolyTemp, tAftInd)
                                    powerPolyTemp = np.delete(                \
                                              powerPolyTemp, tAftInd)
                                    srcPolyTemp = np.delete(                  \
                                              srcPolyTemp, tAftInd)
                                    currentPolyTemp = np.delete(              \
                                              currentPolyTemp, tAftInd)
                                    torquePolyTemp = np.delete(               \
                                              torquePolyTemp, tAftInd)
                                # Add remaining time points to the overall
                                # time polygon
                                timePoly = np.append(timePoly, timePolyTemp)
                                powerPoly = np.append(powerPoly, powerPolyTemp)
                                srcPoly = np.append(srcPoly, srcPolyTemp)
                                currentPoly = np.append(currentPoly,          \
                                                        currentPolyTemp)
                                torquePoly = np.append(torquePoly,            \
                                                       torquePolyTemp)
                            else:
                                timePoly = np.append(timePoly, t0)
                                powerPoly = np.append(powerPoly, multVal[0])
                                srcPoly = np.append(srcPoly, multVal[1])
                                currentPoly = np.append(currentPoly,          \
                                                        multVal[2])
                                torquePoly = np.append(torquePoly, multVal[3])
                        else:
                        # Octant is off - check it wasn't previously left on
                            if (j > 0):
                                if (octOnList[i,j-1] == True):
                                    # Set to zero from this time
                                    timePoly = np.append(timePoly,            \
                                                    [t0List[j]-eps, t0List[j]])
                                    if (len(powerPoly) > 0):
                                        valPrev = powerPoly[-1]
                                    else:
                                        valPrev = 0.0
                                    powerPoly  = np.append(powerPoly,         \
                                                      [valPrev, 0.0])
                                    if (len(srcPoly) > 0):
                                        valPrev = srcPoly[-1]
                                    else:
                                        valPrev = 0.0
                                    srcPoly  = np.append(srcPoly,             \
                                                      [valPrev, 0.0])
                                    if (len(currentPoly) > 0):
                                        valPrev = currentPoly[-1]
                                    else:
                                        valPrev = 0.0
                                    currentPoly  = np.append(currentPoly,     \
                                                      [valPrev, 0.0])
                                    if (len(torquePoly) > 0):
                                        valPrev = torquePoly[-1]
                                    else:
                                        valPrev = 0.0
                                    torquePoly  = np.append(torquePoly,       \
                                                      [valPrev, 0.0])
                                
                    # Write out the overall normalisations
                    modifyJsetValue(outputDir, keyPrefix+                     \
                                        "selectValue[0]", "true", True)
                    modifyJsetValue(outputDir, keyPrefix+                     \
                                        "selectValue[1]", "true", True)
                    modifyJsetValue(outputDir, keyPrefix+                     \
                                        "selectValue[2]", "true", True)
                    modifyJsetValue(outputDir, keyPrefix+                     \
                                        "selectValue[3]", "true", True)
                    modifyJsetValue(outputDir, keyPrefix+                     \
                                        "value[0]", "1.0", True)
                    modifyJsetValue(outputDir, keyPrefix+                     \
                                        "value[1]", "1.0", True)
                    modifyJsetValue(outputDir, keyPrefix+                     \
                                        "value[2]", "1.0", True)
                    modifyJsetValue(outputDir, keyPrefix+                     \
                                        "value[3]", "1.0", True)

                    # Check that we have found some nonzero power
                    # Else turn the octant off again
                    if (np.max(powerPoly) > 0):
                        # Add points at start to zero the waveform
                        eps = 1e-5
                        # We can account for eps edge cases later
                        # if we need to
                        if (timePoly[0]-eps > t0overall):
                            timePoly = np.insert(timePoly, 0,                 \
                                                 [t0overall,timePoly[0]-eps])
                            powerPoly = np.insert(powerPoly, 0, [0.0,0.0])
                            srcPoly = np.insert(srcPoly, 0, [0.0,0.0])
                            currentPoly = np.insert(currentPoly, 0, [0.0,0.0])
                            torquePoly = np.insert(torquePoly, 0, [0.0,0.0])
                        # Add points at end to zero the waveform
                        if (timePoly[-1]+eps < t1overall):
                            timePoly = np.append(timePoly,                    \
                                                 [t1overall,t1overall+eps])
                            powerPoly = np.append(powerPoly,                  \
                                                        [powerPoly[-1],0.0])
                            srcPoly = np.append(srcPoly, [srcPoly[-1],0.0])
                            currentPoly = np.append(currentPoly,              \
                                                        [currentPoly[-1],0.0])
                            torquePoly = np.append(torquePoly,                \
                                                        [torquePoly[-1],0.0])

                        # Simplify time polygons
                        timePoly, powerPoly, srcPoly, currentPoly,            \
                                                               torquePoly =   \
                           simplifyTimePolygon(timePoly, powerPoly, srcPoly,  \
                                               currentPoly, torquePoly)

                        # Write out the time polygons
                        for j in range(0, len(timePoly)):
                            modifyJsetValue(outputDir,                        \
                                 keyPrefix+"tpoly.select["+str(j)+"]",        \
                                 "true", True) 
                            modifyJsetValue(outputDir,                        \
                                 keyPrefix+"tpoly.time["+str(j)+"]",          \
                                 str(timePoly[j]), True)
                            modifyJsetValue(outputDir,                        \
                                 keyPrefix+"tpoly.value["+str(j)+"][0]",      \
                                 str(powerPoly[j]), True)
                            modifyJsetValue(outputDir,                        \
                                 keyPrefix+"tpoly.value["+str(j)+"][1]",      \
                                 str(srcPoly[j]), True)
                            modifyJsetValue(outputDir,                        \
                                 keyPrefix+"tpoly.value["+str(j)+"][2]",      \
                                 str(currentPoly[j]), True)
                            modifyJsetValue(outputDir,                        \
                                 keyPrefix+"tpoly.value["+str(j)+"][3]",      \
                                 str(torquePoly[j]), True)

                        # Plot
                        if (plot):
                            nbiAx[0].plot(timePoly, powerPoly)
                            nbiAx[1].plot(timePoly, srcPoly)
                            nbiAx[2].plot(timePoly, currentPoly)
                            nbiAx[3].plot(timePoly, torquePoly)
                            nbiAx[0].set_ylabel("Power [W]")
                            nbiAx[1].set_ylabel("Source multiplier")
                            nbiAx[2].set_ylabel("Current multiplier")
                            nbiAx[3].set_ylabel("Torque multiplier")
                            nbiLegend = np.append(nbiLegend,                  \
                                         "Octant "+octList[i])
                    else:
                        modifyJsetValue(outputDir,                            \
                              "NBIPencilBoxRef.selectBeamBox[" + str(i) + "]",\
                              "false", True)

        else:
            print("NBI Pencil source '" + nbiPencilSrc + "' not yet handled")
            sys.exit(504)
    else:
        print("NBI source '" + nbiSrc + "' not yet handled")
        sys.exit(502)

    if (plot):
        nbiAx[0].title.set_text("Combined NBI time polygons")
        nbiAx[3].set_xlabel("Time [s]")
        nbiAx[0].legend(nbiLegend)

    return

###############################################################################

# Combine heating waveforms from COCONUT sequence

def makeHeat(settingLists, valueLists, outputDir, tOffsets, t0List, t1List,   \
             ECRHflag, dirCoconutList, plot):

    # Find our overall run time interval
    t0overall = np.min(t0List)
    t1overall = np.max(t1List)

    # NBI
    nbiOn = False
    key = "NBIPanel.select"
    nbiSelects = getValueFromCoconutLists(settingLists, valueLists, key)
    nbiOns = [False] * len(settingLists)
    for i, nbiSelect in enumerate(nbiSelects):
        if (nbiSelect == "true"):
            nbiOns[i] = True
    if (any(nbiOns)):
        nbiOn = True
        modifyJsetValue(outputDir, key, "true", True)
        print("Constructing and writing NBI settings to jetto.jset...")
        makeNbi(settingLists, valueLists, outputDir, tOffsets, nbiOns,        \
                t0overall, t1overall, t0List, t1List, dirCoconutList, plot)
        print("NBI settings written\n")
    else:
        modifyJsetValue(outputDir, key, "false", True)

    # ? RF
    
    # ECRH
    if (ECRHflag):
        ecrhOn = False
        key = "ECRHPanel.select"
        ecrhSelects = getValueFromCoconutLists(settingLists, valueLists, key)
        ecrhOns = [False] * len(settingLists)
        for i, ecrhSelect in enumerate(ecrhSelects):
            if (ecrhSelect == "true"):
                ecrhOns[i] = True
        if (any(ecrhOns)):
            ecrhOn = True
            modifyJsetValue(outputDir, key, "true", True)
            print("Constructing and writing ECRH settings to jetto.jset...")
            makeEcrh(settingLists, valueLists, outputDir, tOffsets, ecrhOns,  \
                     t0overall, t1overall, t0List, t1List, dirCoconutList,    \
                     plot)
            print("ECRH settings written\n")
        else:
            modifyJsetValue(outputDir, key, "false", True)
    else:
        print("Retaining donor run settings for ECRH")

    # ? LH
    # ? EBW
    # ? External
    
    return

###############################################################################

# Locate the given variable in the extra namelist

def findExtraNamelist(settingLists, valueLists, varName):
    keyInds = np.array([])
    keyNums = np.array([])
    keyNames = np.array([])
    keyVals = np.array([])
    keyOns  = np.zeros([len(settingLists)]).astype("bool")
    keyPrefix = "OutputExtraNamelist.selItems.cell["
    keyRePrefix = r"^OutputExtraNamelist\.selItems\.cell"
    for i, valueList in enumerate(valueLists):
        keyFound = False
        try:
            ind = valueList.index(varName)
            keyFound = True
        except:
            keyInds = np.append(keyInds, "Not found")
            keyNums = np.append(keyNums, "Not found")
            keyNames = np.append(keyNames, "Not found")
            keyVals = np.append(keyVals, "Not found")
        if (keyFound):         
            keyInds = np.append(keyInds, ind)
            match = re.search(keyRePrefix + r"\[([0-9]+)\]",                  \
                              settingLists[i][ind])
            keyNums = np.append(keyNums, match.groups(0)[0])
            # Retrieve the data from each line of the entry
            keyStart = keyPrefix + keyNums[i] + "]["
            keyNames = np.append(keyNames, getValueFromCoconutList(           \
                                 settingLists[i], valueList, keyStart+"0]"))
            keyVals = np.append(keyVals, getValueFromCoconutList(            \
                                 settingLists[i], valueList, keyStart+"2]"))
            try:
                onsTemp = getValueFromCoconutList(settingLists[i], valueList,\
                                                                 keyStart+"3]")
            except:
                onsTemp = "false"
            if (onsTemp == "true"):
                keyOns[i] = True

    return(keyInds, keyNums, keyNames, keyVals, keyOns)

###############################################################################

# Set up pellets, including density feedback

def makePellets(settingLists, valueLists, outputDir, tOffsetCoconut,          \
                t0List, t1List, plot):

    # Are the pellets turned on?
    keyPanel = "PelletPanel.select"
    pelletOns2 = getValueFromCoconutLists(settingLists, valueLists, keyPanel)
    pelletOn = False
    pelletOns = np.zeros([len(settingLists)]).astype("bool")
    for i, pelletOnSingle in enumerate(pelletOns2):
        if (pelletOnSingle == "true"):
            pelletOns[i] = True
            pelletOn = True
        else:
            pelletOns[i] = False
    # Get ESCO times in order to avoid setting the pellet to start before
    # the second ESCO time
    # Need to make this more general in case COCONUT is not using ESCO or not
    # using ESCO in this format
    nEsco = int(getValueFromCoconutList(settingLists[0], valueLists[0],       \
                              "EquilEscoRefPanel.tvalue.tinterval.numRange"))
    t0Esco = float(getValueFromCoconutList(settingLists[0], valueLists[0],    \
                              "EquilEscoRefPanel.tvalue.tinterval.startRange"))
    t1Esco = float(getValueFromCoconutList(settingLists[0], valueLists[0],    \
                              "EquilEscoRefPanel.tvalue.tinterval.endRange"))
    dtEsco = (t1Esco - t0Esco) / nEsco
    tEsco = np.linspace(t0Esco, t1Esco, num=nEsco)
    tEscoInd = np.where(tEsco > t0List[0])
    tEscoInd = np.delete(tEscoInd, 0)
    tEscoMin = np.min(tEsco[tEscoInd])
    escoFac = 1.5
    dtList = 5.0
    tPelMin = np.max([tEscoMin+escoFac*dtEsco, t0List[0]+dtList])

    if (pelletOn):
        modifyJsetValue(outputDir, keyPanel, "true", True)

        # These general pellet fields need to match between COCONUT runs
        matchValues = ["pelletModel",                                         \
                       "selReadIds"]
        # Do the above fields match when the pellets are on?
        for i, matchValue in enumerate(matchValues):
            key = "PelletPanel." + matchValue
            matchVals = getValueFromCoconutLists(settingLists, valueLists, key)
            valsOn = []
            for j, settingList in enumerate(settingLists):
                if (pelletOns[j]):
                    valsOn.append(matchVals[j])
            if (not allSame(valsOn)):
                print("Differing values in .jset key " + key + ":")
                print(valsOn)
                sys.exit(602)
            modifyJsetValue(outputDir, key, valsOn[0], True)
            if (matchValue == "pelletModel"):
                pelletModel = valsOn[0]

        if (pelletModel == "HPI2"):
            # These HPI2-model-specific fields also need to match between
            # COCONUT runs
            matchValues = ["driftFactor",                                     \
                           "epsilonParameter",                                \
                           "precooling",                                      \
                           "rocketAccModel"]
            # Do the above fields match when the pellets are on?
            for i, matchValue in enumerate(matchValues):
                key = "PelletModelHPI2Dialog." + matchValue
                matchVals = getValueFromCoconutLists(settingLists,            \
                                                     valueLists, key)
                valsOn = []
                for j, settingList in enumerate(settingLists):
                    if (pelletOns[j]):
                        valsOn.append(matchVals[j])
                if (not allSame(valsOn)):
                    print("Differing values in .jset key " + key + ":")
                    print(valsOn)
                    sys.exit(603)
                modifyJsetValue(outputDir, key, valsOn[0], True)
            # Set IFLUSUR=0 to avoid issues from Flush routine with HPI2
            modifyExtraNamelist(outputDir, "IFLUSUR", "0", True, False)

        # Are we using the continuous pellet model?
        iswpiInds, iswpiArr, iswpiNames, iswpiVals, iswpiOns =                \
                   findExtraNamelist(settingLists, valueLists, "ISWPI")
        iswpiOn = np.any(iswpiOns)
        if (iswpiOn):
            print("    Continuous pellet model is used in COCONUT sequence")
            print("    This is not yet handled")
            sys.exit(604)
        else:
            print("    Continuous pellet model is not used in COCONUT " +     \
                  "sequence:")
            print("        Removing continuous pellet settings from " +       \
                  "jetto.jset")
            print("        Removing PID controller settings from " +          \
                  "jetto.jset")
            print("        Turning off gas puff feedback in jetto.jset")
            ctsPelletVars = ["ISWPI", "SPCEN", "SPCEN2", "SPDEL", "SPMIX",    \
                             "SPMIX2", "SPTOT", "SPTOT2", "SPTOTMIN",         \
                             "SPTOTS", "SPTOTT", "SPWID", "SPWID2"]
            pidVars = ["DTPID", "ICALLPID", "KDPID", "KIPID", "KPPID",        \
                       "SMAXPID", "TDPID"]
            for var in ctsPelletVars:
                modifyExtraNamelist(outputDir, var, "", False, True)
            for var in pidVars:
                modifyExtraNamelist(outputDir, var, "", False, True)
            modifyJsetValue(outputDir, "NeutralSourcePanel.gasPuff",          \
                            "false", True)

        # Are we using pellets as density feedback?
        dnepfbInds, dnepfbNums, dnepfbNames, dnepfbVals, dnepfbOns =          \
                   findExtraNamelist(settingLists, valueLists, "DNEPFB")
 #       print(dnepfbInds, dnepfbNums, dnepfbNames, dnepfbVals, dnepfbOns)
        dnepfbOn = np.any(dnepfbOns)
        if (dnepfbOn):
            print("    Density feedback is used in COCONUT sequence")
            timePelletFb = np.array([])
            valPelletFb = np.array([])
            # Read any time polygon information
            dtnepfbInds, dtnepfbNums, dtnepfbNames, dtnepfbVals, dtnepfbOns = \
                   findExtraNamelist(settingLists, valueLists, "DTNEPFB")

            # Match pellet type and injection conditions
            # Only the first row is read for density feedback
            # Time information is taken from DTNEPFB and DNEPFB
            matchValues = ["injector",                                        \
                           "mass",                                            \
                           "radius",                                          \
                           "select",                                          \
                           "speed"]
            # Do the above fields match when the pellets are on?
            for i, matchValue in enumerate(matchValues):
                key = "PelletPanel.pellet[0]." + matchValue
                matchVals = getValueFromCoconutLists(settingLists,            \
                                                     valueLists, key)
                valsOn = []
                for j, settingList in enumerate(settingLists):
                    if (pelletOns[j]):
                        valsOn.append(matchVals[j])
                if (not allSame(valsOn)):
                    print("Differing values in .jset key " + key + ":")
                    print(valsOn)
                    print("Taking first value (" + str(valsOn[0]) +           \
                          ") - may need to redo this later")
#                    sys.exit(605)
                modifyJsetValue(outputDir, key, valsOn[0], True)
            # Time becomes pellet injector activation time - set to start
            # Could alternatively set to first sequence pellet time?
            modifyJsetValue(outputDir, "PelletPanel.pellet[0].time",          \
                            str(tPelMin), True)
 
            # IPFB - mode of density feedback
            ipfbInds, ipfbArr, ipfbNames, ipfbVals, ipfbOns =                 \
                   findExtraNamelist(settingLists, valueLists, "IPFB")
            ipfbVary = False
            ipfbValInit = False
            ipfbValMatch = True
            for i in range(0, len(settingLists)):
                if (ipfbVals[i] != "Not found"):
                    if (ipfbValInit):
                        if (ipfbVals[i] != ipfbVal):
                            ipfbValMatch = False
                    else:
                        ipfbVal = int(ipfbVals[i])
            if (not ipfbValMatch):
                print("    Multiple IPFB values in COCONUT sequence")
                print("    This is not yet handled")
                sys.exit(606)

            # IPFB value cases
            modifyExtraNamelist(outputDir, "IPFB", str(ipfbVal), True, True)
            if (ipfbVal == 1):
                print("    IPFB = 1: Control neTOP or neLCFS (H/L)")
                print("    This is not yet handled")
                sys.exit(611)
            elif (ipfbVal == 2):
                print("    IPFB = 2: Control vol ave ne")
                print("    This is not yet handled")
                sys.exit(612)
            elif (ipfbVal == 3):
                print("    IPFB = 3: Control line ave ne")
                print("    This is not yet handled")
                sys.exit(613)
            elif (ipfbVal == 4):
                print("    IPFB = 4: DNEPFB is pellet injection frequency")
                print("    This is not yet handled")
                sys.exit(614)
            elif (ipfbVal == 5):
                print("    IPFB = 5: Control edge ne: @ rho_n = 0.92")
                print("    This is not yet handled")
                sys.exit(615)
            elif (ipfbVal == 6):
                print("    IPFB = 6: Control time ave line ave ne")
                print("    This is not yet handled")
                sys.exit(616)             
            elif (ipfbVal == 7):
                print("    IPFB = 7: Control nG fraction (%)")
                valInit = 30.0    # Initialise with this value if absent
                densFbLabel = "Greenwald fraction"
                densFbUnits = "%"
            elif (ipfbVal == 8):
                print("    IPFB = 8: Control neTOP/nG (%)")
                print("    This is not yet handled")
                sys.exit(618)
            else:
                print("     Unknown IPFB value from COCONUT sequence: " +     \
                      str(ipfbVal))
                sys.exit(610)

            # Build time polygon
            initTime = False
            for i in range(0, len(settingLists)):
                # Is there a time polygon in the run?
                numRegex = r"[0-9\.e]+"
                if (dtnepfbOns[i]):
                    # Yes, there is a time polygon
                    # Read in the time and data arrays
                    timeTemp = np.array([])
                    valTemp = np.array([])
                    matchTime = re.findall(numRegex, dtnepfbVals[i])
                    matchVal = re.findall(numRegex, dnepfbVals[i])
                    for j in range(0, len(matchVal)):
                        timeTemp = np.append(timeTemp, float(matchTime[j]))
                        valTemp = np.append(valTemp, float(matchVal[j]))
                    # Reduce arrays to within run time
                    if (timeTemp[0] < t0List[i]):
                        tBefInd = np.where(timeTemp < t0List[i])
                        prevInd = np.max(tBefInd)
                        if (prevInd == len(timeTemp)-1):
                            timeTemp = np.delete(timeTemp, tBefInd)
                            valTemp = np.delete(valTemp, tBefInd)
                        else:
                            if (timeTemp[prevInd+1] > t0List[i]):
                                timeTemp[prevInd] = t0List[i]
                                if (prevInd > 0):
                                    tBefInd = np.delete(tBefInd, prevInd)
                                    timeTemp = np.delete(timeTemp, tBefInd)
                                    valTemp = np.delete(valTemp, tBefInd)
                                else:
                                    timeTemp = np.delete(timeTemp, tBefInd)
                                    valTemp = np.delete(valTemp, tBefInd)
                    if (len(timeTemp) > 0):
                        if (timeTemp[-1] > t1List[i]):
                            tAftInd = np.where(timeTemp >= t1List[i])
                            nextInd = np.min(tAftInd)
                            timeTemp = np.delete(timeTemp, tAftInd)
                            valTemp = np.delete(valTemp, tAftInd)
                    # Add end points if necessary
                    if (timeTemp[0] > t0List[i]):
                        timeTemp = np.insert(timeTemp, 0, t0List[i])
                        valTemp = np.insert(valTemp, 0, valTemp[0])
                    if (timeTemp[-1] < t1List[i]):
                        timeTemp = np.append(timeTemp, t1List[i])
                        valTemp = np.append(valTemp, valTemp[-1])
                    # Add arrays to time polygon
                    if (len(timeTemp) > 0):
                        initTime = True
                    timePelletFb = np.append(timePelletFb, timeTemp)
                    valPelletFb = np.append(valPelletFb, valTemp)
                else:
                    if (dnepfbOns[i]):
                        # No, there isn't a time polygon, but there is a value
                        initTime = True
                        matchVal = re.findall(numRegex, dnepfbVals[i])
                        valMatch = float(matchVal[0])
                        timePelletFb = np.append(timePelletFb, t0List[i])
                        valPelletFb = np.append(valPelletFb, valMatch)
                        timePelletFb = np.append(timePelletFb, t1List[i])
                        valPelletFb = np.append(valPelletFb, valMatch)
                    else:
                        # There is no density feedback
                        print("    No pellet density feedback for run from "  \
                              + str(t0List[i]) + "-" + str(t1List[i]) + "s")
                        if (not initTime):
                            print("    Initialising pellet dfb with value " + \
                                  str(valInit))
                            timePelletFb = np.append(timePelletFb, t0List[i])
                            valPelletFb = np.append(valPelletFb, valInit)
                            timePelletFb = np.append(timePelletFb, t1List[i])
                            valPelletFb = np.append(valPelletFb, valInit)
            # Add end points if necessary
            if (timePelletFb[0] > t0List[0]):
                timePelletFb = np.insert(timePelletFb, 0, t0List[0])
                valPelletFb = np.insert(valPelletFb, 0, valPelletFb[0])
            if (timePelletFb[-1] < t1List[-1]):
                timePelletFb = np.append(timePelletFb, t1List[-1])
                valPelletFb = np.append(valPelletFb, valPelletFb[-1])
            # Simplify polygon
            timePelletFb, valPelletFb =                                       \
                          simplifyTimePolygon(timePelletFb, valPelletFb)

            # Construct and write out time polygon strings
            timePolyStr = "("
            valPolyStr = "("
            for i in range(0, len(timePelletFb)):
                if (i > 0):
                    timePolyStr = timePolyStr + ", "
                    valPolyStr = valPolyStr + ", "
                timePolyStr = timePolyStr + str(timePelletFb[i])
                valPolyStr = valPolyStr + str(valPelletFb[i])
            timePolyStr = timePolyStr + ")"
            valPolyStr = valPolyStr + ")"
            modifyExtraNamelist(outputDir, "DTNEPFB", timePolyStr, True, True)
            modifyExtraNamelist(outputDir, "DNEPFB", valPolyStr, True, True)

            # For now, switch pellet model to Garzotti
            # Start pellet at beginning of run for this setting
            modifyJsetValue(outputDir, "PelletPanel.pelletModel", "Garzotti", \
                            False)
            modifyJsetValue(outputDir, "PelletPanel.pellet[0].time",          \
                            str(t0List[0]), False)

            # Make plots if desired
            if (plot):
                plt.figure()
                plt.plot(timePelletFb, valPelletFb)
                plt.xlabel("Time [s]")
                plt.ylabel("Feedback: " + densFbLabel + " [" + \
                           densFbUnits + "]")
                plt.title("Pellet density feedback")

        else:
            print("    Density feedback is not used in COCONUT sequence")
            print("    This is not yet handled")
            sys.exit(601)        

    else:
        print("    Pellets are not used")
        modifyJsetValue(outputDir, keyPanel, "false", False)

    return

###############################################################################

# Make output plots

def makeOutputPlots(dirCoconutList, fileOutputDirs, jstRead, jspRead,         \
                    tOffsets):

    # Parameters
    tProf = 10.0
    # Special values:
    #   - nirat: NI2 / NI1
    jstPlots = ["CUR", "PTOT", "NGFR", "QFUS", "TEAV", "TIAV", "ALFM",
                "ZEFF", "nirat", "NPEL", "QMIN"
#                """
#               "CUR","PTOT","PNB","PECE","PALF","POH",
#                "NGFR","NHBO","NEAX","NEAV",
#                "TIAX","TEAX","TIAV","TEAV",
#                "QFUS","ALFM","QMIN"
#                """
                ]
    # Special values:
    #    - ptot: QECE + QNBE + QOH + QALE
    jspPlots = ["NE", "TE", "TI", "VTOR", "Q","ptot", "QECE", "QALE"#, "QNBE", "QOH",
               ]
    coconutColours = ["black",                                                \
                      "grey"]
    jettoColours = ["red",                                                    \
                    "blue",                                                   \
                    "green",                                                  \
                    "purple",                                                 \
                    "orange"]

    # Get JETTO directories and JS* data
    dirJettoList, labelJettoList = getJettoOutputDirs(fileOutputDirs)
    jstOutRead = readJstFiles(dirJettoList)
    jspOutRead = readJspFiles(dirJettoList)
    # Extract plot labels
    jstYlabels = []
    for pltName in jstPlots:
        if (pltName == "nirat"):
            descStr = "T/D ni ratio"
            unitsStr = "-"
        else:
            descStr = jstOutRead[0]["INFO"][pltName]["DESC"]
            unitsStr = jstOutRead[0]["INFO"][pltName]["UNITS"]
        # Make numbers superscripted indices
        unitsStr = re.sub(r"(-?[0-9]+)", r"$^{\1}$", unitsStr)
        pltStr = descStr + " [" + unitsStr + "]"
        jstYlabels.append(pltStr)
    jspYlabels = []
    for pltName in jspPlots:
        if (pltName == "ptot"):
            descStr = "Total power"
            unitsStr = "W"
        else:
            descStr = jspOutRead[0]["INFO"][pltName]["DESC"]
            unitsStr = jspOutRead[0]["INFO"][pltName]["UNITS"]
        # Make numbers superscripted indices
        unitsStr = re.sub(r"(-?[0-9]+)", r"$^{\1}$", unitsStr)
        pltStr = descStr + " [" + unitsStr + "]"
        jspYlabels.append(pltStr)

    # Generate plot windows
    # Make sure we have at least one spare at the end for the legend
    # JST
    xFigSizeJst = 12
    yFigSizeJst = 12
    arFigSizeJst = yFigSizeJst / xFigSizeJst
    nPlotsJst = len(jstPlots)
    nPlotsJst2 = 1 + nPlotsJst
    nColsJst = math.ceil(math.sqrt(nPlotsJst/arFigSizeJst))
    nRowsJst = math.ceil(nPlotsJst / nColsJst)
    if (nColsJst*nRowsJst == nPlotsJst):
        nPlotsJst = nPlotsJst + 1
        nColsJst = math.ceil(math.sqrt(nPlotsJst/arFigSizeJst))
        nRowsJst = math.ceil(nPlotsJst / nColsJst)
    opFigJst, opAxJst = plt.subplots(nrows=nRowsJst, ncols=nColsJst,          \
                               figsize=(xFigSizeJst,yFigSizeJst),             \
                               sharex=True, sharey=False)
    # Make sure labels don't spatially conflict with plots or each other
    plt.tight_layout(h_pad=2, w_pad=3, rect=(0.05,0.05,0.95,0.95))
    # JSP
    xFigSizeJsp = 12
    yFigSizeJsp = 12
    arFigSizeJsp = yFigSizeJsp / xFigSizeJsp
    nPlotsJsp = len(jspPlots)
    nPlotsJsp2 = 1 + nPlotsJsp
    nColsJsp = math.ceil(math.sqrt(nPlotsJsp/arFigSizeJsp))
    nRowsJsp = math.ceil(nPlotsJsp / nColsJsp)
    if (nColsJsp*nRowsJsp == nPlotsJsp):
        nPlotsJsp = nPlotsJsp + 1
        nColsJsp = math.ceil(math.sqrt(nPlotsJsp/arFigSizeJsp))
        nRowsJsp = math.ceil(nPlotsJsp / nColsJsp)
    opFigJsp, opAxJsp = plt.subplots(nrows=nRowsJsp, ncols=nColsJsp,          \
                               figsize=(xFigSizeJsp,yFigSizeJsp),             \
                               sharex=True, sharey=False)
    # Make sure labels don't spatially conflict with plots or each other
    plt.tight_layout(h_pad=2, w_pad=3, rect=(0.05,0.05,0.95,0.95))

    # Populate plots
    # Plot JETTO outputs
    # JST
    for i in range(0, len(dirJettoList)):
        colJetto = jettoColours[i%len(jettoColours)]
        outTimeVec = jstOutRead[i]["TVEC1"][:,0]
        for j, dat in enumerate(jstPlots):
            colInd = (j+1) % nColsJst
            rowInd = math.floor((j+1) / nColsJst)
            if (dat == "nirat"):
                ni2DatVec = jstOutRead[i]["NI2"][0,:]
                ni1DatVec = jstOutRead[i]["NI1"][0,:]
                outDatVec = ni2DatVec / ni1DatVec
            else:
                outDatVec = jstOutRead[i][dat][0,:]
            if (nRowsJst > 1):
                opAxJst[rowInd,colInd].plot(outTimeVec, outDatVec,            \
                                            color=colJetto)
                opAxJst[0,0].plot([0,0],[0,0], color=colJetto)
            else:
                opAxJst[colInd].plot(outTimeVec, outDatVec, color=colJetto)
                opAxJst[0].plot([0,0],[0,0], color=colJetto)
    # JSP
    tActualJetto = np.array([])
    for i in range(0, len(dirJettoList)):
        colJetto = jettoColours[i%len(jettoColours)]
        outTimeVec = jspOutRead[i]["TIME"][:,0,0]
        outXVec    = jspOutRead[i]["XVEC1"][0]
        # Find nearest time point
        tProfIndex = (np.abs(outTimeVec - tProf)).argmin()
        tActualJetto = np.append(tActualJetto, outTimeVec[tProfIndex])
        for j, dat in enumerate(jspPlots):
            colInd = (j+1) % nColsJsp
            rowInd = math.floor((j+1) / nColsJsp)
            if (dat == "ptot"):
                ptot1DatVec = jspOutRead[i]["QECE"][tProfIndex,:]
                ptot2DatVec = jspOutRead[i]["QNBE"][tProfIndex,:]
                ptot3DatVec = jspOutRead[i]["QOH"][tProfIndex,:]
                ptot4DatVec = jspOutRead[i]["QALE"][tProfIndex,:]
                outDatVec = ptot1DatVec + ptot2DatVec + ptot3DatVec +         \
                            ptot4DatVec
            else:
                outDatVec = jspOutRead[i][dat][tProfIndex,:]
            if (nRowsJsp > 1):
                opAxJsp[rowInd,colInd].plot(outXVec, outDatVec, color=colJetto)
                opAxJsp[0,0].plot([0,0],[0,0], color=colJetto)
            else:
                opAxJsp[colInd].plot(outXVec, outDatVec, color=colJetto)
                opAxJsp[0].plot([0,0],[0,0], color=colJetto)

    # Plot COCONUT inputs
    # JST
    for i in range(0, len(dirCoconutList)):
        timeVec = jstRead[i]["TVEC1"][:,0] + tOffsets[i]
        for j, dat in enumerate(jstPlots):
            colInd = (j+1) % nColsJst
            rowInd = math.floor((j+1) / nColsJst)
            if (dat == "nirat"):
                ni2DatVec = jstRead[i]["NI2"][0,:]
                ni1DatVec = jstRead[i]["NI1"][0,:]
                datVec = ni2DatVec / ni1DatVec
            else:
                datVec = jstRead[i][dat][0,:]
            col = coconutColours[i%len(coconutColours)]
            if (nRowsJst > 1):
                opAxJst[rowInd,colInd].plot(timeVec, datVec, color=col)
                opAxJst[rowInd,colInd].set_title(jstPlots[j])
                opAxJst[rowInd,colInd].set_ylabel(jstYlabels[j])
                if (rowInd == nRowsJst-1):
                    opAxJst[rowInd,colInd].set_xlabel("Time [s]")
                opAxJst[0,0].plot([0,0],[0,0], color=col)
            else:
                opAxJst[colInd].plot(timeVec, datVec, color=col)
                opAxJst[colInd].set_title(jstPlots[j])
                opAxJst[colInd].set_ylabel(jstYlabels[j])
                opAxJst[colInd].set_xlabel("Time [s]")
                opAxJst[0].plot([0,0],[0,0], color=col)
    # JSP
    # Find which COCONUT run matches the requested profile time
    allCoTimeVec = np.array([])
    allCoTimeRun = np.array([])
    allCoTimeInd = np.array([])
    for i in range(0, len(dirCoconutList)):
        coTimeVec = jspRead[i]["TIME"][:,0,0] + tOffsets[i]
        allCoTimeVec = np.append(allCoTimeVec, coTimeVec)
        allCoTimeRun = np.append(allCoTimeRun, [i]*len(coTimeVec))
        allCoTimeInd = np.append(allCoTimeInd, list(range(0,len(coTimeVec))))
    # Find nearest time point
    tProfIndex = (np.abs(allCoTimeVec - tProf)).argmin()
    coInd = int(allCoTimeRun[tProfIndex])
    tCoInd = int(allCoTimeInd[tProfIndex])
    tCoOverall = allCoTimeVec[tProfIndex]
    # Plot profiles at that time
    xVec = jspRead[coInd]["XVEC1"][0]        
    for j, dat in enumerate(jspPlots):
        colInd = (j+1) % nColsJsp
        rowInd = math.floor((j+1) / nColsJsp)
        if (dat == "ptot"):
            ptot1DatVec = jspRead[coInd]["QECE"][tCoInd,:]
            ptot2DatVec = jspRead[coInd]["QNBE"][tCoInd,:]
            ptot3DatVec = jspRead[coInd]["QOH"][tCoInd,:]
            ptot4DatVec = jspRead[coInd]["QALE"][tCoInd,:]
            datVec = ptot1DatVec + ptot2DatVec + ptot3DatVec + ptot4DatVec
        else:
            datVec = jspRead[coInd][dat][tCoInd,:]
        col = coconutColours[i%len(coconutColours)]
        if (nRowsJsp > 1):
            opAxJsp[rowInd,colInd].plot(xVec, datVec, color=col)
            opAxJsp[rowInd,colInd].set_title(jspPlots[j])
            opAxJsp[rowInd,colInd].set_ylabel(jspYlabels[j])
            if (rowInd == nRowsJsp-1):
                opAxJsp[rowInd,colInd].set_xlabel(r"$\rho$ [-]")
            opAxJsp[0,0].plot([0,0],[0,0], color=col)
        else:
            opAxJsp[colInd].plot(xVec, datVec, color=col)
            opAxJsp[colInd].set_title(jspPlots[j])
            opAxJsp[colInd].set_ylabel(jspYlabels[j])
            opAxJsp[colInd].set_xlabel(r"$\rho$ [-]")
            opAxJsp[0].plot([0,0],[0,0], color=col)

    # x axis labels for trailing plots
    # JST
    if (nPlotsJst2 < nRowsJst*nColsJst):
        finalCol = (nPlotsJst2 % nColsJst)
        for i in range(finalCol, nColsJst):
            if (nRowsJst > 1):
                opAxJst[-1,i].set_xlabel("Time [s]")
            else:
                opAxJst[i].set_xlabel("Time [s[]")
    # JSP
    if (nPlotsJsp2 < nRowsJsp*nColsJsp):
        finalCol = (nPlotsJsp2 % nColsJsp)
        for i in range(finalCol, nColsJsp):
            if (nRowsJsp > 1):
                opAxJsp[-1,i].set_xlabel(r"$\rho$ [-]")
            else:
                opAxJsp[i].set_xlabel(r"$\rho$ [-]")
    # Build legend
    # JST
    patchesJst = []
    for i in range (0, np.min([len(dirCoconutList),len(coconutColours)])):
        col = coconutColours[i]
        patchesJst.append(mpatches.Patch(color=col, label="COCONUT reference"))
    for i in range (0, len(dirJettoList)):
        col = jettoColours[i%len(jettoColours)]
        patchesJst.append(mpatches.Patch(color=col, label=labelJettoList[i]))
    # JSP
    patchesJsp = []
    col = coconutColours[coInd%len(coconutColours)]
    labelCoJsp = "COCONUT reference (profile " +                              \
                 str(round(tCoOverall,2)) + "s)"
    patchesJsp.append(mpatches.Patch(color=col, label=labelCoJsp))
    for i in range (0, len(dirJettoList)):
        col = jettoColours[i%len(jettoColours)]
        labelJsp = labelJettoList[i] + " (profile " +                         \
                   str(round(tActualJetto[i], 2)) + "s)"
        patchesJsp.append(mpatches.Patch(color=col, label=labelJsp))
    # Place legend
    # JST
    if (nRowsJst > 1):
        opAxJst[0,0].axis("off")
        opAxJst[0,0].set_axis_off()
        opAxJst[0,0].legend(handles=patchesJst)
    else:
        opAxJst[0].axis("off")
        opAxJst[0].legend(handles=patchesJst)
    # JSP
    if (nRowsJsp > 1):
        opAxJsp[0,0].axis("off")
        opAxJsp[0,0].set_axis_off()
        opAxJsp[0,0].legend(handles=patchesJsp)
    else:
        opAxJsp[0].axis("off")
        opAxJsp[0].legend(handles=patchesJsp)

    # Display windows
    plt.show()

    return

###############################################################################

# Driver routine

"""
Original plan to generate jetto.jset from scratch seems impractical, in light
of edge2d.coset containing 278 differences between the first two COCONUT run
directories for our first chosen example.
Instead, we choose targeted quantities to harmonise.

Donor run needs to match 'closely' in order for this to be achievable
i.e. Don't pick one with differing e.g. ions
"""

def main():

    # Parse input arguments
    parser = argparse.ArgumentParser(description="Set up JETTO run from " +   \
     "sequence of COCONUT runs and donor JETTO run")
    parser.add_argument("-jd", "--donor", type=str, required=True,            \
     dest="fileDonor",                                                        \
     help="File containing JETTO donor run catalogue location")
    parser.add_argument("-co", "--coconut", type=str, required=True,          \
     dest="fileCoconut",                                                      \
     help="File containing sequential list of COCONUT run catalogue locations")
    parser.add_argument("-jo", "--jsetoutput", type=str, required=True,       \
     dest="outputDir",                                                        \
     help="Output directory for jetto.jset")
    parser.add_argument("--noECRH", action="store_true",                      \
     help="Retain ECRH settings from donor run if set; otherwise from COCONUT")
    parser.add_argument("--noBC", action="store_true",                        \
     help="Do not write boundary condition files")
    parser.add_argument("--graybeam", action="store_true",                    \
     help="If graybeam.data is out of date, update it")
    parser.add_argument("--plot", action="store_true", help="Plotting flag")
    parser.add_argument("--outputplot", action="store_true",                  \
     help="Output plotting mode: Produce output comparisons.")
    parser.add_argument("-opd", "--outputplotdirs", type=str, required=False, \
     dest="fileOutputDir",                                                    \
     help="File containing JETTO output run locations for output plot mode")
    args = parser.parse_args()
    # Main arguments
    fileDonor      = args.fileDonor
    fileCoconut    = args.fileCoconut
    outputDir      = args.outputDir
    # Optional main arguments
    plot           = args.plot
    ECRHflag       = not args.noECRH
    BCflag         = not args.noBC
    graybeamFlag   = args.graybeam
    # Plot mode arguments
    outputPlot     = args.outputplot
    fileOutputDirs = args.fileOutputDir
    
    # Get settings for runs
    checkInputs(fileDonor, fileCoconut, outputDir)
    dirDonor = getJettoInputDir(fileDonor)
    dirCoconutList, tOffsetCoconut = getCoconutInputDirs(fileCoconut)
    settingListJetto, valueListJetto = extractJettoSettings(dirDonor)
    settingLists,     valueLists     = extractCoconutSettings(dirCoconutList)

    # Read in JST and JSP files
    jstRead = readJstFiles(dirCoconutList)
#    if (BCflag and not outputPlot):
    if (BCflag or outputPlot):
        jspRead = readJspFiles(dirCoconutList)
    else:
        jspRead = False # dummy value - saves time if not used

    # Start and end times
    t0List, t1List = timeStartEnd(jstRead, tOffsetCoconut)
    t0 = str(t0List[0])
    t1 = str(t1List[-1])
    print("COCONUT sequence runs from " + t0 + " to " + t1 + " seconds.")

    # Choose script mode
    if (outputPlot):
        # Produce comparison output plots
        makeOutputPlots(dirCoconutList, fileOutputDirs, jstRead, jspRead,     \
                        tOffsetCoconut)
    else:
        # Default: produce modified jetto.jset and files for it

        # Create output jetto.jset, copied from donor run
        if (os.path.exists(outputDir)):
            shutil.rmtree(outputDir)
        os.mkdir(outputDir)
        shutil.copy(dirDonor+"/jetto.jset", outputDir)

        # Modify .jset header info
        print("Modifying jetto.jset headers")
        jsetAbsPath = os.path.abspath(outputDir) + "/jetto.jset"
        now = datetime.datetime.now()
        jsetNewDate = now.strftime("%d/%m/%Y")
        jsetNewTime = now.strftime("%H:%M:%S")
        modifyJsetValue(outputDir, "Creation Name", jsetAbsPath, False)
        modifyJsetValue(outputDir, "Creation Date", jsetNewDate, False)
        modifyJsetValue(outputDir, "Creation Time", jsetNewTime, False)
        print()

        # Tidy the extra namelist section
        print("Removing superfluous Extra Namelist entries...")
        tidyExtraNamelist(outputDir, settingListJetto, valueListJetto)
        print()

        # Set start and end times
        print("Setting run start and end times")
        modifyJsetValue(outputDir, "SetUpPanel.startTime", t0, False)
        modifyJsetValue(outputDir, "SetUpPanel.endTime", t1, False)
        print()

        if (BCflag):
            # Create boundary condition input files from COCONUT JSP output
            boundDir = "/home/" + os.getlogin() + "/cmg/jams/data/boundcond"
            print("Writing boundary cond. files for JETTO input to "  +       \
                  "directory " + f"{boundDir}...")
            #   JST-based
            makeIpBoundaryConditionFile(jstRead, boundDir, fileCoconut,       \
                                        outputDir, tOffsetCoconut, plot)
            #   JSP-based
            makeTeBoundaryConditionFile(jspRead, boundDir, fileCoconut,       \
                                        outputDir, tOffsetCoconut, plot)
            makeTiBoundaryConditionFile(jspRead, boundDir, fileCoconut,       \
                                        outputDir, tOffsetCoconut, plot)
            makeNiBoundaryConditionFiles(jspRead, boundDir, fileCoconut,      \
                                         outputDir, tOffsetCoconut,           \
                                         settingLists, valueLists,            \
                                         settingListJetto, valueListJetto,    \
                                         plot)
            makeVtorBoundaryConditionFile(jspRead, boundDir, fileCoconut,     \
                                          outputDir, tOffsetCoconut, plot)
            print("Boundary condition files written\n")

        # Check and copy over existing input files
        # Check if graybeam.data is latest, cf. ECRH work OPE1057
        datDir = "/home/" + os.getlogin() + "/cmg/jams/data"
        exFileName = exFile(dirCoconutList, datDir, fileCoconut, outputDir)
        modifyExFile(dirCoconutList[0], exFileName[0], ECRHflag)
        modifyJsetValue(outputDir, "EquationsPanel.profileSource",            \
                        "q, Te, Ti, ne from ex-file", False)
        modifyJsetValue(outputDir, "SetUpPanel.selReadIds", "false", False)
        # ? input IDS
        # ? continue case
        boundaryFile(dirCoconutList, datDir, fileCoconut, outputDir)
        grayInputFiles(dirCoconutList, datDir, fileCoconut, outputDir,        \
                       graybeamFlag)
        # ? LH
        # ? external heating

        # Pellets - density feedback
        print("Writing pellet info...")
        makePellets(settingLists, valueLists, outputDir, tOffsetCoconut,      \
                    t0List, t1List, plot)
        print("Pellet info written\n")

        # Construct heating waveforms and write to .jset
        makeHeat(settingLists, valueLists, outputDir, tOffsetCoconut,         \
                 t0List, t1List, ECRHflag, dirCoconutList, plot)

        # Remove all transport panel settings from .jset
        panel = "Transport"
        print("Erasing all " + panel + " panel key values from jetto.jset...")
        eraseJsetPanel(outputDir, panel)
        print("All " + panel + " panel key values erased\n")
        # Copy all transport panel settings from point in COCONUT sequence
        print("Copying all " + panel + " panel key values from COCONUT...")
        setCoconutJsetTransportPanel(outputDir, settingLists, valueLists,     \
                               dirCoconutList, tOffsetCoconut, t0List, t1List)
        print()

        # Remove all MHD ELM panel settings from .jset
        print("Erasing all ELM panel key values from jetto.jset...")
        eraseJsetPanel(outputDir, "ELM")
        eraseJsetPanel(outputDir, "TransportELMS")
        print("All ELM panel key values erased\n")
        # Copy all MHD ELM panel settings from point in COCONUT sequence
        print("Copying all ELM panel key values from COCONUT...")
        setCoconutJsetElmPanel(outputDir, settingLists, valueLists,           \
                               dirCoconutList, tOffsetCoconut, t0List, t1List)
        print()
        # Remove all MHD Sawteeth panel settings from .jset    
        print("Erasing all Sawteeth panel key values from jetto.jset...")
        eraseJsetPanel(outputDir, "Sawteeth")
        eraseJsetPanel(outputDir, "Kdsaw")
        print("All Sawteeth panel key values erased\n")
        # Copy all MHD Sawteeth panel settings from point in COCONUT sequence
        print("Copying all Sawteeth panel key values from COCONUT...")
        setCoconutJsetSawteethPanel(outputDir, settingLists, valueLists,      \
                               dirCoconutList, tOffsetCoconut, t0List, t1List)
        print()

        # Remove all Neutrals panel settings from .jset
        print("Erasing all neutrals panel key values from jetto.jset...")
        eraseJsetPanel(outputDir, "NeutralSource")
        eraseJsetPanel(outputDir, "Frantic")
        eraseJsetPanel(outputDir, "NeutEirene")
        print("All Neutrals panel key values erased\n")
        # Copy all Neutral panel settings from point in COCONUT sequence
        print("Copying all neutrals panel key values from COCONUT...")
        setCoconutJsetNeutralsPanel(outputDir, settingLists, valueLists,      \
                                    dirCoconutList, tOffsetCoconut,           \
                                    t0List, t1List)
        print()

        # L-H transition model
#        print("Setting L-H transition model")
#        lhTransition(outputDir, settingLists, valueLists)
#        print()




#SANCO?




        if plot:
            plt.show()

###############################################################################
    
if __name__ == "__main__":
    main()

###############################################################################
