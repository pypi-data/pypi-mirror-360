import numpy as np
from yaml.loader import SafeLoader
import yaml
import pydantic
from pydantic import TypeAdapter, ValidationError
from pydantic.dataclasses import dataclass
from typing import Union, Optional
import multiprocessing as mp

def read_yaml(FilePath):
        r""""
        Read yaml file and store all information in data

        Parameter
        ---------

        FilePath: string
            Position and name of the yaml file

        Attributes
        ----------

        Data: Dictionnary
            Contains all information that contains the yaml file correctly ordered
        """
        with open(FilePath) as f:
            data = yaml.load(f, Loader=SafeLoader)
        return data


def DataCheck(file: str) -> dict: 
    
    config = read_yaml(file)

    @dataclass
    class Photon:


        @dataclass
        class Telescope:

            @dataclass
            class Detector:
                pix_nbr: int
                pix_size: Union[int,float]
                baseline: str
                calibration: str
                # calibfile: Optional[str]
                weightmap: Optional[Union[bool,str]]
                nbwavelength: int
                point_nb: int
                peakprominence: float

            exposition_time: int
            diameter: Union[int,float]
            obscuration: Union[int,float]
            latitude: Union[int,float]
            transmittance: str
            detector: Detector

        @dataclass
        class Star:

            @dataclass
            class st_distance:
                min: Union[int,float]
                max: Union[int,float]

            @dataclass
            class st_wv:
                min: Union[int,float]
                max: Union[int,float]
                nbr: int
            
            distance: st_distance
            wavelength_array: st_wv
            spectrum_folder: str
            spectrum_desc: str
            crater_file: str

        @dataclass
        class Sky:

            @dataclass
            class sky_guide:
                alt: Union[int,float]
                az: Union[int,float]

            rotation: bool
            guide: sky_guide
            background: Optional[str] = None

        @dataclass
        class psf:
            method: Optional[str] = None
            file: Optional[str] = None
            pix_nbr: Optional[int] = None 
            size: Optional[Union[int,float]] = None
            seeing: Optional[Union[int,float]] = None
            wind: Optional[Union[int,float,list]] = None
            coeff: Optional[list] = None
            L0: Optional[Union[int,float]] = None

        telescope: Telescope
        star: Star
        sky: Sky
        PSF: Optional[psf] = None

    @dataclass
    class phase:
        
        Calib_File: str
        Phase_Noise: Union[int,float]
        Decay: Union[int,float]
        noise_scale: Union[int, float]
        

    @dataclass
    class electronic:
        template_time: Union[int,float]
        trigerinx: int
        point_nb: int

    @dataclass
    class output:
        save: str

    @dataclass
    class SimFile: 
        sim_file : str
        process_nb : Union[int, str]
        Photon_Generation: Photon
     
        Phase: Optional[phase] = None
        Electronic: Optional[electronic] = None
        Output: Optional[output] = None

    ta = TypeAdapter(SimFile)
    try: 
        ta.validate_python(config)
        return(config)
        
    except pydantic.ValidationError as e:
        print(e)



def FileRead(file):


    DATA = DataCheck(file)
    CONST = {}

    # Path to save results
    CONST['path'] = DATA['sim_file']

    # Processor nmber to use
    if type(DATA['process_nb']) == str:
        CONST['process_nb'] = mp.cpu_count()
    else:
        CONST['process_nb'] = DATA['process_nb'] 
    print('CPU number %i'%CONST['process_nb'])

    PhGen = DATA['Photon_Generation']
    Tel = PhGen['telescope']

    # Exposition duration
    CONST['exptime'] = Tel['exposition_time']

    # Telescope diameter
    CONST['diameter'] = Tel['diameter']

    # Telescope obscuration
    CONST['obscuration'] = Tel['obscuration']

    # Observation site latitude (in rad)
    CONST['latitude'] = Tel['latitude'] * np.pi / 180

    # Trasnmittance
    CONST['transmittance'] = Tel['transmittance']

    # Pixel number on the detector
    CONST['pxnbr'] = Tel['detector']['pix_nbr']

    # Pixel size on the detector (in arcsec)
    CONST['pxsize'] = Tel['detector']['pix_size']

    # Detector surface (in arcsec2)
    S = (CONST['pxsize'] * CONST['pxnbr']) ** 2

    # Baseline of the signal
    CONST['baseline'] = Tel['detector']['baseline']

    # Prominence of the filter to detect photons on the signal
    CONST['peakprominence'] = Tel['detector']['peakprominence']

    # Map of pixels sensitivity
    CONST['weightmap'] = Tel['detector']['weightmap']

    # Number of point in a second
    CONST['timelinestep'] = Tel['detector']['point_nb']

    # Calibration type
    CONST['calibtype'] = Tel['detector']['calibration']

    # Number of wavelength used for calibration
    CONST['nbwv'] = Tel['detector']['nbwavelength']

    st = PhGen['star']

    # Number of star
    CONST['stnbr'] = int(S * 0.13)

    # Minimal distance for the star position
    CONST['stdistmin'] = st['distance']['min']

    # Maximal distance for the star position
    CONST['stdistmax'] = st['distance']['max']

    # Wavlength used to define the PSF
    CONST['wv'] = np.linspace(st['wavelength_array']['min'],
                              st['wavelength_array']['max'],
                              st['wavelength_array']['nbr'])
    
    # Folder with all spectrums
    CONST['spectrum'] = st['spectrum_folder']

    # Folder with spectrum description
    CONST['spectrum_desc'] = st['spectrum_desc']

    # Folder with caracteristic of spectrum in Crater 
    CONST['crater_file'] = st['crater_file']

    sky = PhGen['sky']

    # Incuding Earth rotation in the simulation
    CONST['rotation'] = sky['rotation']

    # Altitude of the point at the center of the observation (in rad)
    CONST['altguide'] = sky['guide']['alt'] * np.pi / 180

    # Azimuth of the point at the center of the observation (in rad)
    CONST['azguide'] = sky['guide']['az'] * np.pi / 180

    # Including light emission form the background stars
    try: CONST['background'] = sky['background']
    except: pass

    try: PhGen['PSF']
    except: pass
    else:
        psf = PhGen['PSF']

        # Method for the PSF
        CONST['psfmeth'] = psf['method']

        # File to save or to download the PSF
        CONST['psffile'] = psf['file']

        # PSF creation
        if CONST['psfmeth'] != 'Download':

            # Number of pixel on the PSF
            CONST['psfpxnbr'] = psf['pix_nbr']

            # Size of PSF pixels
            CONST['psfsize'] = psf['size']

            # PSF seeing 
            CONST['seeing'] = psf['seeing']

            # Wind velocity
            CONST['wind'] = psf['wind']

            # L0 value
            CONST['L0'] = psf['L0']

            # Coefficient for different wind layers
            CONST['coeff'] = psf['coeff'] 

    # File with claibration data
    CONST['conversion'] = DATA['Phase']['Calib_File']

    # Noise on phase detection
    CONST['nphase'] = DATA['Phase']['Phase_Noise']

    # Decreasing factor of photon phase
    CONST['decay'] = - DATA['Phase']['Decay']

    # Signal noise scale
    CONST['nreadoutscale'] = DATA['Phase']['noise_scale']

    # Number of point for the filter
    CONST['point_nb'] = DATA['Electronic']['point_nb']

    # Time for the template (in sec)
    CONST['templatetime'] = DATA['Electronic']['template_time']

    # At which time to simulate the pulse to create the filter
    CONST['trigerinx'] = DATA['Electronic']['trigerinx']

    return(CONST)
