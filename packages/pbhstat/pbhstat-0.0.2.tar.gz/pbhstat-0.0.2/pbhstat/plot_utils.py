import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator, FormatStrFormatter
import pickle

plt.rcParams.update({
"text.usetex": False,
"font.family": "serif",
"font.sans-serif": ["TimesNewRoman"]})
plt.rcParams["mathtext.fontset"] = "stix"

# Helper functions for plotting main quantities

def plot_power_spectrum(k_vals, p_k):

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(8, 6))

    # Plot the custom power spectrum
    ax.loglog(k_vals, p_k, label=r"$\mathcal{P}_\zeta(k)$", color="navy", lw=2)

    # Axis labels and title
    ax.set_xlabel(r"$k$ [$\mathrm{Mpc}^{-1}$]", fontsize=14)
    ax.set_ylabel(r"$\mathcal{P}_\zeta(k)$", fontsize=14)
    ax.set_title("Initial Power Spectrum", fontsize=14)

    # Ticks
    ax.tick_params(axis='both', which='major', labelsize=14)
    ax.xaxis.set_major_locator(LogLocator(base=10.0, numticks=10))
    ax.yaxis.set_major_locator(LogLocator(base=10.0, numticks=10))
    ax.xaxis.set_minor_formatter(FormatStrFormatter(""))

    # Layout
    plt.tight_layout()
    plt.savefig('powerspectrum.pdf')
    plt.show()

def plot_mass_variance(r_vals, sigma):
    if isinstance(sigma, tuple):
        sigma_vals = sigma[0](r_vals)
    else: 
        sigma_vals = sigma(r_vals)


    # Create figure and axis
    fig, ax = plt.subplots(figsize=(8, 6))

    # Plot the mass variance
    ax.loglog(r_vals, sigma_vals, color='darkgreen', lw=2)

    # Axis labels and title
    ax.set_xlabel(r"$R$ [$\mathrm{Mpc}$]", fontsize=14)
    ax.set_ylabel(r"$\sigma^2(R)$", fontsize=14)
    ax.set_title("Mass Variance", fontsize=14)

    # Ticks
    ax.xaxis.set_major_locator(LogLocator(base=10.0, numticks=10))
    ax.yaxis.set_major_locator(LogLocator(base=10.0, numticks=10))
    ax.xaxis.set_minor_formatter(FormatStrFormatter(""))

    # Layout
    plt.tight_layout()
    plt.savefig('massvariance.pdf')
    plt.show()

def plot_mass_function(m_vals, f_m_vals, fpbh_val = None):
    fig, ax = plt.subplots(figsize=(8, 6))

    # Plot the mass function
    ax.loglog(m_vals, f_m_vals, label=r"$f_{\rm PBH}(M)$", color="crimson", lw=2)

    # Set limits
    #ax.set_ylim(1e-5, 1)

    # Axis labels and title
    ax.set_xlabel(r"$M_{\rm PBH}$ [$M_\odot$]", fontsize=14)
    ax.set_ylabel(r"$f\,(M)$", fontsize=14)
    ax.set_title("Primordial Black Hole Mass Function", fontsize=14)

    # Ticks
    ax.xaxis.set_major_locator(LogLocator(base=10.0, numticks=10))
    ax.yaxis.set_major_locator(LogLocator(base=10.0, numticks=10))
    ax.xaxis.set_minor_formatter(FormatStrFormatter(""))
    
    if fpbh_val is not None:
        ax.text(m_vals.min(), f_m_vals.max(), rf"$f_{{\rm PBH}} = {fpbh_val:.2e}$", fontsize=12, color="black",
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'))
    
    plt.tight_layout()
    plt.savefig('massfunction.pdf')
    plt.show()

def bounds_utility(m_vals, f_m_vals, path_to_pbhbounds):
    np.savetxt(path_to_pbhbounds + 'm_array.txt', m_vals)
    np.savetxt(path_to_pbhbounds + 'f_array.txt', f_m_vals)
    return None
