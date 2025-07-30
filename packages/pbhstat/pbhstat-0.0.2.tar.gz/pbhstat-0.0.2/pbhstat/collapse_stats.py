import numpy as np
from matplotlib import pyplot as plt
import tqdm

from .constants import OmegaCDM, Meq, req, geq

from .stats_utils import (
    C, fs, initialize_gcf, gamma_f, barg, sigmawtildef, bargfull,
    Sigmagf, Mmax, find_peak_range_indices
)

class PressSchechterModel:
    def __init__(self, power_spectrum, mass_variance, K, C_c, gamma=0.36):
        self.power_spectrum = power_spectrum
        self.mass_variance = mass_variance
        self.K = K
        self.gamma = gamma
        self.C_c = C_c

        if self.mass_variance.window == 'gaussian' and (K != 10 or C_c != 0.28):
            print('Warning: Gaussian window function typically uses K=10 and C_c=0.28')
        if self.mass_variance.window == 'realtophat' and (K != 4 or C_c != 0.77):
            print('Warning: Top hat window function typically uses K=4 and C_c=0.77')

    def mu(self, mh, mbh):
        return mbh / (self.K * mh)

    def C(self, mh, mbh):
        return self.mu(mh, mbh) ** (1 / self.gamma) + self.C_c

    def P(self, C_val, sigma_sq):
        return (1 / np.sqrt(2 * np.pi * sigma_sq)) * np.exp(-C_val**2 / (2 * sigma_sq))

    def beta_mh_integrand(self, mh, mbh, sigma_func):
        mu_val = self.mu(mh, mbh)
        C_val = self.C(mh, mbh)
        R = np.sqrt(mh / Meq) * req  # Inverting MH = Meq * (R/req)^2
        sigma_sq = sigma_func(R)
        prefactor = (1 / OmegaCDM) * np.sqrt(Meq / mh) # prev 1/2^(5/2) at front
        return prefactor * mu_val**(1 / self.gamma) * (mbh / (self.gamma * mh**2)) * self.P(C_val, sigma_sq)

    def evaluate(self, k_values, mpbh_vals):

        klow, khigh = min(k_values), max(k_values)
        rlow, rhigh = 1 / khigh, 1 / klow

        # Arrays for integration
        r_array = np.geomspace(rlow, rhigh, 3000)
        MH_array = Meq * (r_array / req)**2

        sigma_func = self.mass_variance.evaluate(k_values)  # interpolator σ2(R)

        MPBH = np.geomspace(min(MH_array) * 10, max(MH_array), mpbh_vals)
        fm_vals = np.zeros_like(MPBH)

        for i, mbh in enumerate(MPBH):
            integrand = self.beta_mh_integrand(MH_array, mbh, sigma_func)
            fm_vals[i] = np.trapz(integrand, MH_array)

        return MPBH, fm_vals

class PeaksTheoryModel:
    def __init__(self, power_spectrum, mass_variance, K, C_c, gamma=0.36):
        self.power_spectrum = power_spectrum
        self.mass_variance = mass_variance
        self.K = K
        self.gamma = gamma
        self.C_c = C_c

        if mass_variance.window == 'gaussian' and (K != 10 or C_c != 0.28):
            print('Warning: Gaussian window function usually takes K=10, C_c=0.28')
        if self.mass_variance.window == 'realtophat' and (K != 4 or C_c != 0.77):
            print('Warning: Top hat window function typically uses K=4 and C_c=0.77')

    def evaluate(self, k_values, mpbh_vals):
        sigma0f, sigma1f = self.mass_variance.evaluate(k_values)

        k_low = min(k_values)
        k_high = max(k_values)
        r_low = 1 / k_high
        r_high = 1 / k_low

        r_array = np.geomspace(r_low, r_high, 3000)
        MH_array = Meq * (r_array / req)**2

        MPBH = np.geomspace(min(MH_array) * 10, max(MH_array), mpbh_vals)

        def mu(mh, mbh):
            return mbh / (self.K * mh)

        def C(mh, mbh):
            return mu(mh, mbh)**(1 / self.gamma) + self.C_c

        def nu(mh, mbh, sig0):
            R = np.sqrt(mh / Meq) * req
            return C(mh, mbh) / np.sqrt(sig0(R))

        def npeaks(mh, mbh, sig0, sig1):
            R = np.sqrt(mh / Meq) * req 
            ratio = np.sqrt(sig1(R) / sig0(R))
            n = nu(mh, mbh, sig0)
            return (1 / (3**1.5 * (2 * np.pi)**2)) * ratio**3 * n**3 * np.exp(-0.5 * n**2)

        def beta_integrand_old(mh, mbh, sig0, sig1):
            R = np.sqrt(mh / Meq) * req 
            mu_val = mu(mh, mbh)
            n_peak = npeaks(mh, mbh, sig0, sig1)
            if self.mass_variance.window == 'gaussian':
                b_pref = (2 * np.pi)**1.5
            else: b_pref = 4 * np.pi/3
            prefactor = (1/np.sqrt(2)) * (1 / OmegaCDM) * b_pref
            return prefactor * (req**3 / Meq) * (mbh / (self.gamma * mh)) * mu_val**(1 / self.gamma) * n_peak

        def beta_integrand(mh, mbh, sig0, sig1):
            R = np.sqrt(mh / Meq) * req 
            mu_val = mu(mh, mbh)
            n_peak = npeaks(mh, mbh, sig0, sig1)
            if self.mass_variance.window == 'gaussian':
                b_pref = (2 * np.pi)**1.5
            else: b_pref = 4 * np.pi/3
            prefactor = (1/2) * (1 / OmegaCDM) * b_pref
            return prefactor * np.sqrt(Meq/mh**3) * (mbh / (self.gamma * mh)) * mu_val**(1 / self.gamma) * n_peak
        
        fm_vals = np.zeros_like(MPBH)
        for i, mbh in enumerate(MPBH):
            integrand_vals = beta_integrand(MH_array, mbh, sigma0f, sigma1f)
            fm_vals[i] = np.trapz(integrand_vals, MH_array)

        return MPBH, fm_vals

class NonLinearModel:
    def __init__(self, power_spectrum, mass_variance, K, gamma=0.36, vcorr=True):
        self.power_spectrum = power_spectrum
        self.mass_variance = mass_variance
        self.K = K
        self.gamma = gamma
        self.vcorr = vcorr

        if mass_variance.window == 'gaussian' and (K != 10):
            print('Warning: Gaussian window function usually takes K=10')
        if self.mass_variance.window == 'realtophat' and (K != 4):
            print('Warning: Top hat window function typically uses K=4')

    def evaluate(self, k_values, mpbh_vals):
        ps = self.power_spectrum(k_values)
        sigma0f, sigma1f, sigma2f, sigmavf, sigmawf, sigmavgf, sigmagwf, sigmavwf = self.mass_variance.evaluate(k_values)

        k_low = min(k_values)
        k_high = max(k_values)

        idx_min, idx_max = find_peak_range_indices(ps, threshold_factor=0.01)

        kir_real = k_values[idx_min]
        kuv_real = k_values[idx_max]
        alpha = kuv_real / kir_real

        rir_real = 1 / k_low
        ruv_real = 1 / kuv_real

        r_array = np.geomspace(ruv_real, rir_real, 3000)
        MH_array = Meq * (r_array / req)**2 
        LMH = np.log(MH_array)

        MPBH_array = np.geomspace(min(MH_array), max(MH_array), mpbh_vals)

        if alpha < 1.3:
            wmin = 0.1
            wmax =  (rir_real*kuv_real)**2 / (2 * np.log(alpha)) * 4/3 * 50
        else: # require larger wmax and smaller wmin for broad spectra
            wmin = 0.01
            wmax =  (rir_real*kuv_real)**2 / (2 * np.log(alpha)) * 4/3 * 1000 

        w_array = np.geomspace(wmin, wmax, 4000)

        gcf = initialize_gcf(wmax)

        def integrand_w(w, r, M, MH, vcorr=True):
            muj = M / (self.K * MH)
            pM = M / MH**(3/2)
            pv = 1 / np.sqrt(2 * np.pi * sigmavf(r))
            condition = 1 - 3/2 * C(gcf(w)) - 3/2 * muj**(1 / self.gamma)

            g = 4/3 * (1 - np.sqrt(np.abs(condition)))
            dgoverdlogM = 1 / (1 - 3/4 * g) * 1 / self.gamma * muj**(1 / self.gamma)

            ronrstar = (1/3 * sigma2f(r) / sigma1f(r))**(3/2)
            prefactor = 2/3 * np.pi / (2 * np.pi)**(3/2)

            factor_1 = prefactor * ronrstar * dgoverdlogM * fs((2 * g + w) / np.sqrt(sigma2f(r))) * pM * pv

            if self.vcorr:
                bg = bargfull(r, sigmavf, sigmagwf, sigmavwf, sigmavgf, sigmawf)
                sg = Sigmagf(r, sigma0f, sigmawf, sigmavf, sigmavgf, sigmagwf, sigmavwf)
                sw = sigmawtildef(r, sigmavf, sigmawf, sigmavwf)
                pg = np.exp(-(g - bg * w)**2 / (2 * sg)) / np.sqrt(2 * np.pi * sg)
                pw = np.exp(-w**2 / (2 * sw)) / np.sqrt(2 * np.pi * sw)
            else:
                bg = barg(r, sigmagwf, sigmawf)
                sg = sigma0f(r)
                sw = sigmawf(r)
                gam = gamma_f(r, sigmagwf, sigma0f, sigmawf)
                pg = np.exp(-(g - bg * w)**2 / (2 * sg * (1 - gam**2))) / np.sqrt(2 * np.pi * sg * np.sqrt((1 - gam**2)**2))
                pw = np.exp(-w**2 / (2 * sw)) / np.sqrt(2 * np.pi * sw)

            return np.where(condition > 0, factor_1 * w * pg * pw, 0)

        integrand_mh = np.zeros([len(MH_array), len(MPBH_array)])
        fm_vals = np.zeros_like(MPBH_array)

        for j in tqdm.tqdm(range(len(MPBH_array)), desc="Evaluating NonLinearModel"):
            for i in range(len(MH_array)):
                integrand_mh[i, j] = np.trapz(integrand_w(w_array, r_array[i], MPBH_array[j], MH_array[i], self.vcorr), w_array) + 1e-70
            fm_vals[j] = np.trapz(integrand_mh[:, j], LMH)

        return MPBH_array, fm_vals * np.sqrt(Meq)
