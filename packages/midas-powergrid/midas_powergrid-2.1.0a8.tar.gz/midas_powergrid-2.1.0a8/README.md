# Midas Powergrid Simulator

## Description

This package contains a Midas module providing a pandapower simulator and a number of custom powergrids.

Although this package is intended to be used with midas, but you can use in any mosaik simulation scenario.

## Installation

This package will usually installed automatically together with `midas-mosaik` if you opt-in any of the extras, e.g., `base` or `bh`. 
It is available on pypi, so you can install it manually with

```bash
pip install midas-powergrid
```

## Usage

The complete documentation is available at https://midas-mosaik.gitlab.io/midas.

### Inside of midas

To use the powergrid inside of midas, just add `powergrid` to your modules

```yaml
my_scenario:
  modules:
    - powergrid
    - ...
```

and configure it with (`gridfile` is required, everything else is optional and can be left out if the default values, shown below, are used):


```yaml
  powergrid_params:
    my_grid_scope:
      gridfile: midasmv
      grid_params: {}
      step_size: 900
      plotting: False
      plot_path: _plots # Output path defined in runtime config
      save_grid_json: False
```

All simulators that want to connect to this grid, will have to use `my_grid_scope` as their `grid_name` value. 
Activating the plotting will results in a considerably longer execution time. 
Activate it only if you really need this feature and it does not work for all of the grids.

The gridfile can be either a path to a .json or .xlsx file, a simbench grid code, one of `cigre_hv`, `cigre_mv`, `cigre_lv`, `midasmv`, `midaslv`, or `bhv`, or an import path to a function or class that either returns a valid pandapower grid or is a pandapower grid itself. 
The `grid_params` can be used to pass keywork arguments to custom grids.

### Any mosaik scenario

If you don't use midas, you can add the `powergrid` manually to your mosaik scenario file. 
First, the entry in the `sim_config`:

```python
sim_config = {
    "Powergrid": {"python": "midas_powergrid.simulator:PandapowerSimulator"},
    # ...
}
```

Next, you need to start the simulator (assuming a `step_size` of 900):

```python
powergrid_sim = world.start("Powergrid", step_size=900)
```

Finally, the model needs to be started:

```python
powergrid = powergrid_sim.Grid(gridfile="midasmv", grid_params={})
```

To connect the output of the grids' buses to another model, you have to get the list of bus models from the powergrids' children like

```python
bus_models = [e for e in powergrid.children if "bus" in e.eid]
```

and then connect those models either individually or in a loop, e.g.,

```python
for bus in bus_models:
    world.connect(bus, other_entity, "vm_pu", "va_degree", "p_mw", "q_mvar")
```

The inputs are generally handled in the same way. 
Have a look at `powergrid.children` to get the required entity eids.

## License
This software is released under the GNU Lesser General Public License (LGPL). See the license file for more information about the details.