import math
import os
import pathlib
import shutil
import sys

import numpy as np
import pytest

import libcasm.xtal as xtal
import libcasm.xtal.prims as xtal_prims


def _win32_longpath(path):
    """
    Helper function to add the long path prefix for Windows, so that shutil.copytree
     won't fail while working with paths with 255+ chars.
    """
    if sys.platform == "win32":
        # The use of os.path.normpath here is necessary since "the "\\?\" prefix
        # to a path string tells the Windows APIs to disable all string parsing
        # and to send the string that follows it straight to the file system".
        # (See https://docs.microsoft.com/pt-br/windows/desktop/FileIO/naming-a-file)
        return "\\\\?\\" + os.path.normpath(path)
    else:
        return path


@pytest.fixture(scope="session")
def session_shared_datadir(tmpdir_factory):
    original_shared_path = pathlib.Path(os.path.realpath(__file__)).parent / "data"
    session_temp_path = tmpdir_factory.mktemp("session_data")
    shutil.copytree(
        _win32_longpath(original_shared_path),
        _win32_longpath(str(session_temp_path)),
        dirs_exist_ok=True,
    )
    return session_temp_path


@pytest.fixture
def FCC_binary_disp_fix_corner_prim():
    # Lattice vectors
    lattice_column_vector_matrix = np.array(
        [
            [1.0, 0.0, 0.0],  # a
            [0.0, 1.0, 0.0],  # a
            [0.0, 0.0, 1.0],  # a
        ]
    ).transpose()
    lattice = xtal.Lattice(lattice_column_vector_matrix)

    # Basis sites positions, as columns of a matrix,
    # in fractional coordinates with respect to the lattice vectors
    coordinate_frac = np.array(
        [
            [0.0, 0.0, 0.0],
            [0.5, 0.5, 0.0],
            [0.0, 0.5, 0.5],
            [0.5, 0.0, 0.5],
        ]
    ).transpose()

    # Occupation degrees of freedom (DoF)
    occupants = {}
    occ_dof = [
        ["A", "B"],
        ["A", "B"],
        ["A", "B"],
        ["A", "B"],
    ]

    # Local continuous degrees of freedom (DoF)
    disp_dof = xtal.DoFSetBasis("disp")  # Atomic displacement
    local_dof = [
        [],
        [disp_dof],
        [disp_dof],
        [disp_dof],
    ]

    return xtal.Prim(
        lattice=lattice,
        coordinate_frac=coordinate_frac,
        occ_dof=occ_dof,
        local_dof=local_dof,
        occupants=occupants,
    )


@pytest.fixture
def FCC_binary_2d_corner_disp_prim():
    lattice_column_vector_matrix = np.array(
        [
            [1.0, 0.0, 0.0],  # a
            [0.0, 1.0, 0.0],  # a
            [0.0, 0.0, 1.0],  # a
        ]
    ).transpose()
    lattice = xtal.Lattice(lattice_column_vector_matrix)

    # Basis sites positions, as columns of a matrix,
    # in fractional coordinates with respect to the lattice vectors
    coordinate_frac = np.array(
        [
            [0.0, 0.0, 0.0],
            [0.5, 0.5, 0.0],
            [0.0, 0.5, 0.5],
            [0.5, 0.0, 0.5],
        ]
    ).transpose()

    # Occupation degrees of freedom (DoF)
    occupants = {}
    occ_dof = [
        ["A", "B"],
        ["A", "B"],
        ["A", "B"],
        ["A", "B"],
    ]

    # Local continuous degrees of freedom (DoF)
    disp_dof_a = xtal.DoFSetBasis(
        dofname="disp",
        axis_names=["d1", "d2"],
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
            ]
        ).transpose(),
    )
    disp_dof_b = xtal.DoFSetBasis(
        dofname="disp",
    )
    local_dof = [
        [disp_dof_a],
        [disp_dof_b],
        [disp_dof_b],
        [disp_dof_b],
    ]

    return xtal.Prim(
        lattice=lattice,
        coordinate_frac=coordinate_frac,
        occ_dof=occ_dof,
        local_dof=local_dof,
        occupants=occupants,
    )


@pytest.fixture
def FCC_binary_2d_disp_prim():
    # Local continuous degrees of freedom (DoF)
    disp_dof_a = xtal.DoFSetBasis(
        dofname="disp",
        axis_names=["d1", "d2"],
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
            ]
        ).transpose(),
    )
    return xtal_prims.FCC(
        r=1.0,
        occ_dof=["A", "B"],
        local_dof=[disp_dof_a],
    )


@pytest.fixture
def FCC_binary_symadapted_Hstrain_prim():
    # Hstrain continuous degrees of freedom (DoF)
    Hstrain_dof = xtal.DoFSetBasis(
        dofname="Hstrain",
        axis_names=["e_{1}", "e_{2}", "e_{3}", "e_{4}", "e_{5}", "e_{6}"],
        basis=xtal.make_symmetry_adapted_strain_basis(),
    )
    return xtal_prims.FCC(
        r=1.0,
        occ_dof=["A", "B"],
        global_dof=[Hstrain_dof],
    )


@pytest.fixture
def FCC_binary_restricted_symadapted_Hstrain_prim():
    # Hstrain continuous degrees of freedom (DoF)
    Hstrain_dof = xtal.DoFSetBasis(
        dofname="Hstrain",
        axis_names=["e_{1}", "e_{2}", "e_{3}"],
        basis=xtal.make_symmetry_adapted_strain_basis()[:, :3],
    )
    return xtal_prims.FCC(
        r=1.0,
        occ_dof=["A", "B"],
        global_dof=[Hstrain_dof],
    )
