import numpy as np
def compute_principal_stresses(Nx, Ny, Nxy):
    # Compute principal stresses
    N1 = (Nx + Ny) / 2 + np.sqrt(((Nx - Ny) / 2) ** 2 + Nxy ** 2)
    N2 = (Nx + Ny) / 2 - np.sqrt(((Nx - Ny) / 2) ** 2 + Nxy ** 2)

    # Cálculo del ángulo theta (en grados)
    theta_rad = 0.5 * np.arctan2(2 * Nxy, Nx - Ny)
    theta_deg = np.degrees(theta_rad)

    return N1, N2, theta_deg

def crimping_hypersizer_compression(N,G,tc):
    RF = abs(G*tc/N)
    return RF

def crimping_hypersizer_shear(Nxy,Gxz,Gyz,tc):
    N1 = Nxy
    theta_rad = np.radians(45)
    G_iz = (np.sin(theta_rad)**2)*Gxz + (np.cos(theta_rad)**2)*Gyz
    RF = abs(G_iz*tc/N1)
    return RF
def crimping_hypersizer_combined(Nx,Ny, Nxy, Gxz, Gyz,tc):
    # Compute principal stresses
    N1 = (Nx + Ny) / 2 + np.sqrt(((Nx - Ny) / 2) ** 2 + Nxy ** 2)
    # N2 = (Nx + Ny) / 2 - np.sqrt(((Nx - Ny) / 2) ** 2 + Nxy ** 2)

    # Compute theta
    theta_rad = 0.5 * np.arctan2(2 * Nxy, Nx - Ny)
    G_iz = (np.sin(theta_rad)**2)*Gxz + (np.cos(theta_rad)**2)*Gyz
    RF = abs(G_iz*tc/N1)
    return RF