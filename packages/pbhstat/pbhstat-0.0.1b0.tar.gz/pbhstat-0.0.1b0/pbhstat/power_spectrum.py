import numpy as np
from scipy.interpolate import interp1d

class PowerSpectrum:
    def __init__(self,
                 shape: str = None,
                 amplitude: float = None,
                 k_star: float = None,
                 sigma_ln: float = None,
                 k_min: float = None,
                 k_max: float = None,
                 ng: float = None,
                 nd: float = None,
                 min_amplitude: float = 2e-9,
                 k_values: np.ndarray = None,
                 P_k_values: np.ndarray = None):
        """
        Parameters:
        - shape: str, type of power spectrum ('delta', 'flat', 'piecewise', or 'custom')
        - amplitude: float, overall normalization A
        - k_star: float, peak or transition scale
        - k_min, k_max: float, used in flat spectrum
        - ng: float, slope for k < k_star in piecewise shape
        - nd: float, slope for k > k_star in piecewise shape
        - min_amplitude: float, minimum cutoff to avoid zero power
        - k_values, P_k_values: optional arrays to define a custom power spectrum
        """
        self.shape = shape
        self.amplitude = amplitude
        self.k_star = k_star
        self.sigma_ln = sigma_ln
        self.k_min = k_min
        self.k_max = k_max
        self.ng = ng
        self.nd = nd
        self.min_amplitude = min_amplitude

        if k_values is not None and P_k_values is not None:
            if len(k_values) != len(P_k_values):
                raise ValueError("k_values and P_k_values must have the same length")
            self.k_values = k_values
            self.P_k_values = P_k_values
            self.interpolator = interp1d(np.log(k_values), np.log(P_k_values),
                                         bounds_error=False, fill_value=-np.inf)
        else:
            self.k_values = None
            self.P_k_values = None
            self.interpolator = None

    def __call__(self, k: np.ndarray) -> np.ndarray:
        if self.shape == "custom":
            if self.interpolator is None:
                raise ValueError("Interpolator is not defined for custom shape")
            return np.exp(self.interpolator(np.log(k)))

        return self.generate_P_k(k)

    def generate_P_k(self, k: np.ndarray) -> np.ndarray:
        A = self.amplitude
        k_star = self.k_star
        k_min = self.k_min
        k_max = self.k_max

        if self.shape == "delta":
            # δ(k - k_star) approximation using a narrow log-normal bump
            if None in (A, k_star):
                raise ValueError("Amplitude and k_star must be specified for flat shape")
            sigma = 0.001
            return A * np.exp(-0.5 * (np.log(k / k_star) / sigma) ** 2)

        elif self.shape == "flat":
            # Top-hat in log-space
            if None in (A, k_min, k_max):
                raise ValueError("Amplitude, k_min and k_max must be specified for flat shape")
            mask = (k >= k_min) & (k <= k_max)
            return A * mask.astype(float)

        elif self.shape == "piecewise":
            if None in (A, k_star, self.ng, self.nd):
                raise ValueError("Amplitude, k_star, n_g and n_d must be specified for piecewise shape")
            power_spectrum = np.piecewise(
                k,
                [k <= k_star, k > k_star],
                [lambda k: (k / k_star) ** self.ng,
                 lambda k: (k / k_star) ** -self.nd],
            )
            return A * np.maximum(power_spectrum, self.min_amplitude)

        elif self.shape == "lognormal":
            if None in (A, k_star, self.sigma_ln):
                raise ValueError("Amplitude, k_star and sigma_ln must be specified for lognormal shape")
            return A * np.exp(-0.5 * (np.log(k / k_star) / self.sigma_ln) ** 2)


        else:
            raise ValueError(f"Unknown power spectrum shape: {self.shape}")
