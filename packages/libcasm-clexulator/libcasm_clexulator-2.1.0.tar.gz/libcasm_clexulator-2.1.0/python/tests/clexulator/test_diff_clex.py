import numpy as np
import pytest

import libcasm.clexulator
import libcasm.xtal

from .functions import make_source


@pytest.fixture
def diff_clexulator(session_shared_datadir):
    source = make_source(
        session_shared_datadir,
        "DiffClexulatorSquareLatticeTest",
        "DiffClexulatorSquareLatticeTest",
        "default",
    )

    prim_neighbor_list = libcasm.clexulator.PrimNeighborList()
    clexulator = libcasm.clexulator.make_clexulator(source, prim_neighbor_list)
    return clexulator, prim_neighbor_list


def test_make_diff_clexulator(diff_clexulator):
    """Tests if diff clexulator made had the
    correct number of basis functions

    There should be 7 basis functions

    Generated using casm1.X

    .. math::
        \\Phi_{0} = 1
        \\Phi_{1} = \\sqrt{1/2}(dx_{0}^{2} +dy_{0}^{2} )
        \\Phi_{2} = dz_{0}^{2}
        \\Phi_{3} = \\sqrt{1/2}(dx_{0}^{4} +dy_{0}^{4} )
        \\Phi_{4} = \\sqrt{6}dx_{0}^{2} dy_{0}^{2}
        \\Phi_{5} = \\sqrt{3}(dx_{0}^{2} dz_{0}^{2} +dy_{0}^{2} dz_{0}^{2} )
        \\Phi_{6} = dz_{0}^{4}

    Parameters
    ----------
    diff_clexulator : libcasm.clexulator.Clexulator

    """
    clexulator, _ = diff_clexulator
    assert isinstance(clexulator, libcasm.clexulator.Clexulator)
    assert clexulator.n_functions() == 7


def test_gradients_of_correlations(diff_clexulator):
    """Tests if the gradients of correlations being made
    matches the analytical gradients

    Generated using casm1.X

    .. math::
        \\Phi_{0} = 1
        \\Phi_{1} = \\sqrt{1/2}(dx_{0}^{2} +dy_{0}^{2} )
        \\Phi_{2} = dz_{0}^{2}
        \\Phi_{3} = \\sqrt{1/2}(dx_{0}^{4} +dy_{0}^{4} )
        \\Phi_{4} = \\sqrt{6}dx_{0}^{2} dy_{0}^{2}
        \\Phi_{5} = \\sqrt{3}(dx_{0}^{2} dz_{0}^{2} +dy_{0}^{2} dz_{0}^{2} )
        \\Phi_{6} = dz_{0}^{4}

    Parameters
    ----------
    diff_clexulator : libcasm.clexulator.Clexulator

    """

    clexulator, prim_neighbor_list = diff_clexulator

    # make a configuration of supercell size 1
    T = np.eye(3)

    # assign disp site dofs to the configuration
    # There is only one site in volume 1 supercell
    # dof_values correspond to dx, dy, dz of that site
    dof_values = np.array([1.0, -0.5, 0.5])
    config_dof_values = libcasm.clexulator.ConfigDoFValues()
    config_dof_values.set_occupation([0])
    config_dof_values.insert_or_assign_local_dof_values("disp", dof_values)

    # make SuperNeighborList
    supercell_neighbor_list = libcasm.clexulator.SuperNeighborList(
        T, prim_neighbor_list
    )

    # make correlations
    correlations = libcasm.clexulator.Correlations(
        supercell_neighbor_list, clexulator, config_dof_values
    )

    # query gradients of correlations for this config
    gradients_of_correlations = correlations.grad_correlations("disp")

    # the shape of the gradients of correlations matrix should be 3x7
    # because there are 3 degrees of freedom (dx, dy, dz) and 7 correlations
    # you will have derivatives with each of the correlations with
    # each of the degrees of freedom

    assert gradients_of_correlations.shape == (3, 7)

    # comparing the values with analytical derivates
    dx = dof_values[0]
    dy = dof_values[1]
    dz = dof_values[2]

    # first row of gradients_of_correlations will be derviatives
    # of all the 7 correlations with dx
    derviatives_with_dx = gradients_of_correlations[0, :]

    # derivative of \\Phi_{0} with dx will be 0.0
    assert np.allclose(derviatives_with_dx[0], 0.0)
    # derivative of \\Phi_{1} with dx will be \\sqrt{2} * dx
    assert np.allclose(derviatives_with_dx[1], np.sqrt(2) * dx)
    # derivative of \\Phi_{2} with dx will be 0.0
    assert np.allclose(derviatives_with_dx[2], 0.0)
    # derivative of \\Phi_{3} with dx will be 2 * \\sqrt(2) * dx**3
    assert np.allclose(derviatives_with_dx[3], 2 * np.sqrt(2) * np.power(dx, 3))
    # derivative of \\Phi_{4} with dx will be 2 * \\sqrt(6) * dx * dy**2
    assert np.allclose(derviatives_with_dx[4], 2 * np.sqrt(6) * dx * np.power(dy, 2))
    # derivative of \\Phi_{5} with dx will be 2 * \\sqrt(3) * dx * dz**2
    assert np.allclose(derviatives_with_dx[5], 2 * np.sqrt(3) * dx * np.power(dz, 2))
    # derivative of \\Phi_{6} with dx will be 0.0
    assert np.allclose(derviatives_with_dx[6], 0.0)

    # second row of gradients_of_correlations will be derviatives
    # of all the 7 correlations with dy
    derviatives_with_dy = gradients_of_correlations[1, :]

    # derivative of \\Phi_{0} with dy will be 0.0
    assert np.allclose(derviatives_with_dy[0], 0.0)
    # derivative of \\Phi_{1} with dy will be \\sqrt{2} * dy
    assert np.allclose(derviatives_with_dy[1], np.sqrt(2) * dy)
    # derivative of \\Phi_{2} with dy will be 0.0
    assert np.allclose(derviatives_with_dy[2], 0.0)
    # derivative of \\Phi_{3} with dy will be 2 * \\sqrt(2) * dy**3
    assert np.allclose(derviatives_with_dy[3], 2 * np.sqrt(2) * np.power(dy, 3))
    # derivative of \\Phi_{4} with dy will be 2 * \\sqrt(6) * dx**2 * dy
    assert np.allclose(derviatives_with_dy[4], 2 * np.sqrt(6) * np.power(dx, 2) * dy)
    # derivative of \\Phi_{5} with dy will be 2 * \\sqrt(3) * dy * dz**2
    assert np.allclose(derviatives_with_dy[5], 2 * np.sqrt(3) * dy * np.power(dz, 2))
    # derivative of \\Phi_{6} with dy will be 0.0
    assert np.allclose(derviatives_with_dy[6], 0.0)

    # third row of gradients_of_correlations will be derviatives
    # of all the 7 correlations with dz
    derviatives_with_dz = gradients_of_correlations[2, :]

    # derivative of \\Phi_{0} with dz will be 0.0
    assert np.allclose(derviatives_with_dz[0], 0.0)
    # derivative of \\Phi_{1} with dz will be 0.0
    assert np.allclose(derviatives_with_dz[1], 0.0)
    # derivative of \\Phi_{2} with dz will be 2 * dz
    assert np.allclose(derviatives_with_dz[2], 2 * dz)
    # derivative of \\Phi_{3} with dz will be 0.0
    assert np.allclose(derviatives_with_dz[3], 0.0)
    # derivative of \\Phi_{4} with dz will be 0.0
    assert np.allclose(derviatives_with_dz[4], 0.0)
    # derivative of \\Phi_{5} with dz will be 2 * \\sqrt(3) * dz (dx**2 + dy**2)
    assert np.allclose(
        derviatives_with_dz[5],
        2 * np.sqrt(3) * dz * (np.power(dx, 2) + np.power(dy, 2)),
    )
    # derivative of \\Phi_{6} with dz will be 4 * dz**3
    assert np.allclose(derviatives_with_dz[6], 4 * np.power(dz, 3))
