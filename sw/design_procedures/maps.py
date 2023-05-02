"""_summary_
@file       maps.py
@author     Matthew Yu (matthewjkyu@gmail.com)
@brief      Generate maps on various converter aspects for inspection.
@version    0.0.0
@date       2023-04-27
"""

import itertools
import sys

import matplotlib.pyplot as plt
import numpy as np


def get_duty_cycle_map(points, lower_lim_duty=0.0, upper_lim_duty=1.0):
    points = [
        [vi, ii, vo, io, 1 - vi / vo]
        for (vi, ii, vo, io) in points
        if (1 - vi / vo) > lower_lim_duty and (1 - vi / vo) < upper_lim_duty
    ]
    (x, _, y, _, z) = np.transpose(points)

    min_pt = min(points, key=lambda points: points[4])
    max_pt = max(points, key=lambda points: points[4])
    points = np.transpose(np.transpose(points)[:-1])

    # Plot out duty cycle map.
    fig, ax = plt.subplots(1, 1, subplot_kw={"projection": "3d"})
    fig.suptitle(f"Duty Cycle Across I/O Mapping [{min_pt[4] :.2f}, {max_pt[4] :.2f}]")
    ax.scatter(x, y, z, c=z)
    ax.set_xlabel("V_IN (V)")
    ax.set_ylabel("V_OUT (V)")
    ax.set_zlabel("Duty Cycle (%)")
    plt.tight_layout()
    plt.savefig("./outputs/duty_cycle_map.png")
    plt.close()

    return (min_pt, max_pt, points)


def get_current_transfer_map(points, upper_lim_curr=100.0):
    # ii is lower bound input current
    # io is upper bound output current
    # bound usable points based on io and arb. upper_lim_curr
    points = [
        [vi, ii, vo, io, ii, vi * ii / vo]
        for (vi, ii, vo, io) in points
        if vi * ii / vo <= min(io, upper_lim_curr)
    ]
    (x, _, y, _, z1, z2) = np.transpose(points)

    # Plot out current transfer map.
    fig, axs = plt.subplots(1, 2, subplot_kw={"projection": "3d"})
    fig.suptitle("Input/Output Current Across I/O Mapping")
    axs[0].scatter(x, y, z1, c=z1)
    axs[0].set_xlabel("V_IN (V)")
    axs[0].set_ylabel("V_OUT (V)")
    axs[0].set_zlabel("I_IN (A)")
    axs[1].scatter(x, y, z2, c=z2)
    axs[1].set_xlabel("V_IN (V)")
    axs[1].set_ylabel("V_OUT (V)")
    axs[1].set_zlabel("I_OUT (A)")
    plt.tight_layout()
    plt.subplots_adjust(right=0.9, wspace=0.2)
    plt.savefig("./outputs/current_map.png")
    plt.close()

    min_pt = min(points, key=lambda points: points[4])
    max_pt = max(points, key=lambda points: points[4])
    points = np.transpose(np.transpose(points)[:-2])
    return (min_pt, max_pt, points)


def get_power_transfer_map(points, upper_lim_pow=1000.0):
    # bound usable points based on vo*io and arb. upper_lim_pow
    points = [
        [vi, ii, vo, io, vi * ii, vo * io]
        for (vi, ii, vo, io) in points
        if vi * ii <= min(vo * io, upper_lim_pow)
    ]
    (x, _, y, _, z1, z2) = np.transpose(points)

    # Plot out power transfer map.
    fig, axs = plt.subplots(1, 2, subplot_kw={"projection": "3d"})
    fig.suptitle("Input/Output Power Across I/O Mapping")
    axs[0].scatter(x, y, z1, c=z1)
    axs[0].set_xlabel("V_IN (V)")
    axs[0].set_ylabel("V_OUT (V)")
    axs[0].set_zlabel("P_IN (W)")
    axs[1].scatter(x, y, z2, c=z2)
    axs[1].set_xlabel("V_IN (V)")
    axs[1].set_ylabel("V_OUT (V)")
    axs[1].set_zlabel("P_OUT (W)")
    plt.tight_layout()
    plt.subplots_adjust(right=0.9, wspace=0.2)
    plt.savefig("./outputs/power_map.png")
    plt.close()

    min_pt = min(points, key=lambda points: points[4])
    max_pt = max(points, key=lambda points: points[4])
    points = np.transpose(np.transpose(points)[:-2])
    return (min_pt, max_pt, points)


def generate_maps(
    points,
    lower_lim_duty=0.0,
    upper_lim_duty=1.0,
    upper_lim_curr=100.0,
    upper_lim_pow=1000.0,
):
    (min_duty, max_duty, points) = get_duty_cycle_map(
        points, lower_lim_duty, upper_lim_duty
    )
    (min_curr, max_curr, points) = get_current_transfer_map(points, upper_lim_curr)
    (min_pow, max_pow, points) = get_power_transfer_map(points, upper_lim_pow)

    return (min_duty, max_duty), (min_curr, max_curr), (min_pow, max_pow), points
