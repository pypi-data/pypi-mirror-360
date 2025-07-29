def wrinkling_airbus_compression_thin(sigma,k2,Ef,Ec,tf,tc):
    sigma_wr = k2*Ef*(((Ec*tf)/(Ef*tc))**(1/2))
    RF = sigma_wr/abs(sigma)
    return RF

def wrinkling_airbus_compression_thick(sigma,k1, Ef, Ec, Gc):
    sigma_wr = k1*((Ef*Ec*Gc)**(1/3))
    RF = sigma_wr/abs(sigma)
    return RF

def wrinkling_airbus_shear(tau, k3, E_45, Ec, Gc):
    tau_wr = k3 * ((E_45 * Ec * Gc) ** (1 / 3))
    RF = tau_wr/abs(tau)
    return RF

def wrinkling_airbus_biaxial(sigma_x, sigma_y, k1, Efx, Efy,Ec,Gc):
    if abs(sigma_x) >= abs(sigma_y):
        gamma = sigma_y/sigma_x
        Ef = Efx
        sigma_wr = k1 * ((Ef * Ec * Gc) ** (1 / 3)) / ((1 + gamma ** 3) ** (1 / 3))
        RF = sigma_wr / abs(sigma_x)
    else:
        gamma = sigma_x/sigma_y
        Ef = Efy
        sigma_wr = k1*((Ef*Ec*Gc)**(1/3))/((1+gamma**3)**(1/3))
        RF = sigma_wr/abs(sigma_y)

    return RF

def wrinkling_airbus_combined(sigma_x,sigma_y,tau_xy,k1,k3, Efx, Efy, E_45,Ec,Gc):
    if sigma_x == 0 and sigma_y == 0:
        RF_axial = 999999
    elif sigma_x == 0 and sigma_y != 0:
        RF_axial = wrinkling_airbus_compression_thick(sigma_y,k1,Efy,Ec,Gc)
    elif sigma_x != 0 and sigma_y == 0:
        RF_axial = wrinkling_airbus_compression_thick(sigma_x,k1,Efx,Ec,Gc)
    else:
        RF_axial = wrinkling_airbus_biaxial(sigma_x,sigma_y,k1,Efx,Efy,Ec,Gc)

    RF_shear = wrinkling_airbus_shear(tau_xy,k3,E_45,Ec,Gc)

    R_a = 1/RF_axial
    R_s = 1/RF_shear
    RF = 2/(R_a + ((R_a**2) + 4*(R_s**2))**(1/2))
    return RF
