from PyFRS import fs
import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':
    t = np.geomspace(1.e3, 1.e7, 300)
    nu = np.empty(t.shape)
    nu[:] = 1.e9
    Z = {'z': 0.1,  # Redshift
         'k': 0,  # Medium density profile index
         'SSC': 'No',  # SSC
         'XIC': 'No',  # EIC
         'E0': 1.e53,  # Isotropic-equivalent energy in erg
         'Gamma0': 2.,  # Initial bulk Lorentz factor
         'theta_j': 5.,  # Jet opening angle
         'theta_obs': 2.8,  # Viewing angle in deg
         'n18': 1.,  # CNM density at 10^18cm
         'p': 2.2,  # Electron energy distribution index
         'epsilon_e': 0.1,  # Fraction of the shock energy into electrons
         'epsilon_B': 0.01}
    Fnu = fs.FS_flux(t, nu, **Z)
    plt.plot(np.log10(t), np.log10(Fnu))
    fig, ax = plt.subplots(1, 1)
    ax.plot(t, Fnu)
    ax.set(xscale='log', xlabel=r'$t$ (s)',
           yscale='log', ylabel=r'$F_\nu$[$10^{9}$ Hz] (mJy)')

    fig.tight_layout()
    print("Saving figure lc.png")
    fig.savefig("lc1.png")
    plt.close(fig)
