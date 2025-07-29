from __future__ import annotations
from typing import Optional, Sequence

from sys import stderr, exit
from bisect import bisect_left
from argparse import ArgumentParser, Namespace
from pathlib import Path

import numpy as np
from scipy import interpolate, optimize, special, integrate

import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox

from ..results import JettoResults, JsetEcrhParams, GrayFortFile

class AnalysisError(Exception):
    pass


def summarise_ecrh_params(paramlist: Sequence[JsetEcrhParams]) -> None:
    for params in paramlist:
        print(
            f'ECRH beam # {params.index}, {params.beam}, '
            f'pol. = {params.angpec:5.2f}deg, '
            f'tor. = {params.angtec:5.2f}deg, '
            f'pow. = {params.powec:5.2f}W'
        )


def plot_analysis_1(results: JettoResults, t1: float, *, figsize=(8, 8)) -> plt.Figure:
    #jsp, jst, eq
    jjset = results.load_jset()
    jst = results.load_jst()
    jsp = results.load_jsp()
    eq = results.load_eqdsk(t1)
    grc = results.load_gray_central_ray_coord()[0]

    #jsp, jst data
    idt = np.argmin(np.abs(jst['TVEC1'].flatten() - t1))
    idp = np.argmin(np.abs(jsp['TIME'].flatten() - t1))

    NEp = jsp['NE'][idp]
    TEp = jsp['TE'][idp]
    VOLp = jsp['VOL'][idp]
    XRHOp = jsp['XRHO'][idp]
    XPSIp = jsp['XPSI'][idp]
    Qt = jsp['Q'][idp]
    JZt = jsp['JZ'][idp]
    JZECp = jsp['JZEC'][idp]

    #read which beam(s) were used and at what launching angles
    print('jset: the following ECRH settings were used in: {:s}, at jst={:8.3f}s, jsp={:8.3f}s,'.format(
        str(results.root),
        jst['TVEC1'].flatten()[idt],
        jsp['TIME'].flatten()[idp],
    ))

    summarise_ecrh_params(JsetEcrhParams.from_jset(jjset))

    jstE={}
    print('jst: the following ECRH settings were used at {:5.2f}s in: '.format(jst['TVEC1'].T[0,idt]))
    print(str(results.root))
    for key,value in jst.items():
        if key[:2]=='EA' or key[:2]=='EB' or key[:2]=='EP':
             print(key,value[0,idt])
             jstE[key]=value[0,idt]


    fig, ax = plt.subplots(3, 2, sharex=True, figsize=figsize)
    fig.suptitle('{:s}, t1={:5.3f}s, tend={:5.3f}s'.format(str(results.root),jsp['TIME'][idp][0,0],jsp['TIME'][-1][0,0]))

    ax1=ax[0,0]
    ax1.plot(XRHOp, np.sqrt(XPSIp), label='jsp')
    ax1.plot(eq.rhot_n, np.sqrt(eq.psip_n), 'k--', label='eqdsk')
    ax1.plot(np.sqrt(grc.data['rhot']),np.sqrt(grc.data['psin']),'r.', label='grc')
    ax1.set_ylabel('rhop')
    ax1.legend()

    ax2=ax[1,0]
    ax2.plot(XRHOp, Qt, label='jsp')
    ax2.plot(eq.rhot_n, eq.qpsi, 'k--', label='eqdsk')
    ax2.set_ylabel('Safety factor, Q')
    ax2.legend()

    pref = MetricPrefix(np.max(JZt))
    ax3=ax[2,0]
    ax3.plot(XRHOp, pref.adjust(JZt), label='jsp/JZ')
    ax3.plot(XRHOp, pref.adjust(JZECp),'r', label='jsp/JZEC')
    ax3.set_xlabel('rhot')
    ax3.set_ylabel(f'Current density (${pref.symbol}A/m^2$)')
    ax3.legend()

    ax4=ax[0,1]
    ax4.plot(XRHOp, NEp, label='jsp/NE')
    ax4.plot(np.sqrt(grc.data['rhot']),grc.data['ne']*1.e19,'r.', label='grc')
    ax4.set_xlabel('rhot')
    ax4.set_ylabel('NE 1/m^3')
    ax4.legend()

    ax5=ax[1,1]
    ax5.plot(XRHOp, TEp, label='jsp/TE')
    ax5.plot(np.sqrt(grc.data['rhot']),grc.data['Te']*1.e3,'r.', label='grc')
    ax5.set_xlabel('rhot')
    ax5.set_ylabel('TE eV')
    ax5.legend()

    ax6=ax[2,1]

    fig.tight_layout()

    return fig


def plot_analysis_2( results: JettoResults, t1: float, beamname: Optional[str] = None, *, figsize=(7, 8)) -> plt.Figure:
    #jsp, jst, eq
    jjset = results.load_jset()
    jsp = results.load_jsp()
    jst = results.load_jst()
    eq = results.load_eqdsk(t1)

    idp = np.argmin(np.abs(jsp['TIME'] - t1))
    JZECp = jsp['JZEC'][idp]
    # described as "Den., el. from therm. p."
    NEp = jsp['NE'][idp]
    QECEp = jsp['QECE'][idp]
    VOLp = jsp['VOL'][idp]
    XRHOp = jsp['XRHO'][idp]
    XPSIp = jsp['XPSI'][idp]
    RIp = jsp['RI'][idp]

    idt = np.argmin(np.abs(jst['TVEC1'] - t1))
    PECEt = jst['PECE'][0, idt]
    CUECt = jst['CUEC'][0, idt]

    #read which beam(s) were used and at what launching angles
    print('jset: the following ECRH settings were used in: {:s}, at jst={:8.3f}s, jsp={:8.3f}s,'.format(
        str(results.root),
        jst['TVEC1'].flatten()[idt],
        jsp['TIME'].flatten()[idp],
    ))

    ecrh_params = JsetEcrhParams.from_jset(jjset)
    summarise_ecrh_params(ecrh_params)

    jsetselbeams=[params.beam for params in ecrh_params]

    #graybeam input
    graybeams = results.load_graybeams()
    #graybeam central ray output
    all_gray_ray_coords = results.load_gray_central_ray_coord()
    #graybeam individual beam jz, pd
    all_gray_ray_jz_pd=GrayFortFile.load(str(results.root)+'/fort.648')
    print(all_gray_ray_jz_pd[0].data)

    # nothing selected by the user, plot all beams, please don't change this
    if not beamname:
        beamname = jsetselbeams
    if not type(beamname) is list:
        beamname=[beamname]

    allbeamnames = [b.beamname for b in graybeams]
    gray_rays_coords = []
    gray_rays_jz_pds = []
    for bn in beamname:
       ixgraybeam=allbeamnames.index(bn)
       ixgraybeamoutput=jsetselbeams.index(bn)
       gray_rays_coords.append(all_gray_ray_coords[ixgraybeamoutput])
       gray_rays_jz_pds.append(all_gray_ray_jz_pd[ixgraybeamoutput])
       freq = graybeams[ixgraybeam].fghz * 1e9 #only last beam freq. is used. cannot plot amny beams freq.

    #print
    for ic, graybeam in zip(range(len(graybeams)),graybeams):
        print('gray beam # {:d}, {:s}, f = {:5.2f}GHz, launch R0, Z0 = {:5.2f}m, {:5.2f}m'.format(ic+1,graybeam.beamname,graybeam.fghz,graybeam.grid[0].x0/1000.,graybeam.grid[0].z0/1000.))
    
    for gray_ray_coords in gray_rays_coords:
        #print
        print('gray beam traced launch R0, Z0 = {:5.2f}m, {:5.2f}m'.format(gray_ray_coords.data['R'][0],gray_ray_coords.data['z'][0]))
        ixmaxdIds=np.argmax(np.abs(gray_ray_coords.data['dIds']))
        print('gray beam max. abs. at sst={:8.5f}m at R, Z = {:5.2f}m, {:5.2f}m; psin = {:5.3f}, rhot = {:5.3f}'.format(gray_ray_coords.data['sst'][ixmaxdIds],gray_ray_coords.data['R'][ixmaxdIds],gray_ray_coords.data['z'][ixmaxdIds],gray_ray_coords.data['psin'][ixmaxdIds],gray_ray_coords.data['rhot'][ixmaxdIds]))
        print('gray beam at max. abs. B field, Btot={:5.2f}T, B=({:5.2f},{:5.2f},{:5.2f})T'.format(gray_ray_coords.data['Btot'][ixmaxdIds],gray_ray_coords.data['Bx'][ixmaxdIds],gray_ray_coords.data['By'][ixmaxdIds],gray_ray_coords.data['Bx.1'][ixmaxdIds]))
        print('gray beam at max. abs. ne={:5.2e}cm-3, Te={:5.2f}eV'.format(gray_ray_coords.data['ne'][ixmaxdIds],gray_ray_coords.data['Te'][ixmaxdIds]))
        print('gray beam at max. abs. Nperp={:5.2f}, Nparl={:5.2f}, N=({:5.2f},{:5.2f},{:5.2f})'.format(gray_ray_coords.data['Nperp'][ixmaxdIds],gray_ray_coords.data['Npl'][ixmaxdIds],gray_ray_coords.data['Nx'][ixmaxdIds],gray_ray_coords.data['Ny'][ixmaxdIds],gray_ray_coords.data['Nz'][ixmaxdIds]))

    #rhot on 2D R,Z mesh
    rhotf = np.interp(eq.psirz_n.flatten(), eq.psip_n, eq.rhot_n)
    rhotr2z2d = np.reshape(rhotf, eq.psirz_n.shape)

    #res, CO, etc on m.a.
    ixZgridzmag = np.argmin(np.abs(eq.Zgrid - eq.zmag))
    psip_nmag = eq.psirz_n[:, ixZgridzmag]
    NEmag = np.interp(psip_nmag, XPSIp, NEp)
    Btotmag = np.sqrt(eq.B_tor[ixZgridzmag,:]**2+eq.B_pol[ixZgridzmag,:]**2)
    ocemag = 1.76e11 * Btotmag  # in [rad/s], Btotmag[T]
    fcemag = ocemag / 2.0 / np.pi
    R1stharmmag = np.interp(1.0, freq / fcemag, eq.Rgrid)
    R2ndharmmag = np.interp(2.0, freq / fcemag, eq.Rgrid)
    opemag = 56.4 * np.sqrt(NEmag)  # in [rad/s], NE in [m^-3]

    # Cut off, X-mode, cold plasma approx, omCO[rad/s], cold plasma, Stix R=0
    oCOXCP = (np.sqrt(ocemag**2 + 4.0 * opemag**2) + ocemag) / 2.0
    fCOXCP = oCOXCP/2.0/np.pi

    # Cut off, O-mode, cold plasma approx, omCO[rad/s], cold plasma, Stix R=0
    oCOOCP = opemag
    fCOOCP = oCOOCP/2.0/np.pi

    rb_in = eq.rbdry < eq.rmag
    rb_outZ0 = eq.rbdry[~rb_in][np.argmin(np.abs(eq.zbdry[~rb_in]))]
    rb_inZ0 = eq.rbdry[rb_in][np.argmin(np.abs(eq.zbdry[rb_in]))]

    fig = plt.figure(figsize=figsize)
    fig.suptitle('{:s}, t1={:5.3f}s, tend={:5.3f}s'.format(str(results.root),jsp['TIME'][idp][0,0],jsp['TIME'][-1][0,0]))
    gs = fig.add_gridspec(7, 4)

    ax1 = fig.add_subplot(gs[0:5, :2])
    ax1.axvline(R1stharmmag, c='c', lw=1)
    ax1.axvline(R2ndharmmag, c='c', lw=1)
    ax1.plot(eq.rbdry, eq.zbdry, 'k')
    ax1.plot(eq.xlim, eq.ylim, c='C0')

    ax1.contour(
        eq.Rgrid, eq.Zgrid, rhotr2z2d, np.linspace(0, 1, 11),
        colors='k', linestyles='--',
    )
    ax1.plot(eq.rmag, eq.zmag, 'C0+')
    for gray_ray_coords in gray_rays_coords:
        ax1.scatter(
            gray_ray_coords.data['R'], gray_ray_coords.data['z'],
            c=1-gray_ray_coords.data['Pt'],
            s=16, vmin=0, vmax=1,
            )

    ax1.plot(eq.rmag-0.5, eq.zmag,color='k',marker='$\otimes$',markersize=12) #/phi
    ax1.text(eq.rmag-0.5, eq.zmag-0.2,'$\phi$')
    ax1.plot(eq.rmag, eq.zmag,color='k',marker='$\otimes$',markersize=12) #/Ip, Bt
    ax1.text(eq.rmag, eq.zmag-0.2,'$Bt, Ip$')
    ax1.set_xlim([np.min(eq.rbdry), np.max(eq.rbdry)])
    ax1.set_ylim([np.min(eq.zbdry), np.max(eq.zbdry)])
    ax1.set_aspect(aspect='equal')
    ax1.set_xlabel('R'); ax1.set_ylabel('Z')
    ax1.grid()
    ax1pos=ax1.get_position()

    ax2 = fig.add_subplot(gs[5:7, :2])
    ax2pos=ax2.get_position()
    ax2.set_position(Bbox([[ax1pos.x0,ax2pos.y0],[ax1pos.xmax,ax2pos.ymax]]))
    ax2.axhline(freq, color='k', lw=1)
    ax2.plot(eq.Rgrid, fcemag, 'C0')
    ax2.plot(eq.Rgrid, 2*fcemag, 'C0')
    ax2.plot(eq.Rgrid, 3*fcemag, 'C0')
    ax2.plot(eq.Rgrid, fCOXCP, 'C1')
    ax2.plot(eq.Rgrid, fCOOCP, 'C1')
    ax2.set_xlim(ax1.get_xlim())
    ax2.set_ylim([0, 2e11])


    ax3 = fig.add_subplot(gs[0:3, 2:])
    ax3.add_patch(plt.Circle((0, 0), rb_outZ0, color='k', fill=False))
    ax3.add_patch(plt.Circle((0, 0), rb_inZ0, color='k', fill=False))
    ax3.add_patch(plt.Circle((0, 0), eq.rmag / 100, color='b', fill=False))
    #ax3.plot(0.0, 0.0,color='k',marker=r'$\rightarrow$',markersize=12)
    #ax3.text(0.2,0.0,'R')
    ax3.plot(0.0, 0.0,color='k',marker='$\otimes$',markersize=12)
    ax3.text(0.0,-0.2,'Z')
    ax3.plot(eq.rmag-0.5, 0.0,color='k',marker=r'$\uparrow$',markersize=12)
    ax3.text(eq.rmag-0.5,-0.2,'$\phi$')
    ax3.plot(eq.rmag, 0.0,color='k',marker=r'$\uparrow$',markersize=12)
    ax3.text(eq.rmag+0.2,0.0,'$Bt, Ip$')
    ax3.plot([0, 0], [-4, 4], 'k:')
    ax3.plot([-4, 4], [0, 0], 'k:')
    ax3.set_xlim([-0.1, np.max(eq.rbdry)])
    ax3.set_ylim([-np.max(eq.rbdry)-0.05, np.max(eq.rbdry)+0.05])
    for gray_ray_coords in gray_rays_coords:
        phi_rad = gray_ray_coords.data['phi'] * (np.pi / 180)
        ax3.scatter(
            gray_ray_coords.data['R'] * np.cos(phi_rad),
            gray_ray_coords.data['R'] * np.sin(phi_rad),
            c=1-gray_ray_coords.data['Pt'], s=8, vmin=0, vmax=1,
            )
    ax3.set_aspect(aspect='equal')

    # power
    pref = MetricPrefix(np.max(QECEp))
    d_volume = np.gradient(VOLp)
    Peccal = np.sum(QECEp * d_volume)
    ax4 = fig.add_subplot(gs[3:5, 2:])
    ax4.plot(XRHOp, pref.adjust(QECEp), label='jsp/QECE')
    ax4.text(0.95, 0.5, (
        f'{pref.format(Peccal)}W\n'
        f'jst={pref.format(PECEt)}W'
    ), transform=ax4.transAxes, ha='right', va='center')
    ax4.set_xlabel('rhot')
    ax4.set_ylabel(f'Power density (${pref.symbol}W/m^3$)')
    for gray_rays_jz_pd in gray_rays_jz_pds:
        ax4.plot(gray_rays_jz_pd.data['rhot'],gray_rays_jz_pd.data['dPdV'],linestyle='',marker='.')

    #Gauss fit - removed
    #def gaus(x, a, x0, sigma):
    #    return a * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2))
    #guessmax = np.max(QECEp)
    #ixguessmax = np.argmin(np.abs(QECEp - guessmax))
    #guessposmax = XRHOp[ixguessmax]
    #popt, pcov = optimize.curve_fit(
    #    gaus, XRHOp, QECEp,
    #    p0=[guessmax, guessposmax, 0.1],
    #)
    #print('Gauss fit: rho_0={0:5.4f}, sigma={1:5.4f}'.format(popt[1], popt[2]))
    #x = np.linspace(0, 1, 101)
    #ax4.plot(x, pref.adjust(gaus(x, *popt)), ':', label='fit')
    ax4.legend()

    #print('CD eff at rho={0:5.4f}, eta={1:7.4e} A.m/W'.format(
    #    XRHOp[ixguessmax],
    #    JZECp[ixguessmax] / QECEp[ixguessmax]))

    # current
    #pref = MetricPrefix(np.max(JZECp))
    pref = MetricPrefix(1e6)
    RIp0 = RIp[0]
    ec_cal = np.sum(JZECp * d_volume) / (2.0 * np.pi * RIp0)

    ax5 = fig.add_subplot(gs[5:, 2:])
    ax5.plot(XRHOp, pref.adjust(JZECp), label='jsp/JZEC')
    ax5.text(0.95, 0.5, (
        f'{pref.format(ec_cal)}A\n'
        f'jst={pref.format(CUECt)}A'
    ), transform=ax5.transAxes, ha='right', va='center')
    ax5.set_xlabel('rhot')
    ax5.set_ylabel(f'Current density (${pref.symbol}A/m^2)$')
    for gray_rays_jz_pd in gray_rays_jz_pds:
        ax5.plot(gray_rays_jz_pd.data['rhot'],gray_rays_jz_pd.data['Jphi'],linestyle='',marker='.')
    ax5.legend()

    #fig.tight_layout()

    del jsp, jst

    return fig

def plot_wave_part_res(results: JettoResults, t1: float, beamname: Optional[str] = None, beampathsst: Optional[float] = None, *, figsize=(6,6)) -> plt.Figure:

    #define various relativistic functions
    def gamma0u(u):
       return np.sqrt(1.+u**2) #gamma(u), u=p/mc
    def gamma0v(v):
       return 1./np.sqrt(1.-v**2) #gamma(v), v=v/c
    def aMb(mu): #mu=mc^2/Te
       if mu<680.0:
          y=mu*np.exp(-mu)/(4.*np.pi*special.kv(2,mu)) #exact coeff, results in Inf, for mu>680, use approx below instead
       else:
          y=(mu/2./np.pi)**1.5 #approx of aMb for mu>680
       return y
    def fFMaxreluF(upa,upe,mu): #Max relativistic of u_paraller,u_perp, norm to m^3c^3
       #s. Cottrill 08 PoP p.082108, eq.(15) for no drift
       #mu=mc^2/Te, upa=ppar/mc, upe=pper/mc
       #\int FfitMax1vr d^3p= 2*pi*\int upe*FfitMax1vr dupe dupa = 1 e.g.
       # 2*pi*dblquad(@(x,y) y.*fFMaxreluF(a0FfitMax1vr,x,y),-0.5,0.5,0,0.5)=1
       y=aMb(mu)*np.exp(-mu*(np.sqrt(1.+upe**2+upa**2)-1.))
       return y
    def fFMaxrelpK(ppa,ppe,Theta): #Max relativistic of p_parallel,p_perp, norm to pte^3
       #s. Karney report eq.(89)
       #mu=Te/mc^2, ppa=ppar/pte, pper=pe/pte
       #\int FfitMax1vr d^3p= 2*pi*\int ppe*FfitMax1vr dppe dppa = 1 e.g.
       # 2*pi*dblquad(@(x,y) y.*FfitMax1vr(a0FfitMax1vr,x,y),-0.5,0.5,0,0.5)=1
       y=1./4./np.pi*np.sqrt(Theta)*np.exp(-np.sqrt(1.+Theta*ppe**2+Theta*ppa**2)/Theta)/special.kv(2,1./Theta)
       return y


    #check

    print(integrate.dblquad(lambda y,x,arg: 2.*np.pi*y*fFMaxreluF(x,y,arg),-0.5,0.5, lambda x: 0.0, lambda x: 0.5, args=(511./7.,))) #note f(x,y) dbquad reshufles boundaries, i.e. y1,y2,x1,x2
    print(integrate.dblquad(lambda y,x,arg: 2.*np.pi*y*fFMaxrelpK(x,y,arg),-3.0,3.0, lambda x: 0.0, lambda x: 3.0, args=(7./511.,))) #note f(x,y) dbquad reshufles boundaries, i.e. y1,y2,x1,x2

    #load data
    jsp = results.load_jsp()
    #jst = results.load_jst()
    eq = results.load_eqdsk(t1)
    gbs = results.load_graybeams()
    grc = results.load_gray_central_ray_coord()

    #jsp, jst data
    #idt = np.argmin(np.abs(jst['TVEC1'] - t1))
    idp = np.argmin(np.abs(jsp['TIME'] - t1))

    NEp = jsp['NE'][idp]
    TEp = jsp['TE'][idp]
    VOLp = jsp['VOL'][idp]
    XRHOp = jsp['XRHO'][idp]
    XPSIp = jsp['XPSI'][idp]
    QECEp = jsp['QECE'][idp]
    JZECp = jsp['JZEC'][idp]

    #PECEt = jst['PECE'][0, idt]
    #CUECt = jst['CUEC'][0, idt]

    #eq data
    [r2dmg,z2dmg]=np.meshgrid(eq.Rgrid,eq.Zgrid)
    rhotf = np.interp(eq.psirz_n.flatten(), eq.psip_n, eq.rhot_n)
    rhotr2z2d = np.reshape(rhotf, eq.psirz_n.shape)
    Btot = np.sqrt(eq.B_tor**2+eq.B_pol**2)

    #graybeam data
    if beamname:
        beamnames = [b.beamname for b in gbs]
        beam = gbs[beamnames.index(beamname)]
    else:
        beam = gbs[0]
    freq = beam.fghz * 1e9
    ECmoden = beam.iox

    print('gray beam f={:5.2e}Hz traced launch R0, Z0 = {:5.2f}m, {:5.2f}m'.format(freq,grc.data['R'][0],grc.data['z'][0]))
    ixmaxdIds=np.argmax(np.abs(grc.data['dIds']))
    if beampathsst:
       ixbeampathsst=np.argmin(np.abs(grc.data['sst']-beampathsst))
    else:
       ixbeampathsst=ixmaxdIds

    print('gray beam at sst={:8.5f}m at R, Z = {:5.2f}m, {:5.2f}m; psin = {:5.3f}, rhot = {:5.3f}'.format(grc.data['sst'][ixbeampathsst],grc.data['R'][ixbeampathsst],grc.data['z'][ixbeampathsst],grc.data['psin'][ixbeampathsst],grc.data['rhot'][ixbeampathsst]))
    Btota=grc.data['Btot'][ixbeampathsst]
    print('gray beam B field, Btot={:5.2f}T, B=({:5.2f},{:5.2f},{:5.2f})T'.format(Btota,grc.data['Bx'][ixbeampathsst],grc.data['By'][ixbeampathsst],grc.data['Bx.1'][ixbeampathsst]))
    print('gray beam ne={:5.2e}e19m-3, Te={:5.2f}keV'.format(grc.data['ne'][ixbeampathsst],grc.data['Te'][ixbeampathsst]))
    Nper,Npar=grc.data['Nperp'][ixbeampathsst],grc.data['Npl'][ixbeampathsst]
    print('gray beam Nper={:5.2f}, Npar={:5.2f}, N=({:5.2f},{:5.2f},{:5.2f})'.format(Nper,Npar,grc.data['Nx'][ixbeampathsst],grc.data['Ny'][ixbeampathsst],grc.data['Nz'][ixbeampathsst]))

    ixbeampathReq = np.argmin(np.abs(eq.Rgrid - grc.data['R'][ixbeampathsst]))
    ixbeampathZeq = np.argmin(np.abs(eq.Zgrid - grc.data['z'][ixbeampathsst]))
    psip_beampath = eq.psirz_n[ixbeampathReq,ixbeampathZeq]
    rhot_beampath = rhotr2z2d[ixbeampathReq,ixbeampathZeq]
    rhotgbRZ=interpolate.griddata((r2dmg.flatten(),z2dmg.flatten()), rhotr2z2d.flatten(), (grc.data['R'][ixbeampathsst],grc.data['z'][ixbeampathsst]))
    print('eqdsk coord R, Z = ({:5.2f}m, {:5.2f}m), psi={:5.3f}, rhot={:5.3f})'.format(eq.Rgrid[ixbeampathReq],eq.Zgrid[ixbeampathZeq],psip_beampath,rhot_beampath))
    print('eqdsk at graybeam coord R, Z = ({:5.2f}m, {:5.2f}m), rhot={:5.3f})'.format(grc.data['R'][ixbeampathsst],grc.data['z'][ixbeampathsst],rhotgbRZ))
    print('eqdsk coord R, Z = ({:5.2f}m, {:5.2f}m), Btor={:5.3f}T, Bpol={:5.3f}T)'.format(eq.Rgrid[ixbeampathReq],eq.Zgrid[ixbeampathZeq],eq.B_tor[ixbeampathZeq,ixbeampathReq],eq.B_pol[ixbeampathZeq,ixbeampathReq]))
    ixrhonbeampath=np.argmin(np.abs(XRHOp-grc.data['rhot'][ixbeampathsst]))
    NEpa=NEp[ixrhonbeampath]; TEpa=TEp[ixrhonbeampath]
    print('jsp at rhot = {:5.2f}, ne={:5.2e}m-3, Te={:8.3f}eV'.format(XRHOp[ixrhonbeampath],NEpa,TEpa))

    ocea = 1.76e11 * Btota  # in [rad/s], Btota[T]
    fcea = ocea / 2.0 / np.pi
    opeaa = 56.4 * np.sqrt(NEpa)  # in [rad/s], NE in [m^-3]
    Ynres = ECmoden*fcea/freq
    #non-relativistic!
    vthe = 4.19e7*np.sqrt(TEpa) #cm/s, NRL, vth=sqrt(Te/me)
    #relativistic, to be done
    mua=511.e3/TEpa
    Thetaa=TEpa/511.e3
    vtherel1 = 2.9979e10*np.sqrt(2.*(2./mua+1./mua**2)/(1.+2./mua+1./mua**2))
    print('mu = {:8.5f}, vte={:5.2e}cm/s, vtherel1={:5.2e}cm/s'.format(mua,vthe,vtherel1))

    fig, ax = plt.subplots(2, 2, figsize=figsize)

    cs = plt.contour(r2dmg,z2dmg,rhotr2z2d, [rhotgbRZ], alpha=0.0)
    rzrhot = cs.collections[0].get_paths()[0].vertices.T
    Btotonrhot=interpolate.griddata((r2dmg.flatten(),z2dmg.flatten()), Btot.flatten(), (rzrhot[0,:], rzrhot[1,:]))
    minBtotonrhot=np.min(Btotonrhot)
    maxBtotonrhot=np.max(Btotonrhot)
    BtotongbRZ=interpolate.griddata((r2dmg.flatten(),z2dmg.flatten()), Btot.flatten(), (grc.data['R'][ixbeampathsst],grc.data['z'][ixbeampathsst]))
    BoBmaxratio=BtotongbRZ/maxBtotonrhot
    sqrtBoBmaxratio=np.sqrt(BoBmaxratio/(1.-BoBmaxratio))
    print('eqdsk coord R, Z = ({:5.2f}m, {:5.2f}m), rhot={:5.3f}, B={:5.3f}T, Bmin={:5.3f}T, Bmax={:5.3f}T, B/Bmax={:5.3f}'.format(eq.Rgrid[ixbeampathReq],eq.Zgrid[ixbeampathZeq],rhotgbRZ,BtotongbRZ,minBtotonrhot,maxBtotonrhot,BoBmaxratio))
    print('Ynres = {:5.2f}, mu={:8.5f}'.format(Ynres,mua))

    #wave-part resonance func. Pratel, PoP 2004, eq.11
    def vperovteres(vpaovte,Yn=Ynres,mu=mua,Nparl=Npar):
        np.warnings.filterwarnings('ignore')
        return np.sqrt((1.-1./Yn**2)*mu + 2.*Nparl*vpaovte*np.sqrt(mu)/Yn**2 - (1.+Nparl**2/Yn**2)*vpaovte**2)
    #wave-part resonance for pperp/pte Fidone, 1980, Plas Phys p.261, eq.1,2
    def pperopteres(ppaopte,Yn=Ynres,Theta=Thetaa,Nparl=Npar):
        np.warnings.filterwarnings('ignore')
        return np.sqrt((Yn/np.sqrt(Theta)+Nparl*ppaopte)**2 -1./Theta - ppaopte**2)


    ax[0,0].plot(eq.rbdry,eq.zbdry,'k')
    ax[0,0].plot(eq.xlim,eq.ylim,'b')
    ax[0,0].contour(r2dmg,z2dmg,rhotr2z2d,np.arange(0,1.001,0.1),colors='k',linestyles='--')
    ax[0,0].plot(eq.rmag,eq.zmag,'b+')
    #ax[0,0].scatter(r2dmg,z2dmg, c='k', alpha=0.2, marker='.')
    #ax[0,0].contour(r2dmg,z2dmg,Btot)
    ax[0,0].plot(eq.Rgrid[ixbeampathReq],eq.Zgrid[ixbeampathZeq],'rd')
    ax[0,0].plot(grc.data['R'][ixbeampathsst],grc.data['z'][ixbeampathsst],'bs')

    vparperlim=2.0*np.floor(vthe/1.0e9)*1.0e9  #v/vte
    vpara=np.arange(-vparperlim,vparperlim,vparperlim/1000.)
    vpera=np.arange(0,vparperlim,vparperlim/1000.)
    vpertrapped=np.sqrt(sqrtBoBmaxratio)*np.abs(vpara)
    [vparamg,vperamg]=np.meshgrid(vpara,vpera)
    Eamg=(vparamg**2+vperamg**2)/4.19e7/4.19e7/np.sqrt(2.0)  #eV
    fMaxe = np.sqrt(Eamg)*np.exp(-Eamg/(TEpa*1000.))/np.sqrt(np.pi)/np.sqrt((TEpa*1000.)**3)

    pparperlim=5.0  #p/pte
    ppara=np.arange(-pparperlim,pparperlim,pparperlim/1000.)
    ppera=np.arange(0,pparperlim,pparperlim/1000.)
    [pparamg,pperamg]=np.meshgrid(ppara,ppera)
    fMaxep=fFMaxrelpK(pparamg,pperamg,Thetaa)

    #fMaxecntr = np.sqrt(np.array([32.0,16.0,8.0,4.0,2.0])*1000.)*np.exp(-(np.array([32.0,16.0,8.0,4.0,2.0])*1000.)/(TEpa*1000.))/np.sqrt(np.pi)/np.sqrt((TEpa*1000.)**3)
    jlev=np.sqrt(1./mua)*np.exp(-np.sqrt(1.0+(1./mua)*(np.arange(20,0,-0.1)/3.)**2)*mua) /4./np.pi/special.kv(2,mua) #levels from Karney
    #ax[0,1].contourf(vparamg,vperamg,fMaxe,np.sort(fMaxecntr),cmap=plt.cm.plasma)
    ax[0,1].contour(vparamg,vperamg,fMaxe,jlev,cmap=plt.cm.plasma)
    #ax[0,1].contour(vparamg,vperamg,fMaxe,np.array([np.exp(-1.0)/TEpa*1000./np.sqrt(np.pi)]),colors='black')
    ax[0,1].plot(vpara,vpertrapped,'r')
    vperares=vperovteres(vpara/vthe)
    ax[0,1].plot(vpara,vperares*vthe,'c')
    ax[0,1].set_xlim([-pparperlim,pparperlim]); ax[1,1].set_ylim([0,pparperlim])
    ax[0,1].set_xlabel('vparl, cm/s'); ax[0,1].set_ylabel('vperp, cm/s')

    ax[1,0].plot(XRHOp, np.sqrt(XPSIp), label='jsp')
    ax[1,0].plot(eq.rhot_n, np.sqrt(eq.psip_n), 'k--', label='eqdsk')
    ax[1,0].plot(grc.data['rhot'],grc.data['psin'],'r.', label='grc')
    ax[1,0].set_ylabel('rhop')
    ax[1,0].legend()

    jlev=np.sqrt(1./mua)*np.exp(-np.sqrt(1.0+(1./mua)*(np.arange(20,0,-1)/3.)**2)*mua) /4./np.pi/special.kv(2,mua) #levels from Karney
    ax[1,1].contour(pparamg,pperamg,fMaxep,jlev,cmap=plt.cm.plasma)
    pperares=vperovteres(ppara)
    vocres2=Thetaa*(1-2.5*Thetaa)*(vpara/vthe**2+vpertrapped/vthe**2) #p/pte=gamma*v/vte
    ax[1,1].plot(gamma0v(vocres2)*vpara/vthe,gamma0v(vocres2)*vpertrapped/vthe,'r') #to be done for p
    ax[1,1].plot(ppara,pperares,'c')
    ax[1,1].set_xlim([-vparperlim,vparperlim]); ax[0,1].set_ylim([0,vparperlim])
    ax[1,1].set_xlabel('pparl/pte'); ax[0,1].set_ylabel('pperp/pte')

    return fig


class MetricPrefix:
    """Helper for dealing with Metric (SI) Prefixes."""

    _TABLE = (
        (1e-24, 'y'),
        (1e-21, 'z'),
        (1e-18, 'a'),
        (1e-15, 'f'),
        (1e-12, 'p'),
        (1e-9,  'n'),
        (1e-6,  'μ'),
        (1e-3,  'm'),
        (1,     ''),
        (1e3,   'k'),
        (1e6,   'M'),
        (1e9,   'G'),
        (1e12,  'T'),
        (1e15,  'P'),
        (1e18,  'E'),
        (1e21,  'Z'),
        (1e24,  'Y'),
    )

    _FACTORS = [a[0] for a in _TABLE]

    @classmethod
    def _idx(cls, value):
        i = bisect_left(cls._FACTORS, value / 120)
        return min(i, len(cls._TABLE) - 1)

    def __init__(self, value: float):
        """Choose an appropriate prefix for the given value."""
        i = self._idx(value)

        self.factor, self.symbol = self._TABLE[i]

    def adjust(self, value):
        """Apply the chosen prefix to the given value."""
        return value / self.factor

    def format(self, value: float):
        """Format the given value using the current prefix."""
        # TODO: handle cases where the scaled value is out of range
        return f'{value / self.factor:.2f}{self.symbol}'

    @classmethod
    def auto_format(cls, value: float):
        """Format the given value using an appropriate prefix."""
        i = cls._idx(value)

        factor, symbol = cls._TABLE[i]

        return f'{value / factor:.2f}{symbol}'


def parse_args(argv: Optional[Sequence[str]] = None) -> Namespace:
    """Parse command line arguments."""
    parser = ArgumentParser(
        description='Run pre-defined analyses of a JETTO GRAY run',
    )

    parser.add_argument(
        'run', default=None,
        help='directory of run, or from inside ~/jetto/runs',
    )

    parser.add_argument(
        '--beam', default=None,
        help='beam name, will use first by default'
    )

    parser.add_argument(
        '--time', default=None, type=float,
        help='time to perform analysis at, will choose time from eqdsk file by default'
    )

    parser.add_argument(
        '--save', '-s', default=None,
        help='save figures in the specified directory',
    )

    parser.add_argument(
        '--device', default=None,
        help='specify machine name for TRANSP-like symlinks',
    )

    parser.add_argument(
        '--shot', default=None, type=int,
        help='specify shot number for TRANSP-like symlinks',
    )

    ns = parser.parse_args(argv)

    # exactly one of ns.run or ns.path is left specified: if the user
    # has specified something that looks like a path, then use that,
    # otherwise we assume it's a named run.
    if '/' in ns.run:
        path = Path(ns.run)
        if not path.exists():
            print('Error: the specified path does not exist', file=stderr)
            exit(1)
        elif not path.is_dir():
            print('Error: the specified path is not a directory', file=stderr)
            exit(1)
        else:
            ns.path = path
            ns.run = None
    else:
        ns.path = None

    if ns.save is not None:
        ns.root = root = Path(ns.save)
        if not root.is_dir():
            print('Error: the directory to save figures in should exist')

    return ns


def main():
    ns = parse_args()

    res = JettoResults(
        path=ns.path, run=ns.run,
        device=ns.device, spn=ns.shot,
    )

    # if the user hasn't specified a time, then look for eqdsk files
    # as a guess for the time to use
    if ns.time is None:
        times = res.get_eqdsk_times()
        if not times:
            print('Error: unable to locate any timed eqdsk files', file=stderr)

        time = times[-1]
    else:
        time = ns.time

    # do the analyses
    fig1 = plot_analysis_1(res, time)
    fig2 = plot_analysis_2(res, time, ns.beam)

    # save or make plots interactive as appopriate
    if ns.save:
        fig1.savefig(ns.root / 'gray_analysis_01.png', dpi=180)
        fig2.savefig(ns.root / 'gray_analysis_02.png', dpi=180)
    else:
        plt.show(block=True)


if __name__ == '__main__':
    main()
