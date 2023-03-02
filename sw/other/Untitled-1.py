
    # x: plot frequency vs y: r_ds_on vs z: power loss
    x_f_s = []
    y_r_ds_on = []
    z_cond = []
    z_switch = []
    z_tot = []
    z_max = []

    print("Frequencies plotted: 100, 1k, 10k, 100k, 1M Hz")
    for f_s in [100, 1_000, 10_000, 100_000, 1_000_000]:
        r_ds_on = 1e-4  # 100 uOhm
        for i in range(200):
            c_oss = tau / r_ds_on
            v_in = v_in_opt / num_cells
            v_out = 107.2
            i_in = model_nonideal_cell(1000, 298.15, 0, 100, v_in)
            p_conduction, p_switching, p_total = get_losses(
                v_in_opt, i_in, v_out, f_s, r_ds_on, c_oss, r_l
            )

            x_f_s.append(f_s)
            y_r_ds_on.append(r_ds_on)
            z_cond.append(p_conduction)
            z_switch.append(p_switching)
            z_tot.append(p_total)
            z_max.append(v_in_opt * i_mpp * (1 - eff) * sf)

            r_ds_on *= 1.04

    plt.clf()

    def log_tick_formatter(val, pos=None):
        return r"$10^{:.0f}$".format(val)

    # Plot out switching frequency map.
    ax_tau = fig.add_subplot(projection="3d")
    ax_tau.scatter(
        np.log10(x_f_s),
        np.log10(y_r_ds_on),
        np.log10(z_cond),
        s=2,
        label="Conduction Loss (W)",
    )
    ax_tau.scatter(
        np.log10(x_f_s),
        np.log10(y_r_ds_on),
        np.log10(z_switch),
        s=2,
        label="Switching Loss (W)",
    )
    ax_tau.scatter(
        np.log10(x_f_s),
        np.log10(y_r_ds_on),
        np.log10(z_tot),
        s=2,
        label="Total Loss (W)",
    )
    ax_tau.scatter(
        np.log10(x_f_s),
        np.log10(y_r_ds_on),
        np.log10(z_max),
        s=2,
        label="Max Design Loss (W)",
    )
    ax_tau.legend()
    ax_tau.xaxis.set_major_formatter(mticker.FuncFormatter(log_tick_formatter))
    ax_tau.yaxis.set_major_formatter(mticker.FuncFormatter(log_tick_formatter))
    ax_tau.zaxis.set_major_formatter(mticker.FuncFormatter(log_tick_formatter))
    ax_tau.set_title("")
    ax_tau.set_xlabel("Switching Frequency (Hz)")
    ax_tau.set_ylabel("R_DS_ON (Ohm)")
    ax_tau.set_zlabel("Power Loss (W)")

    plt.savefig("frequency_tau_power_map.png")
    plt.show()

    print(f"\nSelect a switching frequency to investigate.")
    f_s = int(input("F_S (hz): "))

    y_r_ds_on = []
    z_cond = []
    z_switch = []
    z_tot = []
    z_max = []

    r_ds_on = 1e-4  # 100 uOhm
    for i in range(500):
        c_oss = tau / r_ds_on
        v_in = v_in_opt / num_cells
        v_out = 107.2
        i_in = model_nonideal_cell(1000, 298.15, 0, 100, v_in)
        p_conduction, p_switching, p_total = get_losses(
            v_in_opt, i_in, v_out, f_s, r_ds_on, c_oss, r_l
        )

        y_r_ds_on.append(r_ds_on)
        z_cond.append(p_conduction)
        z_switch.append(p_switching)
        z_tot.append(p_total)
        z_max.append(v_in_opt * i_mpp * (1 - eff) * sf)

        r_ds_on *= 1.02

    plt.clf()

    # Plot out switching frequency map.
    ax_tau = fig.add_subplot()
    ax_tau.scatter(y_r_ds_on, z_cond, s=2, label="Conduction Loss (W)")
    ax_tau.scatter(y_r_ds_on, z_switch, s=2, label="Switching Loss (W)")
    ax_tau.scatter(y_r_ds_on, z_tot, s=2, label="Total Loss (W)")
    ax_tau.scatter(y_r_ds_on, z_max, s=2, label="Max Design Loss (W)")
    ax_tau.legend()
    ax_tau.set_xscale("log")
    ax_tau.set_yscale("log")
    ax_tau.set_title("")
    ax_tau.set_xlabel("R_DS_ON (Ohm)")
    ax_tau.set_ylabel("Power Loss (W)")

    plt.savefig("tau_power_map.png")
    plt.show()