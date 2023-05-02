"""_summary_
@file       design.py
@author     Matthew Yu (matthewjkyu@gmail.com)
@brief      Calculate parameters of a DC-DC boost converter.

@version    0.2.0
@date       2023-04-27
@NOTE       TODO: add option to configure iteration saves
            TODO: add option to view graphs manually and adjust before saving
            TODO: add logging
"""

import argparse
import itertools
import json
import logging
import sys
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import design_procedures.loader as loader
import design_procedures.maps as maps
import design_procedures.passives_design as passive
import design_procedures.switch_design as switch


def save(file_path, design_spec):
    def round_floats(o):
        if isinstance(o, np.ndarray):
            return round_floats(o.tolist())
        if isinstance(o, float):
            return round(o, 3)
        if isinstance(o, dict):
            return {k: round_floats(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [round_floats(x) for x in o]
        return o

    with open(file_path, "w+") as fp:
        fp.write(json.dumps(round_floats(dict(sorted(design_spec.items()))), indent=4))


if __name__ == "__main__":
    if sys.version_info[0] < 3:
        raise Exception("This program only supports Python 3.")

    try:
        import pretty_traceback

        pretty_traceback.install()
    except ImportError:
        pass  # no need to fail because of missing dev dependency

    plt.ion()

    logging.basicConfig(
        filename="./outputs/log.txt",
        filemode="w",
        format="%(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    logging.warning("Start logging.")

    parser = argparse.ArgumentParser()
    parser.add_argument("design_spec_path")
    parser.add_argument("design_parameters_path")
    parser.add_argument("switch_listing_path")
    parser.add_argument("capacitor_listing_path")
    parser.add_argument("inductor_listing_path")
    parser.add_argument("-s", "--show_images", action="store_true")
    parser.add_argument("-si", "--save_iters", action="store_true")
    parser.add_argument("-l", "--display_logging", action="store_true")
    args = parser.parse_args()

    # Load in component listings.
    switches = pd.read_csv(args.switch_listing_path)
    capacitors = pd.read_csv(args.capacitor_listing_path)
    inductors = pd.read_csv(args.inductor_listing_path)

    # Load in the design requirements file.
    with open(args.design_spec_path) as fp:
        design_specs = json.load(fp)
        try:
            design_specs["DATE_GENERATED"] = datetime.now().strftime(
                "%m/%d/%y %H:%M:%S"
            )

            design = design_specs["DESIGN"]

            # Capture source and sink models.
            input_points = loader.load_source_model(design["input_source"])
            if input_points is None:
                raise Exception(
                    "The source model is poorly defined; could not find a model function."
                )
            output_points = loader.load_sink_model(design["output_sink"])
            if output_points is None:
                raise Exception(
                    "The sink model is poorly defined; could not find a model function."
                )

            def filter_bounds(point, range):
                if point[0] >= range[0] and point[0] <= range[1]:
                    return True
                return False

            input_points = np.transpose(
                list(
                    filter(
                        lambda point: filter_bounds(
                            point, design["input_source"]["user_v_range"]
                        ),
                        np.transpose(input_points),
                    )
                )
            ).tolist()
            output_points = np.transpose(
                list(
                    filter(
                        lambda point: filter_bounds(
                            point, design["output_sink"]["user_v_range"]
                        ),
                        np.transpose(output_points),
                    )
                )
            ).tolist()

            # Update source and sink.
            design["input_source"]["i-v"] = input_points
            design["output_sink"]["i-v"] = output_points

            # Build switches.
            design["switches"] = {
                "duty": [0.0, 1.0],
                "f_sw": 0.0,
                "max_f_sw": design["max_switching_freq"],
            }
            del design["max_switching_freq"]

            # Build i/o caps.
            design["input_cap"] = {
                "v_pk_pk": design["input_source"]["inp_ripple (V)"],
                "r_ci": design["input_source"]["inp_ripple (V)"]
                / design["input_source"]["user_v_range"][1]
                / 2,
            }
            design["output_cap"] = {
                "v_pk_pk": design["output_sink"]["out_ripple (V)"],
                "r_co": design["output_sink"]["out_ripple (V)"]
                / design["output_sink"]["user_v_range"][1]
                / 2,
            }

            # Build inductor.
            design["inductor"] = {
                "i_pk_pk": None,
                "r_l": 0.15,
            }

            # Build efficiency.
            design["efficiency"] = {
                "target_eff": design["starting_efficiency"],
                "min_eff": design["starting_efficiency"],
                "dist": {"sw1": 0.5, "sw2": 0.5, "ci": 0.0, "co": 0.0, "l": 0.00},
            }
            del design["starting_efficiency"]

            # Build IO map.
            design["map"] = {"duty": None, "curr": None, "pow": None, "points": None}
        except:
            raise Exception("Missing spec parameter.")

    source = design["input_source"]
    sink = design["output_sink"]
    sw = design["switches"]
    ci = design["input_cap"]
    co = design["output_cap"]
    ind = design["inductor"]
    eff = design["efficiency"]
    map = design["map"]
    sf = design["safety_factor"]

    # Generate starting maps.
    points = [
        [vi, ii, vo, io]
        for (vi, ii), (vo, io) in itertools.product(
            zip(source["i-v"][0], source["i-v"][1]),
            zip(sink["i-v"][0], sink["i-v"][1]),
        )
    ]
    map["duty"], map["curr"], map["pow"], map["points"] = maps.generate_maps(points)

    # Carry over duty range determined by user manipulation of usable
    # input/output voltage range.
    sw["duty"] = [map["duty"][0][4], map["duty"][1][4]]

    # Generate inductor ripple.
    ind["i_pk_pk"] = ind["r_l"] * map["curr"][1][4] * 2

    # NOTE: ITERATION START
    iteration = 0
    while True:
        save(args.design_parameters_path, design_specs)
        iteration += 1
        logging.info(f"OPTIMIZER ITERATION {iteration}")

        # Start of optimization loop.
        """
        KNOBS TO TUNE, in no particular order

        - Modify input/output range
        - Modify max current
        - Modify current ripple
        - Modify voltage ripple
        - Change power loss distribution
        - Modify target efficiency
        """
        # Generate new point set and maps given constraints
        map["duty"], map["curr"], map["pow"], map["points"] = maps.generate_maps(
            points, *sw["duty"]
        )

        # Update bounds and estimates
        points_tp = np.transpose(map["points"])
        source["lower_bound_voltage"] = min(set(points_tp[0]))
        source["upper_bound_voltage"] = max(set(points_tp[0]))
        source["lower_bound_current"] = min(set(points_tp[1]))
        source["upper_bound_current"] = max(set(points_tp[1]))
        sink["lower_bound_voltage"] = min(set(points_tp[2]))
        sink["upper_bound_voltage"] = max(set(points_tp[2]))
        sink["lower_bound_current"] = min(set(points_tp[3]))
        sink["upper_bound_current"] = max(set(points_tp[3]))
        ci["r_ci"] = ci["v_pk_pk"] / source["upper_bound_voltage"] / 2
        co["r_co"] = co["v_pk_pk"] / sink["upper_bound_voltage"] / 2
        ind["i_pk_pk"] = ind["r_l"] * source["upper_bound_current"] * 2

        # Select switch and switching frequency.
        p_sw = switch.optimize_switches(design, switches, iteration)

        # Select capacitors.
        # passive.optimize_passives(design, capacitors, inductors, iteration)

        # Select inductors.

        # TODO: Unforce break with eval conditions
        break

    # save(args.design_parameters_path, design_specs)
