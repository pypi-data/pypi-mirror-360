#ifndef CASM_unittest_testfunctions
#define CASM_unittest_testfunctions

#include <filesystem>

#include "casm/clexulator/ConfigDoFValuesTools_impl.hh"

using namespace CASM;

namespace test {

inline clexulator::ConfigDoFValues make_dof_values(
    xtal::BasicStructure const &prim, Index N_volume) {
  Index N_sublat = prim.basis().size();
  std::map<DoFKey, xtal::DoFSet> global_dof_info =
      clexulator::make_global_dof_info(prim);
  std::map<DoFKey, std::vector<xtal::SiteDoFSet>> local_dof_info =
      clexulator::make_local_dof_info(prim);

  return clexulator::make_default_standard_config_dof_values(
      N_sublat, N_volume, global_dof_info, local_dof_info);
}

}  // namespace test

#endif
