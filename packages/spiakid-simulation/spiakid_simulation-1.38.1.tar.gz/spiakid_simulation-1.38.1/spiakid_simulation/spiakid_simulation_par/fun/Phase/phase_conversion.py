import numpy as np
import csv
from scipy.optimize import least_squares
import scipy.signal as sg
from scipy import interpolate
import random
from itertools import chain


def ConvInterp(CalibData):

    convwv = []
    convph = []

    for wv in CalibData[1]:
        bin = 50
        
        a = np.histogram(CalibData[0][str(wv)], bins = bin)

        y = a[0]
        x = a[1]
        x = x[:-1]

        val = sg.find_peaks(y, width = 6, distance = 10)
 
        if len(val[0]) == 0:
            while len(val[0]) == 0:

                # Reduce histogram bins to detect peaks
                bin_inter = int(bin -1)
                a = np.histogram(CalibData[0][str(wv)], bins = bin_inter)
                y = a[0]
                x = a[1]
                x = x[:-1]
                val = sg.find_peaks(y, width=5)
                bin = bin_inter
        
        if len(val[0]) > 1:

            center = np.mean(x[val[0]])
            
        else:
            center = x[val[0][0]]

        convwv.append(wv)
        convph.append(center)
    phwvfunc = interpolate.CubicSpline(convph[::-1], convwv[::-1], bc_type = 'not-a-knot')
    wvphfunc = interpolate.CubicSpline(convwv, convph, bc_type = 'not-a-knot')
    return(phwvfunc, wvphfunc)



def fit_gauss(data,time,center):
        def model(x,u):
            return( x[2]/(x[0]*np.sqrt(2*np.pi))*np.exp(-((u-x[1])**2/(2*x[0]**2))))
        
        def fun (x,u,y):
            return( model(x,u)-y)

        def Jac (x,u,y):
            J = np.empty((u.size,x.size))
            J[:,0] = x[2]*np.exp(-(u-x[1])**2/(2*x[0]**2))/(x[0]**4*np.sqrt(2*np.pi))*(u-x[0]-x[1])*(u+x[0]-x[1])
            J[:,1] = x[2]/(x[0]**3*np.sqrt(2*np.pi))*np.exp(-(u-x[1])**2/(2*x[0]**2))*(u-x[1])
            J[:,2] = 1/(x[0]*np.sqrt(2*np.pi))*np.exp(-(u-x[1])**2/(2*x[0]**2))
            return J
        dat = np.array(data)
        t = np.array(time)
        x0 = np.array([1,center,1000])

        res = least_squares(fun, x0, args=(t, dat), jac=Jac, bounds= ([0,0,0],[np.inf,np.inf,np.inf]))
        return res.x[0],res.x[1],res.x[2]


def fit_parabola(wavelength, phase):
        def model(x,u):
            return(x[0]*u**2 + x[1]*u + x[2])     
        def fun(x,u,y):
            return(model(x,u) - y)
        def Jac(x,u,y):
            J = np.empty((u.size,x.size))
            J[:,0] = u**2
            J[:,1] = u
            J[:,2] = 1
            return(J)
        t = np.array(wavelength)
        dat = np.array(phase)
        x0 = [1,1,1]
        res = least_squares(fun, x0, jac=Jac, args=(t,dat)) 
        return res.x[0],res.x[1],res.x[2]


def photon2phase(Photon, convf, nphase):
    r"""Convert the wavelength in phase

    Parameters:
    -----------

    Photon: array
        Photon's wavelength

    convf: list interpolation
        function to convert wavelength into phase

    conv_phase: array
        Calibration's phase

    Output:
    -------

    signal: array
        Signal converted in phase 
    
    
    """
    
    signal = np.copy(Photon)

    ph = convf[1](signal[0])
   
    sigma = ph / (2 * nphase * np.sqrt(2*np.log10(2)))
    signal[0] = np.where(Photon[0] == 0, 0, np.random.normal(loc = ph, scale = sigma))
  
    return(signal)


def PhaseNoise(photon, scale, baseline):

    sig = np.zeros(shape = 2, dtype = object)
    sig[0] = []
    sig[1] = []
    
    if len(photon[0]) > 0:
        for k in range(len(photon[0])):
            
            sig[0].append(np.random.normal(loc = baseline,scale = scale, size = len(photon[0][k] )) + photon[0][k])
            sig[1].append(np.copy(photon[1][k]))
    
    return(sig)



def exp_adding(photon,decay, exptime, baseline, scale):
    r""" Add the exponential decay after the photon arrival

    Parameters:
    -----------

    sig: array
        Signal with the photon arrival

    decay: float
        The decay of the decreasing exponential
    
    Output:
    -------
    
    signal: array
        The signal with the exponential decrease
    
    """

    listph = np.zeros(np.shape(photon[0]), dtype = object)
    listtime = np.zeros(np.shape(photon[0]), dtype = object)
 
    
    listph = []
    listtime = []
    exp = np.exp(decay * np.linspace(0,499,500, dtype = int)/1e6)
    if np.size(photon[0])>0:
                for k in range(np.size(photon[0])):
                    
                    if int(photon[1][k]) + 500 < exptime * 1e6:
                        listtime.append(np.linspace(0,499,500, dtype = int)+int(photon[1][k]))
                        # listph.append(photon[0][k] * exp + np.random.normal(loc = baseline,scale = scale, size = 500))
                        listph.append(photon[0][k] * exp)
                    else:
                        t = int( (int(photon[1][k]) + 500)- int(exptime*1e6))

                        # listph.append(photon[0][k] * exp[:t] + np.random.normal(loc = baseline,scale = scale, size = t))
                        listph.append(photon[0][k] * exp[:t])
                        listtime.append(np.linspace(0,t-1,t, dtype = int)+int(photon[1][k]))

    return([listph, listtime])


def ReadCSV(Path,shape,sep='/'):

    conv = []
    MatCoeff = np.zeros(shape = (shape,shape), dtype = object)
    grille = np.mgrid[0:shape:1,0:shape:1].reshape(2,shape**2).T
    with open(Path,'r') as file:
        data = csv.reader(file,delimiter = sep)
        
        conv = {}
        for i in data:
           
            conv[i[0]] = [eval(i[2]), eval(i[1])]
  
    for i in grille:
        MatCoeff[i[0], i[1]] = fit_parabola(conv[str(i[0])+'_'+str(i[0])][0], conv[str(i[0])+'_'+str(i[0])][1])
    return(MatCoeff)


def PhotonPhase(photondetect, nphase, decay, exptime, baselinepix, nreadoutscale, CalibData, bkgph, bkglbd, bkgflux):
    phase, phbkg, tbkg = [], [], []
    
    if bkgph > 0:
        phbkg = np.array(random.choices(bkglbd, weights = bkgflux, k = bkgph))
   
        tbkg = np.random.uniform(low = 0, high = exptime * 10**6, size = bkgph)
    photondetect[0] = list(chain(photondetect[0], phbkg))
    
    photondetect[1] = list(chain(photondetect[1], tbkg))
    if len(photondetect) > 0:
        convfunc = ConvInterp(CalibData)
        phaseconv = photon2phase(photondetect,convfunc, nphase)
        nexpphase = exp_adding(phaseconv, decay, exptime, baselinepix, nreadoutscale)
        # nexpphase = PhaseNoise(expphase, baselinepix, nreadoutscale)
        for ph in range(0, len(nexpphase[0])):
            phase.append([nexpphase[1][ph], nexpphase[0][ph]])
    
    
    
    return(phase)


                
        
