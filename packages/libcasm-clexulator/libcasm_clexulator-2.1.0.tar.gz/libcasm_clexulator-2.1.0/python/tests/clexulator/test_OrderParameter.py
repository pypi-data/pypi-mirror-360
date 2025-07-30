import numpy as np

import libcasm.xtal as xtal
import libcasm.xtal.prims as xtal_prims
from libcasm.clexulator import DoFSpace, OrderParameter, make_default_config_dof_values


def test_OrderParameter_constructor_1():
    xtal_prim = xtal_prims.FCC(r=1.0, occ_dof=["A", "B", "Va"])
    T = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=int)
    round(np.linalg.det(T))

    dof_space = DoFSpace(
        dof_key="occ", xtal_prim=xtal_prim, transformation_matrix_to_super=T
    )

    # construct a OrderParameter calculator
    order_parameter = OrderParameter(
        dof_space=dof_space,
    )

    assert isinstance(order_parameter, OrderParameter)


def test_OrderParameter_occ_1():
    # DoFSpace is a single unit cell -> eta is mean site composition
    xtal_prim = xtal_prims.FCC(r=1.0, occ_dof=["A", "B", "Va"])
    T_dof_space = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=int)

    # construct occ DoFSpace with default basis
    dof_space = DoFSpace(
        dof_key="occ", xtal_prim=xtal_prim, transformation_matrix_to_super=T_dof_space
    )

    # construct a OrderParameter calculator
    order_parameter = OrderParameter(
        dof_space=dof_space,
    )

    T_config = np.array([[2, 0, 0], [0, 2, 0], [0, 0, 2]], dtype=int)
    n_unitcells = round(np.linalg.det(T_config))

    # construct SiteIndexConverter
    site_index_converter = xtal.SiteIndexConverter(
        transformation_matrix_to_super=T_config,
        n_sublattice=len(xtal_prim.occ_dof()),
    )

    # construct ConfigDoFValues, in the prim DoF basis
    config_dof_values = make_default_config_dof_values(
        xtal_prim=xtal_prim,
        n_unitcells=n_unitcells,
    )

    # set the supercell and ConfigDoFValues used for order parameter calculation
    order_parameter.update(
        transformation_matrix_to_super=T_config,
        site_index_converter=site_index_converter,
        config_dof_values=config_dof_values,
    )

    eta = order_parameter.value()
    assert isinstance(eta, np.ndarray)
    assert eta.shape == (3,)
    assert np.allclose(eta, np.array([1.0, 0.0, 0.0]))

    config_dof_values.set_occupation([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0])
    eta = order_parameter.value()
    assert np.allclose(eta, np.array([0.0, 1.0, 0.0]))

    config_dof_values.set_occupation([2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0])
    eta = order_parameter.value()
    assert np.allclose(eta, np.array([0.0, 0.0, 1.0]))

    config_dof_values.set_occupation([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    eta = order_parameter.value()
    assert np.allclose(eta, np.array([7.0 / 8.0, 1.0 / 8.0, 0.0]))


def test_OrderParameter_occ_2():
    # DoFSpace is a 2 unit cell supercell -> eta is mean sublat composition
    xtal_prim = xtal_prims.FCC(r=1.0, occ_dof=["A", "B", "Va"])
    T_dof_space = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 2]], dtype=int)

    # construct occ DoFSpace with default basis
    dof_space = DoFSpace(
        dof_key="occ", xtal_prim=xtal_prim, transformation_matrix_to_super=T_dof_space
    )

    # construct a OrderParameter calculator
    order_parameter = OrderParameter(
        dof_space=dof_space,
    )

    T_config = np.array([[2, 0, 0], [0, 2, 0], [0, 0, 2]], dtype=int)
    n_unitcells = round(np.linalg.det(T_config))

    # construct SiteIndexConverter
    site_index_converter = xtal.SiteIndexConverter(
        transformation_matrix_to_super=T_config,
        n_sublattice=len(xtal_prim.occ_dof()),
    )

    # Check site order:
    # for i in range(8):
    #     print(site_index_converter.integral_site_coordinate(i).to_list())

    # construct ConfigDoFValues, in the prim DoF basis
    config_dof_values = make_default_config_dof_values(
        xtal_prim=xtal_prim,
        n_unitcells=n_unitcells,
    )

    # set the supercell and ConfigDoFValues used for order parameter calculation
    order_parameter.update(
        transformation_matrix_to_super=T_config,
        site_index_converter=site_index_converter,
        config_dof_values=config_dof_values,
    )

    eta = order_parameter.value()
    assert isinstance(eta, np.ndarray)
    assert eta.shape == (6,)
    assert np.allclose(eta, np.array([1.0, 0.0, 0.0, 1.0, 0.0, 0.0]))

    config_dof_values.set_occupation([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0])
    eta = order_parameter.value()
    assert np.allclose(eta, np.array([0.0, 1.0, 0.0, 0.0, 1.0, 0.0]))

    config_dof_values.set_occupation([1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 2.0])
    eta = order_parameter.value()
    assert np.allclose(eta, np.array([0.0, 1.0, 0.0, 0.0, 0.0, 1.0]))

    config_dof_values.set_occupation([1.0, 0.0, 0.0, 0.0, 1.0, 2.0, 2.0, 2.0])
    eta = order_parameter.value()
    assert np.allclose(
        eta, np.array([3.0 / 4.0, 1.0 / 4.0, 0.0, 0.0, 1.0 / 4.0, 3 / 4.0])
    )


def test_OrderParameter_occ_3():
    # DoFSpace is a 2 unit cell supercell, single basis vector
    xtal_prim = xtal_prims.FCC(r=1.0, occ_dof=["A", "B", "Va"])
    T_dof_space = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 2]], dtype=int)

    # construct occ DoFSpace with default basis
    dof_space = DoFSpace(
        dof_key="occ",
        xtal_prim=xtal_prim,
        transformation_matrix_to_super=T_dof_space,
        basis=np.array(
            [
                [1.0, 0.0, 0.0, 0.0, 1.0, 0.0],
                [0.0, 1.0, 0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0, 0.0, -1.0, 0.0],
                [0.0, 1.0, 0.0, -1.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
            ]
        ).transpose(),
    )

    # construct a OrderParameter calculator
    order_parameter = OrderParameter(
        dof_space=dof_space,
    )

    T_config = np.array([[2, 0, 0], [0, 2, 0], [0, 0, 2]], dtype=int)
    n_unitcells = round(np.linalg.det(T_config))

    # construct SiteIndexConverter
    site_index_converter = xtal.SiteIndexConverter(
        transformation_matrix_to_super=T_config,
        n_sublattice=len(xtal_prim.occ_dof()),
    )

    # Check site order:
    # for i in range(8):
    #     print(site_index_converter.integral_site_coordinate(i).to_list())

    # construct ConfigDoFValues, in the prim DoF basis
    config_dof_values = make_default_config_dof_values(
        xtal_prim=xtal_prim,
        n_unitcells=n_unitcells,
    )

    # set the supercell and ConfigDoFValues used for order parameter calculation
    order_parameter.update(
        transformation_matrix_to_super=T_config,
        site_index_converter=site_index_converter,
        config_dof_values=config_dof_values,
    )

    # Q * eta = \bar{x}
    config_dof_values.set_occupation([0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0])
    eta = order_parameter.value()
    assert isinstance(eta, np.ndarray)
    assert eta.shape == (6,)
    print(eta)
    assert np.allclose(eta, np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0]))

    config_dof_values.set_occupation([1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0])
    eta = order_parameter.value()
    assert isinstance(eta, np.ndarray)
    assert eta.shape == (6,)
    print(eta)
    assert np.allclose(eta, np.array([0.0, 1.0, 0.0, 0.0, 0.0, 0.0]))

    config_dof_values.set_occupation([2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0])
    eta = order_parameter.value()
    assert isinstance(eta, np.ndarray)
    assert eta.shape == (6,)
    print(eta)
    assert np.allclose(eta, np.array([0.0, 0.0, 1.0, 0.0, 0.0, 1.0]))
