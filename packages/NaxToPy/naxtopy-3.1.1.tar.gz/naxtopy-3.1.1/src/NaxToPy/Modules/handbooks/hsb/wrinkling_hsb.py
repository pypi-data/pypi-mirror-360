def antysymmetric_hsb_wrinkling(sigma, Ef, tf, nu_f, Ec, Gc):
    Df = Ef*(tf**3)/(12*(1- (nu_f**2)))
    sigma_w = (3/(2*tf))*((2*Df*Ec*Gc)**(1/3))
    RF = abs(sigma_w/sigma)
    return RF

def symmetric_hsb_wrinkling(sigma, Ef, tf, nu_f, Ec, tc):
    Df = Ef * (tf ** 3) / (12 * (1 - (nu_f ** 2)))
    sigma_w = (8*Df*Ec/(tc*(tf**2)))**(1/2)
    RF = abs(sigma_w/sigma)
    return RF