def wrinkling_nasa_1(sigma, Ef, Ec, Gc, k1):
    sigma_wr = k1*((Ef*Ec*Gc)**(1/3))
    RF = abs(sigma_wr/sigma)
    return RF

def wrinkling_nasa_2(sigma, Ef, Ec, tf,tc, k2):
    sigma_wr = k2*Ef*((Ec*tf/(Ef*tc))**(0.5))
    RF = abs(sigma_wr/sigma)
    return RF

def wrinkling_nasa_composite(sigma, Efx, Efy, tf,Ec, tc, nu_xy, nu_yx):
    sigma_wr = ((2*tf*Ec*((Efx*Efy)**(1/2)))/(3*tc*(1-nu_xy*nu_yx)))**(1/2)
    RF = abs(sigma_wr/sigma)
    return RF