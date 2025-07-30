import numpy as np
from scipy.integrate import simpson

from .collapse_stats import PressSchechterModel, PeaksTheoryModel, NonLinearModel

class MassFunction:
    #def __init__(self, power_spectrum, mass_variance, statistics, K=10, C_c=0.25, gamma=0.36):
     #3   """
       # statistics: an instance of a statistics model class (e.g. PressSchechterModel),
        #"""
        #self.statistics = statistics

    def __init__(self, mass_variance, statistics, **kwargs):
        self.mass_variance = mass_variance
        self.power_spectrum = mass_variance.power_spectrum

        # statistics model can be a string or a model instance
        if isinstance(statistics, str):
            statistics = statistics.lower()
            model_map = {
                'press': PressSchechterModel,
                'peaks': PeaksTheoryModel,
                'nonlinear': NonLinearModel,
            }
        if isinstance(statistics, str):
            stats_key = statistics.lower()
            if stats_key != mass_variance.statistics.lower():
                raise ValueError(f"Inconsistent 'statistics': MassVariance has '{mass_variance.statistics}', "
                                f"but MassFunction received '{statistics}'.")
            if stats_key not in model_map:
                raise ValueError(f"Unknown statistics model '{statistics}'. Must be one of {list(model_map)}")
            self.statistics = model_map[stats_key](
                power_spectrum=self.power_spectrum,
                mass_variance=mass_variance,
                **kwargs
            )

        else:
            self.statistics = statistics
            # Optionally update its parameters with kwargs if it's already an object
            for key, value in kwargs.items():
                if hasattr(self.statistics, key):
                    setattr(self.statistics, key, value)

    def evaluate(self, k_values, mpbh_vals=50):
        """
        Compute the mass function f(M) by passing k_values to the statistics model.

        Parameters
        ----------
        k_values : np.ndarray
            Array of k modes used to define the power spectrum and smoothing.

        Returns
        -------
        m : np.ndarray
            PBH masses.
        f_m : np.ndarray
            Corresponding PBH mass function f(M).
        """
        return self.statistics.evaluate(k_values, mpbh_vals)

    def fpbh(self, fofm, m):
        m, fofm = m[~np.isnan(fofm)], fofm[~np.isnan(fofm)]
        return simpson(fofm/m, m)
