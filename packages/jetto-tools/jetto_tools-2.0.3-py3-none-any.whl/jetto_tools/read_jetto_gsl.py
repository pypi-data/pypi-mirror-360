import numpy as np
import matplotlib.pyplot as plt
import os, sys
from IPython import embed
#jetto-python tools import
#Some of them available in JINTRAC repo but only used for CI
#The most up to date version is in the jetto-pythontools repo
#/home/ITER/suarezg1/jetto-pythontools_230523/jetto_tools
import binary as jbt

#pypath_ep1 = "'/home/ITER/suarezg1/jintrac/imas_latest/"+\
#    "libs/eproc/python/eproc'"
#pypath_ep2 = "'/home/ITER/suarezg1/jintrac/imas_latest/"+\
#    "libs/eproc/python'"
#os.system("export PYTHONPATH=${PYTHONPATH}:" + pypath_ep1)
#os.system("export PYTHONPATH=${PYTHONPATH}:" + pypath_ep2)

#Edge2D Tran files - path in bashrc file
#from pytran import Tran
#Need EPROC to be added to the PYTHONPATH
# - path in bashrc file
import eproc as ep

#Import routines to parse EQDSK files
from results import EqdskFile

#IMAS - To handle IDS output
import imas

__all__ = ["jintrac"]

class jintrac():

    def __init__(self, jetto_path=None, jetto_jsp=None,
                 user=None, database="iter", nshot=None, run=None,
                 backend="auto", data_version=None, out_memory=True):

        """
        backend: str - "hdf5" or "mdsplus"
        """   

        #Autodetect the JINTRAC backend
        #Standard output doesn't have /imasdb folder
        #HDF5 has a structure /imasdb/database/nshot/
        #MDSPLUS has a structure /imasdb/database/0/
        if backend=="auto":
            dir_list = os.listdir(jetto_path)
            if 'imasdb' in dir_list:
                imas_list = os.listdir(jetto_path+
                            '/imasdb/'+database+'/3')
                if nshot == int(imas_list[0]):
                    backend="hdf5"
                else:
                    backend="mdsplus"
            else:
                backend="std"

        self.jetto_path = jetto_path
        self.jetto_jsp = jetto_jsp
        self.sanco_files = []
        self.nshot = nshot
        self.tranfile = True
        self.out_memory = out_memory
        self.backend = backend
        if data_version is None:
            data_version = os.environ['IMAS_VERSION']
        self.data_version = data_version

        #Set default values for some flags
        self.jspfile = False
        self.ssp1file = False
        self.ssp2file = False
        self.ssp3file = False
        self.jse = False

        #If user is None, points to the imasdb folder
        #in jetto_path. Othwerwise, you can provide the
        #full path to the user.
        if user is None:
            user = jetto_path+"/imasdb"

        if self.out_memory:
            self.out = {}

        #Read a Standard Output case
        if backend == "std":
            self._readjetto_standard()
            try:
                self._read_edge2d()
                self._read_eirene()
            except:
                print('No TRAN file')
                self.tranfile = False
            #Read output quantities to memory
            if out_memory:
                self._out_memory_standard()
        #Read an IMAS IDS case
        else:
            self._readjetto_imas(database, nshot, run, user, backend,
                                 data_version)
            #For the time being, parse edge quantities from
            #tran file and EPROC. Most edge IDS are not currently
            #written
            try:
                self._read_edge2d()
            except:
                print('No TRAN file')
                self.tranfile = False
            #Read output quantities to memory
            if out_memory:
                self._out_memory_imas()

        #Compute derived quantities
        try:
            self._calculate_derived_quantities()
        except:
            print("Derived quantities could not be calculated.")

        return


    def _readjetto_standard(self):

        """
         Simulations which have not yet finished
         need to be read from the last written
         jetto.jspXX file, however, jetto.jst file
         is always readily available

         Full JETTO output namelists can be found in:
         https://git.iter.org/projects/SCEN/repos/jintrac-docs/
         browse/webpages/wiki/JETTO_ppfoutputs.md
        """

        #Reading JETTO .jsp file - Profiles
        if self.jetto_jsp:
            jsp_file = self.jetto_path + self.jetto_jsp
        else:
            jsp_file = self.jetto_path + "/jetto.jsp"
        print("JETTO .jsp file:" + str(jsp_file))

        self.jet = {}

        try:
            dataset_jsp = jbt.read_binary_file(jsp_file)
            self.dataset_jsp = dataset_jsp
            self.jet = dataset_jsp
            self.names_jsp = dataset_jsp.keys()
            self.jspfile = True
        except:
            print('No JETTO JSP file')

        #Reading JETTO .jse file - JETTO equilibrium data
        try:
            jse_file = self.jetto_path + "/jetto.jse"
            print("JETTO .jse file:" + str(jse_file))
            dataset_jse = jbt.read_binary_file(jse_file)
            self.dataset_jse = dataset_jse
            self.names_jse = dataset_jse.keys()
            self.dataset_jse["TIME_EQ"] = self.dataset_jse["TIME"]
            #TIME key is different from TIME in jetto.jsp,
            #but both have the same name.
            del self.dataset_jse["TIME"]
            self.jet.update(self.dataset_jse)
            self.jse = True
        except:
            print('No JETTO JSE file')      

        #Reading JETTO .jst file - Time traces
        #tvec1 - Time vector
        #pece  - ECRH Power
        #pnet  - Total aux. + alpha power
        jst_file = self.jetto_path + "/jetto.jst"
        print("JETTO .jst file:" + str(jst_file))
        dataset_jst = jbt.read_binary_file(jst_file)
        self.dataset_jst = dataset_jst
        self.names_jst = dataset_jst.keys()
        self.jet.update(self.dataset_jst)

        #Reading SANCO .sspX file - Profiles
        #Reading SANCO .sstX file - Time traces
        #The X corresponds to each impurity
        #added to the simulation.
        #These files contain several pinch
        #velocities/diffusivities each, where
        #each one is a different ionization state.
        try:
            ssp_file1 = self.jetto_path + "/jetto.ssp1"
            print("JETTO .ssp file:" + str(ssp_file1))
            sst_file1 = self.jetto_path + "/jetto.sst1"
            print("JETTO .sst file:" + str(sst_file1))
            dataset_ssp1 = jbt.read_binary_file(ssp_file1)
            self.dataset_ssp1 = dataset_ssp1
            self.names_ssp1 = list(dataset_ssp1.keys())
            dataset_sst1 = jbt.read_binary_file(sst_file1)
            self.dataset_sst1 = dataset_sst1
            self.names_sst1 = list(dataset_sst1.keys())
            self.ssp1file = True
        except:
            print("Could not read " + str(ssp_file1))
            print("Could not read " + str(sst_file1))
            self.ssp1file = False

        #ssp2
        try:
            ssp_file2 = self.jetto_path + "/jetto.ssp2"
            print("JETTO .ssp file:" + str(ssp_file2))
            sst_file2 = self.jetto_path + "/jetto.sst2"
            print("JETTO .sst file:" + str(sst_file2))
            dataset_ssp2 = jbt.read_binary_file(ssp_file2)
            self.dataset_ssp2 = dataset_ssp2
            self.names_ssp2 = dataset_ssp2.keys()
            dataset_sst2 = jbt.read_binary_file(sst_file2)
            self.dataset_sst2 = dataset_sst2
            self.names_sst2 = dataset_sst2.keys()
            self.ssp2file = True
        except:
            print("Could not read " + str(ssp_file2))
            print("Could not read " + str(sst_file2))
            self.ssp2file = False     

        #ssp3
        try:
            ssp_file3 = self.jetto_path + "/jetto.ssp3"
            print("JETTO .ssp file:" + str(ssp_file3))
            sst_file3 = self.jetto_path + "/jetto.sst3"
            print("JETTO .sst file:" + str(sst_file3))
            dataset_ssp3 = jbt.read_binary_file(ssp_file3)
            self.dataset_ssp3 = dataset_ssp3
            self.names_ssp3 = dataset_ssp3.keys()
            dataset_sst3 = jbt.read_binary_file(sst_file3)
            self.dataset_sst3 = dataset_sst3
            self.names_sst3 = dataset_sst3.keys()
            self.ssp3file = True
        except:
            print("Could not read " + str(ssp_file3))
            print("Could not read " + str(sst_file3))
            self.ssp3file = False

        return


    def _out_memory_standard(self):

        """ 
        Reads into a new data dictionary the standard
        output Database from JINTRAC

        Parameters
        ----------

        Output
        ----------

        Notes
        ----------
        """

        if self.jspfile:
            ##########
            #JETTO JSP
            ##########
            self.out["time"] = np.squeeze(self.jet["TIME"])
            self.out["time_derived"] = np.squeeze(self.jet["TVEC1"])
            self.out["R_omp"] = self.jet["R"]  #Outer Midplane Major radius
            self.out["rho"] = self.jet["RHO"]  #JETTO label [m]
            self.out["rhot_norm"] = self.jet["XRHO"]
            self.out["Te"] = self.jet["TE"]
            self.out["Ti"] = self.jet["TI"]  #Ion temp [eV]
            self.out["Qe"] = self.jet["PEFL"]  #Electron heat flux as afo rho [W]
            self.out["Qi"] = self.jet["PIFL"]  #Ion heat flux as afo rho [W]
            self.out["ne"] = self.jet["NE"]
            self.out["pres"] = self.jet["PR"]    #Total pressure [Pa]
            self.out["De_eff"] = self.jet["DFI"] #D effective (I assume evolving ne) [m2/s]
            self.out["D1_eff"] = self.jet["D1"]  #Particle Diffusion (I assume species 1) [m2/s]
            self.out["D2_eff"] = self.jet["D2"]  #Particle Diffusion species 2 [m2/s]
            self.out["v1_t"] = self.jet["VTCI"]  #Pinch velocity TCI main ion 1st species [m/s]
            self.out["v2_t"] = self.jet["VTC2"]  #Pinch velocity TCI 2nd species [m/s]
            self.out["vnce"] = self.jet["VNCE"]  #NCLASS el. pinch velocity [m/s]
            self.out["v1_n"] = self.jet["VNCI"]  #NCLASS (main?) ion pinch velocity [m/s]
            self.out["v2_n"] = self.jet["VNC1"]  #NCLASS 2nd spec.+1 vel. (Idk what +1 means..)
            self.out["niH"] = self.jet["NIH"]    #Hydrogen density [m-3]
            self.out["niD"] = self.jet["NID"]    #Deuterium density [m-3]
            self.out["niT"] = self.jet["NIT"]    #Tritium density [m-3]
            self.out["nN1"] = self.jet["N01"]    #Neutral density [m-3]
            self.out["nN2"] = self.jet["N02"]    #Neutral density [m-3]
            #Probably assumed the same for all ions:
            self.out["vtor"] = self.jet["VTOR"] #Toroidal velocity [m/s]
            self.out["vpol"] = self.jet["VPOL"] #Poloidal velocity [m/s]
            self.out["D_tormom"] = self.jet["CHIM"] #Toroidal momentum diffusivity [m2/s]
            self.out["v_tormom"] = self.jet["VINM"] #Toroidal momentum pinch [m/s]
            self.out["D_tormom_eff"] = self.jet["XMF"] #Effective Toroidal momentum diff [m2/s]
            self.out["Wth"] = np.squeeze(self.jet["WTH"])
            self.out["jtor"] = self.jet["JZ"] #Total tor. current density [A/m2]
            self.out["jpar"] = self.jet["JP"] #Total par. current density [A/m2]
            self.out["jpar_Bs"] = self.jet["JZBS"] #Total (parallel = Bootstrap) current density [A/m2]
            self.out["jtor_ec"] = self.jet["JZEC"] #EC driven tor. current density [A/m2]
            self.out["qprof"] = self.jet["Q"]
            self.out["qshear"] = self.jet["SH"]    
            self.out["S0"] = self.jet["S0D"]  #Neutral Particle source from FRANTIC
            self.out["S1_pel"] = self.jet["SPE1"] #Pellet source species 1 [s-1]
            self.out["S2_pel"] = self.jet["SPE2"] #Pellet source species 2 [s-1]
            self.out["rhotnbi"] = self.jet["XRHO"]
            self.out["SBD1"] = self.jet["SBD1"] #NBI part. source (spec 1)
            self.out["SBD2"] = self.jet["SBD2"] #NBI part. source (spec 2)
            self.out["Pnbi_i"] = self.jet["QNBI"] #[MW/m^3] Ion NBI heating         
            self.out["Pnbi_e"] = self.jet["QNBE"] #[MW/m^3] Electron NBI heating    
            self.out["Pnbi_itot"] = np.squeeze(self.jet["PNBI"]) #Total NBI power to ions [MW] f(t)
            self.out["Pnbi_etot"] = np.squeeze(self.jet["PNBE"]) #Total NBI power to elec [MW] f(t)
            self.out["Pnbi_tot"] = self.out["Pnbi_itot"]+self.out["Pnbi_etot"]
            self.out["Palf"] = np.squeeze(self.jet["PALF"]) #Total alpha power [MW] f(t)
            self.out["rhotec"] = self.jet["XRHO"]
            self.out["Pecrh"] = self.jet["QECE"]   #ECRH power density [W/m3]
            self.out["Pec_tot"] = np.squeeze(self.jet["PECE"]) #Total power [W] f(t)
            self.out["Poh_tot"] = np.squeeze(self.jet["POH"]) #Ohmic heating [W] f(t)

            #Interleaved grid for diffusivities
            self.out["rhot_Xs"] = 0.5*(self.out["rhot_norm"][:,1:]+\
                                        self.out["rhot_norm"][:,:-1])
            #From the JINTRAC Wiki, part written by Florian
            #JSP/XI is the sum of all XIj.
            #JSP/XI1: neoclassical Xi
            #JSP/XI2: Bohm part of Xi from Bohm/gyroBohm model
            #JSP/XI3: gyroBohm part of Xi from Bohm/gyroBohm model
            #JSP/XI4: Xi from NeoAlcator model
            #JSP/XI5: Xi from CDBM model
            #JSP/XI6: Xi from TCI
            self.out["Xe"] = self.jet["XE"] #Electron heat diffusivity
            self.out["Xi"] = self.jet["XI"] #Total Ion heat diffusivity
            self.out["Xe_neo"] = self.jet["XE1"]
            self.out["Xi_neo"] = self.jet["XI1"] 
            self.out["Xe_Bohm"] = self.jet["XE2"]
            self.out["Xi_Bohm"] = self.jet["XI2"] 
            self.out["Xe_GBohm"] = self.jet["XE3"]
            self.out["Xi_GBohm"] = self.jet["XI3"]
            self.out["Xe_turb"] = self.jet["XE6"]
            self.out["Xi_turb"] = self.jet["XI6"]

            self.out["Vol_rho"] = self.jet["VOL"] #Plasma volume [m^3]
            self.out["dVdrho"] = self.jet["DVEQ"] #dVol/drho [m2]

        ################
        #JETTO JST, f(t)
        ################
        self.out["alpha_max_jetto_edge"] = np.squeeze(self.jet["ALFM"])
        self.out["Zeff"] = self.jet["ZEFF"]
        #I assume this is the volumetric average
        self.out["ne_avg"] = self.jet["NEAV"][0] #e- volume-averaged density [m-3]
        self.out["ne_lavg"] = self.jet["NEL"][0] #e- line-averaged density [m-3]
        self.out["n1_avg"] = self.jet["NI1"][0] #ion 1 volume-averaged density [m-3]
        self.out["n2_avg"] = self.jet["NI2"][0] #ion 2 volume-averaged density [m-3]
        #Greenwal density fraction [%]
        self.out["fGw"] = np.squeeze(self.jet["NGFR"])
        #Some concentrations may not be available,
        #this depends on the impurities used in the run.
        try:
            self.out["IMC1"] = self.jet["IMC1"][0]
        except:
            self.out["IMC1"] = np.zeros_like(self.out["Zeff"])
        try:
            self.out["IMC2"] = self.jet["IMC2"][0]
        except:
            self.out["IMC2"] = np.zeros_like(self.out["Zeff"])
        try:
            self.out["IMC3"] = self.jet["IMC3"][0]
        except:
            self.out["IMC3"] = np.zeros_like(self.out["Zeff"])

        self.out["Prad_tot"] = np.squeeze(self.jet["PRAD"])

        #Energy confinement time - ITER Definition [s]
        self.out["tau_e"] = np.squeeze(self.jet["TAUE"])

        #Fusion Q
        #self.out["Qfus"] = self.jet["QDT"][0]
        self.out["Qfus"] = self.jet["QFUS"][0]
 
        #Particle input (puff 1 and puff 2. Hopefully, total source)
        #Note: These are for main ion species.
        self.out["Spuff_i1_tot"] = np.squeeze(self.jet["PIN1"])
        self.out["Spuff_i2_tot"] = np.squeeze(self.jet["PIN2"])

        #Total plasma current [A]
        self.out["Ip"] = np.squeeze(self.jet["CUR"])
        self.out["jpar_Bstot"] = np.squeeze(self.jet["CUBS"])
        self.out["jtor_ectot"] = np.squeeze(self.jet["CUEC"])
        self.out["jtor_nbitot"] = np.squeeze(self.jet["CUNB"])
        self.out["jtor_ictot"] = np.squeeze(self.jet["CURF"])       
        self.out["Btor"] = np.squeeze(self.jet["BTOR"]) #Btor(R=Raxis)
        #Non-inductive current fraction [%]
        self.out["Jni"] = np.squeeze(self.jet["NIFR"])

        #Bnd. energy flux (el+io)
        self.out["Psep"] = self.jet["PSEP"]
        #L-H transition power [W]
        #I believe this quantity is only written if the
        #IPWDEP L-H transition switch is active
        #I checked against Martin scaling law (30.01.2025)
        #and this quantity doesnt include - Prad_tot.
        try:
            self.out["Plht"] = self.jet["PLHT"]
        except:
            pass

        #{R,Z} positions of magnetic axis.
        self.out["Raxis"] = self.jet["RAXS"]
        self.out["Zaxis"] = self.jet["ZAXS"]

        self.out["Sur_t"] = self.jet["SURF"]

        #Control parameters
        self.out["dtmax"] = self.jet["DTMX"]

        ################
        #JETTO JSE, f(t)
        ################
        if self.jse:
            self.out["time_eq"] = self.jet["TIME_EQ"]
            self.out["Rbnd"] = self.jet["RBND"]
            self.out["Zbnd"] = self.jet["ZBND"]

        ###################
        #EQDSK file
        #Read it to get PFM
        ###################
        try:
            eqdsk = EqdskFile
            eqdsk = eqdsk.load(self.jetto_path+"/jetto.eqdsk_out")
            self.out["Rgrid"] = eqdsk.Rgrid
            self.out["Zgrid"] = eqdsk.Zgrid
            self.out["Psi"] = eqdsk.psirz
            self.out["Psi_n"] = eqdsk.psirz_n
        except:
            print("- No EQDSK file found")

        ####################################################
        #Vessel and buffle coordinates parsed from grid file
        ####################################################
        file = open(self.jetto_path + "/grid", mode="r")
        lines = file.readlines()
        file.close()
        for line in lines:
            line = line.split(',')
            line = [i.strip() for i in line]
        for ii in range (0, len(lines)):
            if 'NVES' in lines[ii]:
                idx_ves = ii
            if 'NBUFLE' in lines[ii]:
                idx_buf = ii
        nvessel = int(lines[idx_ves+1])
        nbuffle = int(lines[idx_buf+1])
        Rves = np.array([], dtype="f8")
        Zves = np.array([], dtype="f8")
        Rbuf = np.array([], dtype="f8")
        Zbuf = np.array([], dtype="f8")
        for jj in range(0,50):
            Rves_tmp = lines[idx_ves+3+jj].replace('\n','').split(' ')
            while '' in Rves_tmp:
                Rves_tmp.remove('')
            Rves = np.append(Rves, Rves_tmp).astype("f8")
            if len(Rves) == nvessel:
                break
        for zz in range(0,50):
            Zves_tmp = lines[idx_ves+jj+zz+5].replace('\n','').split(' ')
            while '' in Zves_tmp:
                Zves_tmp.remove('')
            Zves = np.append(Zves, Zves_tmp).astype("f8")
            if len(Zves) == nvessel:
                break

        for jj in range(0,50):
            Rbuf_tmp = lines[idx_buf+3+jj].replace('\n','').split(' ')
            while '' in Rbuf_tmp:
                Rbuf_tmp.remove('')
            Rbuf = np.append(Rbuf, Rbuf_tmp).astype("f8")
            if len(Rbuf) == nbuffle:
                break
        for zz in range(0,50):
            Zbuf_tmp = lines[idx_buf+jj+zz+5].replace('\n','').split(' ')
            while '' in Zbuf_tmp:
                Zbuf_tmp.remove('')
            Zbuf = np.append(Zbuf, Zbuf_tmp).astype("f8")
            if len(Zbuf) == nbuffle:
                break
    
        self.out["nvessel"] = nvessel
        self.out["Rvessel"] = np.hstack((Rves, Rves[0]))
        self.out["Zvessel"] = np.hstack((Zves, Zves[0]))
        self.out["Rbuffle"] = np.hstack((Rbuf, Rbuf[0]))
        self.out["Zbuffle"] = np.hstack((Zbuf, Zbuf[0]))

        #####################################
        #SANCO Impurity specific Profile data
        #####################################
        if self.ssp1file:
            #Find the number of charged states
            Ds = [x for x in self.names_ssp1 if "ZQ" in x]
            Ds = [int(x[-1]) for x in Ds]
            ns_ssp1 = np.max(Ds)

            self.out["srhot"] = self.dataset_ssp1["XRHO"]
            self.out["t_sanco"] = np.squeeze(self.dataset_ssp1["TIME"])
            ni_ssp1 = np.zeros_like(self.dataset_ssp1["N1"])
            Dn_ssp1 = np.zeros_like(self.dataset_ssp1["D1"])
            vn_ssp1 = np.zeros_like(self.dataset_ssp1["V1"])
            nspecies = 0
            #Sum over all the bundles
            for bb in range(0,20):
                try:
                    ni_ssp1 = ni_ssp1 + self.dataset_ssp1["N"+str(bb)]
                    Dn_ssp1 = Dn_ssp1 + self.dataset_ssp1["D"+str(bb)]*\
                              self.dataset_ssp1["N"+str(bb)]
                    vn_ssp1 = vn_ssp1 + self.dataset_ssp1["V"+str(bb)]*\
                              self.dataset_ssp1["N"+str(bb)]
                    nspecies += 1
                except:
                    pass

            #Weighted average over the bundles
            self.out["ni_ssp1"] = ni_ssp1
            self.out["Dn_ssp1"] = Dn_ssp1/ni_ssp1
            self.out["vn_ssp1"] = vn_ssp1/ni_ssp1

            #External neutral influx [m-2 s-1]
            self.out["Sn_spp1"] = self.dataset_sst1["INFL"]

        if self.ssp2file:
            #Find the number of charged states
            Ds = [x for x in self.names_ssp2 if "ZQ" in x]
            Ds = [int(x[-1]) for x in Ds]
            ns_ssp2 = np.max(Ds)

            self.out["srhot"] = self.dataset_ssp2["XRHO"]
            self.out["t_sanco"] = np.squeeze(self.dataset_ssp2["TIME"])
            ni_ssp2 = np.zeros_like(self.dataset_ssp2["N1"])
            Dn_ssp2 = np.zeros_like(self.dataset_ssp2["D1"])
            vn_ssp2 = np.zeros_like(self.dataset_ssp2["V1"])
            nspecies = 0
            #Sum over all the bundles
            for bb in range(0,20):
                try:
                    ni_ssp2 = ni_ssp2 + self.dataset_ssp2["N"+str(bb)]
                    Dn_ssp2 = Dn_ssp2 + self.dataset_ssp2["D"+str(bb)]*\
                              self.dataset_ssp2["N"+str(bb)]
                    vn_ssp2 = vn_ssp2 + self.dataset_ssp2["V"+str(bb)]*\
                              self.dataset_ssp2["N"+str(bb)]
                    nspecies += 1
                except:
                    pass

            #Weighted average over the bundles
            self.out["ni_ssp2"] = ni_ssp2
            self.out["Dn_ssp2"] = Dn_ssp2/ni_ssp2
            self.out["vn_ssp2"] = vn_ssp2/ni_ssp2

            #External neutral influx [m-2 s-1]
            self.out["Sn_spp2"] = self.dataset_sst2["INFL"]

        if self.ssp3file:
            #Find the number of charged states
            Ds = [x for x in self.names_ssp3 if "ZQ" in x]
            Ds = [int(x[-1]) for x in Ds]
            ns_ssp3 = np.max(Ds)

            self.out["srhot"] = self.dataset_ssp3["XRHO"]
            self.out["t_sanco"] = np.squeeze(self.dataset_ssp3["TIME"])
            ni_ssp3 = np.zeros_like(self.dataset_ssp3["N1"])
            Dn_ssp3 = np.zeros_like(self.dataset_ssp3["D1"])
            vn_ssp3 = np.zeros_like(self.dataset_ssp3["V1"])
            nspecies = 0
            #Sum over all the bundles
            for bb in range(0,20):
                try:
                    ni_ssp3 = ni_ssp3 + self.dataset_ssp3["N"+str(bb)]
                    Dn_ssp3 = Dn_ssp3 + self.dataset_ssp3["D"+str(bb)]*\
                              self.dataset_ssp3["N"+str(bb)]
                    vn_ssp3 = vn_ssp3 + self.dataset_ssp3["V"+str(bb)]*\
                              self.dataset_ssp3["N"+str(bb)]
                    nspecies += 1
                except:
                    pass

            #Weighted average over the bundles
            self.out["ni_ssp3"] = ni_ssp3
            self.out["Dn_ssp3"] = Dn_ssp3/ni_ssp3
            self.out["vn_ssp3"] = vn_ssp3/ni_ssp3

            #External neutral influx [m-2 s-1]
            self.out["Sn_spp3"] = self.dataset_sst3["INFL"]

        return


    def _readjetto_imas(self, database, nshot, run, user, backend, 
                        data_version):

        """
         Reads IMAS Output from JETTO using the IMAS
         module

         Stored in /imasdb/3/0/0/
         shot number = first 5 numbers without following 0s
         run number for output - 2
         Database - 'iter'
         USER - Directory of the Database or 'public'
         for the general one
        """

        if backend == "mdsplus":
            imas_backend = imas.imasdef.MDSPLUS_BACKEND
        elif backend == "hdf5":
            imas_backend = imas.imasdef.HDF5_BACKEND

        input = imas.DBEntry(imas_backend, database, nshot,
                             run, user_name=user,
                             data_version=data_version)
        input.open()
        self.jet = input

        return


    def _out_memory_imas(self):

        """ 
        Reads into a new data dictionary the IMAS
        output Database from JINTRAC

        Parameters
        ----------

        Output
        ----------

        Notes
        ----------
        """

        ############
        #SUMMARY IDS
        ############
        #Load summary IDSs into memory with "get"
        summary = self.jet.get('summary')
        #Get IDS data
        self.out["data_dictionary"] = summary.ids_properties.version_put.data_dictionary
        self.out["access_layer"] = summary.ids_properties.version_put.access_layer
        self.out["time"] = summary.time
        self.out["nt"] = len(summary.time)
        #Set a dummy variable corresponding to the jetto.jst
        #timebase from the standard output.
        self.out["time_derived"] = self.out["time"]
        self.out["Wtot"] = summary.global_quantities.energy_total.value
        self.out["Wth"] = summary.global_quantities.energy_thermal.value
        self.out["Wdia"] = summary.global_quantities.energy_diamagnetic.value

        #Energy confinement time
        self.out["tau_e"] = summary.global_quantities.tau_energy.value
        #Total plasma current
        self.out["Ip"] = summary.global_quantities.ip.value
        self.out["jpar_Bstot"] = summary.global_quantities.current_bootstrap.value
        self.out["R0"] = summary.global_quantities.r0.value

        #Total EC power from all launchers [MW]
        n_ec_launchers = len(summary.heating_current_drive.ec)
        Pec_tot = 0
        jec_tot = 0
        for ll in range(0, n_ec_launchers):
            Pec_tot += summary.heating_current_drive.ec[ll].power.value
            jec_tot += summary.heating_current_drive.ec[ll].current.value
        self.out["Pec_tot"] = Pec_tot
        self.out["jtor_ectot"] = jec_tot

        #Total NBI (e+i) power from all beams [MW]
        n_nbi_beams = len(summary.heating_current_drive.nbi)
        Pnbi_tot = 0
        jnbi_tot = 0
        for ll in range(0, n_nbi_beams):
            Pnbi_tot += summary.heating_current_drive.nbi[ll].power.value
            jnbi_tot += summary.heating_current_drive.nbi[ll].current.value
        self.out["Pnbi_tot"] = Pnbi_tot
        self.out["jtor_nbitot"] = jnbi_tot

        self.out["Palf"] = summary.fusion.power.value
        self.out["Zeff"] = summary.volume_average.zeff.value #f(t)

        #Total IC (e+i) power from all antennas [MW]
        n_ic_ant = len(summary.heating_current_drive.ic)
        Pic_tot = 0
        jic_tot = 0
        for ll in range(0, n_ic_ant):
            Pic_tot += summary.heating_current_drive.ic[ll].power.value
            jic_tot += summary.heating_current_drive.ic[ll].current.value
        self.out["Pic_tot"] = Pnbi_tot
        self.out["jtor_ictot"] = jnbi_tot

        self.out["Palf"] = summary.fusion.power.value
        self.out["Zeff"] = summary.volume_average.zeff.value #f(t)

        #Line-averaged electron density [1e19 m-3]
        self.out["ne_lavg"] = summary.line_average.n_e.value

        #Gas injection rates [el/s]
        self.out["Spuff_H_tot"] = summary.gas_injection_rates.hydrogen.value
        if len(self.out["Spuff_H_tot"]) == 0:
            self.out["Spuff_H_tot"] = np.zeros(self.out["nt"])
        self.out["Spuff_D_tot"] = summary.gas_injection_rates.deuterium.value
        if len(self.out["Spuff_D_tot"]) == 0:
            self.out["Spuff_D_tot"] = np.zeros(self.out["nt"]) 
        self.out["Spuff_T_tot"] = summary.gas_injection_rates.tritium.value
        if len(self.out["Spuff_T_tot"]) == 0:
            self.out["Spuff_T_tot"] = np.zeros(self.out["nt"])
        self.out["Spuff_Ne_tot"] = summary.gas_injection_rates.neon.value
        if len(self.out["Spuff_Ne_tot"]) == 0:
            self.out["Spuff_Ne_tot"] = np.zeros(self.out["nt"])

        #########
        #WALL IDS
        #########
        #Wall contour
        try:
            self.out["Rvessel"] = self.jet.partial_get('wall',
                        'description_2d(0)/limiter/unit(0)/outline/r').T
            self.out["Zvessel"] = self.jet.partial_get('wall',
                        'description_2d(0)/limiter/unit(0)/outline/z').T
        except:
            print("- No wall IDS")

        ################
        #EQUILIBRIUM IDS
        ################
        #f(t)
        self.out["Vol_t"] = Vol_t = self.jet.partial_get('equilibrium',
                   'time_slice(:)/global_quantities(:)/volume').T
        #Outer midplane major radius [m]
        self.out["R_omp"] = self.jet.partial_get('equilibrium',
                    'time_slice(:)/profiles_1d/r_outboard').T
        rho_tor_norm_eq = self.jet.partial_get('equilibrium',
                             'time_slice(:)/profiles_1d/rho_tor_norm').T
        self.out["rho_tor_norm_eq"] = rho_tor_norm_eq
        Vol_rho = self.jet.partial_get('equilibrium',
                          'time_slice(:)/profiles_1d/volume').T
        self.out["Vol_rho"] = Vol_rho

        ds = rho_tor_norm_eq[:,1:]-rho_tor_norm_eq[:,:1]
        dV = (Vol_rho[:,1:]-Vol_rho[:,:-1])
        dVds = dV/ds
        #dVol/drho [m2]
        self.out["dVdrho"] = self.jet.partial_get('equilibrium',
                   'time_slice(:)/profiles_1d(:)/dvolume_drho_tor').T
        self.out["Sur_t"] = Vol_t = self.jet.partial_get('equilibrium',
                   'time_slice(:)/global_quantities(:)/surface').T

        #Btor(R=Raxis)
        self.out["Btor"] = self.jet.partial_get('equilibrium',
                           'time_slice(:)/global_quantities(:)/magnetic_axis/b_field_tor').T

        #2D profiles
        #{R,Z} coordinates of flux grid
        self.out["Rgrid"] = self.jet.partial_get('equilibrium',
                    'time_slice(:)/profiles_2d(0)/r').T
        self.out["Zgrid"] = self.jet.partial_get('equilibrium',
                    'time_slice(:)/profiles_2d(0)/z').T
        self.out["Psi"] = self.jet.partial_get('equilibrium',
                    'time_slice(:)/profiles_2d(0)/psi').T

        #Poloidal flux at the separatrix
        self.out["Psi_sep"] = self.jet.partial_get('equilibrium',
                    'time_slice(:)/boundary_separatrix/psi').T

        ##Interpolate {rsep, zsep} from 2D grid for last time point
        #cs = plt.contour(self.out["Rgrid"][-1,:,:], self.out["Zgrid"][-1,:,:],
        #                 self.out["Psi"][-1,:,:], [self.out["Psi_sep"][-1]])
        #p = cs.collections[0].get_paths()[0]
        #v = p.vertices
        #self.out["Rbnd"] = v[:,0]
        #self.out["Zbnd"] = v[:,1]

        ##################
        #CORE PROFILES IDS
        ##################
        cp = self.jet.get('core_profiles')
        self.out["rhot_norm"] = self.jet.partial_get('core_profiles',
                                'profiles_1d(:)/grid/rho_tor_norm').T
        #JETTO label [m]
        self.out["rho"] = self.jet.partial_get('core_profiles',
                          'profiles_1d(:)/grid/rho_tor').T
        #Use the rhot_norm coordinate
        self.out["srhot"] = self.out["rhot_norm"]
        self.out["Te"] = self.jet.partial_get('core_profiles',
                          'profiles_1d(:)/electrons/temperature').T
        self.out["ne"] = self.jet.partial_get('core_profiles',
                           'profiles_1d(:)/electrons/density').T

        ions = self.jet.partial_get('core_profiles',
                    'profiles_1d(:)/ion')
        nions = len(ions)
        self.out["niH"] = np.zeros_like(self.out["ne"])
        self.out["TiH"] = np.zeros_like(self.out["ne"])
        self.out["niD"] = np.zeros_like(self.out["ne"])
        self.out["TiD"] = np.zeros_like(self.out["ne"])
        self.out["niT"] = np.zeros_like(self.out["ne"])
        self.out["TiT"] = np.zeros_like(self.out["ne"])
        self.out["niHe"] = np.zeros_like(self.out["ne"])
        self.out["TiHe"] = np.zeros_like(self.out["ne"])
        self.out["niNe"] = np.zeros_like(self.out["ne"])
        self.out["TiNe"] = np.zeros_like(self.out["ne"])
        self.out["niW"] = np.zeros_like(self.out["ne"])
        self.out["TiW"] = np.zeros_like(self.out["ne"])
        self.out["vtor"] = np.zeros_like(self.out["ne"])
        for nn in range(0, nions):
            label = np.unique(self.jet.partial_get('core_profiles',
                              'profiles_1d(:)/ion('+str(nn)+')/label'))
            if label == 'H':
                self.out["niH"] = self.jet.partial_get('core_profiles',
                          'profiles_1d(:)/ion('+str(nn)+')/density').T
                self.out["TiH"] = self.jet.partial_get('core_profiles',
                          'profiles_1d(:)/ion('+str(nn)+')/temperature').T
                self.out["vtH"] = self.jet.partial_get('core_profiles',
                          'profiles_1d(:)/ion('+str(nn)+')/velocity_tor').T
                self.out["wtH"] = self.jet.partial_get('core_profiles',
                          'profiles_1d(:)/ion('+str(nn)+')/rotation_frequency_tor').T                         
                if np.any(self.out["vtH"]) is not None:       
                    self.out["vtor"] += self.out["vtH"]
            elif label == 'D':
                self.out["niD"] = self.jet.partial_get('core_profiles',
                          'profiles_1d(:)/ion('+str(nn)+')/density').T
                self.out["TiD"] = self.jet.partial_get('core_profiles',
                          'profiles_1d(:)/ion('+str(nn)+')/temperature').T
                self.out["vtD"] = self.jet.partial_get('core_profiles',
                          'profiles_1d(:)/ion('+str(nn)+')/velocity_tor').T
                self.out["wtD"] = self.jet.partial_get('core_profiles',
                          'profiles_1d(:)/ion('+str(nn)+')/rotation_frequency_tor').T                     
                if np.any(self.out["vtD"]) is not None:
                    self.out["vtor"] += self.out["vtD"]
            elif label == 'T':
                self.out["niT"] = self.jet.partial_get('core_profiles',
                          'profiles_1d(:)/ion('+str(nn)+')/density').T
                self.out["TiT"] = self.jet.partial_get('core_profiles',
                          'profiles_1d(:)/ion('+str(nn)+')/temperature').T
                self.out["vtT"] = self.jet.partial_get('core_profiles',
                          'profiles_1d(:)/ion('+str(nn)+')/velocity_tor').T
                self.out["wtT"] = self.jet.partial_get('core_profiles',
                          'profiles_1d(:)/ion('+str(nn)+')/rotation_frequency_tor').T
                if np.any(self.out["vtT"]) is not None:
                    self.out["vtor"] += self.out["vtT"]
            elif label == 'He':
                self.out["niHe"] = self.jet.partial_get('core_profiles',
                          'profiles_1d(:)/ion('+str(nn)+')/density').T
                self.out["TiHe"] = self.jet.partial_get('core_profiles',
                          'profiles_1d(:)/ion('+str(nn)+')/temperature').T
                self.out["vtHe"] = self.jet.partial_get('core_profiles',
                          'profiles_1d(:)/ion('+str(nn)+')/velocity_tor').T
                self.out["wtHe"] = self.jet.partial_get('core_profiles',
                          'profiles_1d(:)/ion('+str(nn)+')/rotation_frequency_tor').T
                if np.any(self.out["vtHe"]) is not None:
                    self.out["vtor"] += self.out["vtHe"]
            elif label == 'C':
                self.out["niC"] = self.jet.partial_get('core_profiles',
                          'profiles_1d(:)/ion('+str(nn)+')/density').T
                self.out["TiC"] = self.jet.partial_get('core_profiles',
                          'profiles_1d(:)/ion('+str(nn)+')/temperature').T
                self.out["vtC"] = self.jet.partial_get('core_profiles',
                          'profiles_1d(:)/ion('+str(nn)+')/velocity_tor').T
                self.out["wtC"] = self.jet.partial_get('core_profiles',
                          'profiles_1d(:)/ion('+str(nn)+')/rotation_frequency_tor').T
                if np.any(self.out["vtC"]) is not None:
                    self.out["vtor"] += self.out["vtC"]
            elif label == 'Ne':
                self.out["niNe"] = self.jet.partial_get('core_profiles',
                          'profiles_1d(:)/ion('+str(nn)+')/density').T
                self.out["TiNe"] = self.jet.partial_get('core_profiles',
                          'profiles_1d(:)/ion('+str(nn)+')/temperature').T
                self.out["vtNe"] = self.jet.partial_get('core_profiles',
                          'profiles_1d(:)/ion('+str(nn)+')/velocity_tor').T
                self.out["wtNe"] = self.jet.partial_get('core_profiles',
                          'profiles_1d(:)/ion('+str(nn)+')/rotation_frequency_tor').T
                if np.any(self.out["vtNe"]) is not None:
                    self.out["vtor"] += self.out["vtNe"]
            elif label == 'W':
                self.out["niW"] = self.jet.partial_get('core_profiles',
                          'profiles_1d(:)/ion('+str(nn)+')/density').T
                self.out["TiW"] = self.jet.partial_get('core_profiles',
                          'profiles_1d(:)/ion('+str(nn)+')/temperature').T
                self.out["vtW"] = self.jet.partial_get('core_profiles',
                          'profiles_1d(:)/ion('+str(nn)+')/velocity_tor').T
                self.out["wtW"] = self.jet.partial_get('core_profiles',
                          'profiles_1d(:)/ion('+str(nn)+')/rotation_frequency_tor').T
                if np.any(self.out["vtW"]) is not None:
                    self.out["vtor"] += self.out["vtW"]

        self.out["vtor"] = self.out["vtor"]/nions
        self.out["pres"] = self.jet.partial_get('core_profiles',
                                    'profiles_1d(:)/pressure_thermal(:)').T

        #Total toroidal current density = average(J_Tor/R) / average(1/R)
        #{dynamic} [A/m^2]
        self.out["jtor"] = self.jet.partial_get('core_profiles',
                                         'profiles_1d(:)/j_tor').T
        #Bootstrap current density = average(J_Bootstrap.B) / B0,
        #where B0 = Core_Profiles/Vacuum_Toroidal_Field/ B0
        self.out["jpar_Bs"] = self.jet.partial_get('core_profiles',
                                         'profiles_1d(:)/j_bootstrap').T
        self.out["qprof"] = self.jet.partial_get('core_profiles',
                                         'profiles_1d(:)/q').T
        #Magnetic shear
        self.out["qshear"] = self.jet.partial_get('core_profiles',
                                         'profiles_1d(:)/magnetic_shear').T
        #Vacuum Btor(R=Raxis)
        self.out["Btor_vac"] = self.jet.partial_get('core_profiles',
                                'vacuum_toroidal_field/b0(:)').T

        ########
        #NBI IDS
        ########
        n_units = self.jet.partial_get('nbi', 'unit')
        n_units = len(n_units)
        self.out["Pnbi_launched"] = np.zeros_like(self.out["time"])
        if n_units != 0:
            for uu in range(0, n_units):
                p_launched = self.jet.partial_get('nbi',
                            'unit('+str(uu)+')/power_launched/data')
                if p_launched is not None:
                    self.out["Pnbi_launched"] += p_launched
                t_nbi = self.jet.partial_get('nbi',
                            'unit('+str(uu)+')/power_launched/time')
            self.out["t_nbi"] = t_nbi

        ##################
        #EDGE PROFILES IDS
        ##################
        #JETTO simulations don't have the edge profiles IDS,
        #therefore, only read them if it's a Coconut simulation
        #if self.tranfile:
            #self.out["time_e2d"] = self.jet.partial_get('edge_profiles',
            #                    'time(:)')
            #self.out["ne_edge"] = self.jet.partial_get('edge_profiles',
            #                    'profiles_1d(:)/electrons/density(:)')
            #self.out["Te_edge"] = self.jet.partial_get('edge_profiles',
            #                    'profiles_1d(:)/electrons/temperature(:)')

        #################
        #CORE SOURCES IDS
        #################
        #Cource sources identifiers
        # i1: 0 (unspecified) Unspecified source type
        # i1: 1	Total source; combines all sources
        # i1: 2 Source from Neutral Beam Injection
        # i1; 3 Sources from electron cyclotron heating and current drive
        # i1: 6 Sources from fusion reactions, e.g., alpha particle heating
        # i1: 7 Source from ohmic heating
        # i1: 108 (gas_puff) Gas puff
        #Rho of core_sources has the same dimmensionality
        #as rho from core_profiles, and the same values
        #(I compared them), so I assume they are the same
        #radial coordinate
        #rho = self.jet.partial_get('core_sources',
        #      'source(0)/profiles_1d(:)/grid/rho_tor_norm(:)')
        cs = self.jet.get('core_sources')
        for ss in range(0, len(cs.source)):
            #0 (unspecified) Unspecified source type
            if cs.source[ss].identifier.index == 0:
                self.out["S0"] = self.jet.partial_get('core_sources',
                'source(0)/profiles_1d(:)/ion(1)/particles(:)')

            #Total sources
            elif cs.source[ss].identifier.index == 1:
                self.out["rhot_tot"] = self.jet.partial_get('core_sources',
                'source('+str(ss)+')/profiles_1d(:)/grid/rho_tor_norm').T
                self.out["Ptot_e"] = self.jet.partial_get('core_sources',
                'source('+str(ss)+')/profiles_1d(:)/electrons/energy').T
                self.out["Ptot_i"] = self.jet.partial_get('core_sources',
                'source('+str(ss)+')/profiles_1d(:)/total_ion_energy').T

                #Loop over ions for particle sources
                #[part/s*m^3]
                #Total part. source
                ions = self.jet.partial_get('core_sources',
                    'source('+str(ss)+')/profiles_1d(:)/ion')
                nions = len(ions)
                for nn in range(0, nions):
                    label = np.unique(self.jet.partial_get('core_sources',
                            'source('+str(ss)+')/profiles_1d(:)/ion('+\
                            str(nn)+')/label'))[0]
                    if label == 'H':
                        self.out["Stot_H"] = self.jet.partial_get('core_sources',
                            'source('+str(ss)+')/profiles_1d(:)/ion('+
                            str(nn)+')/particles').T
                    if label == 'D':
                        self.out["Stot_D"] = self.jet.partial_get('core_sources',
                            'source('+str(ss)+')/profiles_1d(:)/ion('+
                            str(nn)+')/particles').T
                    elif label == 'T':
                        self.out["Stot_T"] = self.jet.partial_get('core_sources',
                            'source('+str(ss)+')/profiles_1d(:)/ion('+
                            str(nn)+')/particles').T
                    elif label == 'He':
                        self.out["Stot_He"] = self.jet.partial_get('core_sources',
                            'source('+str(ss)+')/profiles_1d(:)/ion('+
                            str(nn)+')/particles').T
                    elif label == 'Ne':
                        self.out["Stot_Ne"] = self.jet.partial_get('core_sources',
                            'source('+str(ss)+')/profiles_1d(:)/ion('+
                            str(nn)+')/particles').T

            #NBI sources
            elif cs.source[ss].identifier.index == 2:
                self.out["rhotnbi"] = self.jet.partial_get('core_sources',
                    'source('+str(ss)+')/profiles_1d(:)/grid/rho_tor_norm').T
                #[W/m3]
                self.out["Pnbi_e"] = self.jet.partial_get('core_sources',
                    'source('+str(ss)+')/profiles_1d(:)/electrons/energy').T
                self.out["Pnbi_i"] = self.jet.partial_get('core_sources',
                    'source('+str(ss)+')/profiles_1d(:)/total_ion_energy').T
                #[A/m^2]
                self.out["j_parallel_nbi"] = self.jet.partial_get('core_sources',
                    'source('+str(ss)+')/profiles_1d(:)/j_parallel').T
                #[kg/ms^2]
                self.out["mom_tor_nbi"] = self.jet.partial_get('core_sources',
                    'source('+str(ss)+')/profiles_1d(:)/momentum_tor').T

                #Loop over ions for particle sources
                #[part/s*m^3]
                #NBI part. source (spec 1)
                #SBD1 = self.jet.partial_get('core_sources',
                #       'source(2)/profiles_1d(:)/ion(1)/particles(:)')
                #NBI part. source (spec 2)
                #SBD2 = self.jet.partial_get('core_sources',
                #       'source(2)/profiles_1d(:)/ion(2)/particles(:)')
                ions = self.jet.partial_get('core_sources',
                    'source('+str(ss)+')/profiles_1d(:)/ion')
                nions = len(ions)
                for nn in range(0, nions):
                    label = np.unique(self.jet.partial_get('core_sources',
                            'source('+str(ss)+')/profiles_1d(:)/ion('+\
                            str(nn)+')/label'))
                    if label == 'D':
                        self.out["Snbi_D"] = self.jet.partial_get('core_sources',
                            'source('+str(ss)+')/profiles_1d(:)/ion('+
                            str(nn)+')/particles').T
                        #Assume for the time being D and T
                        self.out["SBD1"] = self.out["Snbi_D"]
                    elif label == 'T':
                        self.out["Snbi_T"] = self.jet.partial_get('core_sources',
                            'source('+str(ss)+')/profiles_1d(:)/ion('+
                            str(nn)+')/particles').T
                        #Assume for the time being D and T
                        self.out["SBD2"] = self.out["Snbi_T"]
                    elif label == 'He':
                        self.out["Snbi_He"] = self.jet.partial_get('core_sources',
                            'source('+str(ss)+')/profiles_1d(:)/ion('+
                            str(nn)+')/particles').T

            #ECRH sources
            elif cs.source[ss].identifier.index == 3:
                self.out["rhotec"] = self.jet.partial_get('core_sources',
                    'source('+str(ss)+')/profiles_1d(:)/grid/rho_tor_norm').T
                self.out["Pecrh"] = self.jet.partial_get('core_sources',
                    'source('+str(ss)+')/profiles_1d(:)/electrons/energy').T
                self.out["jpar_ec"] = self.jet.partial_get('core_sources',
                    'source('+str(ss)+')/profiles_1d(:)/j_parallel').T

            #Sources from fusion reactions, e.g., alpha particle heating
            elif cs.source[ss].identifier.index == 6:
                self.out["Palh_e"] = self.jet.partial_get('core_sources',
                        'source('+str(ss)+')/profiles_1d(:)/electrons/energy').T
                self.out["Palh_i"] = self.jet.partial_get('core_sources',
                        'source('+str(ss)+')/profiles_1d(:)/ions(0)/energy').T
                #Not populated
                #Palf = self.jet.partial_get('core_sources',
                #       'source(6)/global_quantities(:)/power')

            #Source from ohmic heating
            elif cs.source[ss].identifier.index == 7:
                self.out["Poh_e"] = self.jet.partial_get('core_sources',
                        'source('+str(ss)+')/profiles_1d(:)/electrons/energy').T
                if np.shape(self.out["Poh_e"])[0] is not 0:
                    Poh_tot = np.zeros_like(self.out["time"])
                    for tt in range(0, np.shape(dVds)[0]):
                        Poh_tot[tt] = np.sum(self.out["Poh_e"][tt,1:]*dVds[tt,:]*ds[tt,:])
                    self.out["Poh_tot"] = np.squeeze(Poh_tot)

            #Radiation sources [W/m3]
            elif cs.source[ss].identifier.index == 200:
                self.out["rhotrad"] = self.jet.partial_get('core_sources',
                    'source('+str(ss)+')/profiles_1d(:)/grid/rho_tor_norm').T
                self.out["Prad"] = self.jet.partial_get('core_sources',
                    'source('+str(ss)+')/profiles_1d(:)/electrons/energy').T
                #I couldn't find an IDS for the total radited power as a 
                #function of time, so I compute the integral myself
                if np.shape(self.out["Prad"])[0] is not 0:
                    Prad_tot = np.zeros_like(self.out["time"])
                    for tt in range(0, np.shape(dVds)[0]):
                        Prad_tot[tt] = np.sum(self.out["Prad"][tt,1:]*dVds[tt,:]*ds[tt,:])
                    self.out["Prad_tot"] = np.squeeze(Prad_tot)


        ###################
        #CORE TRANSPORT IDS
        ###################
        #model(i1)/identifier
        #Transport model identifiers
        #i1: 0 unspecified
        #i1: 1 Combination of data from available transport models.
        #i1: 2 Output from a transport solver
        #i3: 3 Background transport level, ad-hoc transport model,
        #      not directly related to a physics model
        #i4: 4 Transport specified by a database entry external to
        #      the dynamic evolution of the plasma
        #i5: 5 Neoclassical
        #i6: 6 Representation of turbulent transport
        nmodels = len(self.jet.partial_get('core_transport', 'model'))
        ct = self.jet.get('core_transport')
        for nn in range(0, nmodels):
            if ct.model[nn].identifier.name == 'combined':
                self.out["rhot_Xs"] = self.jet.partial_get('core_transport',
                       'model('+str(nn)+')/profiles_1d(:)/grid_flux/rho_tor_norm(:)').T
                #[m2/s]
                self.out["Xe"] = self.jet.partial_get('core_transport',
                       'model('+str(nn)+')/profiles_1d(:)/electrons/energy/d(:)').T
                self.out["Xi"] = self.jet.partial_get('core_transport',
                       'model('+str(nn)+')/profiles_1d(:)/total_ion_energy/d(:)').T
                #Electron effective diffusivity
                self.out["De_eff"] = self.jet.partial_get('core_transport',
                             'model('+str(nn)+')/profiles_1d(:)/electrons/particles/d(:)').T
                self.out["ve_eff"] = self.jet.partial_get('core_transport',
                             'model('+str(nn)+')/profiles_1d(:)/electrons/particles/v(:)').T          
                self.out["D1_eff"] = self.jet.partial_get('core_transport',
                             'model('+str(nn)+')/profiles_1d(:)/ions(0)/particles/d(:)').T
                self.out["v1_eff"] = self.jet.partial_get('core_transport',
                             'model('+str(nn)+')/profiles_1d(:)/ions(0)/particles/v(:)').T                  
                self.out["D2_eff"] = self.jet.partial_get('core_transport',
                             'model('+str(nn)+')/profiles_1d(:)/ions(1)/particles/d(:)').T
                self.out["v2_eff"] = self.jet.partial_get('core_transport',
                             'model('+str(nn)+')/profiles_1d(:)/ions(1)/particles/v(:)').T

                #Toroidal momentum transport
                self.out["D_tormom"] = self.jet.partial_get('core_transport',
                             'model('+str(nn)+')/profiles_1d(:)/momentum_tor/d(:)').T
                self.out["v_tormom"] = self.jet.partial_get('core_transport',
                             'model('+str(nn)+')/profiles_1d(:)/momentum_tor/v(:)').T

                #For some old runs, these IDS are not filled
                #Set the arrays to 0
                if np.any(self.out["De_eff"]==None):
                    self.out["De_eff"] = np.zeros_like(self.out["rhot_Xs"])
                    self.out["D1_eff"] = np.zeros_like(self.out["rhot_Xs"])
                    self.out["D2_eff"] = np.zeros_like(self.out["rhot_Xs"])

            #neoclassical
            if ct.model[nn].identifier.name == 'neoclassical':
                nions = len(self.jet.partial_get('core_transport', 'model('+\
                            str(nn)+')/profiles_1d(:)/ion'))
                for ll in range (0, nions):
                    label = np.unique(self.jet.partial_get('core_transport',
                            'model('+str(nn)+')/profiles_1d(:)/ion('+\
                            str(ll)+')/label'))
                    if label == 'H':
                        self.out["Dn_H"] = self.jet.partial_get('core_transport', 'model('+\
                                   str(nn)+')/profiles_1d(:)/ion('+str(ll)+')/particles/d').T
                        self.out["vn_H"] = self.jet.partial_get('core_transport', 'model('+\
                                   str(nn)+')/profiles_1d(:)/ion('+str(ll)+')/particles/v').T
                    if label == 'D':
                        self.out["Dn_D"] = self.jet.partial_get('core_transport', 'model('+\
                                   str(nn)+')/profiles_1d(:)/ion('+str(ll)+')/particles/d').T
                        self.out["vn_D"] = self.jet.partial_get('core_transport', 'model('+\
                                   str(nn)+')/profiles_1d(:)/ion('+str(ll)+')/particles/v').T
                    if label == 'T':
                        self.out["Dn_T"] = self.jet.partial_get('core_transport', 'model('+\
                                   str(nn)+')/profiles_1d(:)/ion('+str(ll)+')/particles/d').T
                        self.out["vn_T"] = self.jet.partial_get('core_transport', 'model('+\
                                   str(nn)+')/profiles_1d(:)/ion('+str(ll)+')/particles/v').T                                
                    if label == 'Ne':
                        self.out["Dn_Ne"] = self.jet.partial_get('core_transport', 'model('+\
                                    str(nn)+')/profiles_1d(:)/ion('+str(ll)+')/particles/d').T
                        self.out["vn_Ne"] = self.jet.partial_get('core_transport', 'model('+\
                                    str(nn)+')/profiles_1d(:)/ion('+str(ll)+')/particles/v').T
                    if label == 'W':
                        self.out["Dn_W"] = self.jet.partial_get('core_transport', 'model('+\
                                   str(nn)+')/profiles_1d(:)/ion('+str(ll)+')/particles/d').T
                        self.out["vn_W"] = self.jet.partial_get('core_transport', 'model('+\
                                   str(nn)+')/profiles_1d(:)/ion('+str(ll)+')/particles/v').T

            #turbulent
            if ct.model[nn].identifier.name == 'anomalous':
                nions = len(self.jet.partial_get('core_transport', 'model('+\
                            str(nn)+')/profiles_1d(:)/ion'))
                for ll in range (0, nions):
                    label = np.unique(self.jet.partial_get('core_transport',
                            'model('+str(nn)+')/profiles_1d(:)/ion('+\
                            str(ll)+')/label'))
                    if label == 'H':
                        self.out["Dt_H"] = self.jet.partial_get('core_transport', 'model('+\
                                   str(nn)+')/profiles_1d(:)/ion('+str(ll)+')/particles/d').T
                        self.out["vt_H"] = self.jet.partial_get('core_transport', 'model('+\
                                   str(nn)+')/profiles_1d(:)/ion('+str(ll)+')/particles/v').T
                    if label == 'D':
                        self.out["Dt_D"] = self.jet.partial_get('core_transport', 'model('+\
                                   str(nn)+')/profiles_1d(:)/ion('+str(ll)+')/particles/d').T
                        self.out["vt_D"] = self.jet.partial_get('core_transport', 'model('+\
                                   str(nn)+')/profiles_1d(:)/ion('+str(ll)+')/particles/v').T
                    if label == 'T':
                        self.out["Dt_T"] = self.jet.partial_get('core_transport', 'model('+\
                                   str(nn)+')/profiles_1d(:)/ion('+str(ll)+')/particles/d').T
                        self.out["vt_T"] = self.jet.partial_get('core_transport', 'model('+\
                                   str(nn)+')/profiles_1d(:)/ion('+str(ll)+')/particles/v').T                                
                    if label == 'Ne':
                        self.out["Dt_Ne"] = self.jet.partial_get('core_transport', 'model('+\
                                    str(nn)+')/profiles_1d(:)/ion('+str(ll)+')/particles/d').T
                        self.out["vt_Ne"] = self.jet.partial_get('core_transport', 'model('+\
                                    str(nn)+')/profiles_1d(:)/ion('+str(ll)+')/particles/v').T
                    if label == 'W':
                        self.out["Dt_W"] = self.jet.partial_get('core_transport', 'model('+\
                                   str(nn)+')/profiles_1d(:)/ion('+str(ll)+')/particles/d').T
                        self.out["vt_W"] = self.jet.partial_get('core_transport', 'model('+\
                                   str(nn)+')/profiles_1d(:)/ion('+str(ll)+')/particles/v').T

        ###################
        #FURTHER QUANTITIES
        ###################
        #I cannot find impurity concentrations as a function
        #of time (.jst output IMC1, IMC2, etc.), so I calculate
        #them here.
        ne_avg = np.zeros_like(Vol_t)
        niW_avg = np.zeros_like(Vol_t)
        niNe_avg = np.zeros_like(Vol_t)
        Pnbi_etot = np.zeros_like(self.out["time"])
        Pnbi_itot = np.zeros_like(self.out["time"])

        #It can be that the equilibrium and kinetic profiles have
        #different radial grids, for instance, when taking input IDS.
        #I need to check for this and interpolate, but for the time being,
        #I simply don't perform the calculations if the grids don't match.
        if np.shape(rho_tor_norm_eq)[1] == np.shape(self.out["ne"])[1]:
            for tt in range(0, np.shape(dVds)[0]):
                ne_avg[tt] = (1/Vol_t[tt]) * np.sum(self.out["ne"][tt,1:]*\
                             dVds[tt,:]*ds[tt,:])
                niNe_avg[tt] = (1/Vol_t[tt]) * np.sum(self.out["niNe"][tt,1:]*\
                               dVds[tt,:]*ds[tt,:])
                niW_avg[tt] = (1/Vol_t[tt]) * np.sum(self.out["niW"][tt,1:]*\
                              dVds[tt,:]*ds[tt,:])
                #Pnbi_etot[tt] = np.sum(self.out["Pnbi_e"][tt,1:]*\
                #                dVds[tt,:]*ds[tt,:])
                #Pnbi_itot[tt] = np.sum(self.out["Pnbi_i"][tt,1:]*\
                #                dVds[tt,:]*ds[tt,:])

            self.out["ne_avg"] = ne_avg
            self.out["niNe_avg"] = niNe_avg
            self.out["niW_avg"] = niW_avg
            self.out["IMC_Ne"] = (niNe_avg/ne_avg)*100
            self.out["IMC_W"] = (niW_avg/ne_avg)*100
            #self.out["Pnbi_etot"] = Pnbi_etot
            #self.out["Pnbi_itot"] = Pnbi_itot
        else:
            pass


        return

    def _calculate_derived_quantities(self):

        """
         Calculates derived quantities from IDS JINTRAC
         output. Since the JINTRAC IMAS driver does not
         fill every IDS that would mimic the standard output,
         we compute some useful quantities here.
        """

        if self.backend == "mdsplus" or self.backend == "hdf5":
            cp = self.jet.get('core_profiles')
            #Poloidal flux
            chi_pol = self.jet.partial_get('core_profiles',
                        'profiles_1d(:)/grid/psi(:)').T
            Vol_t = self.jet.partial_get('equilibrium',
                        'time_slice(:)/global_quantities(:)/volume').T
            Vol_rho = self.jet.partial_get('equilibrium',
                        'time_slice(:)/profiles_1d/volume').T           
            #This IDS is populated with a bunch of Nones..
            #rhop = self.jet.partial_get('core_profiles',
            #     'profiles_1d(:)/grid/rho_pol_norm(:)').T
            dVdchi = (Vol_rho[:,1:]-Vol_rho[:,:-1])/\
                     (chi_pol[:,1:]-chi_pol[:,:-1])
            chi_pol_axis = np.expand_dims(chi_pol[:,0], axis=1)
            chi_pol_axis = np.repeat(chi_pol_axis, np.shape(chi_pol)[1],
                                     axis=1)
            chi_pol_sepa = np.expand_dims(chi_pol[:,-1], axis=1)
            chi_pol_sepa = np.repeat(chi_pol_sepa, np.shape(chi_pol)[1],
                                     axis=1)
            rhop = np.sqrt(np.abs((chi_pol[:,:] - chi_pol_axis)/\
                              (chi_pol_sepa - chi_pol_axis)))                    
            r_omp = self.jet.partial_get('equilibrium',
                    'time_slice(:)/profiles_1d/r_outboard').T            
            pres = self.jet.partial_get('core_profiles',
                    'profiles_1d(:)/pressure_thermal(:)').T
            dpdrp = (pres[:,1:]-pres[:,:-1])/\
                    (rhop[:,1:]-rhop[:,:-1])
            dpdchi = (pres[:,1:]-pres[:,:-1])/\
                    (chi_pol[:,1:]-chi_pol[:,:-1])
            dpdV = (pres[:,1:]-pres[:,:-1])/\
                    (Vol_rho[:,1:]-Vol_rho[:,:-1])
            dpdr = (pres[:,1:]-pres[:,:-1])/\
                    (r_omp[:,1:]-r_omp[:,:-1])  
            dpdrt = (pres[:,1:]-pres[:,:-1])/\
                    (self.out["rhot_norm"][:,1:]-self.out["rhot_norm"][:,:-1])
            qprof = self.jet.partial_get('core_profiles',
                    'profiles_1d(:)/q').T 
            summary = self.jet.get('summary')
            B0 = self.jet.partial_get('core_profiles',
                    'vacuum_toroidal_field/b0(:)').T
            R0 = summary.global_quantities.r0.value
            mu0 = 4*np.pi*1.e-7
            eps = (r_omp-R0)/R0
            B0_1 = np.repeat(np.expand_dims(B0,axis=1),
                        np.shape(dpdrp[-1,:]),axis=1)
            alpha_ballooning = dpdrp* (-2.*mu0*(qprof[:,:-1]**2.0) /\
                           (eps[:,:-1]*B0_1**2.0))
            alpha_cyl = dpdr* (-2.*mu0*R0*(qprof[:,:-1]**2.0) /\
                           (B0_1**2.0))
            alpha_miller = (-2.*dVdchi/(2.*np.pi)**2.0) *\
                            np.sqrt(Vol_rho[:,1:]/(2.*(np.pi**2.0)*R0))*\
                            mu0 * dpdchi
            alpha_mishka =\
            (1/2.*mu0*r_omp[:,1:]**2.0)*(-4.* ((qprof[:,:-1]**2.0)/(eps[:,1:]*B0_1**2.0))*\
                        np.sqrt(Vol_rho[:,:-1]) * dpdV)

            #alpha jetto
            #jetto/alfcalc.f
            #ALFVAL(J) = P8*1.E-7 * (RMAEQ2(J)-RMJT)**2
            #* ABS( (GRDPE(J)+GRDPI(J))/GRDPSI(J)/BPAEQ2(J) )/ ANORM
            B0_2 = np.ones_like(r_omp)*B0[-1]
            B_theta = r_omp/(R0+r_omp)*(B0_2/qprof)

            alpha_jetto = 0.5* mu0 * (r_omp[:,:-1]**2.0) *\
                        np.abs(dpdchi * 1/B_theta[:,:-1])

            self.out['alpha_ballooning'] = alpha_ballooning
            self.out["alpha_jetto"] = alpha_jetto
            #Maximum critical pressure gradients
            self.out["alpha_max_ballooning_edge"] =\
            np.squeeze(np.max(self.out["alpha_ballooning"][:,-100:], axis=1))
            self.out["alpha_max_jetto_edge"] =\
                                    np.max(alpha_jetto[:,-100:], axis=1)
            self.out["alpha_max_mishka_edge"] = np.max(alpha_mishka[:,-100:], axis=1)

            #plt.figure()
            #plt.plot(r_omp[-1,1:], alpha_ballooning[-1,:], label="alpha_ballooning")
            #plt.plot(r_omp[-1,1:], alpha_cyl[-1,:], c="red", label="alpha cyl")
            #plt.plot(r_omp[-1,1:], alpha_miller[-1,:], c="brown", label="alpha miller")
            #plt.plot(r_omp[-1,1:], alpha_jetto[-1,:], c="green", label="alpha jetto")
            #plt.plot(r_omp[-1,1:], alpha_mishka[-1,:], c="orange", label="alpha mishka")
            #plt.legend()
            #plt.show()

            #Greenwald fraction
            #Should be included in Summary IDS, but it's not :)
            r_omp = self.jet.partial_get('equilibrium',
                        'time_slice(:)/profiles_1d/r_outboard').T
            Ip = self.jet.partial_get('equilibrium',
                        'time_slice(:)/global_quantities/ip').T
            r_minor = self.jet.partial_get('equilibrium',
                        'time_slice(:)/boundary/minor_radius').T
            ne_lavg = summary.line_average.n_e.value
            surf = np.pi * r_minor**2.0
            nGw = np.abs((Ip/1.e6)/surf)
            #[%]
            self.out["fGw"] = np.abs(ne_lavg/(1.e20*nGw))*100

            #Fusion Q
            self.out["Paux"] = (self.out["Pnbi_tot"] + self.out["Pec_tot"])
            self.out["Qfus"] = self.out["Palf"]*5/(self.out["Paux"])

            #Martin L-H transition power scaling
            self.out["Plht"] = 0.0488 * 1e6 * ((self.out["ne_lavg"]/1e20)**0.72) *\
                               (np.abs(self.out["Btor"])**0.8) * (self.out["Sur_t"]**0.94)

        #Wth
        drho = self.out["rho"][:,1:] - self.out["rho"][:,:-1]
        array = np.zeros(len(self.out["time"]))
        drho = np.hstack((np.expand_dims(array.T, axis=1), drho))
        #The ETB is especified at 8cm width. Interpolate the rho
        #value so I know where the pedestal is. Since jetto.jsp
        #does not output the minor radius at Z=Zaxis, interpolate
        #from the major radius instead as an approximation
        rhotn_etb = np.interp(np.array([np.max(self.out['R_omp'][-1,:])-0.08]),
                              self.out['R_omp'][-1,:], self.out['rhot_norm'][-1,:])
        idx_etb = np.argmin((self.out["rhot_norm"][-1,:] - rhotn_etb)**2.0)

        self.out["Wth_ped"] = 3/2. * \
        np.sum(((self.out["ne"]*self.out["Te"] + self.out["niH"]*self.out["Ti"] +\
                 self.out["niD"]*self.out["Ti"]+ self.out["niT"]*self.out["Ti"]) *\
                 self.out["dVdrho"]*drho)[:,idx_etb:], axis=1)
        #Convert to MJ
        self.out["Wth_ped"] *= (1.380649e-23 / 8.617333262e-5) / 1.e6

        self.out["Wth_cal"] = 3/2. * \
        np.sum(((self.out["ne"]*self.out["Te"] + self.out["niH"]*self.out["Ti"] +\
                 self.out["niD"]*self.out["Ti"]+ self.out["niT"]*self.out["Ti"]) *\
                 self.out["dVdrho"]*drho), axis=1)
        #Convert to MJ
        self.out["Wth_cal"] *= (1.380649e-23 / 8.617333262e-5) / 1.e6

        return


    def _read_edge2d(self):

        """ 
        Reads EDGE2D TRAN output files

        Parameters
        ----------

        Output
        ----------

        Notes
        ----------
         JINTRAC Wiki EPROC page
         https://users.euro-fusion.org/pages/data-cmg/
         wiki/EPROC_Python_module.html

         Note: Using EPROC requires preloading JINTRAC
         modules, i.e.:
         module use #HOME/jintrac/$JINVER/modules
         module load jintrac
         This will automatically load compatible IMAS,
         Python, IPython and Viz libraries.

         Available rows to read (from row.py):
         xx = Absolute row number.
         OT = Outer target
         IT = Inner Target
         IMP = Inner mid-plane.
         OMP = Outer mid-plane.

         Some EPROC Nomenclature
         Every output is a Struct, you can see what is 
         inside the structure with the command dir(Struct)
         To access one of the quantities just do quant.field
          ep.row - Will read along a row
          ep.ring - Will read along a ring
           - To read along a ring use ep.ring(tran, quantity, 'SX')
             where 'X' is the ring index.
          ep.data - Will fetch particular data
          ep.volint - Will compute vol. integral btw. 2 rings
          OT - Will read along Outer target
          IT - Will read along Inner target
          OMP - Will read along Outer Midplane
          IMP - Will read along Inner Midplane
        """

        nt = 0
        #Use the tran file generated by JINTRAC
        tran_file = self.jetto_path + "/tran"
        varnames = dir(ep.names(tran_file))
        nt = ep.data(tran_file,'TVEC').nPts
        #If tran file does not exist, look in the
        #directory for the last tranXX file.
        if nt==0:
            filelist = os.listdir(self.jetto_path)
            tranfiles = [i for i in filelist if "tran" in i and len(i) < 8]
            numbers = [int(i.replace("tran", "")) for i in tranfiles]
            maxnum = np.max(numbers)
            #TRAN files with number < 10 are named tran+0+num,
            #i.e. tran01, tran02, etc.
            if maxnum < 10:
                str_maxnum = "0" + str(maxnum)
            else:
                str_maxnum = str(maxnum)
            tran_file = self.jetto_path + "/tran" + str_maxnum

            #From the JINTRAC wiki. Arguments to this function.
            #prof = 1 will display profile names.
            #time = 1 will display time traces names.
            #flux = 1 will display Nimbus flux.
            #geom = 1 will display Geometry data.
            #sort = 1 will alphabetically sort signal names.
            varnames = ep.names(tran_file)

        #################################
        #Retrieve time trace signal names
        #################################
        varnames2 = ep.getnames(tran_file, 2).names
        descriptions2 = ep.getnames(tran_file, 2).description

        #Time base is in [ms]
        nt = ep.data(tran_file,'TVEC').nPts
        self.out["time_e2d"] = ep.data(tran_file,'TVEC').data[:nt]/1.e3

        #Maximum power density at the targets [W/m2] -> [MW/m2]
        self.out["Qmax_it"] = ep.data(tran_file,'QMAXIT').data[:nt]/1.e6
        self.out["Qmax_ot"] = ep.data(tran_file,'QMAXOT').data[:nt]/1.e6

        #Effective sputtering factors [Ne, W]
        self.out["Yeff_Ne"] = ep.data(tran_file,'YLDT_1').data[:nt]
        self.out["Yeff_W"] = ep.data(tran_file,'YLDT_2').data[:nt]

        #SOL gas puff - [ions/s as far as I can see]
        #EXTRA NEUTRAL FLUX
        self.out["Stot_main"] = ep.data(tran_file,'HEXTRA').data[:nt]
        #NE- EXTRA NEUTRAL IMPURITIES 
        self.out["Spuff_Ne_tot"] = ep.data(tran_file,'ZEXTRT_1').data[:nt]
        #W - EXTRA NEUTRAL IMPURITIES
        self.out["Spuff_W_tot"] = ep.data(tran_file,'ZEXTRT_2').data[:nt]

        #[eV]
        # These temperatures are at x=0 in the plate
        # (I verified it myself comparing against (TEVE, OT)
        # at Te_ot.xData = 0)
        Te_ot_t = ep.time(tran_file, 'TESOT')
        self.out["Te_ot_t"] = Te_ot_t.yData
        Ti_ot_t = ep.time(tran_file, 'TISOT')
        self.out["Ti_ot_t"] = Ti_ot_t.yData
        Te_it_t = ep.time(tran_file, 'TESIT')
        self.out["Te_it_t"] = Te_it_t.yData
        Ti_it_t = ep.time(tran_file, 'TISIT')
        self.out["Ti_it_t"] = Ti_it_t.yData

        #Electron Temperature [eV]
        Te_ot = ep.row(tran_file,'TEVE','OT')
        self.out['x_div_ot'] = np.array(Te_ot.xData)
        self.out['Te_ot'] = np.array(Te_ot.yData)
        Te_it = ep.row(tran_file,'TEVE','IT')
        self.out['x_div_it'] = np.array(Te_it.xData)
        self.out['Te_it'] = np.array(Te_it.yData)
        Te_im = ep.row(tran_file,'TEVE','IMP')
        self.out['x_im'] = Te_im.xData
        self.out['Te_im'] = Te_im.yData
        Te_om = ep.row(tran_file,'TEVE','OMP')
        self.out['x_om'] = Te_om.xData
        self.out['Te_om'] = Te_om.yData

        #Impurity densities
        n_imp1_im = ep.row(tran_file,'DENZ01', 'IMP')
        self.out["n_imp1_im"] = n_imp1_im.yData
        n_imp1_om = ep.row(tran_file,'DENZ01', 'OMP')
        self.out["n_imp1_om"] = n_imp1_om.yData
        n_imp1_it = ep.row(tran_file,'DENZ01', 'IT')
        self.out["n_imp1_it"] = n_imp1_it.yData
        n_imp1_ot = ep.row(tran_file,'DENZ01', 'OT')
        self.out["n_imp1_ot"] = n_imp1_ot.yData

        #Mesh
        #The mesh is composed of two main regions, the SOL and
        #the private flux region, each with different structures.
        #However, in the geometry data, we only get the {R,Z}
        #positions of all the points in the mesh. To build a 2D
        #grid array, it's easier to call RMESH and ZMESH using
        #ep.ring and pad with masked/NaN values the difference
        #in points between SOL and PFR.
        self.out['Rmesh'] = ep.data(tran_file,'RMESH').data
        self.out['Zmesh'] = ep.data(tran_file,'ZMESH').data
        self.out["npts_mesh"] = ep.data(tran_file,'RMESH').nPts
        mesh_geom = ep.geom(tran_file)
        #Mesh center
        self.out["R0_mesh"] = mesh_geom.r0
        self.out["Z0_mesh"] = mesh_geom.z0    
        #Number of rings and rows
        self.out["nrings_mesh"] = nRings = mesh_geom.nRings
        self.out["nrows_mesh"] = nRows = mesh_geom.nRows

        #Mesh organized by rings
        npoints_sol = len(ep.ring(tran_file,'RMESH', 'S1').yData)
        Rmesh2D = np.zeros((nRings, npoints_sol))
        Zmesh2D = np.zeros((nRings, npoints_sol))
        for i in range(0, nRings):
            Ri = np.array(ep.ring(tran_file,'RMESH', 'S'+str(i)).yData)
            Zi = np.array(ep.ring(tran_file,'ZMESH', 'S'+str(i)).yData)
            if len(Ri) < npoints_sol:
                npoints_pfr = len(Ri)
                Rmesh2D[i,:npoints_pfr] = Ri
                Rmesh2D[i,npoints_pfr:] = np.nan
                Zmesh2D[i,:npoints_pfr] = Zi
                Zmesh2D[i,npoints_pfr:] = np.nan
            else:
                Rmesh2D[i,:] = Ri
                Zmesh2D[i,:] = Zi

        self.out["Rmesh2D_rings"] = Rmesh2D
        self.out["Zmesh2D_rings"] = Zmesh2D

        #Mesh organized by rows
        npoints_sol = len(ep.row(tran_file,'RMESH', '0').yData)
        Rmesh2D = np.zeros((nRows, npoints_sol))
        Zmesh2D = np.zeros((nRows, npoints_sol))
        for i in range(0, nRows):
            Ri = np.array(ep.row(tran_file,'RMESH', str(i)).yData)
            Zi = np.array(ep.row(tran_file,'ZMESH', str(i)).yData)
            if len(Ri) < npoints_sol:
                npoints_pfr = len(Ri)
                Rmesh2D[i,:npoints_pfr] = Ri
                Rmesh2D[i,npoints_pfr:] = np.nan
                Zmesh2D[i,:npoints_pfr] = Zi
                Zmesh2D[i,npoints_pfr:] = np.nan
            else:
                Rmesh2D[i,:] = Ri
                Zmesh2D[i,:] = Zi

        self.out["Rmesh2D_rows"] = Rmesh2D
        self.out["Zmesh2D_rows"] = Zmesh2D


#        #Reading EDGE2D tran file
#        #Names from compare_e2d.py in jintrac's python folder  
#        names =\
#        ["da", "den", "denel", "denptot", "denztot", "dha", "dm",
#         "dperp", "jtargi", "pmach", "prehyd", "pretot", "soun",
#         "souz", "sqehrad", "sqezrad", "tev", "teve", "totpden",
#         "vpi", "vpinch", "vro", "vtri", "zeff"]
#
#        nitems = len(names)
#        data = []
#
#        for item in range(nitems):
#            try:
#                #npts = eproc.data(file1, names[item]).nPts
#                npts = len(tran1.tran[names[item].upper()]['data'])
#                if npts != 0:
#                    #data1.append((eproc.data(file1, names[item])).data
#                    data1.append(tran1.tran[names[item].upper()]['data'])
#                    #data2.append((eproc.data(file2, names[item])).data)
#                    data2.append(tran2.tran[names[item].upper()]['data'])
#                #Deals with empty / non-existent dataset
#                else:
#                    data1.append([])
#                    data2.append([])
#                    
#            except KeyError:
#                if verbosity > 1:
#                    print(names[item].upper(),
#                          "missing from tran file")
#                data1.append([])
#                data2.append([])

        return
    
    def _read_eirene(self):

        """ 
        Reads EIRINE files

        Parameters
        ----------

        Output
        ----------

        Notes
        ----------
        I implement this routine so far to check the EIRINE grid.
        Inspired by the routines in plote2deir by Derek Harting.
        """

        #Get EIRINE grid points stored in eirene.npco_char
        file = open(self.jetto_path + "/eirene.npco_char", mode="r")
        lines = file.readlines()
        file.close()

        self.out["npts_mesh_eirene"] = npts_mesh_eirene = int(lines[0])
        Rmesh_eirene = np.array([])
        Zmesh_eirene = np.array([])
        for ii in range (1, len(lines)):
            linetmp = lines[ii].replace('\n','').split(' ')
            while '' in linetmp:
                linetmp.remove('')
            Rmesh_eirene = np.hstack((Rmesh_eirene, float(linetmp[1])/100))
            Zmesh_eirene = np.hstack((Zmesh_eirene, float(linetmp[2])/100))

        self.out["Rmesh_eirene"] = Rmesh_eirene
        self.out["Zmesh_eirene"] = Zmesh_eirene

        #Get the indeces that compose every triangle in eirene.elemente
        file = open(self.jetto_path + "/eirene.elemente", mode="r")
        lines = file.readlines()
        file.close()
        self.out["nelements_eirene"] = nelements_eirene = int(lines[0])
        Triang_idxs = np.zeros([nelements_eirene, 3])
        for ii in range (1, len(lines)):
            linetmp = lines[ii].replace('\n','').split(' ')
            while '' in linetmp:
                linetmp.remove('')
            Triang_idxs[ii-1,:] = np.array([int(linetmp[1])-1,
                                  int(linetmp[2])-1, int(linetmp[3])-1])

        self.out["Rmesh_eirene"] = Rmesh_eirene
        self.out["Zmesh_eirene"] = Zmesh_eirene
        self.out["Triang_idxs"] = Triang_idxs

        return

    def plot_jettorun(self, savefig=False, verbose=False):

        """
         Plots parameters and profiles of interest from
         a JETTO/Coconut run.
        """

        #Make sure output quantities have been read into
        #memory
        if self.out_memory is False:
            if self.nshot is None:
                self._out_memory_standard()
            else:
                self._out_memory_imas()

        legend_fontsize = 8

        ####################
        #SSP file - Profiles
        #[time, rho]
        ####################
        fig, ax = plt.subplots(figsize=(11,8), nrows=3, ncols=3,
                               sharex=True)
        plt.subplots_adjust(wspace=0.5, top=0.91, bottom=0.05,
                            left=0.1, right=0.95)
        plt.rcParams.update({'font.size': 12})        
        fig.suptitle("t = " + str(self.out["time"][-1]) + " s")
        ax[0][0].plot(self.out["rhot_norm"][-1,:], self.out["ne"][-1,:],
                      label=r"$n_e$", c='blue')
        ax[0][0].plot(self.out["rhot_norm"][-1,:], self.out["niD"][-1,:],
                      label=r"$n_{D}$", c='red')
        ax[0][0].plot(self.out["rhot_norm"][-1,:], self.out["niT"][-1,:],
                      label=r"$n_{T}$", c='orange')
        axy = ax[0][0].twinx()

        #Particle sources [part/m3]
        #axy.plot(self.out["rhot_norm"][-1,:], self.out["S0"][-1,:],
        #         label=r"$S_{part} [1/m^3]$")
        ##NBI spec 1
        #axy.plot(self.out["rhotnbi"][-1,:], self.out["SBD1"][-1,:],
        #         c="k", label=r"$S_{NBI, spec. 1}$")
        ##NBI spec 2
        #axy.plot(self.out["rhotnbi"][-1,:], self.out["SBD2"][-1,:],
        #         c="k", ls="--", label=r"$S_{NBI, spec. 2}$")

        #D (ion?) effective
        ax[1][0].plot(self.out["rhot_Xs"][-1,:],
                      self.out["De_eff"][-1,:], c="k",
                      label=r"$D_i^{eff}$")
        if verbose:
            #Particle diffusion spec. 1 [m2/s]
            ax[1][0].plot(self.out["rhot_norm"][-1,:-1],
                          self.out["D1_eff"][-1,:], c="k",
                          ls="--", label=r"$D_{part}^{1}$")
            #Particle diffusion spec. 2 [m2/s]
            ax[1][0].plot(self.jet["rhot_norm"][-1,:-1],
                          self.out["D2_eff"][-1,:], c="k",
                          ls="-.", label=r"$D_{part}^{2}$")        
            #NCLASS ion diffusivity
            ax[1][0].plot(self.out["rhot_norm"][-1,:-1],
                          self.jet["DNCI"][-1,:], c="orange",
                          ls="-.", label=r"$D_i^{Nclass}$")
            #NCLASS electron diffusivity       
            ax[1][0].plot(self.jet["XRHO"][-1,:-1],
                          self.jet["DNCE"][-1,:], c="blue",
                      ls="-.", label=r"$D_e^{Nclass}$")
            #TCI - 1st species particle diffusivity
            ax[1][0].plot(self.jet["XRHO"][-1,:-1],
                          self.jet["DTCI"][-1,:], c="red",
                          label=r"$D_{i}^{TCI-1}$")
            #TCI - 2nd species particle diffusivity
            ax[1][0].plot(self.jet["XRHO"][-1,:-1],
                          self.jet["DTC2"][-1,:], c="cyan",
            label=r"$D_{part}^{TCI-2}$")
            ax[1][0].legend(fontsize=legend_fontsize, ncol=3,
                            columnspacing=0.6)
        else:
            ax[1][0].legend(loc="upper left")
   
        #The ETB is especified at 8cm width. Interpolate the rho
        #value so I know where the pedestal is. Since jetto.jsp
        #does not output the minor radius at Z=Zaxis, interpolate
        #from the major radius instead as an approximation
        rhotn_etb = np.interp(np.array([np.max(self.out['R_omp'][-1,:])-0.08]),
                             self.out['R_omp'][-1,:], self.out['rhot_norm'][-1,:])
        idx_etb = np.argmin((self.out["rhot_norm"][-1,:] - rhotn_etb)**2.0)

        #Te
        ax[0][1].plot(self.out["rhot_norm"][0,:], self.out["Te"][0,:]/1.e3,
                      ls="--", c="blue")
        ax[0][1].plot(self.out["rhot_norm"][-1,:], self.out["Te"][-1,:]/1.e3,
                      label="Te", c="blue")

        if "IMC1" in self.out.keys():   
            #NCLASS ion pinch velocity
            ax[2][0].plot(self.out["rhot_norm"][-1,:-1], self.out["v1_n"][-1,:],
                          c="orange", label=r"$v_{i}^{Nclass}$")
            ax[2][0].plot(self.out["rhot_norm"][-1,:-1], self.out["v2_n"][-1,:],
                          c="blue", label=r"$v_{i}^{Nclass}$")       
            #TCI main ion pinch velocity
            ax[2][0].plot(self.out["rhot_norm"][-1,:-1], self.out["v1_t"][-1,:],
                          c="red", label=r"$v_{i, 1}^{turb}$")
            #TCI 2nd spec. pinch velocity
            ax[2][0].plot(self.out["rhot_norm"][-1,:-1], self.out["v2_t"][-1,:],
                          c="cyan", label=r"$v_{i, 2}^{turb}$")
        else:
            try:
                #NCLASS ion pinch velocity
                ax[2][0].plot(self.out["rhot_norm"][-1,:], self.out["vn_H"][-1,:],
                              c="orange", label=r"$v_{i}^{Nclass}$")
                #TCI main ion pinch velocity
                ax[2][0].plot(self.out["rhot_norm"][-1,:], self.out["vt_H"][-1,:],
                              c="red", label=r"$v_{i, 1}^{turb}$")
                #Ti
                ax[0][1].plot(self.out["rhot_norm"][0,:], self.out["TiH"][0,:]/1.e3,
                              ls="--", c="orange")
                ax[0][1].plot(self.out["rhot_norm"][-1,:], self.out["TiH"][-1,:]/1.e3,
                              label="Ti", c="orange")
            except:
                pass
            try:
                #NCLASS ion pinch velocity
                ax[2][0].plot(self.out["rhot_norm"][-1,:-1], self.out["vn_D"][-1,:],
                              c="cyan", label=r"$v_{i}^{Nclass}$")
                ax[2][0].plot(self.out["rhot_norm"][-1,:-1], self.out["vt_D"][-1,:],
                              c="blue", label=r"$v_{i}^{Nclass}$")
                #Ti
                ax[0][1].plot(self.out["rhot_norm"][0,:], self.out["TiD"][0,:]/1.e3,
                              ls="--", c="orange")
                ax[0][1].plot(self.out["rhot_norm"][-1,:], self.out["TiD"][-1,:]/1.e3,
                              label="Ti", c="orange")         
            except:
                pass
            try:
                #NCLASS ion pinch velocity
                ax[2][0].plot(self.out["rhot_norm"][-1,:-1], self.out["vn_T"][-1,:],
                              c="brown", label=r"$v_{i}^{Nclass}$")
                ax[2][0].plot(self.out["rhot_norm"][-1,:-1], self.out["vt_T"][-1,:],
                              c="green", label=r"$v_{i}^{Nclass}$")
                #Ti
                ax[0][1].plot(self.out["rhot_norm"][0,:], self.out["TiT"][0,:]/1.e3,
                              ls="--", c="orange")
                ax[0][1].plot(self.out["rhot_norm"][-1,:], self.out["TiT"][-1,:]/1.e3,
                              label="Ti", c="orange")
            except:
                pass

        if "IMC1" in self.out.keys():
            #Qi, Qe [W]
            ax[0][2].plot(self.out["rhot_norm"][-1,:-1], self.out["Qi"][-1,:]/1.e6,
                          c="red", label=r"$Q_{i} \, [MW]$")
            ax[0][2].plot(self.out["rhot_norm"][-1,:-1], self.out["Qe"][-1,:]/1.e6,
                          c="blue", label=r"$Q_{e} \, [MW]$")

        #chi_e [m2/s]
        ax[1][1].plot(self.out["rhot_Xs"][-1,:], self.out["Xe"][-1,:],
                      label=r"$\chi_e$")
        #chi_i [m2/s]
        ax[1][1].plot(self.out["rhot_Xs"][-1,:], self.out["Xi"][-1,:],
                      label=r"$\chi_i$")

        #Add all the heat diffusivity components
        #From the JINTRAC Wiki, part written by Florian
        #JSP/XI is the sum of all XIj.
        #JSP/XI1: neoclassical Xi
        #JSP/XI2: Bohm part of Xi from Bohm/gyroBohm model
        #JSP/XI3: gyroBohm part of Xi from Bohm/gyroBohm model
        #JSP/XI4: Xi from NeoAlcator model
        #JSP/XI5: Xi from CDBM model
        #JSP/XI6: Xi from TCI
        #if verbose:
        #    ax[1][1].plot(self.jet["XRHO"][-1,:-1],
        #                  self.jet["XI1"][-1,:], c="orange",
        #                  ls="--", label=r"$\chi_{i, neo}$")
        #    ax[1][1].plot(self.jet["XRHO"][-1,:-1],
        #                  self.jet["XI3"][-1,:], c="orange",
        #                  ls="-.", label=r"$\chi_{i, GB}$")
        #    ax[1][1].plot(self.jet["XRHO"][-1,:-1],
        #                  self.jet["XI6"][-1,:], c="orange",
        #                  ls="-.", label=r"$\chi_{i, TCI}$")

        #q-profile
        axy21 = ax[2][1].twinx()
        axy21.plot(self.out["rhot_norm"][-1,:], self.out["qprof"][-1,:],
                   label=r"$q_{prof}$")

        #Total current density [A/m2]
        ax[2][1].plot(self.out["rhot_norm"][-1,:], self.out["jtor"][-1,:]/1.e3,
                      label=r"$j_{total}$", c="k")
        #Bootstrap current density [A/m2]
        ax[2][1].plot(self.out["rhot_norm"][-1,:], self.out["jpar_Bs"][-1,:]/1.e3,
                      label=r"$j_{BS}$", c="green")
        ##ECCD current density [A/m2]
        #ax[2][1].plot(self.jet["XRHO"][-1,:],
        #              self.jet["JZEC"][-1,:]/1.e3,
        #              label=r"$j_{ECCD}$", c="blue")
        ##NBI current density [A/m2]
        #ax[2][1].plot(self.jet["XRHO"][-1,:],
        #              self.jet["JZNB"][-1,:]/1.e3,
        #              label=r"$j_{NBI}$", c="orange")        
        ##ICRF current density [A/m2]
        #ax[2][1].plot(self.jet["XRHO"][-1,:],
        #              self.jet["JZRF"][-1,:]/1.e3,
        #              label=r"$j_{ICRF}$", c="red") 

        ax[0][0].legend(fontsize=legend_fontsize)
        axy.legend()
        ax[1][0].set_ylim(0.9*np.min(self.out["De_eff"][-1,:]),
                          1.1*np.max(self.out["De_eff"][-1,:]))
        ax[2][0].legend(fontsize=legend_fontsize)
        ax[0][1].legend(fontsize=legend_fontsize)
        ax[0][2].legend(fontsize=legend_fontsize)        
        ax[0][0].set_ylabel(r"$\mathrm{n \, [m^{-3}]}$")
        ax[1][0].set_ylabel(r"$\mathrm{D \, [m^2/s]}$")
        ax[2][0].set_ylabel(r"$\mathrm{v \, [m/s]}$")
        ax[0][1].set_ylabel(r"$\mathrm{T \, [keV]}$")
        ax[0][2].set_ylabel(r"$\mathrm{Q_{\mu} \, [MW]}$")        
        ax[1][1].set_ylabel(r"$\mathrm{\chi \, [m^2/s]}$")
        ax[2][1].set_ylabel(r"$\mathrm{j \, [kA/m^2]}$")
        axy21.set_ylabel(r"$\mathrm{q_{prof}}$")
        ax[1][1].legend(fontsize=legend_fontsize)
        ax[2][1].legend(fontsize=legend_fontsize)

        if savefig:
            plt.savefig("profiles.png")

        ##################################################
        #SSPX files - SANCO Impurity Profiles #[time, rho]
        #SSTX files - SANCO Impurity Profiles #[time, rho]
        ##################################################     
        if "IMC1" in self.out.keys():   
            #SSP1
            fig_time, ax_time =\
            plt.subplots(figsize=(6,4), nrows=1, ncols=1,
                        sharex=True)
            ax_time.set_xlabel("time [s]")
            ax_time.set_ylabel(r"$\mathrm{P_{rad} \,\, [MW]}$")
            ax_time.ticklabel_format(useOffset=False)

            fig_prad, ax_prad =\
            plt.subplots(figsize=(6,4), nrows=1, ncols=1,
                        sharex=True)
            plt.subplots_adjust(left=0.15, bottom=0.15)
            ax_prad.set_xlabel(r"$\rho$")
            ax_prad.set_ylabel(r"$\mathrm{P_{rad} \, [MW/m^3]}$")
            ax_prad.ticklabel_format(useOffset=False)

            try:
                #Find the number of charged states
                Ds = [x for x in self.names_ssp1 if "ZQ" in x]
                Ds = [int(x[-1]) for x in Ds]
                ns_ssp1 = np.max(Ds)
                fig, ax = plt.subplots(figsize=(ns_ssp1*3,3), nrows=1,
                                       ncols=ns_ssp1, sharex=True)
                fig.suptitle("SANCO output")
                #plt.subplots_adjust(wspace=0.6, left=0.05, right=0.95)
            
                for i in range(1, ns_ssp1+1):
                    labeln = r"$n_{" + str(i) + r"}^{st." + str(i) + "}$"
                    labelD = r"$D_{" + str(i) + r"}^{st." + str(i) + "}$"
                    labelDn = r"$D_{neo, " + str(i) + r"}^{st." + str(i) + "}$"                
                    labelv = r"$v_{" + str(i) + r"}^{st." + str(i) + "}$"
                    labelvn = r"$v_{neo, " + str(i) + r"}^{st." + str(i) + "}$"                

                    #t=0
                    ax[i-1].plot(self.dataset_ssp1["XRHO"][0,:],
                                 self.dataset_ssp1["N"+str(i)][0,:],
                                 c="k", ls="--", label=labeln)
                    #t=tend
                    ax[i-1].plot(self.dataset_ssp1["XRHO"][-1,:],
                                 self.dataset_ssp1["N"+str(i)][-1,:],
                                 c="k", label=labeln)
#                ax[i-1].set_title("Z=" +\
#                    str(self.dataset_ssp1["ZAVG"+str(i)][-1,:]))
                axy = ax[i-1].twinx()
                axy.plot(self.dataset_ssp1["XRHO"][-1,:],
                         self.dataset_ssp1["D"+str(i)][-1,:],
                         c="blue", label=labelD)
                axy.plot(self.dataset_ssp1["XRHO"][-1,:],
                         self.dataset_ssp1["DN"+str(i)][-1,:],
                         c="blue", ls="--", label=labelDn)
                axy.plot(self.dataset_ssp1["XRHO"][-1,:],
                         self.dataset_ssp1["V"+str(i)][-1,:],
                         c="red", ls="-", label=labelv)  
                axy.plot(self.dataset_ssp1["XRHO"][-1,:],
                         self.dataset_ssp1["VN"+str(i)][-1,:],
                         c="red", ls="--", label=labelvn)
                axy.set_ylabel(r"$D [m^2/s], \, v [m/s]$")
                axy.legend(fontsize=legend_fontsize, loc="lower left")

                ax_prad.plot(self.dataset_ssp1["XRHO"][0,:],
                            self.dataset_ssp1["PR"][0,:]/1.e6,
                            c="blue", ls='--')
                ax_prad.plot(self.dataset_ssp1["XRHO"][-1,:],
                            self.dataset_ssp1["PR"][-1,:]/1.e6,
                            c='blue', ls='-', label=r"SANCO imp. 1")
                ax_time.plot(self.dataset_sst1["TVEC1"],
                            self.dataset_sst1["PT"][-1,:]/1.e6,
                            marker="o", label=r"SANCO imp. 1")
                
                fig.tight_layout(w_pad=0.2, h_pad=0.25)
                if savefig:
                    plt.savefig("ssp1.png")
            
            except:
                print("No SSP1 SANCO file")

            #SSP2
            try:
                #Find the number of charged states
                Ds = [x for x in self.names_ssp2 if "ZQ" in x]
                Ds = [int(x[-1]) for x in Ds]
                ns_ssp2 = np.max(Ds)

                fig, ax = plt.subplots(figsize=(ns_ssp2*3,4), nrows=1,
                                       ncols=ns_ssp2, sharex=True)
                fig.suptitle("SANCO output")
                #plt.subplots_adjust(wspace=0.6, left=0.05, right=0.95)

                for i in range(1, ns_ssp2+1):
                    labeln = r"$n_{" + str(i) + r"}^{st." + str(i) + "}$"
                    labelD = r"$D_{" + str(i) + r"}^{st." + str(i) + "}$"
                    labelDn = r"$D_{neo, " + str(i) + r"}^{st." + str(i) + "}$"                
                    labelv = r"$v_{" + str(i) + r"}^{st." + str(i) + "}$"
                    labelvn = r"$v_{neo, " + str(i) + r"}^{st." + str(i) + "}$"                

                    #t=0
                    ax[i-1].plot(self.dataset_ssp2["XRHO"][0,:],
                                 self.dataset_ssp2["N"+str(i)][0,:],
                                 c="k", ls="--", label=labeln)
                    #t=tend
                    ax[i-1].plot(self.dataset_ssp2["XRHO"][-1,:],
                                 self.dataset_ssp2["N"+str(i)][-1,:],
                                 c="k", label=labeln)
                    axy = ax[i-1].twinx()
                    axy.plot(self.dataset_ssp2["XRHO"][-1,:],
                             self.dataset_ssp2["D"+str(i)][-1,:],
                             c="blue", label=labelD)
                    axy.plot(self.dataset_ssp2["XRHO"][-1,:],
                             self.dataset_ssp2["DN"+str(i)][-1,:],
                             c="blue", ls="--", label=labelDn)
                    axy.plot(self.dataset_ssp2["XRHO"][-1,:],
                             self.dataset_ssp2["V"+str(i)][-1,:],
                             c="red", ls="-", label=labelv)  
                    axy.plot(self.dataset_ssp2["XRHO"][-1,:],
                             self.dataset_ssp2["VN"+str(i)][-1,:],
                             c="red", ls="--", label=labelvn)
                    axy.set_ylabel(r"$D [m^2/s], \, v [m/s]$")
                    axy.legend(fontsize=legend_fontsize, loc="lower left")

                ax_prad.plot(self.dataset_ssp2["XRHO"][0,:],
                             self.dataset_ssp2["PR"][0,:]/1.e6,
                             c='orange', ls='--')
                ax_prad.plot(self.dataset_ssp2["XRHO"][-1,:],
                             self.dataset_ssp2["PR"][-1,:]/1.e6,
                             c='orange', ls='-', label=r"SANCO imp. 2")
                ax_time.plot(self.dataset_sst2["TVEC1"],
                             self.dataset_sst2["PT"][-1,:]/1.e6,
                             marker="o", label=r"SANCO imp. 2")
                
                fig.tight_layout(w_pad=0.2, h_pad=0.25)
                if savefig:
                    plt.savefig("ssp2.png")
            except:
                print("No SSP2 SANCO file")

            #SSP3
            try:
                #Find the number of charged states
                Ds = [x for x in self.names_ssp3 if "ZQ" in x]
                Ds = [int(x[-1]) for x in Ds]
                ns_ssp3 = np.max(Ds)

                fig, ax = plt.subplots(figsize=(ns_ssp3*3,4), nrows=1,
                                       ncols=ns_ssp3, sharex=True)
                fig.suptitle("SANCO output")
                plt.subplots_adjust(wspace=0.6, left=0.05, right=0.95)
            
                for i in range(1, ns_ssp3+1):
                    labeln = r"$n_{" + str(i) + r"}^{st." + str(i) + "}$"
                    labelD = r"$D_{" + str(i) + r"}^{st." + str(i) + "}$"
                    labelDn = r"$D_{neo, " + str(i) + r"}^{st." + str(i) + "}$"                
                    labelv = r"$v_{" + str(i) + r"}^{st." + str(i) + "}$"
                    labelvn = r"$v_{neo, " + str(i) + r"}^{st." + str(i) + "}$"                

                    #t=0
                    ax[i-1].plot(self.dataset_ssp3["XRHO"][0,:],
                                 self.dataset_ssp3["N"+str(i)][0,:],
                                 c="k", ls="--", label=labeln)
                    #t=tend
                    ax[i-1].plot(self.dataset_ssp3["XRHO"][-1,:],
                                 self.dataset_ssp3["N"+str(i)][-1,:],
                                 c="k", label=labeln)
                    axy = ax[i-1].twinx()
                    axy.plot(self.dataset_ssp3["XRHO"][-1,:],
                             self.dataset_ssp3["D"+str(i)][-1,:],
                             c="blue", label=labelD)
                    axy.plot(self.dataset_ssp3["XRHO"][-1,:],
                             self.dataset_ssp3["DN"+str(i)][-1,:],
                             c="blue", ls="--", label=labelDn)
                    axy.plot(self.dataset_ssp3["XRHO"][-1,:],
                             self.dataset_ssp3["V"+str(i)][-1,:],
                             c="red", ls="-", label=labelv)  
                    axy.plot(self.dataset_ssp3["XRHO"][-1,:],
                            self.dataset_ssp3["VN"+str(i)][-1,:],
                            c="red", ls="--", label=labelvn)
                    axy.set_ylabel(r"$D [m^2/s], \, v [m/s]$")
                    axy.legend(fontsize=legend_fontsize, loc="lower left")

                ax_prad.plot(self.dataset_ssp3["XRHO"][0,:],
                            self.dataset_ssp3["PR"][0,:]/1.e6,
                            c='green', ls='--')
                ax_prad.plot(self.dataset_ssp3["XRHO"][-1,:],
                            self.dataset_ssp3["PR"][-1,:]/1.e6,
                            c='green', ls='-', label=r"SANCO imp. 3")
                ax_time.plot(self.dataset_sst3["TVEC1"],
                             self.dataset_sst3["PT"][-1,:]/1.e6,
                             marker="o", label=r"SANCO imp. 3")

                fig.tight_layout(w_pad=0.2, h_pad=0.25)
                if savefig:
                    plt.savefig("ssp3.png")
            except:
                self.ssp3file = False
                print("No SSP3 SANCO file")

            #Legends for the impurity plots
            fig_prad.tight_layout()
            ax_prad.legend(fontsize=legend_fontsize)
            fig_time.tight_layout()
            ax_time.legend(fontsize=legend_fontsize)

        ###################################
        #Mag. Equilibrium and wall elements
        ###################################
        fig, ax = plt.subplots(figsize=(4,6), nrows=1, ncols=1)
        fig.tight_layout()
        plt.subplots_adjust(top=0.95, bottom=0.13,
                                left=0.1, right=0.99)
        plt.rcParams.update({'font.size': 14})
        ax.set_aspect("equal")
        ax.set_xlabel("R [m]")
        ax.set_ylabel("Z [m]")

        if self.jse:
            ax.plot(self.out["Rbnd"].T, self.out["Zbnd"].T, c="k")

        #PLot some flux surfaces
        ax.contour(self.out["Rgrid"], self.out["Zgrid"],
                   self.out["Psi_n"], np.array([0.1, 0.3, 0.5, 0.7, 0.9]),
                   colors="k")

        ax.contour(self.out["Rgrid"], self.out["Zgrid"],
                   self.out["Psi_n"], np.array([0]),
                   colors="k", marker="x")

        #Plot EDGE2D grid
        if self.tranfile:
            npts = self.out["npts_mesh"]
            #Rings
            ax.plot(self.out["Rmesh2D_rings"].T, -1.*self.out["Zmesh2D_rings"].T,
                    c='blue', alpha=0.8, lw=0.3)
            #Rows
            ax.plot(self.out["Rmesh2D_rows"].T, -1.*self.out["Zmesh2D_rows"].T,
                    c='k', alpha=0.8, lw=0.3)

        #Plot wall elements
        ax.plot(self.out["Rvessel"], -1.*self.out["Zvessel"], lw="2", c="k")
        ax.plot(self.out["Rbuffle"], -1.*self.out["Zbuffle"], lw="2", c="k")
        ax.set_xlim(np.min(self.out["Rvessel"]-0.1),
                    np.max(self.out["Rvessel"][:npts]+1.4))
        ax.set_ylim(np.min(self.out["Zvessel"][:npts]-0.05),
                    np.max(self.out["Zvessel"][:npts]+0.2))

        #Plor EIRENE grid
        ax.triplot(self.out["Rmesh_eirene"], self.out["Zmesh_eirene"],
                   self.out["Triang_idxs"], c="green", lw="0.3")

        ax.plot(np.array([]), np.array([]), c="blue", label="EDGE2D grid")
        ax.plot(np.array([]), np.array([]), c="green", label="EIRENE grid")
        ax.legend(loc="lower right")

        #################################
        #Current sources (jetto.jst file)
        #################################
        fig, ax = plt.subplots(figsize=(10,4), nrows=1, ncols=2)
        plt.subplots_adjust(wspace=0.4, left=0.1, right=0.95,
                            bottom=0.12)
        axy = ax[0].twinx()
        axy.plot(self.out["rhot_norm"][-1,:], self.out["qprof"][-1,:],
                 label=r"$q_{prof}$", c="k")
        axy.set_ylabel("$q_{prof}$")
        #Bootstrap current density [A/m2]
        ax[0].plot(self.out["rhot_norm"][-1,:],
                   self.out["jpar_Bs"][-1,:]/1.e3,
                   label=r"$j_{BS}$")       
        ax[0].set_ylabel(r"$\mathrm{j \, [kA/m^2]}$")

        #Total BS current as afo time
        ax[1].plot(self.out["time_derived"], self.out["jpar_Bstot"].T/1.e6,
                   label=r"$\mathrm{I_{BS}}$")
        #EC current as afo time
        ax[1].plot(self.out["time_derived"], self.out["jtor_ectot"].T/1.e6,
                   c="blue", label=r"$\mathrm{I_{EC}}$")
        #NBI current drive
        ax[1].plot(self.out["time_derived"], self.out["jtor_nbitot"].T/1.e6,
                   c="orange", label=r"$\mathrm{I_{NBI}}$")
        #IRCF current drive
        ax[1].plot(self.out["time_derived"], self.out["jtor_ictot"].T/1.e6,
                   c="red", label=r"$\mathrm{I_{ICRF}}$")
        ##LH current drive
        #ax[1].plot(self.jet["TVEC1"], self.jet["CULH"].T/1.e6,
        #           c="green", label=r"$\mathrm{I_{LH}}$")
        ##Electron Berstein wave
        #ax[1].plot(self.jet["TVEC1"], self.jet["CUEB"].T/1.e6,
        #           c="cyan", label=r"$\mathrm{I_{EBW}}$")
        ax[1].set_xlabel("time [s]")
        ax[1].set_ylabel("I [MA]")
        ax[1].legend(fontsize=legend_fontsize)
        fig.tight_layout()

        ################################
        #Heating Source Profiles [MW/m3]
        ################################
        fig, ax = plt.subplots(nrows=1, ncols=1)
        plt.subplots_adjust(left=0.12, right=0.95)
        #ax.plot(self.jet["XRHO"][-1,:], self.jet["QRFE"][-1,:]/1.e6,
        #        lw=2, label=r"$P^e_{ICRH}$")
        #ax.plot(self.jet["XRHO"][-1,:], self.jet["QRFI"][-1,:]/1.e6,
        #        lw=2, label=r"$P^i_{ICRH}$")
        ax.plot(self.out["rhot_norm"][-1,:], self.out["Pecrh"][-1,:]/1.e6,
                lw=2, label=r"$Q_{ECRH}$")
        ax.plot(self.out["rhot_norm"][-1,:], self.out["Pnbi_i"][-1,:]/1.e6,
                lw=2, label=r"$Q_{NBI}^{i}$")
        ax.plot(self.out["rhot_norm"][-1,:], self.out["Pnbi_e"][-1,:]/1.e6,
                lw=2, label=r"$Q_{NBI}^{e}$")
        #ax.plot(self.jet["XRHO"][-1,:], self.jet["QALI"][-1,:]/1.e6,
        #        lw=2, c="red", label=r"$P^{i}_{\alpha}$")
        #ax.plot(self.jet["XRHO"][-1,:], self.jet["QALE"][-1,:]/1.e6,
        #        lw=2, c="blue", label=r"$P^{e}_{\alpha}$")        
        ax.set_xlabel(r"$\mathrm{\rho}$")
        ax.set_ylabel(r"$\mathrm{P_{aux} \, [MW/m^3]}$")
        ax.legend(fontsize=legend_fontsize)
        fig.tight_layout()

        #################################
        #Time traces
        #  - Kinetic profiles (jetto.jsp)
        #################################
        fig, ax = plt.subplots(figsize=(10,8), nrows=4, ncols=3,
                               sharex=True)
        plt.subplots_adjust(wspace=0.4, hspace=0.32,
                            left=0.1, right=0.95)
        
        ax[0][0].plot(np.squeeze(self.out["time"]),
                      self.out["Te"][:,0]/1.e3,
                      c="blue", marker="o",
                      label=r"$\mathrm{T_{e,0} \, [keV]}$")

        if "IMC1" in self.out.keys():
            ax[0][0].plot(np.squeeze(self.out["time"]),
                        self.out["Ti"][:,0]/1.e3,
                        c="red", marker="o",
                        label=r"$\mathrm{T_{i,0} \, [keV]}$")
        else:
            try:
                ax[0][0].plot(np.squeeze(self.out["time"]),
                            self.out["TiH"][:,0]/1.e3,
                            c="red", marker="o",
                            label=r"$\mathrm{T_{i,0} \, [keV]}$")
            except:
                pass
            try:
                ax[0][0].plot(np.squeeze(self.out["time"]),
                            self.out["TiD"][:,0]/1.e3,
                            c="red", marker="o",
                            label=r"$\mathrm{T_{i,0} \, [keV]}$")
            except:
                pass
            try:
                ax[0][0].plot(np.squeeze(self.out["time"]),
                            self.out["TiT"][:,0]/1.e3,
                            c="red", marker="o",
                            label=r"$\mathrm{T_{i,0} \, [keV]}$")
            except:
                pass

        ax[0][0].ticklabel_format(useOffset=False)
        ax[0][0].legend(fontsize=legend_fontsize)
            
        #Maximum difference between adjacent points
        #in the electron density profile
        ne_diff = np.max(self.out["ne"][:,1:]-\
                         self.out["ne"][:,:-1], axis=1)
        ax[0][1].plot(np.squeeze(self.out["time"]),
                      self.out["ne"][:,0],
                      c="blue", marker="o",
                      label=r"$\mathrm{n_{e,0} \, [keV]}$")
        ax[0][1].plot(np.squeeze(self.out["time"]),
                      self.out["niD"][:,0],
                      c="red", marker="o",
                      label=r"$\mathrm{n_{D,0} \, [keV]}$")
        ax[0][1].plot(np.squeeze(self.out["time"]),
                      self.out["niT"][:,0],
                      c="orange", marker="o",
                      label=r"$\mathrm{n_{T,0} \, [keV]}$")
        label=r"$\mathrm{max(n_{e, i+1} - n_{e, i})"+\
              r"\, [m^{-3}]}$"
        ax[0][1].plot(np.squeeze(self.out["time"]),
                      ne_diff, c="k", marker="o", label=label)        
        ax[0][1].ticklabel_format(useOffset=False)
        ax[0][1].legend(fontsize=legend_fontsize)

        #q-profile
        ax[0][2].plot(self.out["time"], self.out["qprof"][:,0],
                      c='k', label=r"$q_0$")
        ax[0][2].legend(fontsize=legend_fontsize)

        ##  - Powers (jetto.jst)
        ax[1][0].plot(self.out["time_derived"], self.out["Plht"].T/1.e6,
                      marker="o", ls="--", c="cyan", label=r"$P_{LH}$")
        #ax[1][0].plot(self.jet["TVEC1"], self.jet["PTOT"].T/1.e6,
        #              marker="o", c="k", label=r"$P_{tot}$")
        #Pnet includes dW/dt. As the thermal energy content
        #stabilizes, Pnet -> Ptot.
        #ax[1][0].plot(self.jet["TVEC1"], self.jet["PNET"].T/1.e6,
        #              marker ="o", c="red",
        #              label=r"$P_{net} (+dW/dt)$")
        ax[1][0].plot(self.out["time_derived"], self.out["Pec_tot"]/1.e6,
                      marker ="o", c="blue", label=r"$P_{ecrh}$")
        #ax[1][0].plot(self.jet["TVEC1"], self.jet["PRF"].T/1.e6,
        #              marker ="o", c="brown", label=r"$P_{ICRH}$")
        ax[1][0].plot(self.out["time_derived"], self.out["Pnbi_tot"].T/1.e6,
                      marker ="o", c="green", label=r"$P_{NBI}$")
        ax[1][0].plot(self.out["time_derived"],
                      np.abs(self.out["Prad_tot"].T)/1.e6,
                      marker ="o", c="k", ls="--", label=r"$|P_{rad}|$")
        ax[1][0].plot(self.out["time_derived"], self.out["Palf"]/1.e6,
                      marker ="o", c="magenta",
                      label=r"$P_{\alpha}$")
        ax[1][0].plot(self.out["time_derived"], self.out["Poh_tot"]/1.e6,
                      marker ="o", c="0.5", label=r"$P_{\Omega}$")
        #ax[1][0].set_ylim(0., 1.2*np.max(self.jet["PNET"].T/1.e6))
        ax[1][0].ticklabel_format(useOffset=False)
        ax[1][0].legend(ncol=3, fontsize=legend_fontsize)

        #  - Heat fluxes (jetto.jsp)
#        try:
#            ax[2][0].plot(np.squeeze(self.jet["TIME"]),
#                          np.max(self.jet["PIFL"], axis=1).T/1.e6,
#                          marker="o", c="red",
#                          label=r"$Q_{i, max}$")
#            ax[2][0].plot(np.squeeze(self.jet["TIME"]),
#                          np.max(self.jet["PEFL"], axis=1).T/1.e6,
#                          marker="o", c="blue",
#                          label=r"$Q_{e, max}$")
#            ax[2][0].set_ylabel(r"$\mathrm{Q_{\mu} \, [MW]}$")
#            ax[2][0].ticklabel_format(useOffset=False)
#            ax[2][0].legend()
#        except:
#            print("Cannot use .jsp file in <<time>> mode")

        #Edge energy fluxes (jetto.jst)
        #ax[2][0].plot(np.squeeze(self.jet["TVEC1"]),
        #              np.squeeze(self.jet["PFIO"]).T/1.e6,
        #              marker="o", c="red",
        #              label=r"$Q_{i,B}$")
        #ax[2][0].plot(np.squeeze(self.jet["TVEC1"]),
        #              np.squeeze(self.jet["PFEL"]).T/1.e6,
        #              marker="o", c="blue",
        #              label=r"$Q_{e,B}$")
        #ax[2][0].set_ylabel(r"$\mathrm{Q_{\mu, B} \, [MW]}$")
        #ax[2][0].ticklabel_format(useOffset=False)
        #ax[2][0].legend(fontsize=legend_fontsize)

        #  - Particle sources (jetto.jst)
        #ax[1][1].plot(np.squeeze(self.jet["TVEC1"]),
        #              np.squeeze(self.jet["SIN1"]),
        #              c="blue", marker ="o",
        #              label=r"$S_{puff, spec. 1}$")
        #ax[1][1].plot(np.squeeze(self.jet["TVEC1"]),
        #              np.squeeze(self.jet["SIN2"]),
        #              c="blue", ls="--",
        #              marker ="o", label=r"$S_{puff, spec. 2}$")
        #ax[1][1].plot(np.squeeze(self.jet["TVEC1"]),
        #              np.squeeze(self.jet["SPEL"]), c="k",
        #              marker ="o", label=r"$S_{pellet}$")
        #ax[1][1].ticklabel_format(useOffset=False)
        #ax[1][1].set_ylabel(r"$\mathrm{S  \, [part/s]}$")
        #ax[1][1].legend(fontsize=legend_fontsize)

        #Capital fusion Q - Amplification factor
        ax[2][1].plot(np.squeeze(self.out["time_derived"]),
                      np.squeeze(self.out["Qfus"]),
                      c="blue", marker ="o",
                      label=r"$Q_{fus}$")        
        ax[2][1].ticklabel_format(useOffset=False)
        ax[2][1].legend(fontsize=legend_fontsize)

        ##Impurity concentrations
        #ax[3][0].plot(np.squeeze(self.jet["TVEC1"]),
        #              np.squeeze(self.jet["IMC1"]),
        #              c="blue", marker ="o",
        #              label=r"$c_{imp, 1}$")
        #ax[3][0].plot(np.squeeze(self.jet["TVEC1"]),
        #              np.squeeze(self.jet["IMC2"]),
        #              c="red", marker ="o",
        #              label=r"$c_{imp, 2}$")
        #if self.ssp3file:
        #    ax[3][0].plot(np.squeeze(self.jet["TVEC1"]),
        #                  np.squeeze(self.jet["IMC3"]),
        #                  c="red", marker ="o",
        #                  label=r"$c_{imp, 3}$")        
        #ax[3][0].set_ylabel(r"$\left< n_{imp, X} \right> /$"+\
        #                    r"$\left< n_e \right>$ [%]")
        #ax[3][0].ticklabel_format(useOffset=False)
        #ax[3][0].legend(fontsize=legend_fontsize)        

        #Alpha - Normalized pressured at the ETB
        ax[3][1].plot(self.out["time_derived"], self.out["alpha_max_jetto_edge"],
                      c="blue", marker ="o", label=r"$max(\alpha)$")
        ax[3][1].set_ylabel(r"$\alpha$(ETB)")
        ax[3][1].ticklabel_format(useOffset=False)
        ax[3][1].legend(fontsize=legend_fontsize)
        
        ##################################
        #EDGE2D Output from TRAN fiels/IDS
        ##################################
        if self.tranfile:
            fig, ax = plt.subplots(figsize=(6,6), nrows=1, ncols=1,
                                  sharex=True)
            plt.subplots_adjust(wspace=0.5, top=0.91, bottom=0.05,
                                left=0.1, right=0.95)
            ax.plot(self.out['x_div_it'], self.out['Te_it'],
                    c='blue', label=r'$Te_{IT}$')
            ax.plot(self.out['x_div_ot'], self.out['Te_ot'],
                    c='red', label=r'$Te_{OT}$')
            ax.legend()

        ##################################
        #Time traces of control parameters
        ##################################
        if "IMC1" in self.out.keys():
            fig, ax = plt.subplots(nrows=1, ncols=1)
            ax.scatter(self.out["time_derived"], self.out["dtmax"],
                       c="k", s=20, label=r"$dt_{max}$")
            ax.legend()
            plt.show()

        return