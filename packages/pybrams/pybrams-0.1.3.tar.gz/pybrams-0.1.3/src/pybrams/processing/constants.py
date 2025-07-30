import numpy as np
from scipy.special import erfcinv

SHORT_TO_FLOAT_FACTOR = 1 << 15

MAD_SCALE = -1 / (np.sqrt(2) * erfcinv(3 / 2))
MAD_FACTOR = 3
