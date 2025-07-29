"""Define a library to produce all these nice plots.

.. todo::
    better detection of what is a multiparticle simulation and what is not.
    Currently looking for "'partran': 0" in the name of the solver, making the
    assumption that multipart is the default. But it depends on the .ini...
    update: just use .is_a_multiparticle_simulation

.. todo::
    Fix when there is only one accelerator to plot.

.. todo::
    Different plot according to dimension of FieldMap, or according to if it
    accelerates or not (ex when quadrupole defined by a field map)

"""

import itertools
import logging
from pathlib import Path
from typing import Any, Callable, Literal, Sequence

import matplotlib.pyplot as plt
import numpy as np
from cycler import cycler
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.typing import ColorType
from palettable.colorbrewer.qualitative import Dark2_8  # type: ignore

import lightwin.util.dicts_output as dic
from lightwin.beam_calculation.simulation_output.simulation_output import (
    SimulationOutput,
)
from lightwin.core.accelerator.accelerator import Accelerator
from lightwin.failures.fault import Fault
from lightwin.util import helper
from lightwin.util.typing import GETTABLE_SIMULATION_OUTPUT_T
from lightwin.visualization import structure
from lightwin.visualization.helper import (
    X_AXIS_T,
    create_fig_if_not_exists,
    savefig,
)
from lightwin.visualization.optimization import mark_objectives_position

font = {"family": "serif"}  # , 'size': 25}
plt.rc("font", **font)
plt.rcParams["axes.prop_cycle"] = cycler(color=Dark2_8.mpl_colors)

FALLBACK_PRESETS = {"x_axis": "z_abs", "plot_section": True, "sharex": True}
PLOT_PRESETS = {
    "energy": {
        "x_axis": "z_abs",
        "all_y_axis": ["w_kin", "w_kin_err", "struct"],
        "num": 21,
    },
    "phase": {
        "x_axis": "z_abs",
        "all_y_axis": ["phi_abs", "phi_abs_err", "struct"],
        "num": 22,
    },
    "cav": {
        "x_axis": "elt_idx",
        "all_y_axis": ["v_cav_mv", "phi_s", "struct"],
        "num": 23,
    },
    "emittance": {
        "x_axis": "z_abs",
        "all_y_axis": ["eps_phiw", "struct"],
        "num": 24,
    },
    "twiss": {
        "x_axis": "z_abs",
        "all_y_axis": ["alpha_phiw", "beta_phiw", "gamma_phiw"],
        "num": 25,
    },
    "envelopes": {
        "x_axis": "z_abs",
        "all_y_axis": [
            "envelope_pos_phiw",
            "envelope_energy_zdelta",
            "struct",
        ],
        "num": 26,
        "to_deg": False,
        "symetric_plot": True,
    },
    "mismatch_factor": {
        "x_axis": "z_abs",
        "all_y_axis": ["mismatch_factor_zdelta", "struct"],
        "num": 27,
    },
}
ERROR_PRESETS = {
    "w_kin_err": {"scale": 1.0, "diff": "simple"},
    "phi_abs_err": {"scale": 1.0, "diff": "simple"},
}
#: List of implemented presets for the plots
ALLOWED_PLOT_PRESETS = list(PLOT_PRESETS.keys())

# The one you generally want
ERROR_REFERENCE = "ref accelerator (1st solv w/ 1st solv, 2nd w/ 2nd)"

# These two are mostly useful when you want to study the differences between
# two solvers
# ERROR_REFERENCE = "ref accelerator (1st solver)"
# ERROR_REFERENCE = "ref accelerator (2nd solver)"


# =============================================================================
# Front end
# =============================================================================
def factory(
    accelerators: Sequence[Accelerator],
    plots: dict[str, Any],
    save_fig: bool = True,
    clean_fig: bool = True,
    fault_scenarios: Sequence[list[Fault]] | None = None,
    **kwargs,
) -> list[Figure]:
    """Create all the desired plots.

    Parameters
    ----------
    accelerators :
        The accelerators holding relatable data. Due to bad implementation, the
        following accelerators are expected:

        - Reference linac, first solver
        - Reference linac, second solver
        - Fixed linac, first solver
        - Fixed linac, second solver
        If you provide only the two first linacs, the function will still work
        but they will be plotted twice.
    plots :
        The plot ``TOML`` table.
    save_fig :
        If Figures should be saved.
    clean_fig :
        If Figures should be cleaned between two calls of this function.
    fault_scenarios :
        If provided, the position of the :class:`.Objective` will also appear
        on plots.
    kwargs :
        Other tables from the ``TOML`` configuration file.

    Returns
    -------
    figs : list[matplotlib.figure.Figure]
        The created figures.

    """
    if clean_fig and not save_fig and len(accelerators) > 2:
        logging.warning(
            "You will only see the plots of the last accelerators, previous "
            "will be erased without saving."
        )

    ref_acc = accelerators[0]
    # Dirty patch to force plot even when only one accelerator
    if len(accelerators) == 1:
        accelerators = (ref_acc, ref_acc)

    plots_presets, plots_kwargs = (
        _separate_plot_presets_from_plot_modificators(plots)
    )

    figs: list[Figure]
    figs = [
        _plot_preset(
            preset,
            *(ref_acc, fix_acc),
            save_fig=save_fig,
            clean_fig=clean_fig,
            fault_scenarios=fault_scenarios,
            **_proper_kwargs(preset, kwargs | plots_kwargs),
        )
        for fix_acc in accelerators[1:]
        for preset, plot_me in plots_presets.items()
        if plot_me
    ]
    return figs


def _separate_plot_presets_from_plot_modificators(
    plots: dict[str, Any],
) -> tuple[dict[str, bool], dict[str, Any]]:
    """Separate the config entries corresponding to the name of a plot.

    Parameters
    ----------
    plots :
        Dictionary holding the plot configuration.

    Returns
    -------
    plot_presets : dict[str, bool]
        Subset of ``plots``, with only the keys that can be found in
        :data:`ALLOWED_PLOT_PRESETS`. Indicates which plots presets will be plotted:
        ``"cav"``, ``"emittance"``...
    plot_kwargs : dict[str, Any]
        Subset of ``plots``, with only the keys corresponding to a plot
        modificator, eg ``"add_objectives"``.

    """
    plot_presets: dict[str, bool] = {}
    plot_kwargs: dict[str, Any] = {}
    for key, value in plots.items():
        if key in PLOT_PRESETS:
            plot_presets[key] = value
            continue
        plot_kwargs[key] = value
    return plot_presets, plot_kwargs


def _plot_preset(
    preset: str,
    *args: Accelerator,
    all_y_axis: list[GETTABLE_SIMULATION_OUTPUT_T | Literal["struct"]],
    x_axis: X_AXIS_T = "z_abs",
    save_fig: bool = True,
    clean_fig: bool = True,
    add_objectives: bool = False,
    fault_scenarios: Sequence[list[Fault]] | None = None,
    usr_kwargs: dict[str, Any] | None = None,
    **kwargs,
) -> Figure:
    """Plot a preset.

    Parameters
    ----------
    str_preset :
        Key of :data:`ALLOWED_PLOT_PRESETS`.
    *args :
        Accelerators to plot. In typical usage, ``args = (Working, Fixed)``
    x_axis :
        Name of the x axis.
    all_y_axis :
        Name of all the y axis.
    save_fig :
        To save Figures or not.
    add_objectives :
        To add the position of objectives to the plots; if True, the
        ``fault_scenarios`` must be provided.
    fault_scenarios :
        To plot the objectives, if ``add_objectives == True``.
    usr_kwargs :
        User-defined ``kwargs``, passed to the |axplot| method.
    **kwargs :
        Holds all complementary data on the plots.

    """
    fig, axx = create_fig_if_not_exists(
        len(all_y_axis), clean_fig=clean_fig, **kwargs
    )

    colors = None
    if usr_kwargs is None:
        usr_kwargs = {}
    for i, (ax, y_axis) in enumerate(zip(axx, all_y_axis)):
        _make_a_subplot(ax, x_axis, y_axis, colors, *args, **usr_kwargs)
        if i == 0:
            colors = _used_colors(ax)

        if add_objectives:
            mark_objectives_position(ax, fault_scenarios, y_axis, x_axis)

    axx[0].legend()
    axx[-1].set_xlabel(dic.markdown[x_axis])

    if save_fig:
        file = Path(args[-1].get("accelerator_path"), f"{preset}.png")
        savefig(fig, file)

    return fig


def _proper_kwargs(preset: str, kwargs: dict[str, Any]) -> dict[str, Any]:
    """Merge dicts, priority kwargs > PLOT_PRESETS > FALLBACK_PRESETS.

    We also add a ``"usr_kwargs"`` key holding additional keywords, that will
    be passed to |axplot|.

    """
    merged = FALLBACK_PRESETS | PLOT_PRESETS[preset] | kwargs
    if "kwargs" in merged:
        merged["usr_kwargs"] = merged.pop("kwargs")

    return merged


def _used_colors(axe: Axes) -> dict[str, ColorType]:
    """Associate every line label to a color."""
    lines = axe.get_lines()
    colors = {str(line.get_label()): line.get_color() for line in lines}
    return colors


def _y_label(y_axis: str) -> str:
    """Set the proper y axis label."""
    if "_err" in y_axis:
        key = ERROR_PRESETS[y_axis]["diff"]
        y_label = dic.markdown["err_" + key]
        return y_label
    y_label = dic.markdown[y_axis]
    return y_label


# Data getters
def _single_simulation_data(
    axis: GETTABLE_SIMULATION_OUTPUT_T, simulation_output: SimulationOutput
) -> list[float] | None:
    """lightwin.Get single data array from single SimulationOutput."""
    kwargs: dict[str, Any]
    kwargs = {
        "to_numpy": False,
        "to_deg": True,
        "warn_structure_dependent": False,
    }

    # patch to avoid envelopes being converted again to degrees
    if "envelope_pos" in axis:
        kwargs["to_deg"] = False
    data = simulation_output.get(axis, **kwargs)
    return data


def _single_simulation_all_data(
    x_axis: X_AXIS_T, y_axis: str, simulation_output: SimulationOutput
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    """Get x data, y data, kwargs from a SimulationOutput."""
    x_data = _single_simulation_data(x_axis, simulation_output)
    y_data = _single_simulation_data(y_axis, simulation_output)

    if None in (x_data, y_data):
        x_data = np.full((10, 1), np.nan)
        y_data = np.full((10, 1), np.nan)
        logging.warning(
            f"{x_axis} or {y_axis} not found in {simulation_output}"
        )
        return x_data, y_data, {}

    x_data = np.array(x_data)
    y_data = np.array(y_data)
    plt_kwargs = dic.plot_kwargs[y_axis].copy()
    return x_data, y_data, plt_kwargs


def _single_accelerator_all_simulations_data(
    x_axis: X_AXIS_T, y_axis: str, accelerator: Accelerator
) -> tuple[list[np.ndarray], list[np.ndarray], list[dict[str, Any]]]:
    """Get x_data, y_data, kwargs from all SimulationOutputs of Accelerator."""
    x_data, y_data, plt_kwargs = [], [], []
    ls = "-"
    for solver, simulation_output in accelerator.simulation_outputs.items():
        x_dat, y_dat, plt_kw = _single_simulation_all_data(
            x_axis, y_axis, simulation_output
        )
        short_solver = solver.split("(")[0]
        if simulation_output.is_multiparticle:
            short_solver += " (multipart)"

        plt_kw["label"] = " ".join([accelerator.name, short_solver])
        plt_kw["ls"] = ls
        ls = "--"

        x_data.append(x_dat)
        y_data.append(y_dat)
        plt_kwargs.append(plt_kw)

    return x_data, y_data, plt_kwargs


def _all_accelerators_data(
    x_axis: X_AXIS_T, y_axis: str, *accelerators: Accelerator
) -> tuple[list[np.ndarray], list[np.ndarray], list[dict[str, Any]]]:
    """Get x_data, y_data, kwargs from all Accelerators (<=> for 1 subplot)."""
    x_data, y_data, plt_kwargs = [], [], []

    key = y_axis
    error_plot = y_axis[-4:] == "_err"
    if error_plot:
        key = y_axis[:-4]

    for accelerator in accelerators:
        x_dat, y_dat, plt_kw = _single_accelerator_all_simulations_data(
            x_axis, key, accelerator
        )
        x_data += x_dat
        y_data += y_dat
        plt_kwargs += plt_kw

    if error_plot:
        fun_error = _error_calculation_function(y_axis)
        x_data, y_data, plt_kwargs = _compute_error(
            x_data, y_data, plt_kwargs, fun_error
        )

    plt_kwargs = _avoid_similar_labels(plt_kwargs)

    return x_data, y_data, plt_kwargs


def _avoid_similar_labels(plt_kwargs: list[dict]) -> list[dict]:
    """Append a number at the end of labels in doublons."""
    my_labels = []
    for kwargs in plt_kwargs:
        label = kwargs["label"]
        if label not in my_labels:
            my_labels.append(label)
            continue

        while kwargs["label"] in my_labels:
            try:
                i = int(label[-1])
                kwargs["label"] += str(i + 1)
            except ValueError:
                kwargs["label"] += "_0"

        my_labels.append(kwargs["label"])
    return plt_kwargs


# Error related
def _error_calculation_function(
    y_axis: str,
) -> tuple[Callable[[np.ndarray, np.ndarray], np.ndarray], str]:
    """Set the function called to compute error."""
    scale = ERROR_PRESETS[y_axis]["scale"]
    error_computers = {
        "simple": lambda y_ref, y_lin: scale * (y_ref - y_lin),
        "abs": lambda y_ref, y_lin: scale * np.abs(y_ref - y_lin),
        "rel": lambda y_ref, y_lin: scale * (y_ref - y_lin) / y_ref,
        "log": lambda y_ref, y_lin: scale * np.log10(np.abs(y_lin / y_ref)),
    }
    key = ERROR_PRESETS[y_axis]["diff"]
    fun_error = error_computers[key]
    return fun_error


def _compute_error(
    x_data: list[np.ndarray],
    y_data: list[np.ndarray],
    plt_kwargs: dict[str, Any],
    fun_error: Callable[[np.ndarray, np.ndarray], np.ndarray],
) -> tuple[list[np.ndarray], list[np.ndarray]]:
    """Compute error with proper reference and proper function."""
    simulation_indexes = range(len(x_data))
    if ERROR_REFERENCE == "ref accelerator (1st solv w/ 1st solv, 2nd w/ 2nd)":
        i_ref = [i for i in range(len(x_data) // 2)]
    elif ERROR_REFERENCE == "ref accelerator (1st solver)":
        i_ref = [0]
    elif ERROR_REFERENCE == "ref accelerator (2nd solver)":
        i_ref = [1]
        if len(x_data) < 4:
            logging.error(
                f"{ERROR_REFERENCE = } not supported when only one "
                "simulation is performed."
            )

            return np.full((10, 1), np.nan), np.full((10, 1), np.nan)
    else:
        logging.error(
            f"{ERROR_REFERENCE = }, which is not allowed. Check "
            "allowed values in _compute_error."
        )
        return np.full((10, 1), np.nan), np.full((10, 1), np.nan)

    i_err = [i for i in simulation_indexes if i not in i_ref]
    indexes_ref_with_err = itertools.zip_longest(
        i_ref, i_err, fillvalue=i_ref[0]
    )

    x_data_error, y_data_error = [], []
    for ref, err in indexes_ref_with_err:
        x_interp, y_ref, _, y_err = helper.resample(
            x_data[ref], y_data[ref], x_data[err], y_data[err]
        )
        error = fun_error(y_ref, y_err)

        x_data_error.append(x_interp)
        y_data_error.append(error)

    plt_kwargs = [plt_kwargs[i] for i in i_err]
    return x_data_error, y_data_error, plt_kwargs


# Actual interface with matplotlib
def _make_a_subplot(
    axe: Axes,
    x_axis: X_AXIS_T,
    y_axis: GETTABLE_SIMULATION_OUTPUT_T | Literal["struct"],
    colors: dict[str, ColorType] | None,
    *accelerators: Accelerator,
    plot_section: bool = True,
    symetric_plot: bool = False,
    **usr_kwargs,
) -> None:
    """Get proper data and plot it on an Axe.

    Parameters
    ----------
    axe :
        Object on which to add plot data.
    x_axis :
        Nature of x axis.
    y_axis :
        What to plot.
    colors :
       Holds the line labels from previous plots and associate it to their
       colors.
    accelerators :
        Objects from which we take ``y_axis``.
    plot_section :
        To outline the different sections in the background of the plots.
    symetric_plot :
        If a symetric plot (wrt x axis) should be added.
    usr_kwargs :
        User-defined ``kwargs``, passed to the |axplot| method.

    """
    if plot_section:
        structure.outline_sections(accelerators[0].elts, axe, x_axis=x_axis)

    if y_axis == "struct":
        return structure.plot_structure(
            accelerators[-1].elts, axe, x_axis=x_axis
        )

    x_data, y_data, plt_kwargs = _all_accelerators_data(
        x_axis, y_axis, *accelerators
    )

    # Alternate markers for the "cav" preset
    markers = ("o", "^")
    marker_index = 0

    for x, y, _plt_kwargs in zip(x_data, y_data, plt_kwargs):
        if y_axis in ("v_cav_mv", "phi_s"):
            _plt_kwargs["marker"] = markers[marker_index]
            marker_index = (marker_index + 1) % len(markers)

        if colors is not None and _plt_kwargs["label"] in colors:
            _plt_kwargs["color"] = colors[_plt_kwargs["label"]]

        (line,) = axe.plot(x, y, **_plt_kwargs | usr_kwargs)

        if symetric_plot:
            symetric_kwargs = _plt_kwargs | {
                "color": line.get_color(),
                "label": None,
            }
            axe.plot(x, -y, **symetric_kwargs)

    axe.grid(True)
    axe.set_ylabel(_y_label(y_axis))


def plot_pty_with_data_tags(ax, x, y, idx_list, tags=True):
    """Plot y vs x.

    Data at idx_list are magnified with bigger points and data tags.

    """
    (line,) = ax.plot(x, y)
    ax.scatter(x[idx_list], y[idx_list], color=line.get_color())

    if tags:
        n = len(idx_list)
        for i in range(n):
            txt = (
                str(np.round(x[idx_list][i], 4))
                + ","
                + str(np.round(y[idx_list][i], 4))
            )
            ax.annotate(txt, (x[idx_list][i], y[idx_list[i]]), size=8)
