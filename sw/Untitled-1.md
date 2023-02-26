


1. Second, we put together a list of switches. We define the minimum
   requirements for the switches:

   - V_DS > 134.4 V * 1.25 = 168 V
   - I_DS > 6.15 A * 1.25 = 7.68 A
   - P_DISS > 1 W * 1.25 = 1.25 W

   We organize the list of switches either by their FOM, R_DS_ON, or C_OSS. In
   particular we want to look at the switches in the following case:

   - C_OSS = (C_OSS @ 0V + C_OSS @ 140V) / 2
   - R_DS_ON = (R_DS_ON @ 25 C)

2. After picking a set of comparable switches by FOM (with a broad spectrum of
   R_DS_ON vs C_OSS ratio), we look at the limiting operating points of the
   system.

   - V_MPP and V_OUT_AVG: At V_MPP, we pull in the maximum power generation.
     Minimize P_DISS.
   - V_IN_MIN and V_OUT_MAX. F_SW determined at this operating point that
     remains under our power budget constrains how small we can make L, C_IN,
     C_OUT. Maximize F_SW.

   At both points we look at the ideal R_DS_ON and C_OSS given the FOM, pick a
   components that meets these requirements, and choose the F_SW that meets both
   our optimization criteria.

3. After picking the F_SW, we can generate the minimum inductance and
   capacitances needed to run the system while meeting our ripple requirements.
   We also perform power dissipation on the components and attempt to find
   components that minimize this power dissipation.

4. Determine gate driver
5. Determine inductor core
6. Determine inductor windings
7. Determine layout
8. Determine


    p_sw_ex = v_in_opt * i_mpp * (1 - eff) * sw_pd
    # And a specified efficiency and ripple
    eff = 0.985
    r_ci_v = 0.725  # V
    r_co_v = 1.25  # V
    r_l_a = 1.23  # A
    r_ci = r_ci_v / v_in_range[1] / 2
    r_co = r_co_v / v_out_range[1] / 2
    r_l = r_l_a / i_in_range[1] / 2

    # Power dissipation distribution
    sw_pd = 0.3
    c_pd = 0.1
    l_pd = 0.2