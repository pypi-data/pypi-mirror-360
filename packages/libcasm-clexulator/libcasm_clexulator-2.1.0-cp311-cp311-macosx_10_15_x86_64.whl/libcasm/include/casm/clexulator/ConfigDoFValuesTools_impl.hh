#ifndef CASM_clexulator_ConfigDoFValuesTools_impl
#define CASM_clexulator_ConfigDoFValuesTools_impl

#include "casm/clexulator/ConfigDoFValuesTools.hh"
#include "casm/crystallography/BasicStructure.hh"
#include "casm/crystallography/DoFSet.hh"

namespace CASM {
namespace clexulator {

inline std::map<DoFKey, xtal::DoFSet> make_global_dof_info(
    xtal::BasicStructure const &basic_structure) {
  return basic_structure.global_dofs();
}

inline std::map<DoFKey, std::vector<xtal::SiteDoFSet>> make_local_dof_info(
    xtal::BasicStructure const &basic_structure) {
  std::map<DoFKey, std::vector<xtal::SiteDoFSet>> result;
  auto const &basis = basic_structure.basis();

  auto make_null_dofset = [](DoFKey const &type) {
    AnisoValTraits dof_traits(type);
    std::vector<std::string> component_names({});
    Eigen::MatrixXd basis = Eigen::MatrixXd::Zero(dof_traits.dim(), 0);
    std::unordered_set<std::string> excluded_occs({});
    return xtal::SiteDoFSet(dof_traits, component_names, basis, excluded_occs);
  };

  for (DoFKey const &type : xtal::continuous_local_dof_types(basic_structure)) {
    std::vector<xtal::SiteDoFSet> &type_info = result[type];

    for (Index b = 0; b < basis.size(); ++b) {
      if (basis[b].has_dof(type)) {
        type_info.push_back(basis[b].dof(type));
      } else {
        type_info.push_back(make_null_dofset(type));
      }
    }
  }
  return result;
}

}  // namespace clexulator
}  // namespace CASM

#endif
