"""_summary_
@file       maps.py
@author     Matthew Yu (matthewjkyu@gmail.com)
@brief      Calculate io map of the device
@version    1.0.0
@date       2023-05-06
@file_overview
    constrain_design
        generate_points
        filter points based on duty range
        filter points based on output current range
        filter_points based on power transfer range

    map_design
        map_duty_cycle
        map_current
        map_power
"""

import itertools
import logging

import matplotlib.pyplot as plt
import pandas as pd


def get_duty(vi, vo):
    return 1 - vi / vo


def get_output_current(vi, ii, vo):
    return vi * ii / vo


def get_power(vi, ii):
    return vi * ii


def initialize_design(source, sink, duty_range=[0.0, 1.0], min_pow=0.0):
    # Generate points.
    points = [
        [
            vi,
            ii,
            vo,
            get_output_current(vi, ii, vo),
            get_power(vi, ii),
            get_duty(vi, vo),
        ]
        for (vi, ii), (vo, io) in itertools.product(
            zip(source["i-v"][0], source["i-v"][1]),
            zip(sink["i-v"][0], sink["i-v"][1]),
        )
    ]

    df = pd.DataFrame(
        points, columns=["VI (V)", "II (A)", "VO (V)", "IO (A)", "P (W)", "DUTY (%)"]
    )

    # Constrain points based on range.
    df = df[(duty_range[0] <= df["DUTY (%)"]) & (df["DUTY (%)"] <= duty_range[1])]
    df = df[min_pow <= df["P (W)"]]
    return df


def constrain_design(df, duty_range=[0.0, 1.0], min_pow=0.0):
    # Constrain points based on range.
    df = df[(duty_range[0] <= df["DUTY (%)"]) & (df["DUTY (%)"] <= duty_range[1])]
    df = df[min_pow <= df["P (W)"]]
    return df


def map_duty(points, output_path):
    fig, ax = plt.subplots(1, 1, subplot_kw={"projection": "3d"})
    fig.suptitle(f"Duty Cycle Across I/O Map")
    ax.scatter(
        points["VI (V)"], points["VO (V)"], points["DUTY (%)"], c=points["DUTY (%)"]
    )
    ax.set_xlabel("$V_{IN}$ (V)")
    ax.set_ylabel("$V_{OUT}$ (V)")
    ax.set_zlabel("Duty Cycle (%)")
    plt.tight_layout()
    plt.show()
    fig.savefig(output_path + "/02_duty_cycle_map.png")
    plt.close()

    logging.info(
        f"Highest duty cycle:\n{points[points['DUTY (%)'] == points['DUTY (%)'].max()]}"
    )
    logging.info(
        f"Lowest duty cycle:\n{points[points['DUTY (%)'] == points['DUTY (%)'].min()]}"
    )


def map_current(points, output_path):
    fig, axs = plt.subplots(1, 2, subplot_kw={"projection": "3d"})
    fig.suptitle(f"Inp/Out Current Across I/O Map")
    axs[0].scatter(
        points["VI (V)"], points["VO (V)"], points["II (A)"], c=points["II (A)"]
    )
    axs[0].set_xlabel("$V_{IN}$ (V)")
    axs[0].set_ylabel("$V_{OUT}$ (V)")
    axs[0].set_zlabel("$I_{IN}$ (A)")
    axs[1].scatter(
        points["VI (V)"], points["VO (V)"], points["IO (A)"], c=points["IO (A)"]
    )
    axs[1].set_xlabel("$V_{IN}$ (V)")
    axs[1].set_ylabel("$V_{OUT}$ (V)")
    axs[1].set_zlabel("$I_{OUT}$ (A)")

    fig.set_size_inches(9, 5)
    plt.tight_layout()
    plt.subplots_adjust(right=0.9, wspace=0.1)
    plt.show()
    fig.savefig(output_path + "/03_current_map.png")
    plt.close()

    logging.info(
        f"Highest input current:\n{points[points['II (A)'] == points['II (A)'].max()]}"
    )
    logging.info(
        f"Lowest input current:\n{points[points['II (A)'] == points['II (A)'].min()]}"
    )
    logging.info(
        f"Highest output current:\n{points[points['IO (A)'] == points['IO (A)'].max()]}"
    )
    logging.info(
        f"Lowest output current:\n{points[points['IO (A)'] == points['IO (A)'].min()]}"
    )


def map_power(points, output_path):
    fig, ax = plt.subplots(1, 2, subplot_kw={"projection": "3d"})
    fig.suptitle(f"Power Transfer Across I/O Map")
    ax[0].scatter(
        points["VI (V)"], points["VO (V)"], points["P (W)"], c=points["P (W)"]
    )
    ax[0].set_xlabel("$V_{IN}$ (V)")
    ax[0].set_ylabel("$V_{OUT}$ (V)")
    ax[0].set_zlabel("$P_{TRANSFER}$ (W)")
    ax[1].scatter(
        points["VI (V)"], points["VO (V)"], points["P_LOSS (W)"], c=points["P_LOSS (W)"]
    )
    ax[1].set_xlabel("$V_{IN}$ (V)")
    ax[1].set_ylabel("$V_{OUT}$ (V)")
    ax[1].set_zlabel("$P_{LOSS}$ (W)")

    fig.set_size_inches(9, 5)
    plt.tight_layout()
    plt.subplots_adjust(right=0.9, wspace=0.1)
    plt.show()
    fig.savefig(output_path + "/04_power_map.png")
    plt.close()

    logging.info(
        f"Highest power transfer:\n{points[points['P (W)'] == points['P (W)'].max()]}"
    )
    logging.info(
        f"Lowest power transfer:\n{points[points['P (W)'] == points['P (W)'].min()]}"
    )

    logging.info(
        f"Highest power loss:\n{points[points['P_LOSS (W)'] == points['P_LOSS (W)'].max()]}"
    )
    logging.info(
        f"Lowest power loss:\n{points[points['P_LOSS (W)'] == points['P_LOSS (W)'].min()]}"
    )


def map_efficiency(points, output_path):
    def get_efficiency(point):
        p_transfer = point["P (W)"]
        p_loss = (
            point["PSW_TOT (W)"] * 2
            + point["PI_TOT (W)"]
            + point["PO_TOT (W)"]
            + point["PL_TOT (W)"]
        )
        return pd.Series([p_loss, (1 - p_loss / p_transfer) * 100])

    points[["P_LOSS (W)", "EFF (%)"]] = points.apply(get_efficiency, axis=1)

    fig, ax = plt.subplots(1, 1, subplot_kw={"projection": "3d"})
    fig.suptitle(f"Device Efficiency Across I/O Map")
    ax.scatter(
        points["VI (V)"], points["VO (V)"], points["EFF (%)"], c=points["EFF (%)"]
    )
    ax.set_xlabel("$V_{IN}$ (V)")
    ax.set_ylabel("$V_{OUT}$ (V)")
    ax.set_zlabel("EFF (%)")
    plt.tight_layout()
    plt.show()
    fig.savefig(output_path + "/10_efficiency_map.png")
    plt.close()

    logging.info(
        f"Highest device efficiency:\n{points[points['EFF (%)'] == points['EFF (%)'].max()]}"
    )
    logging.info(
        f"Lowest device efficiency:\n{points[points['EFF (%)'] == points['EFF (%)'].min()]}"
    )

    return points


def map_design(points, output_path):
    map_duty(points, output_path)
    map_current(points, output_path)
    points = map_efficiency(points, output_path)
    map_power(points, output_path)

    return points
