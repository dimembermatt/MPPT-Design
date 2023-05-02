"""_summary_
@file       battery_model.py
@author     Matthew Yu (matthewjkyu@gmail.com)
@brief      Modeling an arbitrary battery.
@version    0.0.0
@date       2023-04-27
"""

import matplotlib.pyplot as plt
import numpy as np


def model_inf_cap_cell():
    return 10.0


def model(sink):
    num_cells = sink["num_cells"]

    v = [v for v in np.linspace(2.5, 4.2, 50)]
    i = [model_inf_cap_cell() for _ in v]
    v = list(np.multiply(v, num_cells))
    p = [v * i for v, i in zip(v, i)]

    fig, (ax1, ax2) = plt.subplots(2, 1)
    fig.suptitle("Battery I-V/P-V Plot")
    ax1.plot(v, i)
    ax1.set_xlabel("Voltage (V)")
    ax1.set_ylabel("Max Charge Current (A)")
    ax1.grid(True, "both", "both")
    ax2.plot(v, p)
    ax2.set_xlabel("Voltage (V)")
    ax2.set_ylabel("Max Charge Power (W)")
    ax2.grid(True, "both", "both")
    plt.tight_layout()
    plt.savefig("./outputs/sink_model.png")
    plt.close()

    return [v, i]
