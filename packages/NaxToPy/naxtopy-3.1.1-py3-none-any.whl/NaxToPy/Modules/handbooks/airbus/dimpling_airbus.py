def dimpling_airbus_compression(sigma, Ef, nu,t_f, s):
    sigma_d = 2/(1-(nu**2))*Ef*((t_f/s)**2)
    RF = sigma_d/abs(sigma)
    return RF

def dimpling_airbus_biaxial(sigma_x, sigma_y, Efx, Efy, nu_xy, nu_yx, t_f,s):
    RF_x = dimpling_airbus_compression(sigma_x,Efx,nu_xy,t_f,s)
    RF_y = dimpling_airbus_compression(sigma_y,Efy,nu_yx,t_f,s)

    R_x = 1/RF_x
    R_y = 1/RF_y

    RF = 1/(R_x+R_y)
    return RF

def dimpling_airbus_shear(tau_xy,Ef, t_f,s):
    tau_d = 0.6*Ef*((t_f/s)**(3/2))
    RF = tau_d/abs(tau_xy)
    return RF

def dimpling_airbus_combined(sigma_x, sigma_y,tau_xy, Efx, Efy, nu_xy, nu_yx, t_f, s):
    RF_x = dimpling_airbus_compression(sigma_x,Efx,nu_xy,t_f,s) if sigma_x < 0 else 999999
    RF_y = dimpling_airbus_compression(sigma_y, Efy, nu_yx, t_f, s) if sigma_y < 0 else 999999
    RF_shear = dimpling_airbus_shear(tau_xy,min(Efx,Efy),t_f,s)

    R_DCx = 1/RF_x
    R_DCy = 1/RF_y
    R_DCs = 1/RF_shear

    RF = 2/(R_DCx + R_DCy + ((((R_DCx+R_DCy)**2) + 4*(R_DCs**2))**(0.5)))
    return RF