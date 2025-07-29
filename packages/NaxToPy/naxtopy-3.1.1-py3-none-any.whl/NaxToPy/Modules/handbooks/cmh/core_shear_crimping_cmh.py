def core_shear_crimping_cmh(F,h,t_up,t_low,tc,Gc):
    F_c = (h**2)*Gc/((t_up+t_low)*tc)
    RF = F_c/abs(F)
    return RF