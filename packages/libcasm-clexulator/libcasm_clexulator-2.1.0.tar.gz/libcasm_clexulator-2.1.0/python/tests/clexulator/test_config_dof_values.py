import math

import numpy as np
import pytest

import libcasm.xtal as xtal
import libcasm.xtal.prims as xtal_prims
from libcasm.clexulator import (
    ConfigDoFValues,
    from_standard_values,
    make_default_config_dof_values,
    make_default_standard_config_dof_values,
    to_standard_values,
)


def test_constructor():
    dof_values = ConfigDoFValues()
    assert isinstance(dof_values, ConfigDoFValues)


def test_constructor_2():
    xtal_prim = xtal_prims.FCC(r=1.0, occ_dof=["A", "B", "Va"])
    n_unitcells = 2
    dof_values = make_default_config_dof_values(xtal_prim, n_unitcells)
    assert isinstance(dof_values, ConfigDoFValues)
    assert dof_values.occupation().shape == (2,)


def test_constructor_3():
    xtal_prim = xtal_prims.HCP(r=1.0, occ_dof=["A", "B", "Va"])
    n_unitcells = 2
    dof_values = make_default_config_dof_values(xtal_prim, n_unitcells)
    assert isinstance(dof_values, ConfigDoFValues)
    assert dof_values.occupation().shape == (4,)
    assert dof_values.occupation().shape == (4,)


def test_constructor_4():
    xtal_prim = xtal_prims.HCP(
        r=1.0,
        occ_dof=["A", "B", "Va"],
        local_dof=[xtal.DoFSetBasis("disp")],
        global_dof=[xtal.DoFSetBasis("Hstrain")],
    )
    n_unitcells = 2
    dof_values = make_default_config_dof_values(xtal_prim, n_unitcells)
    assert isinstance(dof_values, ConfigDoFValues)
    assert dof_values.occupation().shape == (4,)


def test_occupation():
    dof_values = ConfigDoFValues()

    occupation_in = np.array([1, 0, 0, 0], dtype=int)
    # this sets using a copy
    dof_values.set_occupation(occupation_in)

    occupation_out = dof_values.occupation()
    assert np.allclose(occupation_in, occupation_out)

    # so this has no effect
    occupation_in[0] = 2
    assert dof_values.occ(0) == 1

    # but this does
    dof_values.set_occ(0, 2)
    assert dof_values.occ(0) == 2


def test_occupation_2():
    dof_values = ConfigDoFValues()

    occupation_in = np.array([1, 0, 0, 0], dtype=int)
    dof_values.set_occupation(occupation_in)

    # this returns a const reference np.ndarray (writeable==False,owndata==False)
    # so occupation_out should be ready-only
    occupation_out = dof_values.occupation()
    assert np.allclose(occupation_in, occupation_out)
    with pytest.raises(ValueError):
        occupation_out[0] = 2
    assert dof_values.occ(0) == 1
    assert occupation_out.flags.writeable is False
    assert occupation_out.flags.owndata is False


def test_copy_config_dof_values():
    import copy

    dof_values_1 = ConfigDoFValues()

    occupation_in = np.array([1, 0, 0, 0], dtype=int)
    dof_values_1.set_occupation(occupation_in)

    dof_values_2 = copy.copy(dof_values_1)
    assert isinstance(dof_values_1, ConfigDoFValues)
    assert isinstance(dof_values_2, ConfigDoFValues)
    assert dof_values_1 is not dof_values_2


def test_basis_change_1():
    """Local DoF basis change test, starting with standard basis"""
    disp_dof = xtal.DoFSetBasis(
        dofname="disp",
        axis_names=["d1", "d2", "d3"],
        basis=np.array(
            [
                [
                    1.0 / math.sqrt(2.0),
                    1.0 / math.sqrt(2.0),
                    0.0,
                ],
                [
                    -1.0 / math.sqrt(2.0),
                    1.0 / math.sqrt(2.0),
                    0.0,
                ],
                [
                    0.0,
                    0.0,
                    1.0,
                ],
            ]
        ).transpose(),
    )
    xtal_prim = xtal_prims.FCC(
        r=1.0,
        occ_dof=["A", "B", "Va"],
        local_dof=[disp_dof],
    )
    n_unitcells = 4

    dof_values_a = make_default_standard_config_dof_values(
        xtal_prim=xtal_prim, n_unitcells=n_unitcells
    )
    assert dof_values_a.local_dof_values("disp").shape == (3, 4)

    dof_values_a.set_local_dof_site_value("disp", 0, np.array([1.0, 0.0, 1.0]))

    dof_values_b = from_standard_values(
        dof_values_a,
        xtal_prim=xtal_prim,
        n_unitcells=n_unitcells,
    )
    assert dof_values_b.local_dof_values("disp").shape == (3, 4)

    dof_values_c = to_standard_values(
        dof_values_b,
        xtal_prim=xtal_prim,
        n_unitcells=n_unitcells,
    )

    assert np.allclose(
        dof_values_b.local_dof_site_value("disp", 0),
        np.array(
            [
                1.0 / math.sqrt(2.0),
                -1.0 / math.sqrt(2.0),
                1.0,
            ]
        ),
    )

    assert np.allclose(
        dof_values_c.local_dof_site_value("disp", 0),
        np.array(
            [
                1.0,
                0.0,
                1.0,
            ]
        ),
    )


def test_basis_change_2(FCC_binary_2d_corner_disp_prim):
    """Local DoF basis change test, starting with standard basis,
    with a site with non-standard disp DoF
    """
    xtal_prim = FCC_binary_2d_corner_disp_prim
    n_unitcells = 1

    dof_values_a = make_default_standard_config_dof_values(
        xtal_prim=xtal_prim, n_unitcells=n_unitcells
    )
    assert dof_values_a.local_dof_values("disp").shape == (3, 4)

    dof_values_a.set_local_dof_site_value("disp", 0, np.array([1.0, 0.0, 0.0]))

    dof_values_b = from_standard_values(
        dof_values_a,
        xtal_prim=xtal_prim,
        n_unitcells=n_unitcells,
    )
    assert dof_values_b.local_dof_values("disp").shape == (3, 4)

    dof_values_c = to_standard_values(
        dof_values_b,
        xtal_prim=xtal_prim,
        n_unitcells=n_unitcells,
    )

    assert np.allclose(
        dof_values_b.local_dof_site_value("disp", 0),
        np.array(
            [
                1.0 / math.sqrt(2.0),
                -1.0 / math.sqrt(2.0),
                0.0,
            ]
        ),
    )

    assert np.allclose(
        dof_values_c.local_dof_site_value("disp", 0),
        np.array(
            [
                1.0,
                0.0,
                0.0,
            ]
        ),
    )


def test_basis_change_3(FCC_binary_2d_corner_disp_prim):
    """Local DoF basis change test, starting with prim basis,
    with a site with non-standard disp DoF
    """
    xtal_prim = FCC_binary_2d_corner_disp_prim
    n_unitcells = 1

    dof_values_a = make_default_config_dof_values(
        xtal_prim=xtal_prim, n_unitcells=n_unitcells
    )
    assert dof_values_a.local_dof_values("disp").shape == (3, 4)

    dof_values_a.set_local_dof_site_value(
        "disp",
        0,
        np.array(
            [
                1.0 / math.sqrt(2.0),
                -1.0 / math.sqrt(2.0),
                0.0,
            ]
        ),
    )

    dof_values_b = to_standard_values(
        dof_values_a,
        xtal_prim=xtal_prim,
        n_unitcells=n_unitcells,
    )
    assert dof_values_b.local_dof_values("disp").shape == (3, 4)

    dof_values_c = from_standard_values(
        dof_values_b,
        xtal_prim=xtal_prim,
        n_unitcells=n_unitcells,
    )

    assert np.allclose(
        dof_values_b.local_dof_site_value("disp", 0),
        np.array(
            [
                1.0,
                0.0,
                0.0,
            ]
        ),
    )

    assert np.allclose(
        dof_values_c.local_dof_site_value("disp", 0),
        np.array(
            [
                1.0 / math.sqrt(2.0),
                -1.0 / math.sqrt(2.0),
                0.0,
            ]
        ),
    )


def test_basis_change_4(FCC_binary_disp_fix_corner_prim):
    """Non-standard local DoF basis test, starting with standard basis,
    with a site with excluding disp DoF
    """
    xtal_prim = FCC_binary_disp_fix_corner_prim
    n_unitcells = 4

    dof_values_a = make_default_standard_config_dof_values(
        xtal_prim=xtal_prim, n_unitcells=n_unitcells
    )
    assert dof_values_a.local_dof_values("disp").shape == (3, 16)

    dof_values_a.set_local_dof_site_value(
        "disp",
        n_unitcells,
        np.array(
            [
                1.0 / math.sqrt(2.0),
                -1.0 / math.sqrt(2.0),
                0.0,
            ]
        ),
    )

    dof_values_b = to_standard_values(
        dof_values_a,
        xtal_prim=xtal_prim,
        n_unitcells=n_unitcells,
    )
    assert dof_values_b.local_dof_values("disp").shape == (3, 16)

    dof_values_c = from_standard_values(
        dof_values_b,
        xtal_prim=xtal_prim,
        n_unitcells=n_unitcells,
    )

    assert np.allclose(
        dof_values_b.local_dof_site_value("disp", n_unitcells),
        np.array(
            [
                1.0 / math.sqrt(2.0),
                -1.0 / math.sqrt(2.0),
                0.0,
            ]
        ),
    )

    assert np.allclose(
        dof_values_c.local_dof_site_value("disp", n_unitcells),
        np.array(
            [
                1.0 / math.sqrt(2.0),
                -1.0 / math.sqrt(2.0),
                0.0,
            ]
        ),
    )


def test_basis_change_2d_disp_1(FCC_binary_2d_disp_prim):
    """Non-standard local DoF basis test, starting with standard basis"""
    xtal_prim = FCC_binary_2d_disp_prim
    n_unitcells = 4

    dof_values_a = make_default_standard_config_dof_values(
        xtal_prim=xtal_prim, n_unitcells=n_unitcells
    )
    assert dof_values_a.local_dof_values("disp").shape == (3, 4)

    dof_values_a.set_local_dof_site_value("disp", 0, np.array([1.0, 0.0, 0.0]))

    dof_values_b = from_standard_values(
        dof_values_a,
        xtal_prim=xtal_prim,
        n_unitcells=n_unitcells,
    )
    assert dof_values_b.local_dof_values("disp").shape == (2, 4)

    dof_values_c = to_standard_values(
        dof_values_b,
        xtal_prim=xtal_prim,
        n_unitcells=n_unitcells,
    )

    assert np.allclose(
        dof_values_b.local_dof_site_value("disp", 0),
        np.array(
            [
                1.0 / math.sqrt(2.0),
                -1.0 / math.sqrt(2.0),
            ]
        ),
    )

    assert np.allclose(
        dof_values_c.local_dof_site_value("disp", 0),
        np.array(
            [
                1.0,
                0.0,
                0.0,
            ]
        ),
    )


def test_basis_change_Hstrain_1(FCC_binary_symadapted_Hstrain_prim):
    """Global DoF basis change test, starting with prim basis"""
    xtal_prim = FCC_binary_symadapted_Hstrain_prim
    n_unitcells = 1

    dof_values_a = make_default_standard_config_dof_values(
        xtal_prim=xtal_prim, n_unitcells=n_unitcells
    )
    assert dof_values_a.global_dof_values("Hstrain").shape == (6,)

    Exx = 1e-3
    e1 = Exx / math.sqrt(3.0)
    e2 = Exx / math.sqrt(2.0)
    e3 = -Exx / math.sqrt(6.0)

    dof_values_a.set_global_dof_values(
        "Hstrain",
        np.array(
            [
                Exx,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
            ]
        ),
    )

    dof_values_b = from_standard_values(
        dof_values_a,
        xtal_prim=xtal_prim,
        n_unitcells=n_unitcells,
    )
    assert dof_values_b.global_dof_values("Hstrain").shape == (6,)

    dof_values_c = to_standard_values(
        dof_values_b,
        xtal_prim=xtal_prim,
        n_unitcells=n_unitcells,
    )

    assert np.allclose(
        dof_values_b.global_dof_values("Hstrain"),
        np.array(
            [
                e1,
                e2,
                e3,
                0.0,
                0.0,
                0.0,
            ]
        ),
    )

    assert np.allclose(
        dof_values_c.global_dof_values("Hstrain"),
        np.array(
            [
                Exx,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
            ]
        ),
    )


def test_basis_change_Hstrain_2(FCC_binary_restricted_symadapted_Hstrain_prim):
    """Global DoF basis change test, starting with prim basis"""
    xtal_prim = FCC_binary_restricted_symadapted_Hstrain_prim
    n_unitcells = 1

    dof_values_a = make_default_standard_config_dof_values(
        xtal_prim=xtal_prim, n_unitcells=n_unitcells
    )
    assert dof_values_a.global_dof_values("Hstrain").shape == (6,)

    Exx = 1e-3
    e1 = Exx / math.sqrt(3.0)
    e2 = Exx / math.sqrt(2.0)
    e3 = -Exx / math.sqrt(6.0)

    dof_values_a.set_global_dof_values(
        "Hstrain",
        np.array(
            [
                Exx,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
            ]
        ),
    )

    dof_values_b = from_standard_values(
        dof_values_a,
        xtal_prim=xtal_prim,
        n_unitcells=n_unitcells,
    )
    assert dof_values_b.global_dof_values("Hstrain").shape == (3,)

    dof_values_c = to_standard_values(
        dof_values_b,
        xtal_prim=xtal_prim,
        n_unitcells=n_unitcells,
    )

    assert np.allclose(
        dof_values_b.global_dof_values("Hstrain"),
        np.array(
            [
                e1,
                e2,
                e3,
            ]
        ),
    )

    assert np.allclose(
        dof_values_c.global_dof_values("Hstrain"),
        np.array(
            [
                Exx,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
            ]
        ),
    )
