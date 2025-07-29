import numpy as np
from scipy import interpolate
from astropy.coordinates import SkyCoord, EarthLocation, Angle, ICRS, FK5,AltAz
from astropy.timeseries import TimeSeries
from astropy.time import Time
from astropy import units as u


def Rotation(rotation, altguide, azguide, latitude, posx, posy, exptime, pxnbr, pxsize):
               
#   if rotation == True:
    guide_alt_az = [altguide,azguide]
    coo_star=[posx, posy]
    rot, evalt, alt_az_t, pos, star_ra_dec_t, alt_az_guide, ra_dec_guide = rot_with_pixel_scale(latitude, guide_alt_az, coo_star, exptime, pxsize, pxnbr)
   
#   else:
#     t = np.linspace(0,exptime,exptime+1 )
#     pos = [posx, posy]
#     rot = [interpolate.interp1d([0,exptime],[posx,posy]),interpolate.interp1d([0,exptime],[t,t])]
#     evalt = interpolate.interp1d([0,exptime],[np.pi/2,np.pi/2])
#     alt_az_guide =[altguide,azguide]
#     alt_az_t = alt_az_guide
#     star_ra_dec_t = [0,0,0]
    return(rot, evalt, alt_az_t, pos, star_ra_dec_t, alt_az_guide, ra_dec_guide)


def rot_with_pixel_scale(telescope_latitude_rad, 
        guide_star_altaz,
        offset_star_xy,
        duration_sec,
        pixel_scale_arcsec,
        pixel_nb):
    
    earth_rotation_rate = -7.292115*10**-5 # rad/s
    observer_location = EarthLocation(lon=17.89 * u.deg, 
                                      lat=telescope_latitude_rad * u.rad, 
                                      height=2200 * u.m)
    times = np.linspace(0, duration_sec, duration_sec + 1)
    observation_times = Time("2020-01-01 20:00:00", scale = 'utc', location = observer_location) + times * u.s

    alt, az = guide_star_altaz
   
    Xg, Yg, Zg = np.cos(alt) * np.cos(az), np.cos(alt) * np.sin(az), np.sin(alt)

    guide_vector = np.array([Xg, Yg, Zg])
    
    captor_size_rad = pixel_scale_arcsec/3600 * pixel_nb *np.pi/180
    S1_alt = np.random.uniform(alt-captor_size_rad/2, alt+captor_size_rad/2)
    S1_az = np.random.uniform(az-captor_size_rad/2, az+captor_size_rad/2)
    X1, Y1, Z1 = np.cos(S1_alt) * np.cos(S1_az), np.cos(S1_alt) * np.sin(S1_az), np.sin(S1_alt)
    S1 = [X1, Y1, Z1]

    R = np.array([
            [np.sin(alt)*np.cos(az), np.sin(alt)*np.sin(az),-np.cos(alt)],
            [-np.sin(az), np.cos(az), 0],
            [np.cos(alt)*np.cos(az), np.cos(alt)*np.sin(az),np.sin(alt)]
        ])

    S1prime = R@(S1-guide_vector) * 180/np.pi * 3600/pixel_scale_arcsec
    # print(S1prime[0], S1prime[1])
    
    altaz_guide_history = [] 
    current_alt = []
    current_az = []
    pos_guide = []
    pos_star = []
    
    current_az_star = []
    current_alt_star = []
    for i, t in enumerate(times):
        theta = earth_rotation_rate * t
        
        
        # Earth Rotation
        up = np.array([
                [np.cos(telescope_latitude_rad)**2 + np.sin(telescope_latitude_rad)**2 * np.cos(theta), -np.sin(telescope_latitude_rad) * np.sin(theta), (1 - np.cos(theta)) * np.cos(telescope_latitude_rad) * np.sin(telescope_latitude_rad)],
                [np.sin(telescope_latitude_rad) * np.sin(theta), np.cos(theta), -np.cos(telescope_latitude_rad) * np.sin(theta)],
                [(1 - np.cos(theta)) * np.cos(telescope_latitude_rad) * np.sin(telescope_latitude_rad), np.cos(telescope_latitude_rad) * np.sin(theta), np.sin(telescope_latitude_rad)**2 + np.cos(telescope_latitude_rad)**2 * np.cos(theta)]
            ])
        
        # Guide coordinate after rotation
        Sg_dt = up @ guide_vector
        Xg, Yg, Zg = Sg_dt
        current_alt.append(np.arcsin(Zg))
        current_az.append(np.arctan2(Yg, Xg))
        
        # Star coordinate after rotation
        S1_dt = up @ S1
        X1, Y1, Z1 = S1_dt
        current_alt_star.append(np.arcsin(Z1))
        current_az_star.append(np.arctan2(Y1, X1))

        R_dt = np.array([
            [np.sin(current_alt[-1])*np.cos(current_az[-1]), np.sin(current_alt[-1])*np.sin(current_az[-1]),-np.cos(current_alt[-1])],
            [-np.sin(current_az[-1]), np.cos(current_az[-1]), 0],
            [np.cos(current_alt[-1])*np.cos(current_az[-1]), np.cos(current_alt[-1])*np.sin(current_az[-1]),np.sin(current_alt[-1])]
        ])

        dec = np.arcsin(np.sin(telescope_latitude_rad) * np.sin(current_alt[-1]) + np.cos(telescope_latitude_rad)*np.cos(current_alt[-1])*np.cos(current_az[-1]))

        Sg_dt_prime = R_dt @ Sg_dt
        pos_guide.append([Sg_dt_prime[0]*np.cos(dec), Sg_dt_prime[1]])

        dec_star = np.arcsin(np.sin(telescope_latitude_rad) * np.sin(current_alt_star[-1]) + np.cos(telescope_latitude_rad)*np.cos(current_alt_star[-1])*np.cos(current_az_star[-1]))

        S1_dt_prime = R_dt @ ((S1_dt-Sg_dt))
        # pos_star.append([S1_dt_prime[0]*180/np.pi * 3600/pixel_scale_arcsec* np.cos(dec_star), S1_dt_prime[1]*180/np.pi * 3600/pixel_scale_arcsec ])
        pos_star.append([S1_dt_prime[0]*180/np.pi * 3600/pixel_scale_arcsec * np.cos(dec_star), S1_dt_prime[1]*180/np.pi * 3600/pixel_scale_arcsec ])

        # S1_dt_prime = R_dt @ (S1_dt-Sg_dt)
        # dec_star = np.arcsin(np.sin(telescope_latitude_rad) * np.sin(current_alt_star[-1]) + np.cos(telescope_latitude_rad)*np.cos(current_alt_star[-1])*np.cos(current_az_star[-1]))
        # pos_star.append([S1_dt_prime[0]*180/np.pi * 3600/pixel_scale_arcsec, S1_dt_prime[1]*180/np.pi * 3600/pixel_scale_arcsec * np.cos(dec)])
    pos_star = np.array(pos_star)
    altaz_guide_history = np.array(altaz_guide_history)
    
    ev_alt = interpolate.interp1d(times, current_alt_star)
    ev_x = interpolate.interp1d(times, pos_star[:,0])
    ev_y = interpolate.interp1d(times, pos_star[:,1])

    ra_dec_guide = []
    altaz_guide = []

    ra_dec_star = []
    altaz_star = []

    # SI = []

    for i in range(len(current_alt)):
        
        altaz_guide.append([current_alt[i], current_az[i], i])
        altaz_star.append([current_alt_star[i], current_az_star[i]])

    obs_time = Time("2020-01-01 20:00:00", scale = 'utc')
    repere_altaz = AltAz(location = observer_location, obstime =obs_time)
    coord_altaz_guide = SkyCoord(alt = alt*u.rad, az = az*u.rad, frame = repere_altaz)
    coord_equ_guide = coord_altaz_guide.transform_to("icrs")
    ra_dec_guide.append([coord_equ_guide.ra.value*np.pi/180, coord_equ_guide.dec.value*np.pi/180])

    coord_altaz_star = SkyCoord(alt = altaz_star[0][0]*u.rad, az = altaz_star[0][1]*u.rad, frame = repere_altaz)
    coord_equ_star = coord_altaz_star.transform_to("icrs")
    ra_dec_star.append([coord_equ_star.ra.value*np.pi/180, coord_equ_star.dec.value*np.pi/180])

    #     dec = np.arcsin(np.sin(telescope_latitude_rad) * np.sin(current_alt[i]) + np.cos(telescope_latitude_rad)*np.cos(current_alt[i])*np.cos(current_az[i]))
    #     HA = np.arccos((np.sin(current_alt[i]) - np.sin(telescope_latitude_rad)*np.sin(dec))/(np.cos(telescope_latitude_rad)*np.cos(dec))) 

    #     dec_star = np.arcsin(np.sin(telescope_latitude_rad) * np.sin(current_alt_star[i]) + np.cos(telescope_latitude_rad)*np.cos(current_alt_star[i])*np.cos(current_az_star[i]))
    #     HA_star = np.arccos((np.sin(current_alt_star[i]) - np.sin(telescope_latitude_rad)*np.sin(dec_star))/(np.cos(telescope_latitude_rad)*np.cos(dec_star))) 

    #     SI.append(observation_times[i].sidereal_time(kind = 'apparent'))
        
    #     if current_alt[0] < np.max(current_alt) and current_alt[-1] < np.max(current_alt):
    #         meridian_alt = list(current_alt).index(np.max(current_alt))

    #         if i >= meridian_alt:
    #             ra = SI[i].value*15*np.pi/180 * u.rad + HA  * u.rad
    #         else:
    #             ra = SI[i].value*15*np.pi/180 * u.rad - HA * u.rad
    #     else:
    #         ra = SI[i].value*15*np.pi/180 * u.rad  - HA * u.rad
      
    #     if current_alt_star[0] < np.max(current_alt_star) and current_alt_star[-1] < np.max(current_alt_star):
    #         meridian_alt_star = list(current_alt_star).index(np.max(current_alt_star))
    #         if i >= meridian_alt_star:
    #             ra_star = SI[i].value*15*np.pi/180 * u.rad + HA_star *u.rad
    #         else:
    #             ra_star = SI[i].value*15*np.pi/180 * u.rad  - HA_star *u.rad
    #     else: 
    #        ra_star = SI[i].value*15*np.pi/180 * u.rad  - HA_star *u.rad

    #     ra_dec_history.append([ra.value , dec])
    #     ra_dec_star_history.append([ra_star.value , dec_star])
    return ([ev_x, ev_y], ev_alt,altaz_star, pos_star, ra_dec_star, altaz_guide, ra_dec_guide)