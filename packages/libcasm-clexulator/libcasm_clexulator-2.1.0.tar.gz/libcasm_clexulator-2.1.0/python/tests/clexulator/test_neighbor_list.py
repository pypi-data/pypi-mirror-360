import numpy as np

import libcasm.xtal as xtal
import libcasm.xtal.lattices as xtal_lattices
import libcasm.xtal.prims as xtal_prims
from libcasm.clexulator import (
    PrimNeighborList,
    SuperNeighborList,
    make_default_prim_neighbor_list,
)


def test_make_weight_matrix():
    lattice = xtal_lattices.FCC(r=1.0)
    W = PrimNeighborList.make_weight_matrix(lattice.column_vector_matrix())
    W_expected = np.array(
        [
            [2, 1, 1],
            [1, 2, 1],
            [1, 1, 2],
        ],
        dtype=int,
    )
    assert np.allclose(W, W_expected)


def test_prim_neighbor_list_1():
    prim_neighbor_list = PrimNeighborList()
    assert isinstance(prim_neighbor_list, PrimNeighborList)


def test_prim_neighbor_list_2():
    lattice = xtal_lattices.FCC(r=1.0)
    W = PrimNeighborList.make_weight_matrix(lattice.column_vector_matrix())
    prim_neighbor_list = PrimNeighborList(W, [0], 1)
    assert isinstance(prim_neighbor_list, PrimNeighborList)
    assert (prim_neighbor_list.weight_matrix() == W).all()


def test_prim_neighbor_list_3():
    xtal_prim = xtal_prims.HCP(a=1.0, occ_dof=["A", "B"])

    # Construct the default neighbor list
    prim_neighbor_list = make_default_prim_neighbor_list(xtal_prim)

    # Expand the neighbor list to include unit cell :math:`(0, 1, 1)`
    prim_neighbor_list.add_unitcell([0, 1, 1])

    # Expand the neighbor list to ensure it includes the site with
    # sublattice index `1` and unit cell :math:`(1, 0, 0)`.
    prim_neighbor_list.add_site(
        xtal.IntegralSiteCoordinate(sublattice=1, unitcell=[1, 0, 0])
    )

    print("len(prim_neighbor_list):", len(prim_neighbor_list))
    for i, unitcell in enumerate(prim_neighbor_list):
        print(f"unitcell {i}:", unitcell)

    assert len(prim_neighbor_list) == 27
    assert len([unitcell for unitcell in prim_neighbor_list]) == 27
    assert prim_neighbor_list.n_neighborhood_unitcells() == 27
    assert prim_neighbor_list.n_neighborhood_sites() == 54

    site = xtal.IntegralSiteCoordinate(sublattice=0, unitcell=[0, 0, 0])
    assert prim_neighbor_list.neighbor_index(site) == 0

    site = xtal.IntegralSiteCoordinate(sublattice=1, unitcell=[0, 0, 0])
    assert prim_neighbor_list.neighbor_index(site) == 1

    site = xtal.IntegralSiteCoordinate(sublattice=1, unitcell=[0, 1, 1])
    assert prim_neighbor_list.neighbor_index(site) == 45

    transformation_matrix_to_super = np.array([[-1, 1, 1], [1, -1, 1], [1, 1, -1]]) * 10
    super_neighbor_list = SuperNeighborList(
        transformation_matrix_to_super, prim_neighbor_list
    )
    assert super_neighbor_list.n_supercell_unitcells() == 4 * 10 * 10 * 10
    assert super_neighbor_list.n_supercell_sites() == 4 * 10 * 10 * 10 * 2

    # check agreement of SuperNeighborList.sites and SuperNeighborList.linear_site_index
    for linear_unitcell_index in range(super_neighbor_list.n_supercell_unitcells()):
        linear_site_indices = [
            x for x in super_neighbor_list.sites(linear_unitcell_index)
        ]
        assert len(linear_site_indices) == 54
        # print(f"{linear_unitcell_index}:", linear_site_indices)
        for i, j in enumerate(linear_site_indices):
            assert (
                super_neighbor_list.nbor_linear_site_index(linear_unitcell_index, i)
                == j
            )

    # check agreement of SuperNeighborList.unitcells
    # and SuperNeighborList.linear_unitcell_index
    for linear_unitcell_index in range(super_neighbor_list.n_supercell_unitcells()):
        linear_unitcell_indices = [
            x for x in super_neighbor_list.unitcells(linear_unitcell_index)
        ]
        assert len(linear_unitcell_indices) == 27
        # print(f"{linear_unitcell_index}:", linear_unitcell_indices)
        for i, j in enumerate(linear_unitcell_indices):
            assert (
                super_neighbor_list.nbor_linear_unitcell_index(linear_unitcell_index, i)
                == j
            )


def test_prim_neighbor_list_4():
    xtal_prim = xtal_prims.HCP(a=1.0, occ_dof=["A", "B"])

    # Construct the default neighbor list
    prim_neighbor_list = make_default_prim_neighbor_list(xtal_prim)

    # Expand the neighbor list to include unit cell
    prim_neighbor_list.add_unitcell([0, 0, 0])
    assert len(prim_neighbor_list) == 1


def test_prim_neighbor_list_5():
    xtal_prim = xtal_prims.HCP(a=1.0, occ_dof=["A", "B"])

    # Construct the default neighbor list

    # Expand the neighbor list to include unit cell
    prim_neighbor_list = make_default_prim_neighbor_list(xtal_prim)
    prim_neighbor_list.add_unitcell([1, 0, 0])
    assert len(prim_neighbor_list) == 7

    # Expand the neighbor list to include site
    prim_neighbor_list = make_default_prim_neighbor_list(xtal_prim)
    prim_neighbor_list.add_site(xtal.IntegralSiteCoordinate(1, [1, 0, 0]))
    assert len(prim_neighbor_list) == 7
