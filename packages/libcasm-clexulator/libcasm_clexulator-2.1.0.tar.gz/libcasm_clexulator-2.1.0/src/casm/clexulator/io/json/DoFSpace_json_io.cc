#include "casm/clexulator/io/json/DoFSpace_json_io.hh"

#include <optional>

#include "casm/casm_io/container/json_io.hh"
#include "casm/casm_io/json/InputParser_impl.hh"
#include "casm/casm_io/json/optional.hh"
#include "casm/clexulator/DoFSpace.hh"

namespace CASM {

jsonParser &to_json(clexulator::DoFSpace const &dofspace, jsonParser &json) {
  json["dof"] = dofspace.dof_key;
  json["transformation_matrix_to_supercell"] =
      dofspace.transformation_matrix_to_super;
  json["sites"] = dofspace.sites;
  json["basis"] = dofspace.basis.transpose();
  json["glossary"] = dofspace.axis_info.glossary;
  json["glossary"].set_multiline_array();
  json["axis_site_index"] = dofspace.axis_info.site_index;
  json["axis_dof_component"] = dofspace.axis_info.dof_component;

  return json;
}

void parse(InputParser<clexulator::DoFSpace> &parser,
           std::shared_ptr<xtal::BasicStructure const> const &prim) {
  DoFKey dof_key;
  parser.require(dof_key, "dof");

  std::optional<Eigen::Matrix3l> transformation_matrix_to_super;
  parser.optional(transformation_matrix_to_super,
                  "transformation_matrix_to_supercell");

  std::optional<std::set<Index>> sites;
  parser.optional(sites, "sites");

  std::optional<Eigen::MatrixXd> basis;
  parser.optional(basis, "basis");
  if (basis.has_value()) {
    basis->transposeInPlace();
  }

  if (parser.valid()) {
    parser.value = std::make_unique<clexulator::DoFSpace>(
        dof_key, prim, transformation_matrix_to_super, sites, basis);
  }
}

// void from_json(clexulator::DoFSpace &dofspace, jsonParser const &json,
//                std::shared_ptr<xtal::BasicStructure const> const &prim) {
//   dofspace = jsonConstructor<clexulator::DoFSpace>::from_json(json, prim);
// }
//
// clexulator::DoFSpace jsonConstructor<clexulator::DoFSpace>::from_json(
//     jsonParser const &json,
//     std::shared_ptr<xtal::BasicStructure const> const &prim) {
//   InputParser<clexulator::DoFSpace> parser{json, prim};
//
//   std::runtime_error error_if_invalid{"Error reading DoFSpace from JSON"};
//   report_and_throw_if_invalid(parser, CASM::log(), error_if_invalid);
//
//   return std::move(*parser.value);
// }

std::unique_ptr<clexulator::DoFSpace>
jsonMake<clexulator::DoFSpace>::make_from_json(
    jsonParser const &json,
    std::shared_ptr<xtal::BasicStructure const> const &prim) {
  InputParser<clexulator::DoFSpace> parser{json, prim};

  std::runtime_error error_if_invalid{"Error reading DoFSpace from JSON"};
  report_and_throw_if_invalid(parser, CASM::log(), error_if_invalid);

  return std::move(parser.value);
}

}  // namespace CASM
