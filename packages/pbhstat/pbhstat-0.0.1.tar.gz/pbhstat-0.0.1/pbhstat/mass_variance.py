import numpy as np
from scipy.interpolate import interp1d

class MassVariance:
    def __init__(self, window, power_spectrum, statistics=None, cutoff=False):
        """
        Initialize with a window function and a required power spectrum object.
        """
        self.window = window
        self.power_spectrum = power_spectrum
        self.statistics = statistics
        self.cutoff = cutoff

        if statistics == 'nonlinear' and self.window != "realtophat":
            raise ValueError('Must select real top hat window function for non-linear statistics')

    def window_function(self, k, R):
        """
        Computes the window function based on the chosen type ('gaussian', 'realtophat', etc.).
        """
        x = k * R

        if self.window == 'gaussian':
            return np.exp(-x**2 / 4)

        elif self.window == 'realtophat':
            if self.cutoff == True:
                result = 3 * (np.sin(x) - x * np.cos(x)) / x**3
                result = np.where(x > 4.49, 0.0, result)
                return result
            else:
                return 3 * (np.sin(x) - x * np.cos(x)) / x**3

        else:
            raise ValueError(f"Unknown window function: {self.window}")

    def evaluate(self, k_values):
        """
        Computes the integrand of the mass variance formula using explicit k_values.
        """
        kir_real = np.min(k_values)
        kuv_real = np.max(k_values)
        rir_real = 1 / kir_real
        rmin = 1 / kir_real
        rmax = 1 / kuv_real

        size = len(k_values)
        r = np.geomspace(rmin, rmax, size)
        k = k_values
        lnk = np.log(k)

        Pk = self.power_spectrum(k)

        sigma = {name: np.zeros_like(r) for name in [
            "sigma0", "sigma1peaks", "sigma1nl", "sigma2", "sigmaw",
            "sigmav", "sigmavg", "sigmagw", "sigmavw"]}

        pref = 16. / 81.

        for i in range(len(r)):
            kr = k * r[i]
            Wkr = self.window_function(k, r[i])
            Wkr2 = Wkr**2

            sigma["sigma0"][i] = pref * np.trapz(Wkr2 * kr**4 * Pk, lnk)
            sigma["sigma1peaks"][i] = pref * np.trapz(Wkr2 * kr**4 * k**2 * Pk, lnk)
            sigma["sigma1nl"][i] = pref * np.trapz(Wkr2 * kr**6 * Pk, lnk)
            sigma["sigma2"][i] = pref * np.trapz(Wkr2 * kr**8 * Pk, lnk)
            sigma["sigmaw"][i] = pref * np.trapz((Wkr * kr**4 - 2 * kr**2 * Wkr)**2 * Pk, lnk)
            sigma["sigmav"][i] = pref * np.trapz((3 * kr * np.sin(kr) - kr**2 * Wkr)**2 * Pk, lnk)
            sigma["sigmavg"][i] = pref * np.trapz((3 * kr * np.sin(kr) - kr**2 * Wkr) * Wkr * kr**2 * Pk, lnk)
            sigma["sigmagw"][i] = pref * np.trapz((kr**6 - 2 * kr**4) * Wkr2 * Pk, lnk)
            sigma["sigmavw"][i] = pref * np.trapz((3 * kr * np.sin(kr) - kr**2 * Wkr) * (Wkr * kr**4 - 2 * Wkr * kr**2) * Pk, lnk)

        sigma0f = interp1d(r, sigma["sigma0"], bounds_error=False, kind='cubic', fill_value="extrapolate")
        sigma1peaks = interp1d(r, sigma["sigma1peaks"], bounds_error=False, kind='cubic', fill_value="extrapolate")
        sigma1nl = interp1d(r, sigma["sigma1nl"], bounds_error=False, kind='cubic', fill_value="extrapolate")
        sigma2f = interp1d(r, sigma["sigma2"], bounds_error=False, kind='cubic', fill_value="extrapolate")
        sigmawf = interp1d(r, sigma["sigmaw"], bounds_error=False, kind='cubic', fill_value="extrapolate")
        sigmavf = interp1d(r, sigma["sigmav"], bounds_error=False, kind='cubic', fill_value="extrapolate")
        sigmavgf = interp1d(r, sigma["sigmavg"], bounds_error=False, kind='cubic', fill_value="extrapolate")
        sigmagwf = interp1d(r, sigma["sigmagw"], bounds_error=False, kind='cubic', fill_value="extrapolate")
        sigmavwf = interp1d(r, sigma["sigmavw"], bounds_error=False, kind='cubic', fill_value="extrapolate")

        if self.statistics == 'press':
            return sigma0f

        elif self.statistics == 'peaks':
            return sigma0f, sigma1nl

        elif self.statistics == 'nonlinear':
            return sigma0f, sigma1nl, sigma2f, sigmavf, sigmawf, sigmavgf, sigmagwf, sigmavwf

        else:
            raise ValueError(f"Unknown statistics option: {self.statistics}")
