import numpy as np
from astropy.io import fits
import multiprocessing as mp

def generate_Kolmo_screen(N, pixelSize, r0, L0):
    """
    Generate a couple of AO-compensated screens.

    Parameters
    ----------
    N         : int : size of the created phase map [pixels]
    pixelSize : float : pix size of produced phase map [metres]
    r0        : float : r0 [metres]
    L0        : float : outer scale L0 [metres]

    Returns
    -------
    A tuple of phase screens (phi1, phi2)
    """
    # Remember that Fourier pairs are always linked through FFTs using the relation
    #      dx * dk * N = 1
    # where dx is the pixel size in one of the Fourier space, dk is the pixel
    # size in the dual space, N is the number of pixels across the image.
    
    
    # multipurpose array of N consecutive integers, with 0 at index N/2,
    # i.e. starting at N/2, ending at N/2-1, and then FFT-shifted.
    # Always useful when you're about to deal with FFTs.
    x = np.arange(N) - (N/2)
    x = np.fft.fftshift(x)   # Center the 0 value
    
    
    dk = 1. / (N*pixelSize)    # pixel size in frequency space
    # generating 2D spatial frequencies arrays with null frequency at index [0,0]
    nu, xi = np.meshgrid(x*dk, x*dk, indexing='ij')
    k = np.sqrt( nu**2 + xi**2 )  # map of modulus of spatial frequencies

    # spectrum of turbulence in "radians^2 per (1/meters)^2",
    # i.e. in radians^2.m^2
    W = 0.023 * r0**(-5./3.) * (k**2 + L0**-2)**(-11.0/6.0)
    
    # square root of W, useful later to spare CPU time
    w = np.sqrt(W)
    
    # ............... Now generating phases .................
    argu = np.random.rand(N,N) * (2*np.pi)  # flat random numbers between 0 and 2pi
    # Fourier transforming  w*exp(i*argu) :
    # Here the normalisation is important and non-trivial. A classical Fourier
    # transform would have required a normalisation using
    #     (dk**2) * FFT( w*exp(i*argu) )
    # but here it will be different. The random phases are not the fourier
    # transform because of a normalisation of the energy over the area of the
    # support. As a final consequence, after non-trivial calculus, the
    # normalisation shall be
    #     dk * FFT( w*exp(i*argu) )
    phi = dk * np.fft.fft2(w * np.exp(1j * argu))  # Fourier transform
    # phi is complex, and both real and imag parts can be useful. However, the
    # total energy of the spectrum has been spread between them so that they
    # need a factor of sqrt(2) to be properly scaled.
    
    # phi1 and phi2 are in radians, at the wavelength where r0 was given.
    phi1 = np.sqrt(2) * phi.real
    phi2 = np.sqrt(2) * phi.imag

    return (phi1, phi2)

def compute_PSF(phase, pixelSize, D, obscu):
    """
    Compute the PSF for some given phase screen and telescope diameter with
    obscuration

    Parameters
    ----------
    phase     : 2D array : phase screen [radians]
    pixelSize : float : pixel size of the phase screen [metres]
    D         : float : telescope diameter [metres]
    obscu     : float : telescope obscuration [metres]

    Returns
    -------
    PSF array, normalised as Strehl.
    """
    # first we need a pupil, so we generate a map of distances
    N, _ = phase.shape
    x = np.arange(N) - (N/2)
    xx, yy = np.meshgrid(x*pixelSize, x*pixelSize, indexing='ij')
    r = np.sqrt( xx**2 + yy**2 )  # map of distances
    pupil = np.logical_and( r<(D/2.), r>(obscu/2.) )
    pupil = pupil / np.sum(pupil)  # to get a Strehl-normalised psf on output
    
    complexPsf = np.fft.fftshift(np.fft.fft2( pupil * np.exp(1j*phase) ))
    
    # CCD-detected PSF
    PSF = np.abs(complexPsf)**2
    return PSF

def set_parameters(fov_arcsec, wavelength_array, seeing, wind, obs_time):
    """
    Genere les bons parametres puor appeler les fonctions de calcul d'ecran
    de phase  generateKolmoScreen()  et  computePSF(), à partir de params
    système plus simples

    Parameters
    ----------
    fov_arcsec : flaot, field of view of the simulated image [arcsec]
    nb_pixels_img : int. Nb of pixels of the simulated image.
    time_step : float. Number of seconds between two simulated images [s].
    nb_image : int. Number of images to be simulated in the time-series.
    wavelength_array : list of floats. List of wavelengths to be simulated.
    seeing : float. Value of seeing [arcsec].
    wind : float. Wind speed in m/s.
    D : float. Telescope diameter [m].
    obscuration : float. Diameter of the telescope central obscuration [m].

    Returns
    -------
    pixel_screen_size : 
    N_big_screen : int. Nb of pix of the phase screen.
    Npup : int. Number of pixels across the telescope pupil.
    r0_short : float. Value of r0 at the shortest wavelength. [m]
    """
    RASC = 3600 * 180 / np.pi  # conversion rad to arcsec
    lam = np.array(wavelength_array) * 1e-6  # form a numpy array
    lam_short = np.min(lam)
    fov_radians = fov_arcsec / RASC
    
    # pixel size of the phase screen
    pixel_screen_size = lam_short / fov_radians 
    size_big_screen = wind * obs_time
    N_big_screen = int(size_big_screen / pixel_screen_size)
    if N_big_screen%2:
        N_big_screen += 1  # even number is preferred for fft
    
    # seeing conversion, from arcsec to a r0 value, as a function of wavelength
    lam_seeing = 500e-9 # wavelength used for the definition of the seeing (500nm as a standard)
    r0_seeing = lam_seeing / (seeing / RASC) # r0 at 500 nm
    # Conversion of r0 to another wavelength (to the shortest one)
    r0_short = r0_seeing * (lam_short/lam_seeing)**(6/5.)

    return pixel_screen_size, N_big_screen, r0_short

def pad_array(im, N):
    """
    Modify the size of an image <im> by padding with zeros all around.

    Parameters
    ----------
    im : image.
    N : int. Size of new image (square).

    Returns
    -------
    im_out : the new image.
    """
    if N%2:
        print("nombres pairs uniquement, svp ...")
    N += 1
    ni, nj = im.shape
    im_out = np.zeros((N, N)) # on reserve l'image finale
    di = (N - ni)//2 # petits calculs d'index pour placer l'image dedans
    dj = (N - nj)//2
    im_out[di:di+ni, dj:dj+nj] = im # on lui carre l'image dans le groin
    return im_out # et paf


def crop_array(im, N):
    """
    Crop a large image to a reduced dimension (N,N)

    Parameters
    ----------
    im : image
    N  : int. dimension of output image (N, N).

    Returns
    -------
    Cropped image.
    """
    ni, nj = im.shape
    di = (ni - N)//2 # petits calculs d'index pour placer l'image dedans
    dj = (nj - N)//2
    return im[di:di+N, dj:dj+N]
    

def makeven(i):
    # Increments the argument if odd number. Makes it even.
    if i%2:
        i += 1
    return i


def PSF_creation(fov_tot, nb_pixels_img, wavelength_array, seeing, wind, D, obscuration, L0,obs_time,process_nb,save_link = 0):

    pixel_screen_size, Ntot, r0 = set_parameters( fov_tot,wavelength_array, seeing,wind,obs_time )
   
    Npsf = nb_pixels_img
    N,_ = screen_size(Ntot,Npsf)
  
    phi1, _= generate_Kolmo_screen(N, pixel_screen_size, r0, L0)

    lam_short = np.min(np.array(wavelength_array))

    psf_pixel_size = fov_tot / nb_pixels_img
    Displacement = displacement(Ntot,Npsf)
   
    Disp_x = Displacement[0]
    if len(Disp_x) > 100:
        Disp_x = Disp_x[:99]
    
    args = []
    for i in range(len(wavelength_array)):
        
        wavelength_scaling_factor = wavelength_array[i] / lam_short
        Npad = int(np.round(nb_pixels_img * wavelength_scaling_factor))
        Npad = makeven(Npad) 

        args.append([wavelength_scaling_factor,Npad,Disp_x,Displacement,Npsf,phi1,pixel_screen_size, D, obscuration,i])

    with mp.Pool(processes=process_nb) as pool:

        results = pool.map(ParImCompute,args)

    stack_psf = results

    if save_link:
        hdr = fits.Header()
        hdr['CTYPE3'] = 'RA---CAR'
        hdr['CTYPE2'] = 'DEC--CAR'
        hdr['CTYPE1'] = 'WAVE'
        hdr['CUNIT3'] = 'arcsec'
        hdr['CUNIT2'] = 'arcsec'
        hdr['CUNIT1'] = 'um'
        hdr['CRVAL3'] = 0
        hdr['CRVAL2'] = 0
        hdr['CRVAL1'] = wavelength_array[0]
        hdr['CDELT1'] = wavelength_array[1]-wavelength_array[0]
        hdr['CDELT3'] = psf_pixel_size
        hdr['CDELT2'] = psf_pixel_size
        primary_hdu = fits.PrimaryHDU(stack_psf,header=hdr)

        hdul = fits.HDUList([primary_hdu])
        hdul.writeto(save_link,overwrite=True)
    return(stack_psf)


def ParImCompute(args):
    wavelength_scaling_factor = args[0]
    Npad = args[1]
    Disp_x = args[2]
    Displacement = args[3]
    Npsf = args[4]
    phi1 = args[5]
    pixel_screen_size = args[6]
    D = args[7]
    obscuration = args[8]

    for k in range(0,len(Disp_x)): 
        a = Displacement[1][k]
        b = Npsf+Displacement[1][k]
        c = 0+Displacement[0][k]
        d = Npsf+Displacement[0][k]
        local_phase = phi1[int(a):int(b), int(c):int(d)]
        im = compute_PSF(pad_array(local_phase / wavelength_scaling_factor, Npad), pixel_screen_size, D, obscuration)
        im = crop_array(im, Npsf)
        im = im / np.sum(im) / len(Disp_x)
    return(im)

def displacement(Ntot,Npsf):
    N,new_ntot  = screen_size(Ntot,Npsf)

    Disp_x = np.zeros(new_ntot+1)
    Disp_y = np.zeros(new_ntot+1)
    Disp_x[0] = 0
    Disp_y[0] = 0
    ind_x = 0
    ind_y = 0
    dir = 0
    for i in range(1,new_ntot+1):
        # Déplacement coté droit
        if Disp_x[i-1] + 1 + Npsf <= N and Disp_y[i-1] + 1 + Npsf <= N and Disp_y[i-1]%Npsf == 0 and dir == 0: 
            Disp_x[i] = Disp_x[i-1] + 1
            Disp_y[i] = Disp_y[i-1]
            ind_x += 1
            ind_y += 1

        # Déplacement coté gauche
        elif Disp_x[i-1] - 1 >=0 and Disp_y[i-1] - 1 >=0 and Disp_y[i-1]%Npsf == 0 and dir == 1: 

            Disp_x[i] = Disp_x[i-1] -1
            Disp_y[i] = Disp_y[i-1]
            ind_x += 1
            ind_y += 1

        #On monte

        else:
            Disp_x[i] = Disp_x[i-1]
            Disp_y[i] = Disp_y[i-1] + 1
            if Disp_y[i]%Npsf == 0 and Disp_x[i]//(N - Npsf)== 1:
                dir = 1
            elif Disp_y[i]%Npsf == 0 and Disp_x[i]//(N - Npsf) == 0:
                dir = 0

    Displacement = [Disp_x,Disp_y]
    return(Displacement)

def screen_size(Ntot,Npsf):
    N = Npsf
    while N//Npsf *(N-Npsf) + (N//Npsf - 1 ) * Npsf +  (N%Npsf) <Ntot :
          N+=1
    return(N, N//Npsf *(N-Npsf) + (N//Npsf - 1 ) * Npsf + (N%Npsf) )

def PSF_creation_mult(fov_arcsec, nb_pixels_img, wavelength_array, seeing, wind, D, obscuration, L0,obs_time,coeff, save_link = 0):
    
    #Number of screens
    screens = len(wind)

    #Initialisation
    pixel_screen_size = np.zeros(screens)
    Ntot = np.zeros(screens)
    r0 = np.zeros(screens)
    phi = np.zeros(screens,dtype=object)
    Displacement = np.zeros(screens,dtype=object)


    lam_short = np.min(np.array(wavelength_array))
    psf_pixel_size = fov_arcsec / nb_pixels_img
    # Computing parameters and phi
    for i in range(0,screens):
        pixel_screen_size[i],Ntot[i],r0[i] = set_parameters( fov_arcsec,wavelength_array, seeing,wind[i], obs_time)
        Npsf = nb_pixels_img
        N,_ = screen_size(Ntot[i],Npsf)
        phi[i],_ = generate_Kolmo_screen(N, pixel_screen_size[i], r0[i], L0)
        Displacement[i] = displacement(int(Ntot[i]),Npsf)
    arg_max= np.argmax(Ntot)
    stack_psf = np.zeros(shape = (nb_pixels_img,nb_pixels_img,len(wavelength_array)))
    for i in range(len(wavelength_array)):
        wavelength_scaling_factor = wavelength_array[i] / lam_short
        Npad = int(np.round(nb_pixels_img * wavelength_scaling_factor))
        Npad = makeven(Npad)  
        k_wind = np.ones(screens,dtype = int) * -1
        a_wind = np.zeros(screens)
        b_wind = np.zeros(screens)
        for k in range(len(Displacement[arg_max][0])):
            local_phase = np.zeros((Npsf,Npsf))
            for w in range(screens):
                if (k//int(np.ceil(len(Displacement[arg_max][0])/len(Displacement[w][0])+1/2)) != k_wind[w]):
                    k_wind[w]+=1
                a_wind[w] = Displacement[w][0][k_wind[w]]
                b_wind[w] = Displacement[w][1][k_wind[w]]
                local_phase += phi[w][int(b_wind[w]):int(b_wind[w]+Npsf), int(a_wind[w]):int(a_wind[w]+Npsf)]*coeff[w]/100

            im = compute_PSF(pad_array(local_phase / wavelength_scaling_factor, Npad), pixel_screen_size[w], D, obscuration)
            im = crop_array(im, nb_pixels_img)

            im = im / np.sum(im)
 
            stack_psf[:,:,i] += im / len(Displacement[arg_max][0])

    if save_link:
        hdr = fits.Header()
        hdr['CTYPE3'] = 'RA---CAR'
        hdr['CTYPE2'] = 'DEC--CAR'
        hdr['CTYPE1'] = 'WAVE'
        hdr['CUNIT3'] = 'arcsec'
        hdr['CUNIT2'] = 'arcsec'
        hdr['CUNIT1'] = 'um'
        hdr['CRVAL3'] = 0
        hdr['CRVAL2'] = 0
        hdr['CRVAL1'] = wavelength_array[0]
        hdr['CDELT1'] = wavelength_array[1]-wavelength_array[0]
        hdr['CDELT3'] = psf_pixel_size
        hdr['CDELT2'] = psf_pixel_size
        primary_hdu = fits.PrimaryHDU(stack_psf,header=hdr)

        hdul = fits.HDUList([primary_hdu])
        hdul.writeto(save_link,overwrite=True)
    
    return(stack_psf)


def GaussianPSF(pxnbr, pxsize, wv):
    psfpxnbr = pxnbr*10
    psf_grid = np.zeros(shape = (psfpxnbr,psfpxnbr,len(wv)))
    psf_grid[np.int32(psfpxnbr/2),np.int32(psfpxnbr/2),:] = 1
    psfsize = pxsize * psfpxnbr
    psf = psf_grid
    return(psf, psfpxnbr, psfsize)
             

def DefinedPSF(psfargs, wv, diameter, obscuration, exptime, ProcessNb):
    psfpxnbr, psfsize, seeing, wind, L0, coeff, psffile = psfargs

    if type[wind] == list:

        psf = PSF_creation_mult(fov_arcsec=psfsize, nb_pixels_img=psfpxnbr,
                                wavelength_array=wv, seeing=seeing, wind=wind,
                                D=diameter, obscuration=obscuration, L0=L0,
                                obs_time=exptime, coeff=coeff,save_link=psffile)
    else:
        psf = PSF_creation(fov_tot=psfsize, nb_pixels_img=psfpxnbr,
                            wavelength_array=wv, seeing=seeing, wind=wind,
                            D=diameter, obscuration=obscuration, L0=L0,
                            obs_time=exptime, process_nb = ProcessNb,save_link=psffile)
    return(psf, psfpxnbr, psfsize)

def FilePSF(psffile):
    file = fits.open(psffile)[0]
    psf = np.transpose(file.data, (1, 2, 0))

    list_axis = [file.header['NAXIS1'],file.header['NAXIS2'],file.header['NAXIS3']]
    if (list_axis.count(file.header['NAXIS1']) == 2)  and (file.header['CUNIT1'] == 'arcsec'):
        psfpxnbr = file.header['NAXIS1']
        psfsize = psfpxnbr * file.header['CDELT1']
    else:
    
        psfpxnbr =file.header['NAXIS2']
        psfsize = psfpxnbr * file.header['CDELT2']
    return(psf, psfpxnbr, psfsize)