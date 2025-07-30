"""This module contains the mosaik meta definition for the
pandapower simulator.

"""

import numpy as np

ATTRIBUTE_MAP = {
    "Bus": {
        "bus": [
            ("in_service", "bool", 0, 1),  # bus is operational
            ("vn_kv", "float", 0, 440),  # nominal voltage
        ],
        "res_bus": [
            ("p_mw", "float", -np.inf, np.inf),  # active power
            ("q_mvar", "float", -np.inf, np.inf),  # reactive power
            ("vm_pu", "float", 0.0, np.inf),  # voltage magnitude
            ("va_degree", "float", -180.0, 180.0),  # voltage angle
        ],
    },
    "Line": {
        "line": [
            ("in_service", "bool", 0, 1),  # line is operational
            ("max_i_ka", "float", 0, np.inf),  # maximum current
        ],
        "res_line": [
            ("loading_percent", "float", 0, np.inf),  # utilization
            ("p_from_mw", "float", -np.inf, np.inf),  # active power from
            ("p_to_mw", "float", -np.inf, np.inf),  # active power to
            ("q_from_mvar", "float", -np.inf, np.inf),  # reactive power from
            ("q_to_mvar", "float", -np.inf, np.inf),  # reactive power to
            ("vm_from_pu", "float", 0.0, np.inf),  # voltage magnitude from
            ("vm_to_pu", "float", 0.0, np.inf),  # voltage magnitude to
            ("va_from_degree", "float", -180.0, 180.0),  # voltage angle from
            ("va_to_degree", "float", -180.0, 180.0),  # voltage angle to
            ("i_from_ka", "float", -np.inf, np.inf),  # current from
            ("i_to_ka", "float", -np.inf, np.inf),  # current to
        ],
    },
    "Trafo": {
        "trafo": [
            ("in_service", "bool", 0, 1),  # trafo is operational
            ("tap_pos", "int", -np.inf, np.inf),  # position of tap changer
            (
                "delta_tap_pos",
                "int",
                -1,
                1,
            ),  # change of the tap changer in one direction
            ("tap_min", "int", -np.inf, np.inf),  # minimal tap position
            ("tap_max", "int", -np.inf, np.inf),  # maximum tap position
        ],
        "res_trafo": [
            ("loading_percent", "float", 0, np.inf),  # utilization
            ("p_hv_mw", "float", -np.inf, np.inf),  # active power hv
            ("p_lv_mw", "float", -np.inf, np.inf),  # active power lv
            ("q_hv_mvar", "float", -np.inf, np.inf),  # reactive power hv
            ("q_lv_mvar", "float", -np.inf, np.inf),  # reactive power lv
            ("vm_hv_pu", "float", 0.0, np.inf),  # voltage magnitude hv
            ("vm_lv_pu", "float", 0.0, np.inf),  # voltage magnitude lv
            ("va_hv_degree", "float", -180.0, 180.0),  # voltage angle hv
            ("va_lv_degree", "float", -180.0, 180.0),  # voltage angle lv
            ("i_hv_ka", "float", -np.inf, np.inf),  # current hv
            ("i_lv_ka", "float", -np.inf, np.inf),  # current lv
        ],
    },
    "Switch": {
        "switch": [("closed", "bool", 0, 1)],
        "res_switch": [("i_ka", "float", -np.inf, np.inf)],
    },
    "Ext_grid": {
        "ext_grid": [],
        "res_ext_grid": [
            ("p_mw", "float", -np.inf, np.inf),  # active power
            ("q_mvar", "float", -np.inf, np.inf),  # reactive power
        ],
    },
    "Load": {
        "load": [
            ("p_mw", "float", -np.inf, np.inf),  # active power
            ("q_mvar", "float", -np.inf, np.inf),  # reactive power
            ("in_service", "bool", 0, 1),  # load is operational
        ],
        "res_load": [],
    },
    "Sgen": {
        "sgen": [
            ("p_mw", "float", -np.inf, np.inf),  # active power
            ("q_mvar", "float", -np.inf, np.inf),  # reactive power
            ("in_service", "bool", 0, 2),  # generator is operational
        ],
        "res_sgen": [],
    },
    "Storage": {
        "storage": [
            ("p_mw", "float", -np.inf, np.inf),  # active power
            ("q_mvar", "float", -np.inf, np.inf),  # reactive power
            ("in_service", "bool", 0, 2),  # storage is operational
        ],
        "res_storage": [],
    },
}
META = {
    "type": "time-based",
    "models": {
        "Grid": {
            "public": True,
            "params": [
                "gridfile",  # Name of the grid topology
                "pp_params",
                "plotting",  # Flag to activate plotting
                "use_constraints",  # Flag to activate constraints
                "constraints",  # A list of constraints to activate
                "actuator_multiplier",
                "include_slack_bus",
                "surrogate_params",
            ],
            "attrs": ["health", "grid_json"],
        },
        "Ext_grid": {
            "public": False,
            "params": [],
            "attrs": [
                attr[0] for attr in ATTRIBUTE_MAP["Ext_grid"]["ext_grid"]
            ]
            + [attr[0] for attr in ATTRIBUTE_MAP["Ext_grid"]["res_ext_grid"]],
        },
        "Bus": {
            "public": False,
            "params": [],
            "attrs": [attr[0] for attr in ATTRIBUTE_MAP["Bus"]["bus"]]
            + [attr[0] for attr in ATTRIBUTE_MAP["Bus"]["res_bus"]],
        },
        "Load": {
            "public": False,
            "params": [],
            "attrs": [attr[0] for attr in ATTRIBUTE_MAP["Load"]["load"]]
            + [attr[0] for attr in ATTRIBUTE_MAP["Load"]["res_load"]],
        },
        "Sgen": {
            "public": False,
            "params": [],
            "attrs": [attr[0] for attr in ATTRIBUTE_MAP["Sgen"]["sgen"]]
            + [attr[0] for attr in ATTRIBUTE_MAP["Sgen"]["res_sgen"]],
        },
        "Trafo": {
            "public": False,
            "params": [],
            "attrs": [attr[0] for attr in ATTRIBUTE_MAP["Trafo"]["trafo"]]
            + [attr[0] for attr in ATTRIBUTE_MAP["Trafo"]["res_trafo"]],
        },
        "Line": {
            "public": False,
            "params": [],
            "attrs": [attr[0] for attr in ATTRIBUTE_MAP["Line"]["line"]]
            + [attr[0] for attr in ATTRIBUTE_MAP["Line"]["res_line"]],
        },
        "Switch": {
            "public": False,
            "params": [],
            "attrs": [attr[0] for attr in ATTRIBUTE_MAP["Switch"]["switch"]]
            + [attr[0] for attr in ATTRIBUTE_MAP["Switch"]["res_switch"]],
        },
        "Storage": {
            "public": False,
            "params": [],
            "attrs": [attr[0] for attr in ATTRIBUTE_MAP["Storage"]["storage"]]
            + [attr[0] for attr in ATTRIBUTE_MAP["Storage"]["res_storage"]],
        },
    },
}
