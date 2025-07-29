import numpy as np
from itertools import tee, filterfalse
from astropy.io import fits
from pathlib import Path
import h5py
import itertools

import multiprocessing as mp

from spiakid_simulation.spiakid_simulation_par.fun.PSF.turbulence import DefinedPSF, GaussianPSF, FilePSF
from spiakid_simulation.spiakid_simulation_par.fun.Constant.DataChecking import DataCheck, FileRead
from spiakid_simulation.spiakid_simulation_par.fun.Photon.sim_image_photon import StarPhoton, PhotonJoin, Timeline
from spiakid_simulation.spiakid_simulation_par.fun.Rot.rot import Rotation
from spiakid_simulation.spiakid_simulation_par.fun.Phase.phase_conversion import ReadCSV, PhotonPhase
from spiakid_simulation.spiakid_simulation_par.fun.Calibration.Calib import Calib
from spiakid_simulation.spiakid_simulation_par.fun.Filter.filter import PixFilter
from spiakid_simulation.spiakid_simulation_par.fun.Crater.CraterSpectrum import CMDFileRead, FindSpiakidSp
from spiakid_simulation.spiakid_simulation_par.fun.output.HDF5_creation import recursively_save_dict_contents_to_group





class Simulation():
    __slots__ = ('detect', 'psf', 'stars', 'photons', 'wmap')

    @staticmethod
    def InitSeed():
        np.random.seed()

    @staticmethod
    def ParFun(args):

        [
            k,l, CONST, baselinepix, conversion, wmap, photons, bkgph, bkglbd, bkgflux
        ] = args
        pixfilter = PixFilter(CONST['baseline'], CONST['decay'], CONST['templatetime'], CONST['trigerinx'], CONST['point_nb'], CONST['nreadoutscale'], baselinepix, k, l)
        
        pixcalib = Calib(CONST['wv'], CONST['nbwv'], CONST['calibtype'], conversion, pixfilter[0], pixfilter[1],CONST['nphase'],
                         CONST['decay'], CONST['timelinestep'], CONST['nreadoutscale'], baselinepix, wmap, CONST['peakprominence'], k, l)
        
        pixphase = PhotonPhase(photons, CONST['nphase'], CONST['decay'], CONST['exptime'], baselinepix, CONST['nreadoutscale'], pixcalib, bkgph, bkglbd, bkgflux)
        
        print('['+str(k)+','+str(l)+'],', flush = True)
        
        pixpeaks =  Timeline(pixphase, CONST['exptime'], pixfilter[0], pixfilter[1], CONST['nreadoutscale'], CONST['timelinestep'], wmap, CONST['peakprominence'])

        return([k, l, pixfilter, pixcalib, pixpeaks])
    
    def __init__(self,file ):

        CONST = FileRead(file)

        h5file = h5py.File(CONST['path'], 'w')


        if CONST['baseline'] =='random':
            global baselinepix
            baselinepix = np.random.uniform(low = 10, high = 20, size = (CONST['pxnbr'], CONST['pxnbr']))

            h5file['baseline/Baseline'] = baselinepix
            
        elif CONST['baseline'] == 'uniform':
            baselinepix = np.zeros(shape = (CONST['pxnbr'], CONST['pxnbr']))


        if CONST['background']:
            bkgfits = fits.open(CONST['background'])
            bkgdata = bkgfits[1].data
            bkgfits.close()
            mask = (bkgdata['lam'] > CONST['wv'][0]*10**3) & (bkgdata['lam'] < CONST['wv'][-1]*10**3)
            bkglbd = bkgdata['lam'][mask] * 10 **-3
            # Only scattered starlight flux
            bkgflux = bkgdata['flux_ssl'][mask] 
            NbrPhBkgTot = sum(CONST['exptime'] * (3.58/2)**2*np.pi * (CONST['pxnbr'] * CONST['pxsize'])**2 * (0.1e-3) * bkgflux)
            
            print('NbrPhBkgTot = ' + str(NbrPhBkgTot))
            BkgPhDistrib = np.random.poisson(lam = NbrPhBkgTot/CONST['pxnbr']**2, size = [CONST['pxnbr'], CONST['pxnbr']])
          

        else:
            BkgPhDistrib = np.zeros(shape = [CONST['pxnbr'], CONST['pxnbr']])
  
        global spectrumlist 
        spectrumlist = []
        files = Path(CONST['spectrum']).glob('*')
        for i in files:
            spectrumlist.append(i)


        # Saving data in HDF5
        recursively_save_dict_contents_to_group(h5file, '/', DataCheck(file))
        print('DATA DONE')
        
        # PSF computing
        self.psf = self.PSF(CONST, h5file)
        print('PSF done')

        self.stars = {}
        # Star and photon creation
        sp_dict = CMDFileRead(CONST['crater_file'])
        inx, spdict = FindSpiakidSp(sp_dict, CONST['stnbr'], CONST['spectrum_desc'])
        for i in range(0, CONST['stnbr']):
            print('star %i'%i)
            
            self.stars['star_'+str(i)] = self.Star(self.psf,i, spdict, CONST, h5file)
          
          
        print('Star done')
        # Grouping photons pixel per pixel
        self.photons = PhotonJoin(self.stars, CONST['pxnbr'])
        


        for i in range(CONST['pxnbr']):
            for j in range(CONST['pxnbr']):
                if len(self.photons[i,j][0]) > 0:
                    h5file['Photons/Photons/'+str(i)+'_'+str(j)] = list(zip(self.photons[i,j][0], self.photons[i,j][1]))
        h5file['BkgPhotonsNumber'] = NbrPhBkgTot
        print('Photon done')

        if CONST['weightmap'] == True:
            self.wmap = np.random.uniform(low = 0.5, high = 1, size = (CONST['pxnbr'], CONST['pxnbr']))
      
        else:
            self.wmap = np.ones(shape = (CONST['pxnbr'], CONST['pxnbr']))
        h5file['WeightMap'] = self.wmap
            
        # Photon distribution on the detector 
        args = []
        pixlist = np.linspace(0, CONST['pxnbr']-1, CONST['pxnbr'], dtype = int)
        pix = list(itertools.product(pixlist, pixlist))
        MatConv = ReadCSV(CONST['conversion'], CONST['pxnbr'])
            
        for i in range(len(pix)):
            k, l = pix[i][0], pix[i][1]           

            args.append(np.array([k, l, CONST, baselinepix[k,l], MatConv[k,l], self.wmap[k,l], self.photons[k,l], BkgPhDistrib[k,l], bkglbd, bkgflux], dtype = object))
          
        with mp.Pool(processes=CONST['process_nb'], initializer=Simulation.InitSeed) as pool:
            res = pool.map(Simulation.ParFun, args)
            pool.close()
            pool.join()
        print('res')

        for r in res:
            k, l = r[0], r[1] 
            pixfilter = r[2][0]
            pixcalib = r[3]
            pixpeaks = r[4]
            # ftime = r[5]
               
            h5file['Filter/'+str(k)+'_'+str(l)] = pixfilter
            for i in range(len(pixcalib[1])):
                h5file['Calib/'+str(pixcalib[1][i])+'/'+str(k)+'_'+str(l)] = pixcalib[0][str(pixcalib[1][i])]
                    
                
            for i in range(len(pixpeaks)):
                h5file['Photons/'+str(i)+'/'+str(k)+'_'+str(l)] = pixpeaks[i]
                # h5file['ftime/'+str(i)+'/'+str(k)+'_'+str(l)] = ftime[i]

        print('End detector', flush = True)
    
    

    class PSF():
            __slots__ = ('psfpxnbr', 'psfsize','psfenergy','psfpos','maxpsf','psf')
            def __init__(self, CONST, h5file):

        
                try: CONST['psfmeth']
                except:
                    self.psf, self.psfpxnbr, self.psfsize = GaussianPSF(pxnbr=CONST['pxnbr'], pxsize=CONST['pxsize'], wv=CONST['wv'])
                    print(np.shape(self.psf))
                else:
                    if CONST['psfmeth'] == 'Download':
                        self.psf, self.psfpxnbr, self.psfsize = FilePSF(CONST['psffile'])
                    else:
                        psfargs = CONST['psfpxnbr'], CONST['psfsize'], CONST['seeing'], CONST['wind'], CONST['L0'], CONST['coeff'], CONST['psffile']
                        self.psf, self.psfpxnbr, self.psfsize = DefinedPSF(psfargs=psfargs, wv=CONST['wv'], diameter=CONST['diameter'], obscuration=CONST['obscuration'],exptime=CONST['exptime'], ProcessNb=CONST['process_nb'])

                # Create a minimum of intensity on the psf to place a photon
                self.psfenergy = np.zeros(shape = np.shape(CONST['wv']), dtype = object)
                self.psfpos = np.zeros(shape = np.shape(CONST['wv']), dtype = object)
                self.maxpsf = []
         
                for wvl in range(len(CONST['wv'])):
                    self.maxpsf.append(1.1 * np.max(self.psf[:,:,wvl]))
                    self.psfpos[wvl]  = []
                    self.psfenergy[wvl] = []
                    lim = np.max(self.psf[:,:,wvl])/100
                    data  = self.psf[:,:,wvl]
                    for i in range(self.psfpxnbr):
                        for j in range(self.psfpxnbr):
                            if self.psf[:,:,wvl][i,j]> lim: 
                                self.psfpos[wvl].append([i-0.5*self.psfpxnbr,j-0.5*self.psfpxnbr])
                                self.psfenergy[wvl].append(data[i,j])
                    h5file['PSF/psfpos/'+str(wvl)] = self.psfpos[wvl]
                    h5file['PSF/psfenergy/'+ str(wvl)] = [self.psfenergy[wvl]]
               

    class Star():
            __slots__ = ('posx', 'posy', 'spectrumchoice', 'stardist', 'starintensity', 'spectrum', 'phase', 'alt_az_t', 'ra_dec_t', 'ang', 'photondetect','ratio', 'spec')
            def __init__(self, psf,i, sp, CONST, h5file):
                
                self.posx  = np.random.uniform(low = -(0.9 * CONST['pxnbr'])/2, high= (0.9 * CONST['pxnbr'])/2)
                self.posy  = np.random.uniform(low = -(0.9 * CONST['pxnbr'])/2, high= (0.9 * CONST['pxnbr'])/2)
                # print(self.posx+CONST['pxnbr']/2,self.posy+CONST['pxnbr']/2, flush = True)
                spname = sp['star_'+str(i)]['Spectrum'] 
                self.ratio = sp['star_'+str(i)]['ratio']
                T = sp['star_'+str(i)]['Temp']
                mag = sp['star_'+str(i)]['Mag']
                sp = np.loadtxt(CONST['spectrum'] + '/'+ spname)
                
                
                self.stardist = np.random.uniform(CONST['stdistmin'], CONST['stdistmax'])

                #  Applying distance to the spectrum
                self.spectrum = [sp[:,0], (10 /self.stardist)**2 * sp[:,1] * self.ratio]

                # Cutting the wavelength list to be in the required range
                t, wavelength = self.partition(lambda x:x>350, sp[:,0])
                t, wavelength = self.partition(lambda x:x<850, list(wavelength))
                wavelengthsp = list(wavelength)

                # Same for spectrum value
                k, l = list(self.spectrum[0]).index(wavelengthsp[0]), list(self.spectrum[0]).index(wavelengthsp[-1])
                self.spec = self.spectrum[1][k-1:l]
                
                # rotation effect
                rot, evalt, self.alt_az_t, pos, star_ra_dec_t, alt_az_guide, ra_dec_guide = Rotation(CONST['rotation'], CONST['altguide'], CONST['azguide'], CONST['latitude'], self.posx, self.posy, CONST['exptime'], CONST['pxnbr'], CONST['pxsize'])

                # Photon Creation
                self.photondetect = StarPhoton(i, psf, rot, evalt, CONST['wv'],wavelengthsp, self.spec, CONST['exptime'], CONST['diameter'], CONST['timelinestep'], CONST['transmittance'], CONST['pxnbr'], CONST['pxsize'], h5file)
                # photondetect[0] = wv in µm, photondetect[1] = time in µs
                
                h5file['Stars/'+str(i)+'/Spectrum'] = sp
                h5file['Stars/'+str(i)+'/Rotation'] = pos
                # h5file['Stars/'+str(i)+'/Pos'] = [self.posx, self.posy]
                h5file['Stars/'+str(i)+'/Dist'] = self.stardist
                h5file['Stars/'+str(i)+'/alt_az_guide'] = alt_az_guide
                h5file['Stars/'+str(i)+'/alt_az_star'] = self.alt_az_t
                h5file['Stars/'+str(i)+'/Temp'] = T
                h5file['Stars/'+str(i)+'/SpecName'] = spname
                h5file['Stars/'+str(i)+'/Mag'] = mag
                h5file['Stars/'+str(i)+'/star_ra_dec_t'] = star_ra_dec_t
                h5file['Stars/'+str(i)+'/ra_dec_guide'] = ra_dec_guide

            def partition(self, pred, iterable):
                "Use a predicate to partition entries into false entries and true entries"

                t1, t2 = tee(iterable)
                return filterfalse(pred, t1), filter(pred, t2)
