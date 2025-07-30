#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Numba translations for some functions from the finite_elem_mapping module from
AxiSEM's kernel module.

:copyright:
    Lion Krischer (lion.krischer@gmail.com), 2025
:license:
    GNU Lesser General Public License, Version 3 [non-commercial/academic use]
    (http://www.gnu.org/copyleft/lgpl.html)
"""

import numpy as np
from numba import njit
import instaseis


def inside_element(
    s: float, z: float, nodes: np.ndarray, element_type: int, tolerance: float
) -> tuple[bool, float, float]:
    """Tests whether a point described by global coordinates s,z is inside an element
    and returns reference coordinates xi and eta.

    :param s: Global s-coordinate of the point.
    :param z: Global z-coordinate of the point.
    :param nodes: A (4, 2) array with the s and z coordinates of the 4 element nodes.
                  nodes(0,:) corresponds to node 1, nodes(1,:) to node 2, etc.
    :param element_type: Integer specifying the element type:
                         0: spheroid
                         1: subpar
                         2: semino
                         3: semiso
    :param tolerance: Tolerance for checking if the point is inside the element.
    :return: A tuple (in_element, xi, eta):
             in_element (bool): True if the point is inside the element, False otherwise.
             xi (float): Reference xi-coordinate.
             eta (float): Reference eta-coordinate.
    """
    inv_mapping = np.zeros(2, dtype=np.float64)
    in_element = False
    xi = 0.0
    eta = 0.0

    if element_type == 0:
        inv_mapping = inv_mapping_spheroid(s, z, nodes)
    elif element_type == 1:
        inv_mapping = inv_mapping_subpar(s, z, nodes)
    elif element_type == 2:
        inv_mapping = inv_mapping_semino(s, z, nodes)
    elif element_type == 3:
        inv_mapping = inv_mapping_semiso(s, z, nodes)
    else:
        raise ValueError(f"ERROR: unknown element type: {element_type}")

    in_element = (
        inv_mapping[0] >= -1 - tolerance
        and inv_mapping[0] <= 1 + tolerance
        and inv_mapping[1] >= -1 - tolerance
        and inv_mapping[1] <= 1 + tolerance
    )

    if in_element:
        xi = inv_mapping[0]
        eta = inv_mapping[1]

    return in_element, xi, eta


# Helper Numba functions
@njit(cache=instaseis._use_numba_cache)
def compute_theta_r(nodes: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Computes polar coordinates (theta, r) for each node.

    Node numbering of the elements is:
    4 - - - - - - - 3
    |       ^       |
    |   eta |       |
    |       |       |
    |        --->   |
    |        xi     |
    |               |
    |               |
    1 - - - - - - - 2

    :param nodes: A (4, 2) array with the s and z coordinates of the 4 element nodes.
    :return: A tuple (theta, r):
             theta (np.ndarray): Array of 4 theta values (angle from z-axis).
             r (np.ndarray): Array of 4 r values (radial distance).
    """
    r = np.empty(4, dtype=np.float64)
    theta = np.empty(4, dtype=np.float64)
    for i in range(4):
        # Ensure nodes[i,0] and nodes[i,1] are float for Numba type stability if nodes can be int
        s_coord = float(nodes[i, 0])
        z_coord = float(nodes[i, 1])
        r_val = np.sqrt(s_coord**2 + z_coord**2)
        r[i] = r_val
        if r_val != 0.0:
            # Ensure argument for arccos is within [-1, 1]
            acos_arg = z_coord / r_val
            if acos_arg > 1.0:
                acos_arg = 1.0
            elif acos_arg < -1.0:
                acos_arg = -1.0
            theta[i] = np.arccos(acos_arg)
        else:
            theta[i] = 0.0
    return theta, r


@njit(cache=instaseis._use_numba_cache)
def shp4(xi: float, eta: float) -> np.ndarray:
    """Computes the linear shape functions for a 4-node quadrilateral element
    at a given point (xi, eta) in the reference domain.

    :param xi: Reference xi-coordinate (-1 to 1).
    :param eta: Reference eta-coordinate (-1 to 1).
    :return: np.ndarray of shape (4,) containing the shape function values N1, N2, N3, N4.
    """
    shp = np.empty(4, dtype=np.float64)
    xip = 1.0 + xi
    xim = 1.0 - xi
    etap = 1.0 + eta
    etam = 1.0 - eta
    shp[0] = xim * etam / 4.0
    shp[1] = xip * etam / 4.0
    shp[2] = xip * etap / 4.0
    shp[3] = xim * etap / 4.0
    return shp


@njit(cache=instaseis._use_numba_cache)
def shp4der(xi: float, eta: float) -> np.ndarray:
    """Computes the derivatives of the linear shape functions for a 4-node
    quadrilateral element with respect to xi and eta at a given point (xi, eta)
    in the reference domain.

    :param xi: Reference xi-coordinate (-1 to 1).
    :param eta: Reference eta-coordinate (-1 to 1).
    :return: np.ndarray of shape (4, 2) containing the derivatives.
             Column 0: derivatives with respect to xi (dN/dxi).
             Column 1: derivatives with respect to eta (dN/deta).
    """
    shpder_val = np.empty((4, 2), dtype=np.float64)
    xip = 1.0 + xi
    xim = 1.0 - xi
    etap = 1.0 + eta
    etam = 1.0 - eta

    # derivatives with respect to xi (column 0)
    shpder_val[0, 0] = -etam / 4.0
    shpder_val[1, 0] = etam / 4.0
    shpder_val[2, 0] = etap / 4.0
    shpder_val[3, 0] = -etap / 4.0

    # derivatives with respect to eta (column 1)
    shpder_val[0, 1] = -xim / 4.0
    shpder_val[1, 1] = -xip / 4.0
    shpder_val[2, 1] = xip / 4.0
    shpder_val[3, 1] = xim / 4.0
    return shpder_val


# Subpar Numba functions
@njit(cache=instaseis._use_numba_cache)
def mapping_subpar(xi: float, eta: float, nodes: np.ndarray) -> np.ndarray:
    """Computes the physical coordinates (s, z) for a point (xi, eta)
    in the reference element using subparametric mapping.

    :param xi: Reference xi-coordinate.
    :param eta: Reference eta-coordinate.
    :param nodes: A (4, 2) array with the s and z coordinates of the 4 element nodes.
    :return: np.ndarray of shape (2,) containing the physical coordinates [s, z].
    """
    shp_vals = shp4(xi, eta)
    mapping_val = np.zeros(2, dtype=np.float64)
    for i in range(4):
        mapping_val[0] += shp_vals[i] * nodes[i, 0]
        mapping_val[1] += shp_vals[i] * nodes[i, 1]
    return mapping_val


@njit(cache=instaseis._use_numba_cache)
def jacobian_subpar(xi: float, eta: float, nodes: np.ndarray) -> np.ndarray:
    """Computes the Jacobian matrix for subparametric mapping at (xi, eta).
    J = | ds/dxi  ds/deta |
        | dz/dxi  dz/deta |.

    :param xi: Reference xi-coordinate.
    :param eta: Reference eta-coordinate.
    :param nodes: A (4, 2) array with the s and z coordinates of the 4 element nodes.
    :return: np.ndarray of shape (2, 2) representing the Jacobian matrix.
    """
    shpder_vals = shp4der(xi, eta)
    jacobian_val = np.zeros((2, 2), dtype=np.float64)
    for i in range(4):
        jacobian_val[0, 0] += nodes[i, 0] * shpder_vals[i, 0]
        jacobian_val[0, 1] += nodes[i, 0] * shpder_vals[i, 1]
        jacobian_val[1, 0] += nodes[i, 1] * shpder_vals[i, 0]
        jacobian_val[1, 1] += nodes[i, 1] * shpder_vals[i, 1]
    return jacobian_val


@njit(cache=instaseis._use_numba_cache)
def inv_jacobian_subpar(
    xi: float, eta: float, nodes: np.ndarray
) -> np.ndarray:
    """Computes the inverse of the Jacobian matrix for subparametric mapping at (xi, eta).
    J^-1 = | dxi/ds  dxi/dz |
           | deta/ds deta/dz |.

    :param xi: Reference xi-coordinate.
    :param eta: Reference eta-coordinate.
    :param nodes: A (4, 2) array with the s and z coordinates of the 4 element nodes.
    :return: np.ndarray of shape (2, 2) representing the inverse Jacobian matrix.
    """
    inv_jacobian_val = np.empty((2, 2), dtype=np.float64)
    jacobian_val = jacobian_subpar(xi, eta, nodes)
    det = (
        jacobian_val[0, 0] * jacobian_val[1, 1]
        - jacobian_val[0, 1] * jacobian_val[1, 0]
    )
    if det == 0:  # Avoid division by zero; can happen for degenerate elements
        # Return a zero matrix or raise an error, depending on desired handling
        # For now, returning a matrix that might lead to non-convergence or NaN
        det = 1e-100  # A very small number to avoid direct zero division
    inv_jacobian_val[0, 0] = jacobian_val[1, 1] / det
    inv_jacobian_val[0, 1] = -jacobian_val[0, 1] / det
    inv_jacobian_val[1, 0] = -jacobian_val[1, 0] / det
    inv_jacobian_val[1, 1] = jacobian_val[0, 0] / det
    return inv_jacobian_val


# Spheroid Numba functions
@njit(cache=instaseis._use_numba_cache)
def mapping_spheroid(xi: float, eta: float, nodes: np.ndarray) -> np.ndarray:
    """Computes the physical coordinates (s, z) for a point (xi, eta)
    in the reference element using spheroidal mapping.

    :param xi: Reference xi-coordinate.
    :param eta: Reference eta-coordinate.
    :param nodes: A (4, 2) array with the s and z coordinates of the 4 element nodes.
    :return: np.ndarray of shape (2,) containing the physical coordinates [s, z].
    """
    theta_vals, r_vals = compute_theta_r(nodes)
    mapping_val = np.empty(2, dtype=np.float64)

    term1_factor = (1.0 + eta) * r_vals[3] / 2.0
    arg1_sin_cos = (
        (1.0 - xi) * theta_vals[3] + (1.0 + xi) * theta_vals[2]
    ) / 2.0

    term2_factor = (1.0 - eta) * r_vals[0] / 2.0
    arg2_sin_cos = (
        (1.0 - xi) * theta_vals[0] + (1.0 + xi) * theta_vals[1]
    ) / 2.0

    mapping_val[0] = term1_factor * np.sin(
        arg1_sin_cos
    ) + term2_factor * np.sin(arg2_sin_cos)
    mapping_val[1] = term1_factor * np.cos(
        arg1_sin_cos
    ) + term2_factor * np.cos(arg2_sin_cos)

    return mapping_val


@njit(cache=instaseis._use_numba_cache)
def jacobian_spheroid(xi: float, eta: float, nodes: np.ndarray) -> np.ndarray:
    """Computes the Jacobian matrix for spheroidal mapping at (xi, eta).
    J = | ds/dxi  ds/deta |
        | dz/dxi  dz/deta |.

    :param xi: Reference xi-coordinate.
    :param eta: Reference eta-coordinate.
    :param nodes: A (4, 2) array with the s and z coordinates of the 4 element nodes.
    :return: np.ndarray of shape (2, 2) representing the Jacobian matrix.
    """
    theta_vals, r_vals = compute_theta_r(nodes)
    jacobian_val = np.empty((2, 2), dtype=np.float64)

    arg1 = ((1.0 - xi) * theta_vals[3] + (1.0 + xi) * theta_vals[2]) / 2.0
    arg2 = ((1.0 - xi) * theta_vals[0] + (1.0 + xi) * theta_vals[1]) / 2.0

    term1_ds_dxi = (
        (1.0 + eta)
        * r_vals[3]
        * (theta_vals[2] - theta_vals[3])
        / 4.0
        * np.cos(arg1)
    )
    term2_ds_dxi = (
        (1.0 - eta)
        * r_vals[0]
        * (theta_vals[1] - theta_vals[0])
        / 4.0
        * np.cos(arg2)
    )
    jacobian_val[0, 0] = term1_ds_dxi + term2_ds_dxi

    term1_ds_deta = r_vals[3] * np.sin(arg1)
    term2_ds_deta = r_vals[0] * np.sin(arg2)
    jacobian_val[0, 1] = 0.5 * (term1_ds_deta - term2_ds_deta)

    term1_dz_dxi = (
        -(1.0 + eta)
        * r_vals[3]
        * (theta_vals[2] - theta_vals[3])
        / 4.0
        * np.sin(arg1)
    )
    term2_dz_dxi = (
        -(1.0 - eta)
        * r_vals[0]
        * (theta_vals[1] - theta_vals[0])
        / 4.0
        * np.sin(arg2)
    )
    jacobian_val[1, 0] = term1_dz_dxi + term2_dz_dxi

    term1_dz_deta = r_vals[3] * np.cos(arg1)
    term2_dz_deta = r_vals[0] * np.cos(arg2)
    jacobian_val[1, 1] = 0.5 * (term1_dz_deta - term2_dz_deta)

    return jacobian_val


@njit(cache=instaseis._use_numba_cache)
def inv_jacobian_spheroid(
    xi: float, eta: float, nodes: np.ndarray
) -> np.ndarray:
    """Computes the inverse of the Jacobian matrix for spheroidal mapping at (xi, eta).
    J^-1 = | dxi/ds  dxi/dz |
           | deta/ds deta/dz |.

    :param xi: Reference xi-coordinate.
    :param eta: Reference eta-coordinate.
    :param nodes: A (4, 2) array with the s and z coordinates of the 4 element nodes.
    :return: np.ndarray of shape (2, 2) representing the inverse Jacobian matrix.
    """
    inv_jacobian_val = np.empty((2, 2), dtype=np.float64)
    jacobian_val = jacobian_spheroid(xi, eta, nodes)
    det = (
        jacobian_val[0, 0] * jacobian_val[1, 1]
        - jacobian_val[0, 1] * jacobian_val[1, 0]
    )
    if det == 0:
        det = 1e-100
    inv_jacobian_val[0, 0] = jacobian_val[1, 1] / det
    inv_jacobian_val[0, 1] = -jacobian_val[0, 1] / det
    inv_jacobian_val[1, 0] = -jacobian_val[1, 0] / det
    inv_jacobian_val[1, 1] = jacobian_val[0, 0] / det
    return inv_jacobian_val


# Semino Numba functions
@njit(cache=instaseis._use_numba_cache)
def mapping_semino(xi: float, eta: float, nodes: np.ndarray) -> np.ndarray:
    """Computes the physical coordinates (s, z) for a point (xi, eta)
    in the reference element using semi-spheroidal mapping (semino type:
    linear at bottom, curved at top).

    :param xi: Reference xi-coordinate.
    :param eta: Reference eta-coordinate.
    :param nodes: A (4, 2) array with the s and z coordinates of the 4 element nodes.
    :return: np.ndarray of shape (2,) containing the physical coordinates [s, z].
    """
    theta_vals, r_vals = compute_theta_r(nodes)
    mapping_val = np.empty(2, dtype=np.float64)

    factor_top_coeff = (1.0 + eta) / 2.0
    r4 = r_vals[3]
    arg_top_sin_cos = (
        (1.0 - xi) * theta_vals[3] + (1.0 + xi) * theta_vals[2]
    ) / 2.0
    s_top = factor_top_coeff * r4 * np.sin(arg_top_sin_cos)
    z_top = factor_top_coeff * r4 * np.cos(arg_top_sin_cos)

    factor_bottom_coeff = (1.0 - eta) / 2.0
    s_bottom_interp = (
        (1.0 - xi) * nodes[0, 0] + (1.0 + xi) * nodes[1, 0]
    ) / 2.0
    z_bottom_interp = (
        (1.0 - xi) * nodes[0, 1] + (1.0 + xi) * nodes[1, 1]
    ) / 2.0
    s_bottom = factor_bottom_coeff * s_bottom_interp
    z_bottom = factor_bottom_coeff * z_bottom_interp

    mapping_val[0] = s_top + s_bottom
    mapping_val[1] = z_top + z_bottom
    return mapping_val


@njit(cache=instaseis._use_numba_cache)
def jacobian_semino(xi: float, eta: float, nodes: np.ndarray) -> np.ndarray:
    """Computes the Jacobian matrix for semi-spheroidal mapping (semino type) at (xi, eta).
    J = | ds/dxi  ds/deta |
        | dz/dxi  dz/deta |.

    :param xi: Reference xi-coordinate.
    :param eta: Reference eta-coordinate.
    :param nodes: A (4, 2) array with the s and z coordinates of the 4 element nodes.
    :return: np.ndarray of shape (2, 2) representing the Jacobian matrix.
    """
    theta_vals, r_vals = compute_theta_r(nodes)
    jacobian_val = np.empty((2, 2), dtype=np.float64)
    r4 = r_vals[3]
    arg_top = ((1.0 - xi) * theta_vals[3] + (1.0 + xi) * theta_vals[2]) / 2.0

    jacobian_val[0, 0] = (1.0 + eta) * r4 * (
        theta_vals[2] - theta_vals[3]
    ) / 4.0 * np.cos(arg_top) + (1.0 - eta) / 4.0 * (nodes[1, 0] - nodes[0, 0])
    jacobian_val[0, 1] = r4 / 2.0 * np.sin(arg_top) - 1.0 / 4.0 * (
        (1.0 - xi) * nodes[0, 0] + (1.0 + xi) * nodes[1, 0]
    )
    jacobian_val[1, 0] = -(1.0 + eta) * r4 * (
        theta_vals[2] - theta_vals[3]
    ) / 4.0 * np.sin(arg_top) + (1.0 - eta) / 4.0 * (nodes[1, 1] - nodes[0, 1])
    jacobian_val[1, 1] = r4 / 2.0 * np.cos(arg_top) - 1.0 / 4.0 * (
        (1.0 - xi) * nodes[0, 1] + (1.0 + xi) * nodes[1, 1]
    )
    return jacobian_val


@njit(cache=instaseis._use_numba_cache)
def inv_jacobian_semino(
    xi: float, eta: float, nodes: np.ndarray
) -> np.ndarray:
    """Computes the inverse of the Jacobian matrix for semi-spheroidal mapping (semino type)
    at (xi, eta).
    J^-1 = | dxi/ds  dxi/dz |
           | deta/ds deta/dz |.

    :param xi: Reference xi-coordinate.
    :param eta: Reference eta-coordinate.
    :param nodes: A (4, 2) array with the s and z coordinates of the 4 element nodes.
    :return: np.ndarray of shape (2, 2) representing the inverse Jacobian matrix.
    """
    inv_jacobian_val = np.empty((2, 2), dtype=np.float64)
    jacobian_val = jacobian_semino(xi, eta, nodes)
    det = (
        jacobian_val[0, 0] * jacobian_val[1, 1]
        - jacobian_val[0, 1] * jacobian_val[1, 0]
    )
    if det == 0:
        det = 1e-100
    inv_jacobian_val[0, 0] = jacobian_val[1, 1] / det
    inv_jacobian_val[0, 1] = -jacobian_val[0, 1] / det
    inv_jacobian_val[1, 0] = -jacobian_val[1, 0] / det
    inv_jacobian_val[1, 1] = jacobian_val[0, 0] / det
    return inv_jacobian_val


# Semiso Numba functions
@njit(cache=instaseis._use_numba_cache)
def mapping_semiso(xi: float, eta: float, nodes: np.ndarray) -> np.ndarray:
    """Computes the physical coordinates (s, z) for a point (xi, eta)
    in the reference element using semi-spheroidal mapping (semiso type:
    linear at top, curved at bottom).

    :param xi: Reference xi-coordinate.
    :param eta: Reference eta-coordinate.
    :param nodes: A (4, 2) array with the s and z coordinates of the 4 element nodes.
    :return: np.ndarray of shape (2,) containing the physical coordinates [s, z].
    """
    theta_vals, r_vals = compute_theta_r(nodes)
    mapping_val = np.empty(2, dtype=np.float64)

    factor_top_coeff = (1.0 + eta) / 2.0
    s_top_interp = ((1.0 - xi) * nodes[3, 0] + (1.0 + xi) * nodes[2, 0]) / 2.0
    z_top_interp = ((1.0 - xi) * nodes[3, 1] + (1.0 + xi) * nodes[2, 1]) / 2.0
    s_top = factor_top_coeff * s_top_interp
    z_top = factor_top_coeff * z_top_interp

    factor_bottom_coeff = (1.0 - eta) / 2.0
    r1 = r_vals[0]
    arg_bottom_sin_cos = (
        (1.0 - xi) * theta_vals[0] + (1.0 + xi) * theta_vals[1]
    ) / 2.0
    s_bottom = factor_bottom_coeff * r1 * np.sin(arg_bottom_sin_cos)
    z_bottom = factor_bottom_coeff * r1 * np.cos(arg_bottom_sin_cos)

    mapping_val[0] = s_top + s_bottom
    mapping_val[1] = z_top + z_bottom
    return mapping_val


@njit(cache=instaseis._use_numba_cache)
def jacobian_semiso(xi: float, eta: float, nodes: np.ndarray) -> np.ndarray:
    """Computes the Jacobian matrix for semi-spheroidal mapping (semiso type) at (xi, eta).
    J = | ds/dxi  ds/deta |
        | dz/dxi  dz/deta |.

    :param xi: Reference xi-coordinate.
    :param eta: Reference eta-coordinate.
    :param nodes: A (4, 2) array with the s and z coordinates of the 4 element nodes.
    :return: np.ndarray of shape (2, 2) representing the Jacobian matrix.
    """
    theta_vals, r_vals = compute_theta_r(nodes)
    jacobian_val = np.empty((2, 2), dtype=np.float64)
    r1 = r_vals[0]
    arg_bottom = (
        (1.0 - xi) * theta_vals[0] + (1.0 + xi) * theta_vals[1]
    ) / 2.0

    jacobian_val[0, 0] = (1.0 + eta) / 4.0 * (nodes[2, 0] - nodes[3, 0]) + (
        1.0 - eta
    ) * r1 * (theta_vals[1] - theta_vals[0]) / 4.0 * np.cos(arg_bottom)
    jacobian_val[0, 1] = 1.0 / 4.0 * (
        (1.0 - xi) * nodes[3, 0] + (1.0 + xi) * nodes[2, 0]
    ) - r1 / 2.0 * np.sin(arg_bottom)
    jacobian_val[1, 0] = -(1.0 - eta) * r1 * (
        theta_vals[1] - theta_vals[0]
    ) / 4.0 * np.sin(arg_bottom) + (1.0 + eta) / 4.0 * (
        nodes[2, 1] - nodes[3, 1]
    )
    jacobian_val[1, 1] = -r1 / 2.0 * np.cos(arg_bottom) + 1.0 / 4.0 * (
        (1.0 - xi) * nodes[3, 1] + (1.0 + xi) * nodes[2, 1]
    )
    return jacobian_val


@njit(cache=instaseis._use_numba_cache)
def inv_jacobian_semiso(
    xi: float, eta: float, nodes: np.ndarray
) -> np.ndarray:
    """Computes the inverse of the Jacobian matrix for semi-spheroidal mapping (semiso type)
    at (xi, eta).
    J^-1 = | dxi/ds  dxi/dz |
           | deta/ds deta/dz |.

    :param xi: Reference xi-coordinate.
    :param eta: Reference eta-coordinate.
    :param nodes: A (4, 2) array with the s and z coordinates of the 4 element nodes.
    :return: np.ndarray of shape (2, 2) representing the inverse Jacobian matrix.
    """
    inv_jacobian_val = np.empty((2, 2), dtype=np.float64)
    jacobian_val = jacobian_semiso(xi, eta, nodes)
    det = (
        jacobian_val[0, 0] * jacobian_val[1, 1]
        - jacobian_val[0, 1] * jacobian_val[1, 0]
    )
    if det == 0:
        det = 1e-100
    inv_jacobian_val[0, 0] = jacobian_val[1, 1] / det
    inv_jacobian_val[0, 1] = -jacobian_val[0, 1] / det
    inv_jacobian_val[1, 0] = -jacobian_val[1, 0] / det
    inv_jacobian_val[1, 1] = jacobian_val[0, 0] / det
    return inv_jacobian_val


# Main inverse mapping functions
@njit(cache=instaseis._use_numba_cache)
def _inv_mapping_iterative(
    s: float, z: float, nodes: np.ndarray, mapping_func, inv_jacobian_func
) -> np.ndarray:
    """Iteratively computes the reference coordinates (xi, eta) for a physical
    point (s, z) using Newton's method. This is a generic function used by
    the type-specific inverse mapping functions.

    :param s: Global s-coordinate of the point.
    :param z: Global z-coordinate of the point.
    :param nodes: A (4, 2) array with the s and z coordinates of the 4 element nodes.
    :param mapping_func: The forward mapping function (e.g., mapping_spheroid).
    :param inv_jacobian_func: The inverse Jacobian function (e.g., inv_jacobian_spheroid).
    :return: np.ndarray of shape (2,) containing the reference coordinates [xi, eta].
    """
    xi_curr = 0.0
    eta_curr = 0.0
    numiter = 10

    for _i in range(numiter):
        sz_mapped = mapping_func(xi_curr, eta_curr, nodes)
        ds = s - sz_mapped[0]
        dz = z - sz_mapped[1]

        current_error_sq = ds**2 + dz**2
        # If target is origin and mapped point is origin, error is 0.
        if (
            current_error_sq < 1e-28
        ):  # Absolute tolerance for squared error (1e-14)^2
            break

        s_sq_plus_z_sq = s**2 + z**2
        # Relative error check, only if denominator is not too small
        if (
            s_sq_plus_z_sq > 1e-40
        ):  # Avoid division by very small number or zero
            if (current_error_sq / s_sq_plus_z_sq) < (1e-7) ** 2:
                break
        # If s_sq_plus_z_sq is very small, only absolute error check above applies.

        inv_jac = inv_jacobian_func(xi_curr, eta_curr, nodes)

        delta_xi = inv_jac[0, 0] * ds + inv_jac[0, 1] * dz
        delta_eta = inv_jac[1, 0] * ds + inv_jac[1, 1] * dz

        xi_curr = xi_curr + delta_xi
        eta_curr = eta_curr + delta_eta

    return np.array([xi_curr, eta_curr], dtype=np.float64)


@njit()
def inv_mapping_spheroid(s: float, z: float, nodes: np.ndarray) -> np.ndarray:
    """Computes the reference coordinates (xi, eta) for a physical point (s, z)
    for a spheroidal element.

    :param s: Global s-coordinate of the point.
    :param z: Global z-coordinate of the point.
    :param nodes: A (4, 2) array with the s and z coordinates of the 4 element nodes.
    :return: np.ndarray of shape (2,) containing the reference coordinates [xi, eta].
    """
    return _inv_mapping_iterative(
        s, z, nodes, mapping_spheroid, inv_jacobian_spheroid
    )


@njit()
def inv_mapping_subpar(s: float, z: float, nodes: np.ndarray) -> np.ndarray:
    """Computes the reference coordinates (xi, eta) for a physical point (s, z)
    for a subparametric element.

    :param s: Global s-coordinate of the point.
    :param z: Global z-coordinate of the point.
    :param nodes: A (4, 2) array with the s and z coordinates of the 4 element nodes.
    :return: np.ndarray of shape (2,) containing the reference coordinates [xi, eta].
    """
    return _inv_mapping_iterative(
        s, z, nodes, mapping_subpar, inv_jacobian_subpar
    )


@njit()
def inv_mapping_semino(s: float, z: float, nodes: np.ndarray) -> np.ndarray:
    """Computes the reference coordinates (xi, eta) for a physical point (s, z)
    for a semi-spheroidal element (semino type).

    :param s: Global s-coordinate of the point.
    :param z: Global z-coordinate of the point.
    :param nodes: A (4, 2) array with the s and z coordinates of the 4 element nodes.
    :return: np.ndarray of shape (2,) containing the reference coordinates [xi, eta].
    """
    return _inv_mapping_iterative(
        s, z, nodes, mapping_semino, inv_jacobian_semino
    )


@njit()
def inv_mapping_semiso(s: float, z: float, nodes: np.ndarray) -> np.ndarray:
    """Computes the reference coordinates (xi, eta) for a physical point (s, z)
    for a semi-spheroidal element (semiso type).

    :param s: Global s-coordinate of the point.
    :param z: Global z-coordinate of the point.
    :param nodes: A (4, 2) array with the s and z coordinates of the 4 element nodes.
    :return: np.ndarray of shape (2,) containing the reference coordinates [xi, eta].
    """
    return _inv_mapping_iterative(
        s, z, nodes, mapping_semiso, inv_jacobian_semiso
    )
