def core_shear_crimping_airbus(sigma,t_inf,t_sup,t_core,Gc):
    sigma_cr = t_core*Gc/(t_inf+t_sup)
    RF = sigma_cr/abs(sigma)
    return RF

