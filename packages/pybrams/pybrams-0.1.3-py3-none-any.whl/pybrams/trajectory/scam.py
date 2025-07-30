import numpy as np
from tqdm import tqdm
from typing import Optional
import matplotlib.pyplot as plt

from pybrams.utils import Config


# Adapted and extended from an implementation of Daniel Kastinen


class Scam:
    """Markov Chain Monte Carlo sampling of the posterior,
    assuming all measurement errors are Gaussian (thus the log likelihood
    becomes a least squares).
    """

    OPTIONS = {
        "accept_max": Config.get(__name__, "accept_max"),
        "accept_min": Config.get(__name__, "accept_min"),
        "adapt_interval": Config.get(__name__, "adapt_interval"),
        "proposal_adapt_interval": Config.get(__name__, "proposal_adapt_interval"),
        "tune": Config.get(__name__, "tune"),
        "proposal": Config.get(__name__, "proposal"),
        "progress_bar": Config.get(__name__, "progress_bar"),
    }

    def __init__(self, base_step_size, **kwargs):
        self.base_step_size = base_step_size
        self.options = {}
        self.options.update(self.OPTIONS)
        self.options.update(kwargs)

    def run(self, posterior, start, steps, constraints, seed=None):
        if seed is not None:
            seed_state = np.random.seed()
            np.random.seed(seed)
        xnow = np.copy(start)
        step = np.copy(self.base_step_size)

        n_var = len(start)

        run_steps = self.options["tune"] + steps
        chain = np.empty((n_var, run_steps), dtype=np.float64)

        logpost = posterior(xnow)

        accept = np.zeros((n_var,), dtype=np.float64)
        tries = np.zeros((n_var,), dtype=np.float64)

        proposal_mu = np.zeros((n_var,), dtype=np.float64)

        if self.options["proposal"] in ["normal", "adaptive"]:
            proposal_cov = np.eye(n_var, dtype=np.float64)
            proposal_axis = np.eye(n_var, dtype=np.float64)

        if self.options["proposal"] == "custom":
            proposal_cov = self.options["proposal_cov"]
            _, proposal_axis = np.linalg.eig(proposal_cov)

        else:
            raise ValueError(
                f'proposal option "{self.options["proposal"]}"\
                not recognized'
            )

        if self.options["progress_bar"]:
            pbar = tqdm(position=0, total=run_steps)

        ind = 0
        while ind < run_steps:
            xtry = np.copy(xnow)

            pi = int(np.floor(np.random.rand(1) * n_var))

            proposal0 = np.random.multivariate_normal(proposal_mu, proposal_cov)
            proposal = proposal0[pi] * proposal_axis[:, pi]

            xtry += proposal * step[pi]

            if not constraints(xtry):
                continue

            if self.options["progress_bar"]:
                pbar.update(1)
                pbar.set_description(
                    "Sampling log-posterior = {:<10.3f} ".format(logpost)
                )

            logpost_try = posterior(xtry)
            alpha = np.log(np.random.rand(1))

            if logpost_try > logpost:
                _accept = True
            elif (logpost_try - alpha) > logpost:
                _accept = True
            else:
                _accept = False

            tries[pi] += 1.0

            if _accept:
                logpost = logpost_try
                xnow = xtry
                accept[pi] += 1.0

            ad_inv = self.options["adapt_interval"]
            cov_ad_inv = self.options["proposal_adapt_interval"]
            ac_min = self.options["accept_min"]
            ac_max = self.options["accept_max"]

            if ind % ad_inv == 0 and ind > 0:
                for var_ind in range(n_var):
                    ratio = accept[var_ind] / tries[var_ind]

                    if ratio > ac_max:
                        step[var_ind] *= 2.0

                    elif ratio < ac_min:
                        step[var_ind] /= 2.0

                    accept[var_ind] = 0.0
                    tries[var_ind] = 0.0

            if (
                ind % cov_ad_inv == 0
                and ind > 0
                and self.options["proposal"] == "adaptive"
            ):
                _data = chain[:, :ind]
                _proposal_cov = np.corrcoef(_data)

                if not np.any(np.isnan(_proposal_cov)):
                    eigs, proposal_axis = np.linalg.eig(_proposal_cov)
                    proposal_cov = np.diag(eigs)

            chain[:, ind] = xnow
            ind += 1

        if seed is not None:
            np.random.seed(seed_state)

        return chain


def rhat(chains):
    """
    Calculate the Gelman-Rubin R-hat statistic for MCMC chains.

    Parameters:
    - chains (ndarray): A 2D NumPy array with shape (n_chains, n_samples),
                        where each row represents a chain.

    Returns:
    - float: The R-hat statistic.
    """
    n_chains, n_samples = chains.shape

    # Calculate the mean within each chain
    chain_means = np.mean(chains, axis=1)

    # Calculate the between-chain variance (B)
    B = n_samples * np.var(chain_means, ddof=1)

    # Calculate the within-chain variance (W)
    W = np.mean(np.var(chains, axis=1, ddof=1))

    # Estimate the variance of the target distribution (V-hat)
    V_hat = (W * (n_samples - 1) / n_samples) + (B / n_samples)

    # Calculate the R-hat statistic
    R_hat = np.sqrt(V_hat / W)

    return R_hat


def plot_chain_autocorr(chain, max_k=None):
    param_names = [
        r"$x_0$ [km]",
        r"$y_0$ [km]",
        r"$z_0$ [km]",
        r"$v_x$ [km/s]",
        r"$v_y$ [km/s]",
        r"$v_z$ [km/s]",
    ]

    fig, axes = plt.subplots(chain.shape[0], 1, figsize=(8, 15))
    if max_k == None or max_k > chain.shape[1]:
        max_k = chain.shape[1]
    Kv, MC_gamma = autocovariance(chain, min_k=0, max_k=max_k, number_k=1000)
    flat_ax = axes.flatten()
    for vari in range(chain.shape[0]):
        ax = flat_ax[vari]
        ax.grid()
        ax.plot(Kv, MC_gamma[vari, :] / MC_gamma[vari, 0])
        ax.set(
            xlabel="Number of samples",
            ylabel="$\\hat{\\gamma}_k/\\hat{\\gamma}_0$",
            title=f"Autocorrelation for {param_names[vari]}",
        )
    plt.tight_layout()
    plt.show()


def autocovariance(
    chain: np.ndarray,
    max_k: Optional[int] = None,
    min_k: Optional[int] = None,
    number_k: Optional[int] = None,
) -> np.ndarray:
    """Calculate the natural estimator of the autocovariance function of a Markov chain.

    The autocovariance function is defined as
    $$
        \\gamma_k = cov(g(X_i), g(X_{i + k}))
    $$
    where $g$ is a real-valued function on the state space and $X_j$ is a sample of the
    Markov chain in that state space.

    The natural estimator of the autocovariance function and the mean is
    $$
        \\gamma_k = \\frac{1}{n} \\sum_{i=1}^{n - k} 
            (g(X_i) - \\hat{\\mu}_n)(g(X_{i + k) - \\hat{\\mu}_n), \\\\
        \\hat{\\mu}_n = \\frac{1}{n} \\sum_{i=1}^{n} g(X_i)
    $$

    Parameters
    ----------
    chain : np.ndarray
        The Markov chain represented as a (N, M) matrix where N is the number of dimensions
        and M is the number of steps
    max_k : optional, int
        The maximum autocorrelation length
    min_k : optional, int
        The minimum autocorrelation length

    Returns
    -------
    float or numpy.ndarray
        autocovariance function between $k_min$ and $k_max$ [1]

    """
    _n = chain.shape[1]
    dims = chain.shape[0]

    if max_k is None:
        max_k = _n
    else:
        if max_k >= _n:
            max_k = _n

    if min_k is None:
        min_k = 0
    else:
        if min_k >= _n:
            min_k = _n - 1

    if number_k is None:
        number_k = max_k - min_k

    gamma = np.empty(
        (
            dims,
            number_k,
        ),
        dtype=chain.dtype,
    )
    mu = np.mean(chain, axis=1)
    k_vector = np.linspace(min_k, max_k, number_k, dtype=int)

    for vari in range(dims):
        for index_k, k in enumerate(k_vector):
            covi = chain[vari, : (_n - k)] - mu[vari]
            covik = chain[vari, k:] - mu[vari]
            autocov = np.sum(covi * covik)
            gamma[vari, index_k] = autocov / _n

    return k_vector, gamma
