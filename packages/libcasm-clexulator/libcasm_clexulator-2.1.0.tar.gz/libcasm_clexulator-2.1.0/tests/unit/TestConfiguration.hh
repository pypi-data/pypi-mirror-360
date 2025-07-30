#ifndef CASM_unittest_TestConfiguration
#define CASM_unittest_TestConfiguration

#include "casm/clexulator/ConfigDoFValues.hh"
#include "casm/clexulator/ConfigDoFValuesTools_impl.hh"
#include "casm/clexulator/NeighborList.hh"
#include "casm/crystallography/BasicStructure.hh"
#include "casm/crystallography/LinearIndexConverter.hh"

using namespace CASM;

namespace test {

// A configuration-like data structure for testing. The "real" Configuration,
// with implementation of comparison and symmetry application,
// will be implemented separately in the CASM `configuration` library
struct TestConfiguration {
  // A default-value initialized configuration (all zero ConfigDoFValues)
  TestConfiguration(std::shared_ptr<xtal::BasicStructure const> _prim,
                    Eigen::Matrix3l const &_transformation_matrix_to_super,
                    clexulator::PrimNeighborList const &prim_neighbor_list)
      : prim(_prim),
        transformation_matrix_to_super(_transformation_matrix_to_super),
        n_sublat(prim->basis().size()),
        volume(transformation_matrix_to_super.determinant()),
        global_dof_info(clexulator::make_global_dof_info(*prim)),
        local_dof_info(clexulator::make_local_dof_info(*prim)),
        dof_values(clexulator::make_default_config_dof_values(
            n_sublat, volume, global_dof_info, local_dof_info)),
        supercell_neighbor_list(
            std::make_shared<clexulator::SuperNeighborList const>(
                transformation_matrix_to_super, prim_neighbor_list)),
        unitcellcoord_index_converter(transformation_matrix_to_super,
                                      prim->basis().size()) {}

  std::shared_ptr<xtal::BasicStructure const> prim;
  Eigen::Matrix3l transformation_matrix_to_super;
  int n_sublat;
  int volume;
  std::map<DoFKey, xtal::DoFSet> global_dof_info;
  std::map<DoFKey, std::vector<xtal::SiteDoFSet>> local_dof_info;
  clexulator::ConfigDoFValues dof_values;
  std::shared_ptr<clexulator::SuperNeighborList const> supercell_neighbor_list;
  xtal::UnitCellCoordIndexConverter unitcellcoord_index_converter;

  std::vector<Index> linear_site_index(
      std::vector<xtal::UnitCellCoord> const &unitcellcoord);
};

inline std::vector<Index> TestConfiguration::linear_site_index(
    std::vector<xtal::UnitCellCoord> const &unitcellcoord) {
  std::vector<Index> _linear_site_index;
  for (xtal::UnitCellCoord const &value : unitcellcoord) {
    _linear_site_index.push_back(unitcellcoord_index_converter(value));
  }
  return _linear_site_index;
}

}  // namespace test

#endif
