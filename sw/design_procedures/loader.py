"""_summary_
@file       loader.py
@author     Matthew Yu (matthewjkyu@gmail.com)
@brief      Load in models for sources and sinks.
@version    1.0.0
@date       2023-05-06
"""

import design_procedures.battery_model as battery_model
import design_procedures.solar_cell_nonideal_model as solar_cell_nonideal_model


def load_source_model(source):
    model = None
    match source["source_model_type"]:
        case "solar_cell":
            model = solar_cell_nonideal_model
        case _:
            model = None

    return model.model(source)

def load_sink_model(sink):
    model = None
    match sink["sink_model_type"]:
        case "battery":
            model = battery_model
        case _:
            model = None

    return model.model(sink)

def map_source_model(source, output_path):
    model = None
    match source["source_model_type"]:
        case "solar_cell":
            model = solar_cell_nonideal_model
        case _:
            model = None

    model.map(source, output_path)

def map_sink_model(sink, output_path):
    model = None
    match sink["sink_model_type"]:
        case "battery":
            model = battery_model
        case _:
            model = None

    model.map(sink, output_path)