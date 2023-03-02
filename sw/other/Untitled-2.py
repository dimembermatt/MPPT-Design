
    # Step 6. Derive inductor requirements.
    input("Press any key to continue.\n")
    print(f"----------------------------------------")
    print(f"STEP 6")
    print(f"Deriving inductor requirements:\n")

    # NOTE: NO SAFETY FACTOR
    i_pk_min = i_mpp + r_l_a / 2
    print(f"Inductor should be rated for {i_pk_min :.3f} A.")
    print(f"KG method. Assume ")
    print(f"Given inductor power budget of {p_ind} W and max ripple current {r_l_a}:")

    # r_max = p_ind / r_l_a ** 2
    # i_pk = i_pk_min
    # n_loops = l_min * i_pk / ()

    # print(f"Max resistance: {r_max} ohms")

    # B = L

    input("Press any key to end.")
