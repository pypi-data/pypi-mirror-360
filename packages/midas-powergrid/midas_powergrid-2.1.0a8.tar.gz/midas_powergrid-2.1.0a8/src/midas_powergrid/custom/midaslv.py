"""In this module, the midas lv grid is defined and configured."""

# pyright: reportArgumentType=false
import pandapower as pp
import pandapower.networks as pn


def build_grid(**kwargs):
    """Create the default midas lv grid."""

    grid = pn.create_cigre_network_lv()
    grid.load = grid.load[0:0]
    grid.sgen = grid.sgen[0:0]
    grid.storage = grid.storage[0:]

    res = [2, 12, 16, 17, 18, 19]
    ind = [22]
    com = [24, 35, 36, 37, 40, 41, 42, 43]

    for dist, name in [(res, "RES"), (ind, "IND"), (com, "COM")]:
        for bus_id in dist:
            pp.create_load(
                grid,
                bus=bus_id,
                p_mw=0.0,
                q_mvar=0.0,
                name=f"LOAD_{name}_{bus_id}",
                scaling=1.0,
                in_service=True,
                controllable=False,
            )
            pp.create_sgen(
                grid,
                bus=bus_id,
                p_mw=0.0,
                q_mvar=0.0,
                name=f"SGEN_{name}_{bus_id}",
                scaling=1.0,
                type=None,
                in_service=True,
                controllable=False,
            )
            pp.create_storage(
                grid,
                bus=bus_id,
                p_mw=0.0,
                max_e_mwh=1,
                q_mvar=0,
                name=f"STORAGE_{name}_{bus_id}",
                scaling=1.0,
                type=None,
                in_service=True,
                controllable=False,
            )

    num = len(res + ind + com)

    if "constant_load_p_mw" in kwargs:
        grid.load.p_mw.values[:] = [
            kwargs["constant_load_p_mw"] for _ in range(num)
        ]
    if "constant_load_q_mvar" in kwargs:
        grid.load.q_mvar.values[:] = [
            kwargs["constant_load_q_mvar"] for _ in range(num)
        ]

    if "constant_sgen_p_mw" in kwargs:
        grid.sgen.p_mw.values[:] = [
            kwargs["constant_sgen_p_mw"] for _ in range(num)
        ]

    if "constant_sgen_q_mvar" in kwargs:
        grid.sgen.q_mvar.values[:] = [
            kwargs["constant_sgen_q_mvar"] for _ in range(num)
        ]
    if "constant_storage_p_mw" in kwargs:
        grid.storage.p_mw.values[:] = [
            kwargs["constant_storage_p_mw"] for _ in range(num)
        ]
    if "constant_storage_q_mvar" in kwargs:
        grid.storage.q_mvar.values[:] = [
            kwargs["constant_storage_q_mvar"] for _ in range(num)
        ]

    tap_changer = {
        0: {"min": -10, "max": 10, "mid": 0, "ts_size": 0.625},
        1: {"min": -10, "max": 10, "mid": 0, "ts_size": 0.625},
    }

    for trafo_id, trafo_config in tap_changer.items():
        grid.trafo.loc[trafo_id, "tap_side"] = "lv"
        grid.trafo.loc[trafo_id, "tap_min"] = trafo_config["min"]
        grid.trafo.loc[trafo_id, "tap_max"] = trafo_config["max"]
        grid.trafo.loc[trafo_id, "tap_neutral"] = trafo_config["mid"]
        grid.trafo.loc[trafo_id, "tap_step_percent"] = trafo_config["ts_size"]

    return grid
