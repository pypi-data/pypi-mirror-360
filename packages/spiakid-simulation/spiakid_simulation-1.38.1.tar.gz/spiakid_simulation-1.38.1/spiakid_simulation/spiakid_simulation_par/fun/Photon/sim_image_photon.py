import numpy as np
from scipy import interpolate
import random
import csv
from scipy.signal import find_peaks, lfilter



def photon_nbr(wavelength,spectre,time,diam,transmission):
    
    if type(transmission) == str:
        func_trans = trans_read(transmission)
        wv = np.array(wavelength) * 10 ** -3
        value = func_trans(wv)
        spectre *= value
    S = (diam/2)**2 * np.pi # Telescope surface
    h = 6.62607015e-34
    c = 3e8
    
    sp = spectre * wavelength / (h * c) * S * time * (wavelength[1]-wavelength[0]) * 10e-9
    nbr = sum(sp) 
    return(int(nbr), sp)



def photon(wavelength, spec,time,diam,point_nb,transmission=False):

        wv, flux = [], []
        for i in range(len(spec)):
            if spec[i] > 400 and spec[i] < 800:
                wv.append(wavelength[i])
                flux.append(spec[i])

        ph_nbr, spectre = photon_nbr(wavelength,spec,time,diam,transmission)
 
        lbd = random.choices(population=wavelength, weights=spectre*10**-3, k=ph_nbr)
        t=np.random.uniform(low=0,high = time*point_nb,size = ph_nbr)
        phlist = list(zip(lbd, t))
     
        return(phlist)


def trans_read(path,sep='/'):

    wv = []
    trans = []
    with open(path,'r') as file:
        data = csv.reader(file,delimiter = sep)
        for i in data:
            wv.append(eval(i[0]) * 10 **3)
            trans.append(eval(i[1]))

    Trans_func = interpolate.interp1d(wv,trans, kind = 'cubic')

    return(Trans_func)


def detector_scale(detector_dim,photon_dict):
  
    Wavelength = np.zeros([detector_dim,detector_dim],dtype = object)
    Time = np.zeros([detector_dim,detector_dim],dtype = object)
    for i in range(detector_dim):
        for j in range(detector_dim):
            Wavelength[i,j] = []
            Time[i,j] = []

    for ph in range(len(photon_dict)):
        if int(photon_dict[ph][0]+detector_dim/2) < detector_dim and int(photon_dict[ph][1]+detector_dim/2) < detector_dim and int(photon_dict[ph][0]+detector_dim/2) > 0 and int(photon_dict[ph][1]+detector_dim/2) > 0 :
            Wavelength[int(photon_dict[ph][0]+detector_dim/2),int(photon_dict[ph][1]+detector_dim/2)].append(photon_dict[ph][2])
            Time[int(photon_dict[ph][0]+detector_dim/2),int(photon_dict[ph][1]+detector_dim/2)].append(photon_dict[ph][3])
    return([Wavelength,Time])


def photon_pos_on_PSF(photon, psf, wv):

    photondict = []
    x, y =0, 0
    for ph in range(len(photon)):
        phwv = photon[ph][0]
        t = photon[ph][1]
        wvinx = (np.abs(wv-phwv)).argmin()

        stop = 0
        while stop == 0:
            pix = np.random.randint(len(psf.psfpos[wvinx]))
            energy = np.random.uniform(low = 0,high = psf.maxpsf[wvinx])
            if energy<= psf.psfenergy[wvinx][pix]:
                x = psf.psfpos[wvinx][pix][0] 
                y = psf.psfpos[wvinx][pix][1] 
                stop += 1
 
        photondict.append([x,y, phwv,t])
    return(photondict)


def closest_wavelength(wl, PSFwv):
    return int(PSFwv[np.argmin(np.abs(PSFwv - wl))])


def photon_proj(photon, psf,rot, alt_ev, size, FOV,lam0,point_nb):

    dict_photon = []
    pix_length = FOV/size
    psf2detect = psf.psfpxnbr / psf.psfsize #psf_pix_nbr / psf_size

    for ph in range(len(photon)):
            # Adding the star position taking account of rotation + ratio psf size to dectector size
            x_ph = photon[ph][0] / psf2detect + rot[0](photon[ph][3]/point_nb)
            y_ph = photon[ph][1] / psf2detect + rot[1](photon[ph][3]/point_nb)
            alt = alt_ev(photon[ph][3]/point_nb)  # photon altitude at t
            DR = dispersion(np.pi/2 - alt, lam0, photon[ph][2])
            y_ph = y_ph + DR * pix_length
            dict_photon.append([x_ph,y_ph,photon[ph][2],photon[ph][3]])
    
    return(dict_photon)


def dispersion(Z, Lam0, Lam, TC=11.5, RH=14.5, P=743):
    """
    The routine compute the Differential Atmospheric Dispersion
    for a given zenithal distance "Z" for different wavelengths "Lam"
    with respect to a reference wavelength "Lam0".

    The atmospheric parameters can be adjusted to those characterstic
    of the site the computation is made for.
    The parameters listed below refer to the average Paranal conditions.
    
    Routine from Enrico Marchetti, taken on eso.org website, translated from
    IDL by E Gendron.
    
    Parameters
    ----------
    Z       : float. The zenithal distance 
    Lam0 : float. The reference wavelength in microns.
    Lam  : float or array. Wavelength(s) in microns.
    TC      : float. Temperature at the ground [C°]
    RH      : flaot. Relative humidity at the ground [%]
    P       : float. Pressure at the ground [mbar]
    
    For La Silla site, the median params are TC=11.5, RH=14.5, P=743.
    For Armazones site, the median params are TC=7.5, RH=15, P=712.

    Returns
    -------
    DR : Same array as Lam. Amplitude of the differential atmospheric
    dispersion with respect to the reference wavelength Lam0.
    """
    T = TC + 273.16
    PS = -10474.0+116.43*T-0.43284*T**2+0.00053840*T**3
    P2 = RH/100.0*PS
    P1 = P-P2
    D1 = P1/T*(1.0+P1*(57.90*1.0E-8-(9.3250*1.0E-4/T)+(0.25844/T**2)))
    D2 = P2/T*(1.0+P2*(1.0+3.7E-4*P2)*(-2.37321E-3+(2.23366/T)-
            (710.792/T**2)+(7.75141E4/T**3)))
    S0 = 1.0/Lam0
    S = 1.0/Lam
    N0_1 = 1.0E-8*((2371.34+683939.7/(130-S0**2)+4547.3/(38.9-S0**2))*D1+
            (6487.31+58.058*S0**2-0.71150*S0**4+0.08851*S0**6)*D2)
    N_1 = 1.0E-8*((2371.34+683939.7/(130-S**2)+4547.3/(38.9-S**2))*D1+
            (6487.31+58.058*S**2-0.71150*S**4+0.08851*S**6)*D2)
    DR = np.tan(Z)*(N0_1-N_1)*206264.8
    return (DR)


def StarPhoton(i, psf, rot, evalt, wv, wvsp, spec, exptime, diameter, timelinestep, transmittance, pxnbr, pxsize, h5file):
   
    photonlist = PhotonCreation(i, wvsp, spec, exptime, diameter, timelinestep, transmittance, h5file)
    photonPSF = photon_pos_on_PSF(photonlist, psf, wv)
    detectpos = PhotonProj(psf, rot, evalt,photonPSF, wv, pxnbr, pxsize, timelinestep)
    photondetect = detector_scale(pxnbr, detectpos)

    x = []
    y = []
    for ph in range(len(detectpos)):
        x.append(detectpos[ph][0])
        y.append(detectpos[ph][1])
    h5file['Stars/'+str(i)+'/PhotonsPos'] = [x, y]
    for k in range(pxnbr):
        for l in range(pxnbr):
            h5file['Stars/'+str(i)+'/Photons/'+str(k)+'_'+str(l)] = [np.array(photondetect[0][k,l]), photondetect[1][k,l]]
    return(photondetect)


def PhotonCreation(i, wv, spec, exptime, diameter, timelinestep, transmittance, h5file):
    
    photonlist = photon(wavelength=wv, spec=spec, time=exptime,diam=diameter, point_nb=timelinestep, transmission=transmittance)
    print('Photon Number: '+str(len(photonlist)), flush = True)
    h5file['Stars/'+str(i)+'/PhotonNumber'] = len(photonlist)
    h5file['Stars/'+str(i)+'/PhotonsList'] = photonlist
    return(photonlist)

def PhotonProj(psf, rot, evalt,photonPSF, wv, pxnbr, pxsize, timelinestep):
               
    lam0 = (max(wv)+min(wv))/2
    detectpos = photon_proj(photonPSF, psf, rot,evalt, pxnbr, pxsize, lam0, timelinestep)
    return(detectpos)


#  Photon projection on detector from all stars 
def PhotonJoin(stars, pixnb):

    nbstars = len(stars)
    detect = np.zeros(shape = [pixnb, pixnb], dtype = object)

    for i in range(pixnb):
        for j in range(pixnb):
            detect[i,j] = np.zeros(shape = 2, dtype = object)
            detect[i,j][0] = []
            detect[i,j][1] = []


    for st in range(nbstars):
     
        for i in range(pixnb):
            for j in range(pixnb):
                # detect[i,j] = []
                if len(stars['star_'+str(st)].photondetect[0][i,j]) > 0 :
                    for ph in range(len(stars['star_'+str(st)].photondetect[0][i,j])):
                        detect[i,j][0].append(stars['star_'+str(st)].photondetect[0][i,j][ph] * 10**-3)
                        detect[i,j][1].append(stars['star_'+str(st)].photondetect[1][i,j][ph])
    
    return(detect)



def Timeline(phase, exptime, filter, noisetimeline, nreadoutscale, timelinestep, wmap, peakprominence):
    # Photon Distribution and Detection
    timeline = np.zeros(shape = exptime, dtype = object)
    fgtime =  np.zeros(shape = exptime, dtype = object)

    for t in range(exptime):
        timeline[t] = []
        fgtime[t] = []
    
    fm_noise = max(lfilter(filter, 1, noisetimeline[1]))

    for t in range(exptime):
        ntime = np.random.normal(loc = 0, scale = nreadoutscale, size = int(timelinestep))

        for ph in range(int(wmap * len(phase))):
                if int(phase[ph][0][0]/1e6) == t:

                    if int(phase[ph][0][0]/1e6) == int(phase[ph][0][-1]/1e6):
                        inx = list(map(np.int32, phase[ph][0] - np.int32(phase[ph][0][-1]/1e6)*1e6))
                        ntime[inx] +=phase[ph][1]
                    
                    else:
                        inx = abs(phase[ph][0]-np.int32(phase[ph][0][-1]/1e6)*1e6).argmin()
                        inxa = list(map(np.int32, np.linspace(0, len(phase[ph][0]) - inx -1, len(phase[ph][0]))))
                        inxb = np.linspace(0, len(phase[ph][0][inx:])-1, len(phase[ph][0][inx:]), dtype = int)
                        ntime[inxa] += phase[ph][1][inxa]
                        if int(phase[ph][0][-1]/1e6) < exptime:
                            phase.append([inxb + np.int32(phase[ph][0][-1]/1e6)*1e6, phase[ph][1][inxb]])
        
        fntime = lfilter(filter, 1, ntime)
        peaks, _ = find_peaks(fntime,  prominence=peakprominence, height=fm_noise)
        timeline[t] = [peaks, fntime[peaks]]
        fgtime[t] = fntime

    # return(timeline, fgtime)
    return(timeline)