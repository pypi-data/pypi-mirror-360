import json

import numpy as np
import pytest

import libcasm.clexulator as clex
import libcasm.xtal as xtal

from .functions import make_source


@pytest.mark.slow
@pytest.mark.very_slow
def test_calc_per_unitcell_correlations(session_shared_datadir):
    source = make_source(
        session_shared_datadir,
        "OccClexulatorZrOTest",
        "OccClexulatorZrOTest",
        "default",
    )

    with open(session_shared_datadir / "ZrO_prim.json", "r") as f:
        xtal_prim = xtal.Prim.from_dict(json.load(f))
    prim_neighbor_list = clex.PrimNeighborList()
    clexulator = clex.make_clexulator(source, prim_neighbor_list)

    T = np.array([[2, 0, 0], [0, 2, 0], [0, 0, 1]], dtype=int)
    supercell_neighbor_list = clex.SuperNeighborList(T, prim_neighbor_list)
    n_unitcells = round(np.linalg.det(T))

    dof_values = clex.make_default_config_dof_values(xtal_prim, n_unitcells)
    assert len(dof_values.occupation()) == 4 * n_unitcells
    correlations = clex.calc_per_unitcell_correlations(
        clexulator, dof_values, supercell_neighbor_list
    )
    assert isinstance(correlations, np.ndarray)
    assert len(correlations) == 74

    corr = clex.Correlations(
        supercell_neighbor_list=supercell_neighbor_list,
        clexulator=clexulator,
        config_dof_values=dof_values,
    )
    neighbors = corr.required_update_neighborhood()
    assert len(neighbors) == 176

    corr = clex.Correlations(
        supercell_neighbor_list=supercell_neighbor_list,
        clexulator=clexulator,
        config_dof_values=dof_values,
        indices=[0],  # constant function only -> no neighborhood required
    )
    neighbors = corr.required_update_neighborhood()
    assert len(neighbors) == 0

    corr = clex.Correlations(
        supercell_neighbor_list=supercell_neighbor_list,
        clexulator=clexulator,
        config_dof_values=dof_values,
        indices=[0, 1],  # constant + point functions only
    )
    neighbors = corr.required_update_neighborhood()
    assert len(neighbors) == 2  # 2 Va-O sites


@pytest.mark.slow
@pytest.mark.very_slow
def test_calc_local_correlations(session_shared_datadir):
    source = make_source(
        session_shared_datadir, "LocalOccClexulatorZrOTest", "ZrO", "hop0"
    )

    with open(session_shared_datadir / "ZrO_prim.json", "r") as f:
        xtal_prim = xtal.Prim.from_dict(json.load(f))
    prim_neighbor_list = clex.PrimNeighborList()
    local_clexulator = clex.make_local_clexulator(source, prim_neighbor_list)
    assert local_clexulator.n_equivalents() == 2

    T = np.array([[2, 0, 0], [0, 2, 0], [0, 0, 1]], dtype=int)
    supercell_neighbor_list = clex.SuperNeighborList(T, prim_neighbor_list)
    n_unitcells = round(np.linalg.det(T))

    dof_values = clex.make_default_config_dof_values(xtal_prim, n_unitcells)
    assert len(dof_values.occupation()) == 4 * n_unitcells
    dof_values.set_occ(n_unitcells * 2, 1)

    for unitcell_index in range(n_unitcells):
        # Test calculate all correlations
        for equivalent_index in range(local_clexulator.n_equivalents()):
            correlations = clex.calc_local_correlations(
                local_clexulator=local_clexulator,
                config_dof_values=dof_values,
                supercell_neighbor_list=supercell_neighbor_list,
                unitcell_index=unitcell_index,
                equivalent_index=equivalent_index,
            )
            assert isinstance(correlations, np.ndarray)
            assert len(correlations) == 6
            # print(unitcell_index, equivalent_index, correlations.tolist())

            restricted = clex.calc_local_correlations(
                local_clexulator=local_clexulator,
                config_dof_values=dof_values,
                supercell_neighbor_list=supercell_neighbor_list,
                unitcell_index=unitcell_index,
                equivalent_index=equivalent_index,
                indices=[1, 2],
            )
            assert isinstance(restricted, np.ndarray)
            assert len(restricted) == 6
            assert np.allclose(restricted[0], [0.0])
            assert np.allclose(correlations[1:3], restricted[1:3])
            assert np.allclose(restricted[3:], [0.0, 0.0, 0.0])
            #  print("(*)", unitcell_index, equivalent_index, restricted.tolist())

    corr = clex.LocalCorrelations(
        supercell_neighbor_list=supercell_neighbor_list,
        clexulator=local_clexulator,
        config_dof_values=dof_values,
    )
    neighbors_0 = corr.required_update_neighborhood(equivalent_index=0)
    assert len(neighbors_0) == 14
    neighbors_1 = corr.required_update_neighborhood(equivalent_index=1)
    assert len(neighbors_1) == 14

    corr = clex.LocalCorrelations(
        supercell_neighbor_list=supercell_neighbor_list,
        clexulator=local_clexulator,
        config_dof_values=dof_values,
        indices=[0],  # constant function only -> no neighborhood required
    )
    neighbors_0 = corr.required_update_neighborhood(equivalent_index=0)
    assert len(neighbors_0) == 0
    neighbors_1 = corr.required_update_neighborhood(equivalent_index=1)
    assert len(neighbors_1) == 0

    corr = clex.LocalCorrelations(
        supercell_neighbor_list=supercell_neighbor_list,
        clexulator=local_clexulator,
        config_dof_values=dof_values,
        indices=[0, 1],  # constant + first point functions only
    )
    neighbors_0 = corr.required_update_neighborhood(equivalent_index=0)
    assert [x.to_list() for x in neighbors_0] == [[2, 0, 0, 0], [3, 0, 0, 1]]
    neighbors_1 = corr.required_update_neighborhood(equivalent_index=1)
    assert [x.to_list() for x in neighbors_1] == [[3, 0, 0, -1], [2, 0, 0, 1]]
