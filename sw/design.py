"""_summary_
@file       design.py
@author     Matthew Yu (matthewjkyu@gmail.com)
@brief      Calculate parameters of a DC-DC boost converter.

@version    0.2.0
@date       2023-05-06
@TODO: Get min/max input/output voltage from min/max power and propagate to
source/load I-V maps
@TODO: small signal model
@TODO: large signal model
@TODO: MPPT Simulation
"""

import argparse
import json
import logging
import sys
from datetime import datetime

import design_procedures.loader as loader
import design_procedures.maps as maps
import design_procedures.passives_design as passive
import design_procedures.switch_design as switch
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from lmfit import Parameters, fit_report, minimize

MAX_OPTIMIZER_ROUNDS = 5


class BoostConverter:
    def __init__(
        self,
        design_specs_path,
        switch_listing_path,
        capacitor_listing_path,
        inductor_listing_path,
        inductor_shapes_listing_path,
        inductor_materials_listing_path,
        awg_listing_path,
        output_path,
    ):
        self.switches = pd.read_csv(switch_listing_path, comment='#')
        self.capacitors = pd.read_csv(capacitor_listing_path, comment='#')
        self.inductors = pd.read_csv(inductor_listing_path, comment='#')
        self.inductor_shapes = pd.read_csv(inductor_shapes_listing_path)
        self.inductor_materials = pd.read_csv(inductor_materials_listing_path)
        self.awg = pd.read_csv(awg_listing_path)
        self.design_specs_path = design_specs_path
        self.output_path = output_path

        # Load in the design specifications
        self.load_design()

        # Setup optimizer
        fit_params = Parameters()
        fit_params.add("R_L", value=0.15 * 1e-7, min=0.01 * 1e-7, max=0.5 * 1e-7)
        fit_params.add("P_SW_BUD", value=2.5 * 1e-7, min=0.1 * 1e-7, max=10.0 * 1e-7)
        self.iteration = 0
        self.fit_params = fit_params


    def load_design(self):
        # Load in design specification file.
        with open(self.design_specs_path) as fp:
            design_specs = json.load(fp)
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

            if "user_v_range" in design["input_source"]:
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

            if "user_v_range" in design["output_sink"]:
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
            design["switches"] = {"duty": [0.0, 1.0], "f_sw": 0.0, "p_bud": 10}

            # Build i/o caps.
            design["input_cap"] = {
                "v_pp": design["input_source"]["inp_ripple (V)"],
            }
            design["output_cap"] = {
                "v_pp": design["output_sink"]["out_ripple (V)"],
            }

            # Build inductor.
            design["inductor"] = {
                "i_pp": None,
                "r_l": 0.5,
            }

            # Build IO map.
            design["map"] = {}

            self.design_specs = design_specs

        design = self.design_specs["DESIGN"]
        source = design["input_source"]
        sink = design["output_sink"]
        sw = design["switches"]
        ci = design["input_cap"]
        co = design["output_cap"]
        ind = design["inductor"]
        map = design["map"]

        # Initialize the design.
        if "min_power" in source:
            points = maps.initialize_design(source, sink, min_pow=source["min_power"])
        else:
            points = maps.initialize_design(source, sink)
        map["duty"] = [points["DUTY (%)"].min(), points["DUTY (%)"].max()]
        map["inp_vol"] = [points["VI (V)"].min(), points["VI (V)"].max()]
        map["out_vol"] = [points["VO (V)"].min(), points["VO (V)"].max()]
        map["inp_cur"] = [points["II (A)"].min(), points["II (A)"].max()]
        map["out_cur"] = [points["IO (A)"].min(), points["IO (A)"].max()]
        map["pow"] = [points["P (W)"].min(), points["P (W)"].max()]
        map["points"] = points

        sw["duty"] = map["duty"]
        ci["r_ci"] = ci["v_pp"] / map["inp_vol"][1] / 2
        co["r_co"] = co["v_pp"] / map["out_vol"][1] / 2
        ind["i_pp"] = ind["r_l"] * map["inp_cur"][1] * 2

    def optimize_design(self):
        def residual(params, self):
            values = params.valuesdict()

            # Set design parameters
            design = self.design_specs["DESIGN"]
            design["inductor"]["r_l"] = values["R_L"] * 1e7
            design["switches"]["p_bud"] = values["P_SW_BUD"] * 1e7

            # Iterate design and return total loss
            try:
                loss = self.iterate_design()
            except KeyboardInterrupt:
                sys.exit()
            except Exception as e:
                # print(e)
                loss = 1e6
            return loss, 0.0

        res = minimize(
            residual,
            self.fit_params,
            args=(self,),
            method="powell",
        )
        logging.info(fit_report(res))

        # Update with best run.clear
        design = self.design_specs["DESIGN"]
        design["inductor"]["r_l"] = res.params["R_L"].value * 1e7
        design["switches"]["p_bud"] = res.params["P_SW_BUD"].value * 1e7
        tot_loss = self.iterate_design()
        self.save_design()
        print(f"TOTAL_LOSS {tot_loss} W", end="\r")

    def iterate_design(self):
        self.save_design()
        design = self.design_specs["DESIGN"]
        sw = design["switches"]
        ci = design["input_cap"]
        co = design["output_cap"]
        ind = design["inductor"]
        map = design["map"]

        self.iteration += 1
        print(
            f"ITERATION {self.iteration} R_L: {ind['r_l']} | SW_P_BUD: {sw['p_bud']}",
            end="\r",
        )

        # Generate new points given any changes in constraints
        points = maps.constrain_design(map["points"], duty_range=sw["duty"])
        map["duty"] = [points["DUTY (%)"].min(), points["DUTY (%)"].max()]
        map["inp_vol"] = [points["VI (V)"].min(), points["VI (V)"].max()]
        map["out_vol"] = [points["VO (V)"].min(), points["VO (V)"].max()]
        map["inp_cur"] = [points["II (A)"].min(), points["II (A)"].max()]
        map["out_cur"] = [points["IO (A)"].min(), points["IO (A)"].max()]
        map["pow"] = [points["P (W)"].min(), points["P (W)"].max()]
        map["points"] = points

        sw["duty"] = map["duty"]
        ci["r_ci"] = ci["v_pp"] / map["inp_vol"][1] / 2
        co["r_co"] = co["v_pp"] / map["out_vol"][1] / 2
        ind["i_pp"] = ind["r_l"] * map["inp_cur"][1] * 2

        # Select the optimal components
        optimal_switch, p_sw_loss = switch.optimize_switches(design, self.switches)
        (
            (optimal_inp_caps, p_ci_loss),
            (optimal_out_caps, p_co_loss),
            (optimal_ind, p_l_loss),
        ) = passive.optimize_passives(
            design,
            self.capacitors,
            self.inductors,
            self.inductor_shapes,
            self.inductor_materials,
            self.awg,
        )

        # Needed for post-design mapping
        self.p_sw_loss = p_sw_loss
        self.optimal_sw = optimal_switch
        self.optimal_inp_caps = optimal_inp_caps
        self.optimal_out_caps = optimal_out_caps
        self.optimal_ind = optimal_ind

        # Needed for optimizer
        p_tot_loss = p_sw_loss * 2 + p_ci_loss + p_co_loss + p_l_loss
        return p_tot_loss

    def map_design(self):
        self.save_design()

        design = self.design_specs["DESIGN"]

        loader.map_source_model(design["input_source"], self.output_path)
        loader.map_sink_model(design["output_sink"], self.output_path)

        points = switch.map_switches(
            design,
            self.optimal_sw,
            self.output_path,
        )

        optimal_ind_shape = self.inductor_shapes[
            (self.inductor_shapes["SHAPE"] == self.optimal_ind.iloc[0]["SHAPE"])
        ]
        optimal_ind_material = self.inductor_materials[
            (
                self.inductor_materials["MATERIAL"]
                == self.optimal_ind.iloc[0]["MATERIAL"]
            )
        ]
        points = passive.map_passives(
            design,
            self.optimal_inp_caps,
            self.optimal_out_caps,
            self.optimal_ind,
            optimal_ind_shape,
            optimal_ind_material,
            self.awg,
            self.output_path,
        )
        points = maps.map_design(points, self.output_path)
        points.to_csv(self.output_path + "/operating_map.csv")

    def save_design(
        self,
    ):
        def round_floats(o):
            if isinstance(o, pd.DataFrame):
                return None
            if isinstance(o, np.ndarray):
                return round_floats(o.tolist())
            if isinstance(o, np.integer):
                return int(o)
            if isinstance(o, float):
                return round(o, 3)
            if isinstance(o, dict):
                return {k: round_floats(v) for k, v in o.items()}
            if isinstance(o, (list, tuple)):
                return [round_floats(x) for x in o]
            return o

        with open(self.output_path + "/design_parameters.json", "w+") as fp:
            fp.write(
                json.dumps(
                    round_floats(dict(sorted(self.design_specs.items()))), indent=4
                )
            )

    def set_design(self, sw_name, inp_cap_list, out_cap_list, ind_name, f_sw, r_l):
        self.optimal_sw = self.switches[self.switches["PART_NAME"] == sw_name]

        caps = pd.DataFrame()
        for inp_cap_name in inp_cap_list:
            caps = pd.concat(
                [caps, self.capacitors[self.capacitors["PART_NAME"] == inp_cap_name]]
            )
        self.optimal_inp_caps = (caps, None)

        caps = pd.DataFrame()
        for out_cap_name in out_cap_list:
            caps = pd.concat(
                [caps, self.capacitors[self.capacitors["PART_NAME"] == out_cap_name]]
            )
        self.optimal_out_caps = (caps, None)

        self.optimal_ind = self.inductors[self.inductors["PART_NAME"] == ind_name]

        design = self.design_specs["DESIGN"]
        design["switches"]["f_sw"] = f_sw
        design["inductor"]["r_l"] = r_l


if __name__ == "__main__":
    if sys.version_info[0] < 3:
        raise Exception("This program only supports Python 3.")

    try:
        import pretty_traceback

        pretty_traceback.install()
    except ImportError:
        pass  # no need to fail because of missing dev dependency

    parser = argparse.ArgumentParser()
    parser.add_argument("design_spec_path")
    parser.add_argument("output_path")
    parser.add_argument("switch_listing_path")
    parser.add_argument("capacitor_listing_path")
    parser.add_argument("inductor_listing_path")
    parser.add_argument("-vi", "--view_images", action="store_true")
    args = parser.parse_args()


    logging.basicConfig(
        filename=args.output_path + "/log.txt",
        filemode="w",
        format="\n%(message)s",
        level=logging.INFO,
    )
    logging.warning("Start logging.")

    if args.view_images:
        plt.ioff()
    else:
        plt.ion()

    boost_converter = BoostConverter(
        args.design_spec_path,
        args.switch_listing_path,
        args.capacitor_listing_path,
        args.inductor_listing_path,
        "./design_files/inductors/shapes.csv",
        "./design_files/inductors/materials.csv",
        "./design_files/inductors/awg.csv",
        args.output_path,
    )

    boost_converter.optimize_design()

    # switch_choice = "EPC2059"
    # inp_cap_choice = ("HZA336M080G24T-F")
    # out_cap_choice = ("A759MS186M2CAAE090", "A759MS186M2CAAE090")
    # ind_choice = "PQ32/20-3C96"
    # f_sw = 85000
    # r_l = 0.30
    # boost_converter.set_design(switch_choice, inp_cap_choice, out_cap_choice, ind_choice, f_sw, r_l)
    boost_converter.map_design()
