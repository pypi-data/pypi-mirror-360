import autograd.numpy as np

TX_COORD = np.array([0, 0, 0])
TX_FREQUENCY = 49.97 * 10**6  # [Hz]
SPEED_OF_LIGHT = 299792.458  # [km/s]
WAVELENGTH = SPEED_OF_LIGHT / TX_FREQUENCY  # [km]
