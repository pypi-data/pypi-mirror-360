# -*- coding: utf-8 -*-
"""
Components that require PyWake.

@author: ricriv
"""

# %% Import.


import jax.numpy as jnp
import xarray as xr
from autograd.scipy.special import erf
from py_wake import np as anp  # Autograd numpy
from py_wake.flow_map import Points
from py_wake.utils import gradients
from py_wake.wind_farm_models.engineering_models import (
    All2AllIterative,
    PropagateDownwind,
    PropagateUpDownIterative,
)

from wind_farm_loads.tool_agnostic import (
    _get_sensor_names,
    _predict_loads_pod,
    _predict_loads_sector_average,
    preallocate_ilktn,
    rotate_grid,
)

# %% Pot functions.


def pot_tanh(r, R, exponent=20):
    r"""
    Smooth pot function based on tanh.

    .. math::
      y = \mathrm{tanh}\left(\left(\frac{r}{R}\right)^{a}\right)

    Values where :math:`|r| < R` are mapped to 0, while values outside of it are mapped to 1.

    Parameters
    ----------
    r : ndarray
        Radial distance :math:`r`.
    R : ndarray
        Distance at which to clip :math:`R`.
    exponent : int, optional
        Exponent :math:`a`. The default is 20.

    Returns
    -------
    y : ndarray
        Smooth pot of radius :math:`R`.

    """
    # Uses Autograd numpy because it is meant to work with PyWake.
    return anp.tanh((r / R) ** exponent)


def pot_arctan(r, R, exponent=100):
    r"""
    Smooth pot function based on arctan.

    .. math::
      y = \frac{2}{\pi} \mathrm{arctan}\left(\left(\frac{r}{R}\right)^{a}\right)

    Values where :math:`|r| < R` are mapped to 0, while values outside of it are mapped to 1.

    Parameters
    ----------
    r : ndarray
        Radial distance :math:`r`.
    R : ndarray
        Distance at which to clip :math:`R`.
    exponent : int, optional
        Exponent :math:`a`. The default is 100.

    Returns
    -------
    y : ndarray
        Smooth pot of radius :math:`R`.

    """
    # Uses Autograd numpy because it is meant to work with PyWake.
    return 2.0 / anp.pi * anp.arctan((r / R) ** exponent)


def pot_erf(r, R, exponent=20):
    r"""
    Smooth pot function based on the error function, implemented with JAX.

    .. math::
      y = \mathrm{erf}\left(\left(\frac{r}{R}\right)^{a}\right)

    Values where :math:`|r| < R` are mapped to 0, while values outside of it are mapped to 1.

    Parameters
    ----------
    r : ndarray
        Radial distance :math:`r`.
    R : ndarray
        Distance at which to clip :math:`R`.
    exponent : int, optional
        Exponent :math:`a`. The default is 20.

    Returns
    -------
    y : ndarray
        Smooth pot of radius :math:`R`.

    """
    # Uses Autograd numpy and Scipy because it is meant to work with PyWake.
    return erf((r / R) ** exponent)


def pot_sharp(r, R):
    r"""
    Sharp pot function.
    
    .. math::
      y = \begin{cases}
              0  &  \left| r \right| < R,    \\
              1  &  \left| r \right| \ge R
          \end{cases}

    Parameters
    ----------
    r : ndarray
        Radial distance :math:`r`.
    R : ndarray
        Distance at which to clip :math:`R`.

    Returns
    -------
    y : ndarray
        Sharp pot of radius :math:`R`.

    """
    # Uses Autograd numpy because it is meant to work with PyWake.
    return anp.where(anp.abs(r) < R, 0.0, 1.0)


# %% Classes to avoid self wake and self blockage.


class PropagateDownwindNoSelfInduction(PropagateDownwind):
    """Same as `PropagateDownwind`, but the wake, added turbulence and blockage are set to 0 in a sphere that surrounds each rotor.

    The objective of this class is to obtain a flow map that does not measure
    the induction of the current turbine, while keeping the same wind farm power.
    """

    def __init__(self, *args, pot=pot_sharp, **kwargs):
        PropagateDownwind.__init__(self, *args, **kwargs)
        self.pot = pot

    def _calc_deficit(self, dw_ijlk, cw_ijlk, D_src_il, **kwargs):
        deficit, blockage = PropagateDownwind._calc_deficit(
            self, dw_ijlk, cw_ijlk=cw_ijlk, D_src_il=D_src_il, **kwargs
        )
        r = gradients.hypot(dw_ijlk, cw_ijlk)
        weight = self.pot(r, 0.75 * D_src_il[:, anp.newaxis, :, anp.newaxis])
        deficit = deficit * weight
        if blockage is not None:
            blockage = blockage * weight
        return deficit, blockage

    def _calc_deficit_convection(self, dw_ijlk, cw_ijlk, D_src_il, **kwargs):
        deficit, uc, sigma_sqr = self.wake_deficitModel.calc_deficit_convection(
            dw_ijlk=dw_ijlk, cw_ijlk=cw_ijlk, D_src_il=D_src_il, **kwargs
        )
        deficit, blockage = self._add_blockage(deficit, dw_ijlk, **kwargs)
        r = gradients.hypot(dw_ijlk, cw_ijlk)
        weight = self.pot(r, 0.75 * D_src_il[:, anp.newaxis, :, anp.newaxis])
        deficit = deficit * weight
        if blockage is not None:
            blockage = blockage * weight
        return deficit, uc, sigma_sqr, blockage

    def _calc_added_turbulence(self, dw_ijlk, cw_ijlk, D_src_il, **kwargs):
        added_ti = self.turbulenceModel.calc_added_turbulence(
            dw_ijlk=dw_ijlk, cw_ijlk=cw_ijlk, D_src_il=D_src_il, **kwargs
        )
        r = gradients.hypot(dw_ijlk, cw_ijlk)
        weight = self.pot(r, 0.75 * D_src_il[:, anp.newaxis, :, anp.newaxis])
        added_ti = added_ti * weight
        return added_ti


class PropagateUpDownIterativeNoSelfInduction(PropagateUpDownIterative):
    """Same as `PropagateUpDownIterative`, but the wake, added turbulence and blockage are set to 0 in a sphere that surrounds each rotor.

    The objective of this class is to obtain a flow map that does not measure
    the induction of the current turbine, while keeping the same wind farm power.
    """

    def __init__(self, *args, pot=pot_sharp, **kwargs):
        PropagateUpDownIterative.__init__(self, *args, **kwargs)
        self.pot = pot

    def _calc_deficit(self, dw_ijlk, cw_ijlk, D_src_il, **kwargs):
        deficit, blockage = PropagateUpDownIterative._calc_deficit(
            self, dw_ijlk, cw_ijlk=cw_ijlk, D_src_il=D_src_il, **kwargs
        )
        r = gradients.hypot(dw_ijlk, cw_ijlk)
        weight = self.pot(r, 0.75 * D_src_il[:, anp.newaxis, :, anp.newaxis])
        deficit = deficit * weight
        if blockage is not None:
            blockage = blockage * weight

        return deficit, blockage

    def _calc_deficit_convection(self, dw_ijlk, cw_ijlk, D_src_il, **kwargs):
        deficit, uc, sigma_sqr = self.wake_deficitModel.calc_deficit_convection(
            dw_ijlk=dw_ijlk, cw_ijlk=cw_ijlk, D_src_il=D_src_il, **kwargs
        )
        deficit, blockage = self._add_blockage(deficit, dw_ijlk, **kwargs)
        r = gradients.hypot(dw_ijlk, cw_ijlk)
        weight = self.pot(r, 0.75 * D_src_il[:, anp.newaxis, :, anp.newaxis])
        deficit = deficit * weight
        if blockage is not None:
            blockage = blockage * weight
        return deficit, uc, sigma_sqr, blockage

    def _calc_added_turbulence(self, dw_ijlk, cw_ijlk, D_src_il, **kwargs):
        added_ti = self.turbulenceModel.calc_added_turbulence(
            dw_ijlk=dw_ijlk, cw_ijlk=cw_ijlk, D_src_il=D_src_il, **kwargs
        )
        r = gradients.hypot(dw_ijlk, cw_ijlk)
        weight = self.pot(r, 0.75 * D_src_il[:, anp.newaxis, :, anp.newaxis])
        added_ti = added_ti * weight
        return added_ti


class All2AllIterativeNoSelfInduction(All2AllIterative):
    """Same as `All2AllIterative`, but the wake, added turbulence and blockage are set to 0 in a sphere that surrounds each rotor.

    The objective of this class is to obtain a flow map that does not measure
    the induction of the current turbine, while keeping the same wind farm power.
    """

    def __init__(self, *args, pot=pot_sharp, **kwargs):
        All2AllIterative.__init__(self, *args, **kwargs)
        self.pot = pot

    def _calc_deficit(self, dw_ijlk, cw_ijlk, D_src_il, **kwargs):
        deficit, blockage = All2AllIterative._calc_deficit(
            self, dw_ijlk, cw_ijlk=cw_ijlk, D_src_il=D_src_il, **kwargs
        )
        r = gradients.hypot(dw_ijlk, cw_ijlk)
        weight = self.pot(r, 0.75 * D_src_il[:, anp.newaxis, :, anp.newaxis])
        deficit = deficit * weight
        if blockage is not None:
            blockage = blockage * weight
        return deficit, blockage

    def _calc_deficit_convection(self, dw_ijlk, cw_ijlk, D_src_il, **kwargs):
        deficit, uc, sigma_sqr = self.wake_deficitModel.calc_deficit_convection(
            dw_ijlk=dw_ijlk, cw_ijlk=cw_ijlk, D_src_il=D_src_il, **kwargs
        )
        deficit, blockage = self._add_blockage(deficit, dw_ijlk, **kwargs)
        r = gradients.hypot(dw_ijlk, cw_ijlk)
        weight = self.pot(r, 0.75 * D_src_il[:, anp.newaxis, :, anp.newaxis])
        deficit = deficit * weight
        if blockage is not None:
            blockage = blockage * weight
        return deficit, uc, sigma_sqr, blockage

    def _calc_added_turbulence(self, dw_ijlk, cw_ijlk, D_src_il, **kwargs):
        added_ti = self.turbulenceModel.calc_added_turbulence(
            dw_ijlk=dw_ijlk, cw_ijlk=cw_ijlk, D_src_il=D_src_il, **kwargs
        )
        r = gradients.hypot(dw_ijlk, cw_ijlk)
        weight = self.pot(r, 0.75 * D_src_il[:, anp.newaxis, :, anp.newaxis])
        added_ti = added_ti * weight
        return added_ti


# %% Functions to extract the inflow.


def _arg2ilk(v, I, L, K=None):
    """
    Convert a variable to shape `(I, L, K)` or `(I, L)` if `K` is not provided.

    Similar to `py_wake.utils.functions.arg2ilk`, with the difference that
    the variable is broadcasted to the specified shape and that a 2D output is allowed.
    The variable may be:

        - Constant.
        - Dependent on wind turbine `(I)`.
        - Dependent on wind turbine and wind direction or wind turbine and time `(IL)`.
        - Dependent on wind turbine, wind direction and wind speed `(ILK)`.


    Parameters
    ----------
    v : float, array_like
        Input variable that needs to be converted to `(I, L, K)` or `(I, L)` shape.
    I : int
        Number of turbines.
    L : int
        Number of wind directions or time.
    K : int, optional
        Number of wind speeds. When provided, `L` is the wind direction. The default is `None` which means that `L` is time.

    Returns
    -------
    r : (I, L, K) or (I, L) ndarray
        Input variable converted to `(I, L, K)` shape.

    """
    # Adapted from py_wake.utils.functions.arg2ilk
    if v is None:
        return v
    v_ = jnp.asarray(v)
    if v_.shape == ():
        #       wt           time                              wt           wd           ws
        v_ = v_[jnp.newaxis, jnp.newaxis] if K is None else v_[jnp.newaxis, jnp.newaxis, jnp.newaxis]  # fmt: skip

    elif v.shape in [(I,), (1,)]:
        #       wt time                              wt wd           ws
        v_ = v_[:, jnp.newaxis] if K is None else v_[:, jnp.newaxis, jnp.newaxis]

    elif v.shape in [(I, L), (1, L), (I, 1), (1, 1)]:
        #                            wt wd ws
        v_ = v_ if K is None else v_[:, :, jnp.newaxis]

    elif v.shape in {
        (I, L, K),
        (1, L, K),
        (I, 1, K),
        (I, L, 1),
        (1, 1, K),
        (1, L, 1),
        (I, 1, 1),
        (1, 1, 1),
    }:
        pass

    elif v.shape == (L,):
        #       wt           time                    wt           wd ws
        v_ = v_[jnp.newaxis, :] if K is None else v_[jnp.newaxis, :, jnp.newaxis]

    elif v.shape in [(L, K), (L, 1), (1, K)]:
        #       wt           time                    wt           wd ws
        v_ = v_[jnp.newaxis, :] if K is None else v_[jnp.newaxis, :, :]

    elif v.shape == (K,):
        #       wt           wd or time
        v_ = v_[jnp.newaxis, jnp.newaxis]

    else:
        valid_shapes = f"(), ({I}), ({I},{L}), ({I},{L},{K}), ({L},), ({L}, {K})"
        raise ValueError(
            f"Argument has shape {v.shape}, which is not supported. Valid shapes are {valid_shapes} (interpreted in this order)"
        )

    if K is None:
        return jnp.broadcast_to(v_, (I, L))
    else:
        return jnp.broadcast_to(v_, (I, L, K))


def get_rotor_averaged_wind_speed(sim_res):
    """
    Get rotor-averaged wind speed.

    Parameters
    ----------
    sim_res : py_wake SimulationResult
        A simulation result from PyWake. Must follow a call to the wind farm model.

    Returns
    -------
    WS_eff : xarray DataArray
        Effective wind speed as a function of: ambient wind speed, ambient wind direction, turbine number and type.

    """
    return sim_res["WS_eff"]


def get_rotor_averaged_turbulence_intensity(sim_res):
    """
    Get rotor-averaged turbulence intensity.

    Parameters
    ----------
    sim_res : py_wake SimulationResult
        A simulation result from PyWake. Must follow a call to the wind farm model.

    Returns
    -------
    TI_eff : xarray DataArray
        Effective turbulence intensity as a function of: ambient wind speed, ambient wind direction, turbine number and type.

    """
    return sim_res["TI_eff"]


def compute_flow_map(
    sim_res,
    grid,
    align_in_yaw=True,
    align_in_tilt=True,
    axial_wind=False,
    wt=None,
    wd=None,
    ws=None,
    time=None,
    dtype=jnp.float32,
    save_grid=False,
):
    r"""
    Compute the effective wind speed and Turbulence Intensity over a rotor.

    This function receives a grid, and then rotates it by the wind direction. Optionally,
    the grid is also rotated by the yaw and tilt of each turbine to align it with the rotor plane.
    Finally, the grid is translated to each rotor center and the flow map is computed.

    Parameters
    ----------
    sim_res : py_wake SimulationResult
        Simulation result computed by PyWake. Must follow a call to the wind farm model.
    grid : (N, M, 3) or (N, M, 3, Type) ndarray
        x, y and z coordinate of the grid points, before rotation by yaw and tilt.
        Typically generated by `make_rectangular_grid` or `make_polar_grid`.
        The first 2 dimensions cover the rotor, then there are x, y, z and finally (optionally) the turbine type.
        If the user passes a 3D array, the grid is assumed to be the same for all turbine types.
    align_in_yaw : bool, optional
        If `True` (default) the grid is aligned in yaw with the rotor plane.
    align_in_tilt : bool, optional
        If `True` (default) the grid is aligned in tilt with the rotor plane.
    axial_wind : bool, optional
        If `True` the axial wind speed and TI are returned. That is, the downstream wind speed computed by PyWake
        is multiplied by :math:`\cos(\mathrm{yaw}) \cos(\mathrm{tilt})`. The default is `False`.
    wt : int, (I) array_like, optional
        Wind turbines. Must be a subset of the one contained in `sim_res`.
        The default is `None`, which means to use all available wind turbines.
    wd : float, (L) array_like, optional
        Wind direction, in deg. Must be a subset of the one contained in `sim_res`.
        The default is `None`, which means to use all available wind directions.
    ws : float, (K) array_like, optional
        Wind speed. Must be a subset of the one contained in `sim_res`.
        The default is `None`, which means to use all available wind speeds.
    time : float, (Time) array_like, optional
        Time. Must be a subset of the one contained in `sim_res`.
        The default is `None`, which means to use all available time instants.
    dtype : data-type, optional
        The desired data-type for the result. The default is single precision,
        which should be enough for all outputs. The properties of each type can
        be checked with `np.finfo(np.float32(1.0))`.
    save_grid : bool, optional
        If `True` the grid will be saved for all inflow conditions. Since this comes at a significant
        memory cost, it is recommended to switch it on only for debug purposes.
        The default is `False`.

    Returns
    -------
    flow_map : xarray DataSet
        Effective wind speed, effective turbulence intensity and corresponding grid points
        for each turbine and flow case.

    """
    # Get the number of turbine types.
    n_types = len(sim_res.windFarmModel.windTurbines._names)

    # The grid must be a numpy array with 3 or 4 dimensions.
    # The first 2 cover the rotor, while the third is x, y and z.
    # The 4th dimension, if present, is over the types.
    # If the grid is a 3D array, then all turbine types share the same grid.
    if grid.ndim == 3:
        grid_t = jnp.broadcast_to(grid[:, :, :, jnp.newaxis], (*grid.shape, n_types))
    elif grid.ndim == 4:
        grid_t = grid
        # Check that there is 1 grid per turbine type.
        if grid_t.shape[3] != n_types:
            raise ValueError(
                f"{grid_t.shape[3]} grid types provided, but {n_types} were expected."
            )
    else:
        raise ValueError("The grid must be a 3D or 4D array.")

    # The default value of wt, wd, ws and time is the one in sim_res.
    wt_ = sim_res["wt"].values if wt is None else jnp.atleast_1d(wt)
    wd_ = sim_res["wd"].values if wd is None else jnp.atleast_1d(wd)
    ws_ = sim_res["ws"].values if ws is None else jnp.atleast_1d(ws)
    if "time" in sim_res.dims:
        if time is None:
            time_ = sim_res["time"].values
        else:
            if isinstance(time, xr.DataArray):
                time_ = time.values
            else:
                time_ = jnp.atleast_1d(time)

    # Convert yaw and tilt to arrays.
    # If time is not present the result has shape (I, L, K), i.e. (turbines, wind directions, wind speeds).
    # Instead, if time is present, the result has shape (I, Time), i.e. (turbines, time).
    # These arrays are contained in sim_res, therefore all turbines, directions and speeds and times must be used.
    I = sim_res.sizes["wt"]
    if "time" in sim_res.dims:
        Time = sim_res.sizes["time"]
        if align_in_yaw:
            yaw_turbines_ = _arg2ilk(sim_res["yaw"].values, I, Time)
        else:
            yaw_turbines_ = _arg2ilk(0.0, I, Time)
        if align_in_tilt:
            tilt_turbines_ = _arg2ilk(sim_res["tilt"].values, I, Time)
        else:
            tilt_turbines_ = _arg2ilk(0.0, I, Time)
    else:
        L = sim_res.sizes["wd"]
        K = sim_res.sizes["ws"]
        if align_in_yaw:
            yaw_turbines_ = _arg2ilk(sim_res["yaw"].values, I, L, K)
        else:
            yaw_turbines_ = _arg2ilk(0.0, I, L, K)
        if align_in_tilt:
            tilt_turbines_ = _arg2ilk(sim_res["tilt"].values, I, L, K)
        else:
            tilt_turbines_ = _arg2ilk(0.0, I, L, K)

    # Conveniently access turbine position.
    x_turbines_ = sim_res["x"].values
    y_turbines_ = sim_res["y"].values
    z_turbines_ = jnp.atleast_1d(sim_res["h"].values)

    # Convert all angles from deg to rad.
    wd_rad = jnp.deg2rad(wd_)
    yaw_turbines_ = jnp.deg2rad(yaw_turbines_)
    tilt_turbines_ = jnp.deg2rad(tilt_turbines_)

    cos_yaw_cos_tilt = jnp.cos(yaw_turbines_) * jnp.cos(tilt_turbines_)

    angle_ref = jnp.deg2rad(90.0)

    # Preallocate arrays to store the flow and grid.
    # In the flow map computed by PyWake the order of dimensions is: points (1D), wd, ws, or points (1D), time.
    # In the flow map returned by this function wt, wd and ws, or time, are placed first, followed by the quantity and grid dimensions.
    # This order enables vectorization in predict_loads_pod().
    # Each turbine type is allowed to have a different grid, but all grids must have the same number of points.
    if "time" in sim_res.dims:
        flow = jnp.full(
            (
                wt_.size,
                time_.size,
                2,  # Effective wind speed and TI.
                grid_t.shape[0],
                grid_t.shape[1],
            ),
            jnp.nan,
            dtype=dtype,
        )
        if save_grid:
            grid_saved = jnp.full(
                (
                    wt_.size,
                    time_.size,
                    3,  # x, y, z
                    grid_t.shape[0],
                    grid_t.shape[1],
                ),
                jnp.nan,
                dtype=dtype,
            )
    else:  # "time" not in sim_res.dims
        flow = jnp.full(
            (
                wt_.size,
                wd_.size,
                ws_.size,
                2,  # Effective wind speed and TI.
                grid_t.shape[0],
                grid_t.shape[1],
            ),
            jnp.nan,
            dtype=dtype,
        )
        if save_grid:
            grid_saved = jnp.full(
                (
                    wt_.size,
                    wd_.size,
                    ws_.size,
                    3,  # x, y, z
                    grid_t.shape[0],
                    grid_t.shape[1],
                ),
                jnp.nan,
                dtype=dtype,
            )

    # Save the grid for all turbines. We are going to update it at each time instant or wind direction and speed.
    # It is used to vectorize PyWake flow map over the turbines.
    grid_all_turbines = jnp.zeros(
        (
            wt_.size,
            grid_t.shape[0],
            grid_t.shape[1],
            3,  # x, y, z
        ),
        dtype=dtype,
    )

    if "time" in sim_res.dims:
        # Loop over time.
        for t in range(time_.size):
            # Loop over turbines.
            for i in range(wt_.size):
                # Get type of current turbine.
                # Convert DataArray to int, or it cannot be used for indexing.
                i_type = int(sim_res["type"][i])

                # Convert grid from downwind-crosswind-z to east-north-z.
                # While doing that, also rotate by yaw and tilt.
                # This can be done because the order of rotations is first yaw and then tilt.
                # It will NOT work for a floating turbine.
                # The formula for the yaw is taken from py_wake.wind_turbines._wind_turbines.WindTurbines.plot_xy()
                grid_current = rotate_grid(
                    grid_t[:, :, :, i_type],
                    yaw=angle_ref - wd_rad[t] + yaw_turbines_[i, t],  # [rad]
                    tilt=-tilt_turbines_[i, t],  # [rad]
                    degrees=False,
                )
                grid_all_turbines = grid_all_turbines.at[i, :, :, :].set(grid_current)

            # Translate grids to each rotor center. The turbine position is in east-north-z coordinates.
            grid_all_turbines = grid_all_turbines.at[:, :, :, 0].add(
                x_turbines_[wt_, jnp.newaxis, jnp.newaxis]
            )
            grid_all_turbines = grid_all_turbines.at[:, :, :, 1].add(
                y_turbines_[wt_, jnp.newaxis, jnp.newaxis]
            )
            grid_all_turbines = grid_all_turbines.at[:, :, :, 2].add(
                z_turbines_[wt_, jnp.newaxis, jnp.newaxis]
            )

            if save_grid:
                grid_saved = grid_saved.at[:, t, :, :, :].set(
                    grid_all_turbines.transpose(0, 3, 1, 2)
                )

            # Now that the grid is available for all rotors, compute the flow map.
            flow_map = sim_res.flow_map(
                grid=Points(
                    grid_all_turbines[:, :, :, 0].ravel(),
                    grid_all_turbines[:, :, :, 1].ravel(),
                    grid_all_turbines[:, :, :, 2].ravel(),
                ),
                time=time_[t],
            )
            flow = flow.at[:, t, 0, :, :].set(
                flow_map["WS_eff"].values.reshape(
                    wt_.size, grid_t.shape[0], grid_t.shape[1]
                )
            )
            flow = flow.at[:, t, 1, :, :].set(
                flow_map["TI_eff"].values.reshape(
                    wt_.size, grid_t.shape[0], grid_t.shape[1]
                )
            )

        # Project wind speed.
        if axial_wind:
            flow = flow * cos_yaw_cos_tilt[:, :, jnp.newaxis, jnp.newaxis, jnp.newaxis]

    else:  # "time" not in sim_res.dims
        # Loop over wind directions and wind speeds.
        for l in range(wd_.size):
            for k in range(ws_.size):
                # Loop over the turbines.
                for i in range(wt_.size):
                    # Get type of current turbine.
                    # Convert DataArray to int, or it cannot be used for indexing.
                    i_type = int(sim_res["type"][i])

                    # Convert grid from downwind-crosswind-z to east-north-z.
                    # While doing that, also rotate by yaw and tilt.
                    # This can be done because the order of rotations is first yaw and then tilt.
                    # It will NOT work for a floating turbine.
                    # We rely on this function to create new arrays, so that the following
                    # translation will not affect the original ones.
                    # The formula for the yaw is taken from py_wake.wind_turbines._wind_turbines.WindTurbines.plot_xy()
                    grid_current = rotate_grid(
                        grid_t[:, :, :, i_type],
                        yaw=angle_ref - wd_rad[l] + yaw_turbines_[i, l, k],  # [rad]
                        tilt=-tilt_turbines_[i, l, k],  # [rad]
                        degrees=False,
                    )
                    grid_all_turbines = grid_all_turbines.at[i, :, :, :].set(
                        grid_current
                    )

                # Translate grids to each rotor center. The turbine position is in east-north-z coordinates.
                grid_all_turbines = grid_all_turbines.at[:, :, :, 0].add(
                    x_turbines_[wt_, jnp.newaxis, jnp.newaxis]
                )
                grid_all_turbines = grid_all_turbines.at[:, :, :, 1].add(
                    y_turbines_[wt_, jnp.newaxis, jnp.newaxis]
                )
                grid_all_turbines = grid_all_turbines.at[:, :, :, 2].add(
                    z_turbines_[wt_, jnp.newaxis, jnp.newaxis]
                )

                if save_grid:
                    grid_saved = grid_saved.at[:, l, k, :, :, :].set(
                        grid_all_turbines.transpose(0, 3, 1, 2)
                    )

                # Now that the grid is available for all rotors, compute the flow map.
                flow_map = sim_res.flow_map(
                    grid=Points(
                        grid_all_turbines[:, :, :, 0].ravel(),
                        grid_all_turbines[:, :, :, 1].ravel(),
                        grid_all_turbines[:, :, :, 2].ravel(),
                    ),
                    wd=wd_[l],
                    ws=ws_[k],
                )
                flow = flow.at[:, l, k, 0, :, :].set(
                    flow_map["WS_eff"].values.reshape(
                        wt_.size, grid_t.shape[0], grid_t.shape[1]
                    )
                )
                flow = flow.at[:, l, k, 1, :, :].set(
                    flow_map["TI_eff"].values.reshape(
                        wt_.size, grid_t.shape[0], grid_t.shape[1]
                    )
                )

        # Project wind speed.
        if axial_wind:
            flow = (
                flow * cos_yaw_cos_tilt[:, :, :, jnp.newaxis, jnp.newaxis, jnp.newaxis]
            )

    # Store results into xarray Dataset.
    # The grid dimensions are labeled q0 and q1 because they might either be y and z or radius and azimuth.
    xr_dict = {}
    if "time" in sim_res.dims:
        # Set the independent coordinates: turbine, time and quantity.
        coords_flow = {
            "wt": wt_,
            "time": time_,
            "quantity": ["WS_eff", "TI_eff"],
        }
        dims_flow = list(coords_flow) + ["q0", "q1"]
        # Set the dependent coordinates: wind direction and wind speed.
        time_index = jnp.searchsorted(sim_res["time"].values, time_)
        coords_flow["wd"] = (["time"], wd_[time_index])
        coords_flow["ws"] = (["time"], ws_[time_index])

        xr_dict["flow"] = xr.DataArray(
            data=flow,
            coords=coords_flow,
            dims=dims_flow,
        )

        if save_grid:
            xr_dict["grid"] = xr.DataArray(
                data=grid_saved,
                coords={
                    "wt": wt_,
                    "time": time_,
                    "axis": ["x", "y", "z"],
                },
                dims=("wt", "time", "axis", "q0", "q1"),
            )

    else:  # "time" not in sim_res.dims
        xr_dict["flow"] = xr.DataArray(
            data=flow,
            coords={
                "wt": wt_,
                "wd": wd_,
                "ws": ws_,
                "quantity": ["WS_eff", "TI_eff"],
            },
            dims=("wt", "wd", "ws", "quantity", "q0", "q1"),
        )

        if save_grid:
            xr_dict["grid"] = xr.DataArray(
                data=grid_saved,
                coords={
                    "wt": wt_,
                    "wd": wd_,
                    "ws": ws_,
                    "axis": ["x", "y", "z"],
                },
                dims=("wt", "wd", "ws", "axis", "q0", "q1"),
            )
    ds = xr.Dataset(xr_dict)

    return ds


# %% Functions to evaluate the loads.


def predict_loads_rotor_average(
    surrogates, sim_res, *additional_inputs, dtype=jnp.float32, ti_in_percent=True
):
    r"""
    Evaluate the load surrogate models based on rotor-averaged wind speed and turbulence intensity. Additional (control) inputs are supported as well.

    Each load surrogate is evaluated as

    .. math::
      y = f(\mathrm{WS}, \mathrm{TI}, \boldsymbol{\theta})

    where :math:`\mathrm{WS}` is the rotor-averaged wind speed, :math:`\mathrm{TI}` is the rotor-averaged turbulence intensity and
    :math:`\boldsymbol{\theta}` are the additional inputs (typically, control parameters). The surrogates are evaluated
    for all turbines and ambient inflow conditions.

    The load database has been described in
    `Guilloré, A., Campagnolo, F. & Bottasso, C. L. (2024). A control-oriented load surrogate model based on sector-averaged inflow quantities: capturing damage for unwaked, waked, wake-steering and curtailed wind turbines <https://doi.org/10.1088/1742-6596/2767/3/032019>`_
    where it was proposed to include the controller set point by adding the yaw, pitch and rotor speed.
    This function has been developed using the surrogate models trained by Hari, which are based on the database provided by TUM.

    Parameters
    ----------
    surrogates : dict of surrogates_interface.surrogates.SurrogateModel
        Dictionary containing surrogate models. The keys will be used as sensor names.
    sim_res : py_wake SimulationResult
        Simulation result computed by PyWake. Must follow a call to the wind farm model.
    additional_inputs : list of ndarray
        Additional inputs to evaluate the load surrogate models.
        Must be coherent with the simulation result. PyWake rules are applied to broadcast each additional
        input to shape `(wt, wd, ws)` or `(wt, time)`. Typical additional inputs are:

            - Yaw, pitch and rotor speed.
            - Yaw and curtailment level.

        It is the user responsibility to pass the inputs in the order required by the surrogates, and to use the correct units.
    dtype : data-type, optional
        The desired data-type for the result. The default is single precision,
        which should be enough for all outputs. The properties of each type can
        be checked with `np.finfo(np.float32(1.0))`.
    ti_in_percent : bool
        If `True` (default) the turbulence intensity is multiplied by 100 before evaluating the surrogates.

    Returns
    -------
    loads : xarray.DataArray
        Loads for each turbine, ambient inflow condition and sensor.

    """
    # Preallocate JAX array to store the loads.
    name_sensors = _get_sensor_names(surrogates)
    if "time" in sim_res.dims:
        loads_data = jnp.full(
            (
                sim_res["wt"].size,
                sim_res["time"].size,
                len(name_sensors),
            ),
            jnp.nan,
            dtype=dtype,
        )
    else:
        loads_data = jnp.full(
            (
                sim_res["wt"].size,
                sim_res["wd"].size,
                sim_res["ws"].size,
                len(name_sensors),
            ),
            jnp.nan,
            dtype=dtype,
        )

    # Multiply the turbulence intensity by 100?
    if ti_in_percent:
        ti = sim_res["TI_eff"].values.ravel() * 100.0
    else:
        ti = sim_res["TI_eff"].values.ravel()

    # Ensure that the additional inputs have shape [wt, wd, ws] or [wt, time].
    if "time" in sim_res.dims:
        theta = [
            _arg2ilk(th, sim_res["wt"].size, sim_res["time"].size).ravel().astype(dtype)
            for th in additional_inputs
        ]
    else:
        theta = [
            _arg2ilk(
                th,
                sim_res["wt"].size,
                sim_res["wd"].size,
                sim_res["ws"].size,
            )
            .ravel()
            .astype(dtype)
            for th in additional_inputs
        ]

    # Compose input for load surrogate.
    x = jnp.column_stack(
        (
            sim_res["WS_eff"].values.astype(dtype).ravel(),  # [m/s]
            ti.astype(dtype),
            *theta,
        )
    )

    # Loop over the surrogate models and evaluate them.
    for i, sensor in zip(range(len(surrogates)), list(surrogates.keys())):
        loads_data = loads_data.at[..., i].set(
            surrogates[sensor].predict_output(x).reshape(sim_res["WS_eff"].shape)
        )

    # Store the loads into a xarray DataArray.
    loads = preallocate_ilktn(
        wt=sim_res["wt"].values,
        wd=sim_res["wd"].values,
        ws=sim_res["ws"].values,
        time=sim_res["time"].values if "time" in sim_res.dims else None,
        name=name_sensors,
        data=loads_data,
    )

    return loads


def predict_loads_pod(
    surrogates,
    flow_map,
    *additional_inputs,
    dtype=jnp.float32,
    ti_in_percent=True,
):
    r"""
    Evaluate the load surrogate models based on Proper Orthogonal Decomposition of wind speed and turbulence intensity. Additional (control) inputs are supported as well.

    Each load surrogate is evaluated as

    .. math::
      y = f(\mathrm{WS}, \mathrm{TI}, \boldsymbol{\theta})

    where :math:`\mathrm{WS}` is the wind speed over the grid used to generated the POD basis, :math:`\mathrm{TI}` is
    the turbulence intensity over the grid used to generated the POD basis and :math:`\boldsymbol{\theta}` are the
    additional inputs (typically, control parameters). The surrogates are evaluated for all turbines and ambient inflow conditions.

    The load database has been described in
    `Guilloré, A., Campagnolo, F. & Bottasso, C. L. (2024). A control-oriented load surrogate model based on sector-averaged inflow quantities: capturing damage for unwaked, waked, wake-steering and curtailed wind turbines <https://doi.org/10.1088/1742-6596/2767/3/032019>`_
    where it was proposed to include the controller set point by adding the yaw, pitch and rotor speed.
    This function has been developed using the surrogate models trained by Hari, which are based on the database provided by TUM.

    Parameters
    ----------
    surrogates : dict of surrogates_interface.surrogates.SurrogateModel
        Dictionary containing surrogate models. The keys will be used as sensor names.
    flow_map : xarray DataSet
        Effective wind speed, effective turbulence intensity and corresponding grid points
        for each turbine and flow case. Generated by `compute_flow_map()`.
    additional_inputs : list of ndarray
        Additional inputs to evaluate the load surrogate models.
        Must be coherent with the flow map. PyWake rules are applied to broadcast each additional
        input to shape `(wt, wd, ws)` or `(wt, time)`. Typical additional inputs are:

            - Yaw, pitch and rotor speed.
            - Yaw and curtailment level.

        It is the user responsibility to pass the inputs in the order required by the surrogates, and to use the correct units.
    dtype : data-type, optional
        The desired data-type for the result. The default is single precision,
        which should be enough for all outputs. The properties of each type can
        be checked with `np.finfo(np.float32(1.0))`.
    ti_in_percent : bool
        If `True` (default) the turbulence intensity is multiplied by 100 before evaluating the surrogates.

    Returns
    -------
    loads : xarray.DataArray
        Loads for each turbine, ambient inflow condition and sensor.

    """
    return _predict_loads_pod(
        surrogates,
        flow_map,
        _arg2ilk,
        *additional_inputs,
        dtype=jnp.float32,
        ti_in_percent=True,
    )


def predict_loads_sector_average(
    surrogates,
    sector_average,
    *additional_inputs,
    dtype=jnp.float32,
    ti_in_percent=True,
):
    r"""
    Evaluate the load surrogate models based on sector average of wind speed and turbulence intensity. Additional (control) inputs are supported as well.

    Each load surrogate is evaluated as

    .. math::
      y = f(\mathrm{WS}, \mathrm{TI}, \boldsymbol{\theta})

    where :math:`\mathrm{WS}` is the sector-averaged wind speed, :math:`\mathrm{TI}` is the sector-averaged
    turbulence intensity and :math:`\boldsymbol{\theta}` are the additional inputs (typically, control parameters).
    The surrogates are evaluated for all turbines and ambient inflow conditions.

    The load database has been described in
    `Guilloré, A., Campagnolo, F. & Bottasso, C. L. (2024). A control-oriented load surrogate model based on sector-averaged inflow quantities: capturing damage for unwaked, waked, wake-steering and curtailed wind turbines <https://doi.org/10.1088/1742-6596/2767/3/032019>`_
    where it was proposed to include the controller set point by adding the yaw, pitch and rotor speed.
    This function has been developed using the surrogate models trained by Hari, which are based on the database provided by TUM.

    Parameters
    ----------
    surrogates : dict of surrogates_interface.surrogates.SurrogateModel
        Dictionary containing surrogate models. The keys will be used as sensor names.
    sector_average : xarray DataArray
        Sector average of effective wind speed and effective turbulence intensity
        for each turbine and flow case. Generated by `compute_sector_average()`.
    additional_inputs : list of ndarray
        Additional inputs to evaluate the load surrogate models.
        Must be coherent with the sector average. PyWake rules are applied to broadcast each additional
        input to shape `(wt, wd, ws)` or `(wt, time)`. Typical additional inputs are:

            - Yaw, pitch and rotor speed.
            - Yaw and curtailment level.

        It is the user responsibility to pass the inputs in the order required by the surrogates, and to use the correct units.
    dtype : data-type, optional
        The desired data-type for the result. The default is single precision,
        which should be enough for all outputs. The properties of each type can
        be checked with `np.finfo(np.float32(1.0))`.
    ti_in_percent : bool
        If `True` (default) the turbulence intensity is multiplied by 100 before evaluating the surrogates.

    Returns
    -------
    loads : xarray.DataArray
        Loads for each turbine, ambient inflow condition and sensor.

    """
    return _predict_loads_sector_average(
        surrogates,
        sector_average,
        _arg2ilk,
        *additional_inputs,
        dtype=jnp.float32,
        ti_in_percent=True,
    )
