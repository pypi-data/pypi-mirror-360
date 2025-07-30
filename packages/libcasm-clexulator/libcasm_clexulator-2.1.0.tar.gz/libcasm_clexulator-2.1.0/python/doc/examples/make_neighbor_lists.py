"""
Tests the code snippets in usage/neighbor_lists.rst
"""

import libcasm.xtal as xtal
import libcasm.xtal.prims as xtal_prims
from libcasm.clexulator import make_default_prim_neighbor_list

xtal_prim = xtal_prims.HCP(a=1.0, occ_dof=["A", "B"])
prim_neighbor_list = make_default_prim_neighbor_list(xtal_prim)

###
import numpy as np  # noqa

site = xtal.IntegralSiteCoordinate(
    sublattice=1,
    unitcell=np.array([0, 2, 0]),
)
neighbor_index = prim_neighbor_list.neighbor_index(site)

###
site = xtal.IntegralSiteCoordinate(
    sublattice=1,
    unitcell=np.array([0, 2, 0]),
)
reference_unitcell = np.array([0, 1, 0])
site -= reference_unitcell
neighbor_index = prim_neighbor_list.neighbor_index(site)

###
from libcasm.clexulator import SuperNeighborList  # noqa

# transformation_matrix_to_super: numpy.ndarray[numpy.int64[3, 3]
transformation_matrix_to_super = np.eye(3, dtype=int) * 10

super_neighbor_list = SuperNeighborList(
    transformation_matrix_to_super, prim_neighbor_list
)

###
# Get the linear site index of sites neighboring unitcell [0, 3, 1]:

super_neighbor_list = SuperNeighborList(
    transformation_matrix_to_super, prim_neighbor_list
)
unitcell_index_converter = xtal.UnitCellIndexConverter(transformation_matrix_to_super)
site_index_converter = xtal.SiteIndexConverter(
    transformation_matrix_to_super, prim_neighbor_list.total_n_sublattice()
)

unitcell = np.array([0, 3, 1])
linear_unitcell_index = unitcell_index_converter.linear_unitcell_index(unitcell)

print("Neighbor sites")
for i, linear_site_index in enumerate(super_neighbor_list.sites(linear_unitcell_index)):
    integral_site_coordinate = site_index_converter.integral_site_coordinate(
        linear_site_index
    )
    print(
        f"neighbor {i}: "
        f"linear_site_index: {linear_site_index} "
        f"integral_site_coordinate: {integral_site_coordinate}"
    )

###
print()

###

print("Neighbor unit cells")
for i, nbor_linear_unitcell_index in enumerate(
    super_neighbor_list.unitcells(linear_unitcell_index)
):
    nbor_unitcell = unitcell_index_converter.unitcell(nbor_linear_unitcell_index)
    print(
        f"neighbor {i}: "
        f"nbor_linear_unitcell_index: {nbor_linear_unitcell_index} "
        f"nbor_unitcell: {nbor_unitcell}"
    )

###
print()
