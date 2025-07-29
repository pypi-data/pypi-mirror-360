import re
import copy
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from jetto_tools import binary

# Common numerical data types, for ease of type-checking
np_itypes = (np.int8, np.int16, np.int32, np.int64)
np_utypes = (np.uint8, np.uint16, np.uint32, np.uint64)
np_ftypes = (np.float16, np.float32, np.float64)

int_types = (int, np_itypes, np_utypes)
float_types = (float, np_ftypes)
number_types = (float_types, int_types)
array_types = (list, tuple, np.ndarray)

def read_qualikiz_gamhistory_data(rundir, gamhistory=1):
    """
    Reads QuaLiKiz printout files generated inside the JETTO run directory
    during a simuation. Since the 'qlk_gamhistory' option determines the
    shape of these data files and is not printed, the user must specify it.

    :returns: dict.
    """
    rpath = Path(rundir) if not isinstance(rundir, Path) else rundir
    gamhist = int(gamhistory) if isinstance(gamhistory, int_types) else 0
    ptopt = 0 # 0 signifies QLK run
    flagpath = rpath / 'gamhistory.qlk'
    if flagpath.is_file():
        # Override passed option with value specified inside run directory, if present
        gamhist = int(np.genfromtxt(str(flagpath)))
    optpath = rpath / 'NN_part_trans_switch.qlk'
    if optpath.is_file():
        ptopt = int(np.genfromtxt(str(optpath)))

    rho = np.genfromtxt(str(rpath / 'rho.qlk')).flatten()
    rhomin = float(np.genfromtxt(str(rpath / 'rhomin.qlk')))
    rhomax = float(np.genfromtxt(str(rpath / 'rhomax.qlk')))
    dimx = len(rho)
    dimt = 1

    output = {}
    output["gamhistory"] = gamhist
    output["part_trans"] = ptopt
    output["rho"] = rho.copy()
    output["rhomin"] = rhomin
    output["rhomax"] = rhomax

    numsols = 0
    dimn = 0
    kpath = rpath / 'kthetarhos.qlk'
    if kpath.exists() and kpath.is_file():
        numsols = int(np.genfromtxt(str(rpath / 'numsols.qlk')))
        dimn = int(np.genfromtxt(str(rpath / 'dimn.qlk')))
        dimx = int(np.genfromtxt(str(rpath / 'dimx.qlk')))
        k = np.genfromtxt(str(rpath / 'kthetarhos.qlk')).flatten()
        output["k"] = k.copy()

    x = np.genfromtxt(str(rpath / 'x.qlk'))
    rzero = np.genfromtxt(str(rpath / 'R0.qlk')) if (rpath / 'R0.qlk').is_file() else np.array([0.0])
    if gamhist <= 2:
        output["x"] = x.flatten()
        output["rzero"] = rzero.reshape(-1, 1)

    if gamhist > 0:

        tpath = rpath / 'time.qlk'
        opath = rpath / 'jetto.out'
        tvec = None
        if tpath.is_file():
            tvec = np.genfromtxt(str(tpath))
            if len(tvec) > 0:
                output["t"] = tvec[::2]
        if "t" not in output and opath.is_file():
            tvec = []
            with open(str(opath), 'r') as ff:
                for line in ff:
                    mm = re.search(r'^\s*STEP=\s*[0-9]+\s+TIME=\s*([0-9\.]+)\s+', line)
                    if mm:
                        tvec.append(float(mm.group(1)))
            if len(tvec) > 0:
                output["t"] = np.array(tvec).flatten()
        dimt = len(tvec)

    if dimn > 0:

        gam = np.genfromtxt(str(rpath / 'gam_GB.qlk'))
        ome = np.genfromtxt(str(rpath / 'ome_GB.qlk'))

        if gamhist in [0, 4]:

            gam = gam.reshape(numsols, dimx, dimn)
            ome = ome.reshape(numsols, dimx, dimn)
            output["gam"] = np.moveaxis(gam, 0, -1)
            output["ome"] = np.moveaxis(ome, 0, -1)

        else:

            gam = gam.reshape(-1, numsols, dimx, dimn)
            gam = np.moveaxis(gam, 1, -1)

            ome = ome.reshape(-1, numsols, dimx, dimn)
            ome = np.moveaxis(ome, 1, -1)

            # Take every other entry due to predictor-corrector scheme
            output["gam"] = gam[::2]
            output["ome"] = ome[::2]

            dimtt = int(output["gam"].shape[0])
            if dimt != dimtt:
                dimt = dimtt

    if gamhist > 1:

        #vpath = rpath / 'verbose.qlk'
        #verbose = int(np.genfromtxt(str(vpath))) if vpath.is_file() else 0
        #if verbose < 2:
        #    raise IOError("JETTO execution not performed with qlk_verbose >= 2!")

        nions = int(np.genfromtxt(str(rpath / 'nions.qlk')))
        ai = np.genfromtxt(str(rpath / 'Ai.qlk'))
        zi = np.genfromtxt(str(rpath / 'Zi.qlk'))

        # File names still use old QuaLiKiz naming convention, output will use the new one
        # Using SI for consistency but these variables are also printed in GB
        efe = np.genfromtxt(str(rpath / 'eef_SI.qlk'))
        pfe = np.genfromtxt(str(rpath / 'epf_SI.qlk'))
        efi = np.genfromtxt(str(rpath / 'ief_SI.qlk'))
        pfi = np.genfromtxt(str(rpath / 'ipf_SI.qlk'))
        vfi = np.genfromtxt(str(rpath / 'ivf_SI.qlk'))

        # The ones below are only printed in SI
        dfe = np.genfromtxt(str(rpath / 'dfe_SI.qlk'))
        vce = np.genfromtxt(str(rpath / 'vce_SI.qlk'))
        vte = np.genfromtxt(str(rpath / 'vte_SI.qlk'))
        dfi = np.genfromtxt(str(rpath / 'dfi_SI.qlk'))
        vci = np.genfromtxt(str(rpath / 'vci_SI.qlk'))
        vti = np.genfromtxt(str(rpath / 'vti_SI.qlk'))
        vri = np.genfromtxt(str(rpath / 'vri_SI.qlk'))

        output["nions"] = nions
        output["ai"] = ai.copy()
        output["zi"] = zi.copy()

        efe = efe.reshape(-1, dimx)
        pfe = pfe.reshape(-1, dimx)
        efi = efi.reshape(-1, dimx, nions)
        pfi = pfi.reshape(-1, dimx, nions)
        vfi = vfi.reshape(-1, dimx, nions)

        dfe = dfe.reshape(-1, dimx)
        vce = vce.reshape(-1, dimx)
        vte = vte.reshape(-1, dimx)
        dfi = dfi.reshape(-1, dimx, nions)
        vci = vci.reshape(-1, dimx, nions)
        vti = vti.reshape(-1, dimx, nions)
        vri = vri.reshape(-1, dimx, nions)

        # Take every other entry due to predictor-corrector scheme
        output["efe"] = efe[::2]
        output["pfe"] = pfe[::2]
        output["efi"] = efi[::2]
        output["pfi"] = pfi[::2]
        output["vfi"] = vfi[::2]
        output["dfe"] = dfe[::2]
        output["vce"] = vce[::2]
        output["vte"] = vte[::2]
        output["dfi"] = dfi[::2]
        output["vci"] = vci[::2]
        output["vti"] = vti[::2]
        output["vri"] = vri[::2]

        nto = int(output["efe"].shape[0])

    if gamhist > 2:

        nions = int(np.genfromtxt(str(rpath / 'nions.qlk')))

        # Geometry variables
        ro = np.genfromtxt(str(rpath / 'Ro.qlk'))
        rmin = np.genfromtxt(str(rpath / 'Rmin.qlk'))
        bo = np.genfromtxt(str(rpath / 'Bo.qlk'))

        # Gradient variables
        smag = np.genfromtxt(str(rpath / 'smag.qlk'))
        alpha = np.genfromtxt(str(rpath / 'alphax.qlk'))
        rlne = np.genfromtxt(str(rpath / 'Ane.qlk'))
        rlte = np.genfromtxt(str(rpath / 'Ate.qlk'))
        rlni = np.genfromtxt(str(rpath / 'Ani.qlk'))
        rlti = np.genfromtxt(str(rpath / 'Ati.qlk'))

        # Kinetic variables
        q = np.genfromtxt(str(rpath / 'qx.qlk'))
        ne = np.genfromtxt(str(rpath / 'Nex.qlk'))
        te = np.genfromtxt(str(rpath / 'Tex.qlk'))
        ni = np.genfromtxt(str(rpath / 'ninorm.qlk'))
        ti = np.genfromtxt(str(rpath / 'Tix.qlk'))
        nustar = np.genfromtxt(str(rpath / 'Nustar.qlk'))
        zeff = np.genfromtxt(str(rpath / 'Zeffx.qlk'))
        ai = np.genfromtxt(str(rpath / 'Ai.qlk'))
        zi = np.genfromtxt(str(rpath / 'Zi.qlk'))

        # Rotation variables
        mtor = np.genfromtxt(str(rpath / 'Machtor.qlk'))
        mpar = np.genfromtxt(str(rpath / 'Machpar.qlk'))
        rlutor = np.genfromtxt(str(rpath / 'Autor.qlk'))
        rlupar = np.genfromtxt(str(rpath / 'Aupar.qlk'))
        gammae = np.genfromtxt(str(rpath / 'gammaE.qlk'))

        rzero = rzero.reshape(-1, 1)   # This variable is read at the start
        ro = ro.reshape(-1, dimx)
        rmin = rmin.reshape(-1, dimx)
        bo = bo.reshape(-1, dimx)
        smag = smag.reshape(-1, dimx)
        alpha = alpha.reshape(-1, dimx)
        rlne = rlne.reshape(-1, dimx)
        rlte = rlte.reshape(-1, dimx)
        rlni = rlni.reshape(-1, dimx, nions)
        rlti = rlti.reshape(-1, dimx, nions)
        x = x.reshape(-1, dimx)   # This variable is read at the start
        q = q.reshape(-1, dimx)
        ne = ne.reshape(-1, dimx)
        te = te.reshape(-1, dimx)
        ni = ni.reshape(-1, dimx, nions)
        ti = ti.reshape(-1, dimx, nions)
        nustar = nustar.reshape(-1, dimx)
        zeff = zeff.reshape(-1, dimx)
        ai = ai.reshape(-1, dimx, nions)
        zi = zi.reshape(-1, dimx, nions)
        mtor = mtor.reshape(-1, dimx)
        mpar = mpar.reshape(-1, dimx)
        rlutor = rlutor.reshape(-1, dimx)
        rlupar = rlupar.reshape(-1, dimx)
        gammae = gammae.reshape(-1, dimx)

        for ii in range(nions):
            ni[:,:,ii] = ni[:,:,ii] * ne

        output["rzero"] = rzero[::2]
        output["ro"] = ro[::2]
        output["rmin"] = rmin[::2]
        output["bo"] = bo[::2]
        output["smag"] = smag[::2]
        output["alpha"] = alpha[::2]
        output["rlne"] = rlne[::2]
        output["rlte"] = rlte[::2]
        output["rlni"] = rlni[::2]
        output["rlti"] = rlti[::2]
        output["x"] = x[::2]
        output["q"] = q[::2]
        output["ne"] = ne[::2] * 1.0e19
        output["te"] = te[::2] * 1.0e3
        output["ni"] = ni[::2] * 1.0e19
        output["ti"] = ti[::2] * 1.0e3
        output["nustar"] = nustar[::2]
        output["zeff"] = zeff[::2]
        output["ai"] = ai[::2]
        output["zi"] = zi[::2]
        output["machtor"] = mtor[::2]
        output["machpar"] = mpar[::2]
        output["rlutor"] = rlutor[::2]
        output["rlupar"] = rlupar[::2]
        output["gammae"] = gammae[::2]

        nti = int(output["smag"].shape[0])

    return output


def remove_duplicate_times(data):
    """
    Removes entries with an identical time signature as another entry.
    In case of duplicates, keeps the last entry in vector.

    :returns: dict.
    """
    if isinstance(data, dict) and "t" in data:

        tmask = []
        tprev = -999.0
        for ii in range(len(data["t"])-1, -1, -1):
            if np.abs(data["t"][ii] - tprev) < 1.0e-6:
                tmask.append(False)
            else:
                tmask.append(True)
                tprev = float(data["t"][ii])
        tmask = tmask[::-1]

        for key in data:
            if isinstance(data[key], np.ndarray) and data[key].shape[0] == len(tmask):
                data[key] = data[key][tmask]

    return data


def separate_gamhistory_species(data):
    """
    Separates the ions into separate entries for ease of generalization.
    This also renames these respective fields.

    :returns: dict.
    """
    qlkdata = {}
    direct_transfer_labels = ["t",
                              "rho",
                              "x",
                              "q",
                              "smag",
                              "alpha",
                              "nustar",
                              "zeff",
                              "machtor",
                              "machpar",
                              "rlutor",
                              "rlupar",
                              "gammae"
                             ]

    if isinstance(data, dict):

        # Assume latest updates have not yet been added, if flag is not specified
        qlkdata["histopt"] = data["gamhistory"] if "gamhistory" in data else 2
        qlkdata["ptopt"] = data["part_trans"] if "part_trans" in data else 0

        for key in direct_transfer_labels:
            if key in data:
                qlkdata[key] = data[key].copy()

        # Expands rzero variable to have the same shape as the other input variables (better to place elsewhere?)
        if "t" in data and "rho" in data and "rzero" in data and data["rzero"].shape[0] == len(data["t"]):
            rzero = data["rzero"].copy()
            for ii in range(1,len(data["rho"])):
                rzero = np.hstack((rzero, data["rzero"].copy()))
            qlkdata["rzero"] = rzero
        elif "rzero" in data:
            qlkdata["rzero"] = data["rzero"].copy()

        numions = 1
        numimps = 0
        if "zi" in data:
            zion1 = 1.0
            for ii in range(0, data["zi"].shape[-1]):
                zion = np.mean(data["zi"][:,:,ii])
                if ii == 0:
                    zion1 = zion
                elif zion < (zion1 + 0.5):
                    numions += 1
            numimps = data["zi"].shape[-1] - numions
        qlkdata["numi"] = numions
        qlkdata["numimp"] = numimps
        if (qlkdata["numi"] + qlkdata["numimp"]) != data["nions"]:
            print("Odd behaviour in gamhistory extraction tool, separation of main ion and impurities creates inconsistency.")

        if "efe" in data:
            qlkdata["efae"] = data["efe"].copy()
        if "pfe" in data:
            qlkdata["pfae"] = data["pfe"].copy()
        if "dfe" in data:
            qlkdata["dae"] = data["dfe"].copy()
            qlkdata["vae"] = np.zeros(qlkdata["dae"].shape)
            if "vce" in data:
                qlkdata["vae"] += data["vce"]
            if "vte" in data:
                qlkdata["vae"] += data["vte"]
        for ii in range(0, numions):
            ftag = "i%d" % (ii+1)
            if "efi" in data:
                qlkdata["efa"+ftag] = data["efi"][:,:,ii].squeeze()
            if "pfi" in data:
                qlkdata["pfa"+ftag] = data["pfi"][:,:,ii].squeeze()
            if "dfi" in data:
                qlkdata["da"+ftag] = data["dfi"][:,:,ii].squeeze()
                qlkdata["va"+ftag] = np.zeros(qlkdata["da"+ftag].shape)
                if "vci" in data:
                    qlkdata["va"+ftag] += data["vci"][:,:,ii].squeeze()
                if "vti" in data:
                    qlkdata["va"+ftag] += data["vti"][:,:,ii].squeeze()
                if "vri" in data:
                    qlkdata["va"+ftag] += data["vri"][:,:,ii].squeeze()
        for ii in range(0, numimps):
            ftag = "imp%d" % (ii+1)
            idx = ii + numions
            if "efi" in data:
                qlkdata["efa"+ftag] = data["efi"][:,:,idx].squeeze()
            if "pfi" in data:
                qlkdata["pfa"+ftag] = data["pfi"][:,:,idx].squeeze()
            if "dfi" in data:
                qlkdata["da"+ftag] = data["dfi"][:,:,idx].squeeze()
                qlkdata["va"+ftag] = np.zeros(qlkdata["da"+ftag].shape)
                if "vci" in data:
                    qlkdata["va"+ftag] += data["vci"][:,:,idx].squeeze()
                if "vti" in data:
                    qlkdata["va"+ftag] += data["vti"][:,:,idx].squeeze()
                if "vri" in data:
                    qlkdata["va"+ftag] += data["vri"][:,:,idx].squeeze()

        if "ne" in data:
            qlkdata["ne"] = data["ne"].copy()
            qlkdata["ze"] = -np.ones(qlkdata["ne"].shape)
        if "te" in data:
            qlkdata["te"] = data["te"].copy()
        if "rlne" in data:
            qlkdata["rlne"] = data["rlne"].copy()
        if "rlte" in data: 
            qlkdata["rlte"] = data["rlte"].copy()
        for ii in range(0, numions):
            ftag = "i%d" % (ii+1)
            if "ni" in data:
                qlkdata["n"+ftag] = data["ni"][:,:,ii].squeeze()
                if "zi" in data:
                    qlkdata["z"+ftag] = data["zi"][:,:,ii].squeeze()
            if "ti" in data:
                qlkdata["t"+ftag] = data["ti"][:,:,ii].squeeze()
            if "rlni" in data:
                qlkdata["rln"+ftag] = data["rlni"][:,:,ii].squeeze()
            if "rlti" in data: 
                qlkdata["rlt"+ftag] = data["rlti"][:,:,ii].squeeze()
            if "ai" in data:
                qlkdata["a"+ftag] = np.atleast_2d(data["ai"][:,:,ii].squeeze())
        for ii in range(0, numimps):
            ftag = "imp%d" % (ii+1)
            idx = ii + numions
            if "ni" in data:
                qlkdata["n"+ftag] = data["ni"][:,:,idx].squeeze()
                if "zi" in data:
                    qlkdata["z"+ftag] = data["zi"][:,:,idx].squeeze()
            if "ti" in data:
                qlkdata["t"+ftag] = data["ti"][:,:,idx].squeeze()
            if "rlni" in data:
                qlkdata["rln"+ftag] = data["rlni"][:,:,idx].squeeze()
            if "rlti" in data: 
                qlkdata["rlt"+ftag] = data["rlti"][:,:,idx].squeeze()
            if "ai" in data:
                qlkdata["a"+ftag] = np.atleast_2d(data["ai"][:,:,idx].squeeze())

        # Transfer growth rate and frequency information
        if qlkdata["histopt"] not in [0, 4] and "k" in data and "gam" in data and "ome" in data:
            qlkdata["k"] = data["k"].copy()
            numsols = int(data["gam"].shape[-1])
            qlkdata["nums"] = numsols
            for ss in range(0, numsols):
                stag = "s%d" % (ss+1)
                qlkdata["gam"+stag] = data["gam"][:,:,:,ss].squeeze()
                qlkdata["ome"+stag] = data["ome"][:,:,:,ss].squeeze()

    return qlkdata


def transfer_transport_quantities(data):
    """
    Fills in effective transport coefficients based on particle transport option chosen
    within the JETTO run, only applicable when using QLKNN.

    :returns: dict.
    """
    if isinstance(data, dict) and "numi" in data and "numimp" in data and "ptopt" in data and data["ptopt"] != 0:

        print("QLKNN run detected with particle transport option %d, transferring coefficients..." % (data["ptopt"]))

        # Option 3 only transfers main ion D to all ions, option 6 transfers main ion D and V to all ions
        if data["ptopt"] in [3, 6] and "dai1" in data and np.sum(data["dai1"]) > 0.0:
            for ii in range(1, data["numi"]):
                itag = "i%d" % (ii+1)
                data["da"+itag] = data["dai1"].copy()
                if data["ptopt"] == 6:
                    data["va"+itag] = data["vai1"].copy()
            for ii in range(data["numimp"]):
                itag = "imp%d" % (ii+1)
                data["da"+itag] = data["dai1"].copy()
                if data["ptopt"] == 6:
                    data["va"+itag] = data["vai1"].copy()

        # Option 2 only transfers electron D to all ions, option 5 transfers electron D and V to all ions
        if data["ptopt"] in [2, 5] and "dae" in data and np.sum(data["dae"]) > 0.0:
            for ii in range(data["numi"]):
                itag = "i%d" % (ii+1)
                data["da"+itag] = data["dae"].copy()
                if data["ptopt"] == 5:
                    data["va"+itag] = data["vae"].copy()
            for ii in range(data["numimp"]):
                itag = "imp%d" % (ii+1)
                data["da"+itag] = data["dae"].copy()
                if data["ptopt"] == 5:
                    data["va"+itag] = data["vae"].copy()

    return data


def read_jetto_neoclassical_data(rundir, numions=1, numimps=0):
    """
    Reads the neoclassical transport coefficients from the official JETTO
    run output files. Currently does not check if existing files in the
    directory form a complete set, only that specific individual files
    exist.

    :returns: dict.
    """
    ncdata = {}
    rpath = Path(rundir) if isinstance(rundir, str) else rundir
    if rpath.is_dir():

        nions = numions if isinstance(numions, int_types) and numions > 0 else 1
        nimps = numimps if isinstance(numimps, int_types) and numimps > 0 else 0

        # Neoclassical transport coefficients for electrons and main ions found in JSP
        tpath = rpath / "jetto.jsp"
        temprout = None
        temprhoout = None
        temprminout = None
        if tpath.is_file():
            tempdata = binary.read_binary_file(str(tpath.resolve()))
            if tempdata:
                # Note that JETTO output time vector is read from JSP!
                ncdata["jt"] = tempdata["TIME"].copy()
                temprout = np.hstack((np.atleast_2d(tempdata["R"][:,0]).T,tempdata["R"]))
                temprhoout = np.hstack((np.atleast_2d(tempdata["XRHO"][:,0]).T,tempdata["XRHO"]))
                temprminout = np.abs(temprout - np.hstack((np.atleast_2d(tempdata["RI"][:,0]).T,tempdata["RI"]))) / 2.0
                ndim0 = temprout.shape[0]

                ncdata["afs"] = np.hstack((np.atleast_2d(tempdata["SURF"][:,0]).T,tempdata["SURF"]))
                ncdata["acs"] = np.hstack((np.atleast_2d(tempdata["AREA"][:,0]).T,tempdata["AREA"]))
                ncdata["vfs"] = np.hstack((np.atleast_2d(tempdata["VOL"][:,0]).T,tempdata["VOL"]))

                outn = np.hstack((np.atleast_2d(tempdata["NE"][:,0]).T,tempdata["NE"]))
                outdn = np.hstack((np.zeros((ndim0,1)),np.diff(outn,axis=1) / np.diff(temprminout,axis=1)))
                outt = np.hstack((np.atleast_2d(tempdata["TE"][:,0]).T,tempdata["TE"]))
                outdt = np.hstack((np.zeros((ndim0,1)),np.diff(outt,axis=1) / np.diff(temprminout,axis=1)))
                outd = np.hstack((np.atleast_2d(tempdata["DNCE"][:,0]).T,tempdata["DNCE"],np.atleast_2d(tempdata["DNCE"][:,-1]).T))
                outv = np.hstack((np.atleast_2d(tempdata["VNCE"][:,0]).T,tempdata["VNCE"],np.atleast_2d(tempdata["VNCE"][:,-1]).T))
                outx = np.hstack((np.atleast_2d(tempdata["XE1"][:,0]).T,tempdata["XE1"],np.atleast_2d(tempdata["XE1"][:,-1]).T))
                ncdata["dnce"] = outd.copy()
                ncdata["vnce"] = outv.copy()
                ncdata["pfnce"] = -outd * outdn + outv * outn
                ncdata["xnce"] = outx.copy()
                ncdata["efnce"] = -outx * outdt

                outn = np.hstack((np.atleast_2d(tempdata["NI"][:,0]).T,tempdata["NI"]))
                outdn = np.hstack((np.zeros((ndim0,1)),np.diff(outn,axis=1) / np.diff(temprminout,axis=1)))
                outt = np.hstack((np.atleast_2d(tempdata["TI"][:,0]).T,tempdata["TI"]))
                outdt = np.hstack((np.zeros((ndim0,1)),np.diff(outt,axis=1) / np.diff(temprminout,axis=1)))
                outd = np.hstack((np.atleast_2d(tempdata["DNCI"][:,0]).T,tempdata["DNCI"],np.atleast_2d(tempdata["DNCI"][:,-1]).T))
                outv = np.hstack((np.atleast_2d(tempdata["VNCI"][:,0]).T,tempdata["VNCI"],np.atleast_2d(tempdata["VNCI"][:,-1]).T))
                outx = np.hstack((np.atleast_2d(tempdata["XI1"][:,0]).T,tempdata["XI1"],np.atleast_2d(tempdata["XI1"][:,-1]).T))
                ncdata["dnci1"] = outd.copy()
                ncdata["vnci1"] = outv.copy()
                ncdata["pfnci1"] = -outd * outdn + outv * outn
                ncdata["xnci1"] = outx.copy()
                ncdata["efnci1"] = -outx * outdt

                # This does not really work with multiple main ions... nonsense lines commented out
                if nions > 1:
                    #outn = np.hstack((np.atleast_2d(tempdata["NI"][:,0]).T,tempdata["NI"]))
                    #outdn = np.hstack((np.zeros((ndim0,1)),np.diff(outn,axis=1) / np.diff(temprminout,axis=1)))
                    #outt = np.hstack((np.atleast_2d(tempdata["TI"][:,0]).T,tempdata["TI"]))
                    #outdt = np.hstack((np.zeros((ndim0,1)),np.diff(outt,axis=1) / np.diff(temprminout,axis=1)))
                    outd = np.hstack((np.atleast_2d(tempdata["DNC1"][:,0]).T,tempdata["DNC1"],np.atleast_2d(tempdata["DNC1"][:,-1]).T))
                    outv = np.hstack((np.atleast_2d(tempdata["VNC1"][:,0]).T,tempdata["VNC1"],np.atleast_2d(tempdata["VNC1"][:,-1]).T))
                    #outx = np.hstack((np.atleast_2d(tempdata["XI1"][:,0]).T,tempdata["XI1"],np.atleast_2d(tempdata["XI1"][:,-1]).T))
                    ncdata["dnci2"] = outd.copy()
                    ncdata["vnci2"] = outv.copy()
                    #ncdata["pfnci2"] = -outd * outdn + outv * outn
                    #ncdata["xnci2"] = outx.copy()
                    #ncdata["efnci2"] = -outx * outdt

        # Neoclassical transport coefficients for impurity ions found in SSP#
        temprin = None
        tpath = rpath / "jetto.ssp"
        if tpath.is_file():
            tempdata = binary.read_binary_file(str(tpath.resolve()))
            temprin = tempdata["RMJC"]
            temprhoin = tempdata["XRHO"] if "XRHO" in tempdata else None
            for ii in range(nimps):
                fname = "jetto.ssp%d" % (ii+1)
                tpath = rpath / fname
                impdata = binary.read_binary_file(str(tpath.resolve()))
                if impdata and temprout is not None and temprin is not None:
                    ftag = "imp%d" % (ii+1)
                    tempn = impdata["NI"]
                    tempd = impdata["DNAV"]
                    tempv = impdata["VNAV"]
                    ndim0 = temprout.shape[0]
                    ndim1 = temprout.shape[1]
                    outn = np.zeros((ndim0,ndim1))
                    outd = np.zeros((ndim0,ndim1))
                    outv = np.zeros((ndim0,ndim1))
                    # SSP# files only have major radius (outer?) as a true radial coordinate, requires major radius vector from JSP to unify grids
                    for tt in range(temprout.shape[0]):
                        rintin = temprhoin.copy() if temprhoout is not None and temprhoin is not None else temprin.copy()
                        rintout = temprhoout[tt,:] if temprhoout is not None and temprhoin is not None else temprout[tt,:]
                        if tt+1 < rintin.shape[0]:
                            infunc = interp1d(rintin[tt+1,:],tempn[tt,:],kind='linear',bounds_error=False,fill_value='extrapolate')
                            outn[tt,:] = infunc(rintout)
                            idfunc = interp1d(rintin[tt+1,:],tempd[tt,:],kind='linear',bounds_error=False,fill_value='extrapolate')
                            outd[tt,:] = idfunc(rintout)
                            ivfunc = interp1d(rintin[tt+1,:],tempv[tt,:],kind='linear',bounds_error=False,fill_value='extrapolate')
                            outv[tt,:] = ivfunc(rintout)
                    outdn = np.hstack((np.atleast_2d(np.zeros((ndim0,1))),np.diff(outn,axis=1) / np.diff(temprminout,axis=1)))
                    ncdata["dnc"+ftag] = outd.copy()
                    ncdata["vnc"+ftag] = outv.copy()
                    ncdata["pfnc"+ftag] = -outd * outdn + outv * outn

    return ncdata


def unify_base_vectors(data, time_start=None, time_end=None, time_window=None, time=None, rho=None):
    """
    Unifies the radial and time vectors of the extracted data. Places all the data,
    with unified base vectors, into a pandas DataFrame to aid further processing.

    Note: Not all fields in the input dictionary are transferred!

    :returns: dict
    """
    output = None
    constants = None
    if isinstance(data, dict):

        output = {}
        constants = {}

        # Select appropriate time vector to use as the basis - JSP or gamhistory
        time_option = 0
        tvec = data["t"].copy()
        twin = None
        if isinstance(time_window, number_types):
            twin = float(np.abs(time_window))
            time_option = 1
            if "jt" in data and len(data["jt"]) < len(tvec):
                tvec = data["jt"].copy()
                if (1.25 * twin) < float(np.mean(np.abs(np.diff(tvec.flatten())))):
                    time_option = 2
                    print("Requested time window is sufficiently smaller than average time resolution in JETTO output, centering windows on JETTO times")

        # Map requested time points onto nearest time point in output - avoids interpolation but risks duplicate time entries
        if isinstance(time, number_types):
            tidxv = np.where(tvec >= time)[0]
            tidxt = -1
            if len(tidxv) > 0:
                tidxt = tidxv[0]-1 if tidxv[0] > 0 and np.abs(tvec[tidxv[0]] - time) > np.abs(tvec[tidxv[0]-1] - time) else tidxv[0]
            tidx = [tidxt]
            tvec = np.array([tvec[tidx]]).flatten()
            time_option = 2
        elif isinstance(time, array_types):
            tidx = []
            for tt in range(len(time)):
                tidxv = np.where(tvec >= time[tt])[0]
                tidxt = -1
                if len(tidxv) > 0:
                    tidxt = tidxv[0]-1 if tidxv[0] > 0 and np.abs(tvec[tidxv[0]] - time[tt]) > np.abs(tvec[tidxv[0]-1] - time[tt]) else tidxv[0]
                if tidxt not in tidx:
                    tidx.append(tidxt)
            if len(tidx) > 0:
                tvec = np.array([tvec[tidx]]).flatten()
                time_option = 2

        # Determine start and end times of analysis range
        ts = float(time_start) if isinstance(time_start, number_types) else float(np.nanmin(data["t"])) - 0.001
        te = float(time_end) if isinstance(time_end, number_types) else float(np.nanmax(data["t"])) + 0.001
        if te < ts:
            dummy = ts
            ts = te
            te = dummy
        tfilt = (tvec >= ts) & (tvec <= te)
        if not np.all(tfilt):
            tvec = tvec[tfilt]
        if "t" in data:
            constants["t_full"] = data["t"].copy()
        if "jt" in data:
            constants["t_jsp"] = data["jt"].copy()

        # Separate time range into windows, if requested
        tlist = []
        ftvec = tvec.copy()
        if twin is not None and time_option == 1:
            ftvec = np.array([])
            nwindows = int((te - ts) / twin)
            ti = ts
            for tt in range(nwindows):
                tf = ti + twin
                ftvec = np.hstack((ftvec, (ti + tf) / 2.0))
                tlist.append((ti, tf))
                ti = tf
        elif twin is not None and time_option == 2:
            for tt in range(len(tvec)):
                ti = float(tvec[tt]) - 0.5 * twin
                tf = float(tvec[tt]) + 0.5 * twin
                tlist.append((ti, tf))
        else:
            for tt in range(len(tvec)):
                tlist.append((tvec[tt], None))
        output["t"] = ftvec.copy()

        # Map requested radial points onto nearest radial point in output - avoids interpolation but risks duplicate radial entries
        rvec = data["rho"].copy()
        ridx = np.arange(0, len(rvec)).tolist()
        if isinstance(rho, number_types):
            ridxv = np.where(rvec >= rho)[0]
            ridxt = -1
            if len(ridxv) > 0:
                ridxt = ridxv[0]-1 if ridxv[0] > 0 and np.abs(rvec[ridxv[0]] - rho) > np.abs(rvec[ridxv[0]-1] - rho) else ridxv[0]
            ridx = [ridxt]
            rvec = np.array([rvec[ridx]]).flatten()
        elif isinstance(rho, array_types):
            ridx = []
            for xx in range(len(rho)):
                ridxv = np.where(rvec >= rho[xx])[0]
                ridxt = -1
                if len(ridxv) > 0:
                    ridxt = ridxv[0]-1 if ridxv[0] > 0 and np.abs(rvec[ridxv[0]] - rho[xx]) > np.abs(rvec[ridxv[0]-1] - rho[xx]) else ridxv[0]
                if ridxt not in ridx:
                    ridx.append(ridxt)
            if len(ridx) > 0:
                rvec = np.array([rvec[ridx]]).flatten()
        if "rho" in data:
            constants["rho_full"] = data["rho"].copy()
        if "jrho" in data:
            constants["rho_jsp"] = data["jrho"].copy()
        output["rho"] = rvec.copy()

        kvec = data["k"].copy() if "k" in data else None
        if kvec is not None:
            output["k"] = kvec.copy()

        # Move inappropriately shaped or typed data into a separate container
        for key in ["histopt", "ptopt", "numi", "numimp", "nums"]:
            if key in data:
                constants[key] = copy.deepcopy(data[key])

        # Loop through each determined time window for averaging and storing data
        for tstep in range(len(tlist)):

            # Setup list of fields to ignore due to inappropriate shape
            oddfields = ["histopt", "ptopt", "numi", "numimp", "nums", "t", "rho", "k", "jt", "jrho"]
            if "histopt" in data and data["histopt"] <= 2:
                oddfields.append("rzero")
            if "rzero" in data and len(data["rzero"]) == 1:
                oddfields.append("rzero")
                output["rzero"] = data["rzero"].copy()

            # Loop over remaining keys and average data within the window mask
            for key in data:

                if key not in oddfields:

                    flattvec = data["t"].flatten()
                    if "jt" in data and data[key].shape[0] < len(flattvec):
                        flattvec = data["jt"].flatten()

                    # Generate mask in time basis for selecting which entries to average over
                    tidxv = np.where(flattvec >= tlist[tstep][0])[0]
                    tidx = [tidxv[0]] if len(tidxv) > 0 else [len(flattvec) - 1]
                    tidx1 = tidx[0]
                    if tidx1 > 0 and np.abs(flattvec[tidx1-1] - tlist[tstep][0]) < np.abs(flattvec[tidx1] - tlist[tstep][0]):
                        tidx1 -= 1
                    if tlist[tstep][1] is not None:
                        tidxv2 = np.where(flattvec > tlist[tstep][1])[0]
                        tidx2 = tidxv2[0] if len(tidxv2) > 0 else len(flattvec) - 1
                        if tidx2 > 0 and np.abs(flattvec[tidx2-1] - tlist[tstep][1]) < np.abs(flattvec[tidx2] - tlist[tstep][1]):
                            tidx2 -= 1
                        if tidx2 != tidx1:
                            tidx = np.arange(tidx1, tidx2+1).tolist()

                    fadd = False
                    if key.startswith("gams") or key.startswith("omes"):
                        dtemp = np.atleast_3d(data[key][tidx])
                        if dtemp.shape[0] > 1:
                            dtemp = np.mean(dtemp, axis=0)
                        dtemp = np.atleast_3d(dtemp.squeeze()[ridx])
                        dtemp = np.moveaxis(dtemp, -1, 0)
                        fadd = True
                    elif key.startswith("ai"):
                        dtemp = np.atleast_2d(data[key])
                        if dtemp.ndim == 3:
                            dtemp = np.atleast_2d(data[key][tidx])
                        if dtemp.shape[0] > 1:
                            dtemp = np.mean(dtemp, axis=0)
                        dtemp = np.atleast_2d(dtemp.squeeze()[ridx])
                        fadd = True
                    else:
                        dtemp = np.atleast_2d(data[key][tidx])
                        if dtemp.shape[0] > 1:
                            dtemp = np.mean(dtemp, axis=0)
                        dtemp = np.atleast_2d(dtemp.squeeze()[ridx])
                        fadd = True
                    if fadd:
                        if key not in output:
                            output[key] = dtemp.copy()
                        else:
                            output[key] = np.concatenate((output[key], dtemp), axis=0)

    return (output, constants)


def convert_fluxes_to_dataframe(data):
    """
    Inserts 2D flux arrays (t, rho) into a multi-indexed pd.DataFrame object by
    flattening them. This improves user-friendly when working with the data.

    :returns: pd.DataFrame
    """
    output = None
    if isinstance(data, dict) and "t" in data and "rho" in data:

        # Expand time and radius base vectors to match 2D gamhistory output
        (rmesh, tmesh) = np.meshgrid(data["rho"], data["t"])

        # Flatten all corresponding data and transfer into a separate container, correspondence based on shape
        fpass = False
        fdict = {"t": tmesh.flatten(), "rho": rmesh.flatten()}
        for key in data:
            if data[key].shape == tmesh.shape:
                fdict[key] = data[key].flatten()
                fpass = True

        # Store entries into a pandas DataFrame, assumes consistent data array shapes
        if fpass:
            trange = np.arange(len(data["t"]))
            rrange = np.arange(len(data["rho"]))
            findex = pd.MultiIndex.from_product([trange, rrange], names=["t_idx","rho_idx"])
            output = pd.DataFrame(fdict, index=findex)

    return output


def convert_eigenvalues_to_dataframe(data):
    """
    Inserts 3D eigenvalue arrays (t, rho, k) into a multi-indexed pd.DataFrame object by
    flattening them. This improves user-friendly when working with the data.

    :returns: pd.DataFrame
    """
    output = None
    if isinstance(data, dict) and "t" in data and "rho" in data and "k" in data:

        # Expand time and radius base vectors to match 3D gamhistory output
        (rmesh, tmesh, kmesh) = np.meshgrid(data["rho"], data["t"], data["k"])

        # Flatten all corresponding data and transfer into a separate container, correspondence based on shape
        fpass = False
        edict = {"t": tmesh.flatten(), "rho": rmesh.flatten(), "k": kmesh.flatten()}
        for key in data:
            if data[key].shape == tmesh.shape:
                edict[key] = data[key].flatten()
                fpass = True

        if fpass:
            trange = np.arange(len(data["t"]))
            rrange = np.arange(len(data["rho"]))
            krange = np.arange(len(data["k"]))
            eindex = pd.MultiIndex.from_product([trange, rrange, krange], names=["t_idx","rho_idx","k_idx"])
            output = pd.DataFrame(edict, index=eindex)

    return output


##### The functions in this block are meant to be specific to an analysis routine

def compute_derived_quantities(data, rzero=None, numions=0, numimps=0):
    """
    Computes various derived quantities from the extracted transport coefficients,
    including:
    
    Metrics for density peaking, assuming dn/dt = 0.
    Metrics for total particle flux

    :returns: pd.DataFrame
    """
    if isinstance(data, (dict, pd.DataFrame)):

        lref = float(rzero) if isinstance(rzero, number_types) else 3.0
        if "rzero" in data:
            lref = data["rzero"]
            if isinstance(rzero, number_types):
                print("Reference length quantity found in run directory, overriding the user-defined value!")

        qtag = "ne"
        if "da"+qtag[1:] in data:
            d_turb = data["da"+qtag[1:]]
            v_turb = np.zeros(d_turb.shape)
            if "va"+qtag[1:] in data:
                v_turb = data["va"+qtag[1:]]
            if np.sum(d_turb) > 0.0 and np.sum(v_turb) == 0.0 and "pfa"+qtag[1:] in data and qtag in data:
                gtemp = data["rl"+qtag] if "rl"+qtag in data else data["a"+qtag]
                v_turb = data["pfa"+qtag[1:]] / data[qtag] - data["da"+qtag[1:]] * gtemp / lref
            data["rvd"+qtag[1:]] = -lref * v_turb / (d_turb + 1.0e-10)
            if "dnc"+qtag[1:] in data:
                d_nc = data["dnc"+qtag[1:]]
                v_nc = np.zeros(d_nc.shape)
                if "vnc"+qtag[1:] in data:
                    v_nc = data["vnc"+qtag[1:]]
                data["rvdt"+qtag[1:]] = -lref * (v_turb + v_nc) / (d_turb + d_nc + 1.0e-10)
        else:
            data["rvd"+qtag[1:]] = 0.0
            data["rvdt"+qtag[1:]] = 0.0
        if "pfa"+qtag[1:] in data:
            f_turb = data["pfa"+qtag[1:]]
            f_nc = np.zeros(f_turb.shape)
            if "pfnc"+qtag[1:] in data:
                f_nc = data["pfnc"+qtag[1:]]
            data["pft"+qtag[1:]] = (f_turb + f_nc)
        else:
            data["pft"+qtag[1:]] = 0.0

        qtag = "te"
        if "efa"+qtag[1:] in data and "rl"+qtag in data and qtag in data:
            data["xa"+qtag[1:]] = data["efa"+qtag[1:]] * lref / (data["rl"+qtag] * data[qtag] + 1.0e-10)
        else:
            data["xa"+qtag[1:]] = 0.0

        for ii in range(numions):

            qtag = "ni%d" % (ii+1)
            if "da"+qtag[1:] in data:
                d_turb = data["da"+qtag[1:]]
                v_turb = np.zeros(d_turb.shape)
                if "va"+qtag[1:] in data:
                    v_turb = data["va"+qtag[1:]]
                if np.sum(d_turb) != 0.0 and np.sum(v_turb) == 0.0 and "pfa"+qtag[1:] in data and qtag in data:
                    gtemp = data["rl"+qtag] if "rl"+qtag in data else data["a"+qtag]
                    v_turb = data["pfa"+qtag[1:]] / data[qtag] - data["da"+qtag[1:]] * gtemp / lref
                data["rvd"+qtag[1:]] = -lref * v_turb / (d_turb + 1.0e-10)
                if "dnc"+qtag[1:] in data:
                    d_nc = data["dnc"+qtag[1:]]
                    v_nc = np.zeros(d_nc.shape)
                    if "vnc"+qtag[1:] in data:
                        v_nc = data["vnc"+qtag[1:]]
                    data["rvdt"+qtag[1:]] = -lref * (v_turb + v_nc) / (d_turb + d_nc + 1.0e-10)
            else:
                data["rvd"+qtag[1:]] = 0.0
                data["rvdt"+qtag[1:]] = 0.0
            if "pfa"+qtag[1:] in data:
                f_turb = data["pfa"+qtag[1:]]
                f_nc = np.zeros(f_turb.shape)
                if "pfnc"+qtag[1:] in data:
                    f_nc = data["pfnc"+qtag[1:]]
                data["pft"+qtag[1:]] = (f_turb + f_nc)
            else:
                data["pft"+qtag[1:]] = 0.0

            qtag = "ti%d" % (ii+1)
            if "efa"+qtag[1:] in data and "rl"+qtag in data and qtag in data:
                data["xa"+qtag[1:]] = data["efa"+qtag[1:]] * lref / (data["rl"+qtag] * data[qtag] + 1.0e-10)
            else:
                data["xa"+qtag[1:]] = 0.0

        for ii in range(numimps):

            qtag = "nimp%d" % (ii+1)
            if "da"+qtag[1:] in data:
                d_turb = data["da"+qtag[1:]]
                v_turb = np.zeros(d_turb.shape)
                if "va"+qtag[1:] in data:
                    v_turb = data["va"+qtag[1:]]
                if np.sum(d_turb) != 0.0 and np.sum(v_turb) == 0.0 and "pfa"+qtag[1:] in data and qtag in data:
                    gtemp = data["rl"+qtag] if "rl"+qtag in data else data["a"+qtag]
                    v_turb = data["pfa"+qtag[1:]] / data[qtag] - data["da"+qtag[1:]] * gtemp / lref
                data["rvd"+qtag[1:]] = -lref * v_turb / (d_turb + 1.0e-10)
                if "dnc"+qtag[1:] in data:
                    d_nc = data["dnc"+qtag[1:]]
                    v_nc = np.zeros(d_nc.shape)
                    if "vnc"+qtag[1:] in data:
                        v_nc = data["vnc"+qtag[1:]]
                    data["rvdt"+qtag[1:]] = -lref * (v_turb + v_nc) / (d_turb + d_nc + 1.0e-10)
            else:
                data["rvd"+qtag[1:]] = 0.0
                data["rvdt"+qtag[1:]] = 0.0
            if "pfa"+qtag[1:] in data:
                f_turb = data["pfa"+qtag[1:]]
                f_nc = np.zeros(f_turb.shape)
                if "pfnc"+qtag[1:] in data:
                    f_nc = data["pfnc"+qtag[1:]]
                data["pft"+qtag[1:]] = (f_turb + f_nc)
            else:
                data["pft"+qtag[1:]] = 0.0

            qtag = "timp%d" % (ii+1)
            if "efa"+qtag[1:] in data and "rl"+qtag in data and qtag in data:
                data["xa"+qtag[1:]] = data["efa"+qtag[1:]] * lref / (data["rl"+qtag] * data[qtag] + 1.0e-10)
            else:
                data["xa"+qtag[1:]] = 0.0

    return data

def compute_effective_quantities(data, rzero=None, numions=0, numimps=0):
    """
    Computes various derived quantities from the extracted transport coefficients,
    including:
    
    Metrics for density peaking, assuming dn/dt = 0.
    Metrics for total particle flux

    :returns: pd.DataFrame
    """
    if isinstance(data, (dict, pd.DataFrame)):

        lref = float(rzero) if isinstance(rzero, number_types) else 3.0
        if "rzero" in data:
            lref = data["rzero"]
            if isinstance(rzero, number_types):
                print("Reference length quantity found in run directory, overriding the user-defined value!")

        qtag = "ne"
        if "pfa"+qtag[1:] in data and "rl"+qtag in data and qtag in data:
            data["deffa"+qtag[1:]] = data["pfa"+qtag[1:]] * lref / (data["rl"+qtag] * data[qtag] + 1.0e-10)
        else:
            data["deffa"+qtag[1:]] = 0.0
        if "pfnc"+qtag[1:] in data and "rl"+qtag in data and qtag in data:
            data["deffnc"+qtag[1:]] = data["pfnc"+qtag[1:]] * lref / (data["rl"+qtag] * data[qtag] + 1.0e-10)
        else:
            data["deffnc"+qtag[1:]] = 0.0
        if "pft"+qtag[1:] in data and "rl"+qtag in data and qtag in data:
            data["defft"+qtag[1:]] = data["pft"+qtag[1:]] * lref / (data["rl"+qtag] * data[qtag] + 1.0e-10)
        else:
            data["defft"+qtag[1:]] = 0.0

        qtag = "te"
        if "efa"+qtag[1:] in data and "rl"+qtag in data and qtag in data:
            data["xeffa"+qtag[1:]] = data["efa"+qtag[1:]] * lref / (data["rl"+qtag] * data[qtag] + 1.0e-10)
        else:
            data["xeffa"+qtag[1:]] = 0.0
        if "efnc"+qtag[1:] in data and "rl"+qtag in data and qtag in data:
            data["xeffnc"+qtag[1:]] = data["efnc"+qtag[1:]] * lref / (data["rl"+qtag] * data[qtag] + 1.0e-10)
        else:
            data["xeffnc"+qtag[1:]] = 0.0
        if "eft"+qtag[1:] in data and "rl"+qtag in data and qtag in data:
            data["xefft"+qtag[1:]] = data["eft"+qtag[1:]] * lref / (data["rl"+qtag] * data[qtag] + 1.0e-10)
        else:
            data["xefft"+qtag[1:]] = 0.0

        for ii in range(numions):

            qtag = "ni%d" % (ii+1)
            if "pfa"+qtag[1:] in data and "rl"+qtag in data and qtag in data:
                data["deffa"+qtag[1:]] = data["pfa"+qtag[1:]] * lref / (data["rl"+qtag] * data[qtag] + 1.0e-10)
            else:
                data["deffa"+qtag[1:]] = 0.0
            if "pfnc"+qtag[1:] in data and "rl"+qtag in data and qtag in data:
                data["deffnc"+qtag[1:]] = data["pfnc"+qtag[1:]] * lref / (data["rl"+qtag] * data[qtag] + 1.0e-10)
            else:
                data["deffnc"+qtag[1:]] = 0.0
            if "pft"+qtag[1:] in data and "rl"+qtag in data and qtag in data:
                data["defft"+qtag[1:]] = data["pft"+qtag[1:]] * lref / (data["rl"+qtag] * data[qtag] + 1.0e-10)
            else:
                data["defft"+qtag[1:]] = 0.0

            qtag = "ti%d" % (ii+1)
            if "efa"+qtag[1:] in data and "rl"+qtag in data and qtag in data:
                data["xeffa"+qtag[1:]] = data["efa"+qtag[1:]] * lref / (data["rl"+qtag] * data[qtag] + 1.0e-10)
            else:
                data["xeffa"+qtag[1:]] = 0.0
            if "efnc"+qtag[1:] in data and "rl"+qtag in data and qtag in data:
                data["xeffnc"+qtag[1:]] = data["efnc"+qtag[1:]] * lref / (data["rl"+qtag] * data[qtag] + 1.0e-10)
            else:
                data["xeffnc"+qtag[1:]] = 0.0
            if "eft"+qtag[1:] in data and "rl"+qtag in data and qtag in data:
                data["xefft"+qtag[1:]] = data["eft"+qtag[1:]] * lref / (data["rl"+qtag] * data[qtag] + 1.0e-10)
            else:
                data["xefft"+qtag[1:]] = 0.0

        for ii in range(numimps):

            qtag = "nimp%d" % (ii+1)
            if "pfa"+qtag[1:] in data and "rl"+qtag in data and qtag in data:
                data["deffa"+qtag[1:]] = data["pfa"+qtag[1:]] * lref / (data["rl"+qtag] * data[qtag] + 1.0e-10)
            else:
                data["deffa"+qtag[1:]] = 0.0
            if "pfnc"+qtag[1:] in data and "rl"+qtag in data and qtag in data:
                data["deffnc"+qtag[1:]] = data["pfnc"+qtag[1:]] * lref / (data["rl"+qtag] * data[qtag] + 1.0e-10)
            else:
                data["deffnc"+qtag[1:]] = 0.0
            if "pft"+qtag[1:] in data and "rl"+qtag in data and qtag in data:
                data["defft"+qtag[1:]] = data["pft"+qtag[1:]] * lref / (data["rl"+qtag] * data[qtag] + 1.0e-10)
            else:
                data["defft"+qtag[1:]] = 0.0

            qtag = "timp%d" % (ii+1)
            if "efa"+qtag[1:] in data and "rl"+qtag in data and qtag in data:
                data["xeffa"+qtag[1:]] = data["efa"+qtag[1:]] * lref / (data["rl"+qtag] * data[qtag] + 1.0e-10)
            else:
                data["xeffa"+qtag[1:]] = 0.0
            if "efnc"+qtag[1:] in data and "rl"+qtag in data and qtag in data:
                data["xeffnc"+qtag[1:]] = data["efnc"+qtag[1:]] * lref / (data["rl"+qtag] * data[qtag] + 1.0e-10)
            else:
                data["xeffnc"+qtag[1:]] = 0.0
            if "eft"+qtag[1:] in data and "rl"+qtag in data and qtag in data:
                data["xefft"+qtag[1:]] = data["eft"+qtag[1:]] * lref / (data["rl"+qtag] * data[qtag] + 1.0e-10)
            else:
                data["xefft"+qtag[1:]] = 0.0

    return data

#####


def gamhistory_pipeline_extraction(rundirpath, nc_flag=False):
    """
    Simplifies the extraction pipeline for the JETTO-QuaLiKiz gamhistory output
    into a single function with user-friendly arguments.

    :returns: dict
    """
    tdata = None
    if isinstance(rundirpath, str):

        rpath = Path(rundirpath)
        if rpath.is_dir():

            qdata = read_qualikiz_gamhistory_data(str(rpath.resolve()))
            qdata = remove_duplicate_times(qdata)
            tdata = separate_gamhistory_species(qdata)
            if "ptopt" in tdata and tdata["ptopt"] != 0:
                tdata = transfer_transport_quantities(tdata)
            if nc_flag:
                tdata.update(read_jetto_neoclassical_data(str(rpath.resolve()), numions=tdata["numi"], numimps=tdata["numimp"]))

    return tdata


def gamhistory_pipeline_conversion(data, time_start=None, time_end=None, time_window=None, time_vector=None, radial_vector=None, include_eigenvalues=False):
    """
    Simplifies the conversion pipeline for the JETTO-QuaLiKiz gamhistory output
    into a single function with user-friendly arguments.

    :returns: pd.DataFrame, pd.DataFrame, dict
    """
    odata = None
    edata = None
    if isinstance(data, dict):

        ti = float(time_start) if isinstance(time_start, number_types) else None
        tf = float(time_end) if isinstance(time_end, number_types) else None
        twin = float(time_window) if isinstance(time_window, number_types) else None
        tvec = np.array(time_vector).flatten() if isinstance(time_vector, array_types) else None
        rvec = np.array(radial_vector).flatten() if isinstance(radial_vector, array_types) else None

        (vdata, cdata) = unify_base_vectors(data, time_start=ti, time_end=tf, time_window=twin, time=tvec, rho=rvec)
        odata = convert_fluxes_to_dataframe(vdata)
        if include_eigenvalues:
            edata = convert_eigenvalues_to_dataframe(vdata)

    return (odata, edata, cdata)


def perform_gamhistory_pipeline(rundirpath, time_start=None, time_end=None, time_window=None, time_vector=None, radial_vector=None, nc_flag=False, include_eigenvalues=False, analysis_type=0):
    """
    Simplifies the processing pipeline for the JETTO-QuaLiKiz gamhistory output
    into a single function with user-friendly arguments. Allows expansion of
    targeted output implementations under analysis_type argument.

    :returns: pd.DataFrame, pd.DataFrame
    """
    odata = None
    edata = None

    twin = float(time_window) if isinstance(time_window, number_types) else None
    if nc_flag and twin is None:
        twin = 0.001   # Recommended default window to ensure empty slices do not occur

    tdata = gamhistory_pipeline_extraction(rundirpath, nc_flag=nc_flag)
    if tdata is not None:
        rpath = Path(rundirpath)
        (odata, edata, cdata) = gamhistory_pipeline_conversion(tdata, time_start=time_start, time_end=time_end, time_window=twin, time_vector=time_vector, radial_vector=radial_vector, include_eigenvalues=include_eigenvalues)
        if include_eigenvalues and edata is None:
            print("Requested QuaLiKiz eigenvalue information not available in JETTO folder, %s. Skipping..." % (rpath.stem))

        atype = int(analysis_type) if isinstance(analysis_type, int_types) else 0
        if odata is not None and atype > 0:
            if cdata["histopt"] > 2:
                print("Computing additional derived quantities on %s..." % (rpath.stem))
                odata = compute_derived_quantities(odata, numions=cdata["numi"], numimps=cdata["numimp"])
                odata = compute_effective_quantities(odata, numions=cdata["numi"], numimps=cdata["numimp"])
            else:
                print("JETTO-QuaLiKiz run does not have the sufficient printout level (gamhistory > 2) for built-in extended computations. Skipping...")
    else:
        print("Specified run folder, %s, not found. Skipping..." % (rundirpath))

    return (odata, edata)
