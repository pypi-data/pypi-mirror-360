def wrinkling_hypersizer_isotropic(sigma, Ef, Ec, Gc, k1):
    sigma_wr = k1*((Ef*Ec*Gc)**(1/3))
    RF = abs(sigma_wr/sigma)
    return RF

def wrinkling_hypersizer_honeycomb(sigma, Ef, Ec, tf,tc, k2):
    sigma_wr = k2*Ef*((Ec*tf/(Ef*tc))**(0.5))
    RF = abs(sigma_wr/sigma)
    return RF

def wrinkling_hypersizer_composite(sigma, Efx, Efy, tf,Ec, tc, nu_xy, nu_yx,k3):
    sigma_wr = k3*((2*tf*Ec*((Efx*Efy)**(1/2)))/(3*tc*(1-nu_xy*nu_yx)))**(1/2)
    RF = abs(sigma_wr/sigma)
    return RF

def wrinkling_hypersizer_composite_biaxial(sigma_x, sigma_y,k2 ,Efx, Efy, tf, Ec, tc, core_type):
    if core_type == 'Honeycomb' and (abs(sigma_y) > abs(sigma_x)):
        K = 0.95
    else:
        K = 1
    sigma_wr_x = k2*Efx*((Ec*tf/(Efx*tc))**(0.5))
    sigma_wr_y = k2 * Efy * ((Ec * tf / (Efy * tc)) ** (0.5))
    sigma_wr = (abs(sigma_x)*sigma_wr_x + abs(sigma_y)*sigma_wr_y) / (abs(sigma_x)+abs(sigma_y))
    RF = K*sigma_wr/((abs(sigma_x)**3 + abs(sigma_y)**3)**(1/3))
    return RF

def wrinkling_hypersizer_composite_shear(tau_xy,k2, Efx, Efy, tf, Ec,tc):
    sigma_wr_x = k2 * Efx * ((Ec * tf / (Efx * tc)) ** (0.5))
    sigma_wr_y = k2 * Efy * ((Ec * tf / (Efy * tc)) ** (0.5))
    sigma_wr = min(sigma_wr_x,sigma_wr_y)
    RF = sigma_wr/abs(tau_xy)
    return RF

def wrinkling_hypersizer_composite_combined(sigma_x, sigma_y, tau_xy, k2, Efx, Efy, tf, Ec, tc, core_type):
    if core_type == 'Honeycomb' and (abs(sigma_y) > abs(sigma_x)):
        K = 0.95
    else:
        K = 1

    sigma_wr_x = k2 * Efx * ((Ec * tf / (Efx * tc)) ** 0.5)
    sigma_wr_y = k2 * Efy * ((Ec * tf / (Efy * tc)) ** 0.5)

    abs_sigma_x = abs(sigma_x)
    abs_sigma_y = abs(sigma_y)
    abs_tau_xy = abs(tau_xy)

    if sigma_x < 0 and sigma_y < 0:
        sigma_wr = (abs_sigma_x * sigma_wr_x + abs_sigma_y * sigma_wr_y) / (abs_sigma_x + abs_sigma_y)
        Ra = ((abs_sigma_x**3 + abs_sigma_y**3) ** (1/3)) / (K * sigma_wr)
    elif sigma_x < 0:
        sigma_wr = sigma_wr_x
        Ra = abs_sigma_x / (K * sigma_wr)
    elif sigma_y < 0:
        sigma_wr = sigma_wr_y
        Ra = abs_sigma_y / (K * sigma_wr)
    else:
        return wrinkling_hypersizer_composite_shear(tau_xy, k2, Efx, Efy, tf, Ec, tc)

    Rs = abs_tau_xy / sigma_wr
    RF = 2 / (Ra + ((Ra**2 + 4 * Rs**2) ** 0.5))

    return RF
