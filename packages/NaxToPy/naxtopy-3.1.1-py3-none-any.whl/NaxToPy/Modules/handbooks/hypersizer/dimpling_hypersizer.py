def dimpling_hypersizer_compression(sigma, Ef, nu_xy, nu_yx, tf, s):
    sigma_dp = ((2*Ef)/(1-nu_xy*nu_yx)) * ((tf/s)**2)
    RF = sigma_dp/abs(sigma)
    return RF

def dimpling_hypersizer_biaxial(sigma_x, sigma_y, Efx, Efy, nu_xy, nu_yx, tf, s):
    sigma_dp_x = ((2*Efx)/(1-nu_xy*nu_yx)) * ((tf/s)**2)
    sigma_dp_y = ((2*Efy)/(1-nu_xy*nu_yx)) * ((tf/s)**2)
    sigma_dp = (abs(sigma_x)*sigma_dp_x + abs(sigma_y)*sigma_dp_y) / (abs(sigma_x)+abs(sigma_y))
    if s/tf > 15.63:
        n = 3
    else:
        n = 2 + ((15.63/(s/tf))**2)

    RF = sigma_dp/(((abs(sigma_x)**n) + (abs(sigma_y)**n))**(1/n))
    return RF

def dimpling_hypersizer_shear(sigma_x, sigma_y, tau_xy,Efx,Efy, nu_xy, nu_yx, tf,s):
    sigma_dp_x = ((2 * Efx) / (1 - nu_xy * nu_yx)) * ((tf / s) ** 2)
    sigma_dp_y = ((2 * Efy) / (1 - nu_xy * nu_yx)) * ((tf / s) ** 2)
    sigma_dp = (abs(sigma_x)*sigma_dp_x + abs(sigma_y)*sigma_dp_y) / (abs(sigma_x)+abs(sigma_y))

    RF = 0.8*sigma_dp/abs(tau_xy)
    return RF

def dimpling_hypersizer_combined(sigma_x, sigma_y,tau_xy,Efx, Efy, nu_xy, nu_yx,tf,s):
    sigma_dp_x = ((2 * Efx) / (1 - nu_xy * nu_yx)) * ((tf / s) ** 2)
    sigma_dp_y = ((2 * Efy) / (1 - nu_xy * nu_yx)) * ((tf / s) ** 2)

    abs_sigma_x = abs(sigma_x)
    abs_sigma_y = abs(sigma_y)
    abs_tau_xy = abs(tau_xy)

    if sigma_x < 0 and sigma_y < 0:
        sigma_dp = (abs_sigma_x * sigma_dp_x + abs_sigma_y * sigma_dp_y) / (abs_sigma_x + abs_sigma_y)
        if s/tf > 15.63:
            n = 3
        else:
            n = 2 + ((15.63/(s/tf))**2)
        Ra = (((abs(sigma_x)**n) + (abs(sigma_y)**n))**(1/n))/sigma_dp

    elif sigma_x < 0:
        sigma_dp = sigma_dp_x
        Ra = abs_sigma_x/sigma_dp
    elif sigma_y < 0:
        sigma_dp = sigma_dp_y
        Ra = abs_sigma_y/sigma_dp
    else:
        return dimpling_hypersizer_shear(sigma_x, sigma_y, tau_xy, Efx, Efy, nu_xy, nu_yx,tf,s)

    Rs = abs_tau_xy/(0.8*sigma_dp)
    RF = 2 / (Ra + ((Ra ** 2 + 4 * Rs ** 2) ** 0.5))

    return RF