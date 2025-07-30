import numpy as np
import matplotlib.pyplot as plt
from PyFRS import cgs,fs
if __name__ == '__main__':
    Z={ 'z':         0.1,              # Redshift
        'k':         0,                # Medium density profile index
        'SSC':       'No',             # SSC
        'XIC':       'No',             # EIC
        'E0':        1.e53,            # Isotropic-equivalent energy in erg
        'Gamma0':    2.,               # Initial bulk Lorentz factor
        'theta_j':   5.,               # Jet opening angle
        'theta_obs': 2.8,              # Viewing angle in deg
        'n18':       1.,               # CNM density at 10^18cm
        'p':         2.2,              # Electron energy distribution index
        'epsilon_e': 0.1,              # Fraction of the shock energy into electrons
        'epsilon_B': 0.01 }

    ta = 1.0e-1 * cgs.day
    tb = 1.0e3 * cgs.day
    t = np.geomspace(ta, tb, num=100)

    nuR=np.empty(t.shape)
    nuO=np.empty(t.shape)
    nuX=np.empty(t.shape)

    nuR[:] = 6.0e9
    nuO[:] = 1.0e14
    nuX[:] = 1.0e18

    print("Calc Radio")
    FnuR = fs.FS_flux(t, nuR, **Z)
    print("Calc Optical")
    FnuO = fs.FS_flux(t, nuO, **Z)
    print("Calc X-ray")
    FnuX = fs.FS_flux(t, nuX, **Z)
    print("Plot")

    tday = t / cgs.day

    fig, ax = plt.subplots(1, 1)
    ax.plot(tday, FnuR, ls='-', label=r'$\nu=6$ GHz')
    ax.plot(tday, FnuO, ls='--', label=r'$\nu=10^{14}$ Hz')
    ax.plot(tday, FnuX, ls='-.', label=r'$\nu=10^{18}$ Hz')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel(r'$t$ (d)')
    ax.set_ylabel(r'$F_\nu$ (mJy)')
    ax.legend()
    fig.tight_layout()

    print("Saving lc_multi.png")
    fig.savefig("lc_multi.png")
    plt.close(fig)