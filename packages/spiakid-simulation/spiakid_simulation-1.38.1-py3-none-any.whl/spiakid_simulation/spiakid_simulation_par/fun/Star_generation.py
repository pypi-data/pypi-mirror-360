import numpy as np
import numpy.random as rand

from pathlib import Path

from astropy.io import fits
from scipy import interpolate

def image_sim(pix_nb,pix_size, object_number, distance,Path_file,Wavelength,spectrum,save = False):  # Wavelength in µm

    image = []
    Image_size = int(pix_nb)
    # importing spectrums
    files = Path(spectrum).glob('*')
    Spectrum_path = []
    Point = len(Wavelength)
    Object_dict = {}
    posx = []
    posy = []
    dist = []
    pos = []
    for i in files:
        Spectrum_path.append(i)