def wriknling_cmh_honeycomb_thick(sigma,C1,C2,Ef,tf,Ec,tc,Gc):
    sigma_wr = C1*((Ef*Ec*Gc)**(1/3)) + C2*Gc*tc/tf
    RF = sigma_wr/abs(sigma)
    return RF

def wrinkling_cmh_honeycomb_thin(sigma,C3,C4,Ef,tf,Ec,tc,Gc):
    sigma_wr = C3*((Ef*Ec*tf/tc)**(1/2)) + C4*Gc*tc/tf
    RF = sigma_wr/abs(sigma)
    return RF

def wrinkling_cmh_honeycomb_biaxial_thick(sigma_x, sigma_y,C1,C2,Efx, Efy,tf,Ec,tc,Gc):
    sigma_wr_x = C1 * ((Efx * Ec * Gc) ** (1 / 3)) + C2 * Gc * tc / tf
    sigma_wr_y = C1 * ((Efy * Ec * Gc) ** (1 / 3)) + C2 * Gc * tc / tf

    if abs(sigma_x) > abs(sigma_y):
        RF = 1/(((abs(sigma_x)/sigma_wr_x)**3) + (abs(sigma_y)/sigma_wr_y))
    else:
        RF = 1 / (((abs(sigma_y) / sigma_wr_y) ** 3) + (abs(sigma_x) / sigma_wr_x))
    return RF

def wrinkling_cmh_honeycomb_biaxial_thin(sigma_x, sigma_y,C3,C4,Efx, Efy,tf,Ec,tc,Gc):
    sigma_wr_x = C3 * ((Efx * Ec * tf/tc) ** (1 / 2)) + C4 * Gc * tc / tf
    sigma_wr_y = C3 * ((Efy * Ec * tf/tc) ** (1 / 2)) + C4 * Gc * tc / tf

    if abs(sigma_x) > abs(sigma_y):
        RF = 1/(((abs(sigma_x)/sigma_wr_x)**3) + (abs(sigma_y)/sigma_wr_y))
    else:
        RF = 1 / (((abs(sigma_y) / sigma_wr_y) ** 3) + (abs(sigma_x) / sigma_wr_x))
    return RF