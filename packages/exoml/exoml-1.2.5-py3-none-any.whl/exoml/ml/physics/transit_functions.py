import numpy

G = 6.67384e-11  # gravitational constant [m^3 / kg / s^2]
R_sun = 695508000  # radius of the Sun [m]
R_earth = 6371000  # radius of the Earth [m]
R_jup = 69911000  # radius of Jupiter [m]
M_sun = 1.989 * 10 ** 30  # mass of the Sun [kg]
SECONDS_PER_DAY = 86400


def t14(R_s, M_s, P, R_p=None, small_planet=False):
    """Planetary transit duration assuming a central transit on a circular orbit

    Parameters
    ----------
    R_s : float
        Stellar radius (in solar radii)
    M_s : float
        Stellar mass (in solar masses)
    P : float
        Planetary period (in days)
    small_planet : bool, default: `False`
        Small planet assumption if `True` (zero planetary radius). Otherwise, a
        planetary radius of 2 Jupiter radii is assumed (maximum reasonable planet size)

    Returns
    -------
    t14 : float
        Planetary transit duration (in days)
    """
    if R_p is not None:
        planet_size = R_sun * R_p
    elif small_planet:
        planet_size = 0
    else:
        planet_size = 2 * R_jup
    t14 = (
                  (R_sun * R_s + planet_size)
                  * (
                          (4 * P * SECONDS_PER_DAY)
                          / (numpy.pi * G * M_sun * M_s)
                  )
                  ** (1 / 3)
          ) / SECONDS_PER_DAY
    return t14