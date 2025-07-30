#include "casm/clexulator/io/json/ConfigDoFValues_json_io.hh"

#include "casm/casm_io/container/json_io.hh"
#include "casm/casm_io/json/InputParser_impl.hh"
#include "casm/clexulator/ConfigDoFValues.hh"

namespace CASM {

std::unique_ptr<clexulator::ConfigDoFValues>
jsonMake<clexulator::ConfigDoFValues>::make_from_json(jsonParser const &json) {
  InputParser<clexulator::ConfigDoFValues> parser(json);

  auto &log = CASM::log();
  std::runtime_error error_if_invalid{
      "Error reading clexulator::ConfigDoFValues from JSON input"};
  report_and_throw_if_invalid(parser, log, error_if_invalid);

  return std::move(parser.value);
}

clexulator::ConfigDoFValues jsonConstructor<
    clexulator::ConfigDoFValues>::from_json(jsonParser const &json) {
  InputParser<clexulator::ConfigDoFValues> parser(json);

  auto &log = CASM::log();
  std::runtime_error error_if_invalid{
      "Error reading clexulator::ConfigDoFValues from JSON input"};
  report_and_throw_if_invalid(parser, log, error_if_invalid);

  return *parser.value;
}

/// \brief Insert ConfigDoFValues to JSON
///
/// Format:
/// \code
/// {
///   "occ": <array of integer>,
///   "global_dofs": {
///     <dof_name>: {
///       "values": <1d array of numbers, DoF values as provided>
///     },
///     ...
///   },
///   "local_dofs": {
///     <dof_name>: {
///       "values": <2d array of numbers, DoF values as provided>
///     },
///     ...
///   }
/// }
/// \endcode
///
/// Reminder about standard DoF basis vs prim DoF basis:
/// - This function does not convert ConfigDoFValues between bases, it writes
///   values as they are.
/// - Conversions, if necessary, must be done before calling `to_json` / after
///   calling `from_json`.
///
/// Note:
/// - "occ":
///       The integer value for each site corresponding to which Molecule in the
///       Site::occupant_dof vector is occupying that site.
///
///       Example: supercell volume=3, prim basis size=2,
///
///           "occ": [
///               occ[1], // "occ" value on site sublattice 0, unit cell 0
///               occ[2], // "occ" value on site sublattice 0, unit cell 1
///               occ[3], // "occ" value on site sublattice 0, unit cell 2
///               occ[4], // "occ" value on site sublattice 1, unit cell 0
///               occ[5], // "occ" value on site sublattice 1, unit cell 1
///               occ[6]  // "occ" value on site sublattice 1, unit cell 2
///             ]
///
/// - "local_dofs":
///       The local DoF values are represented as a matrix, with each row
///       representing a site DoF value and each colum representing a component
///       of the DoF value:
///           number of cols = DoF dimension (i.e. 3 for "disp" in standard
///               basis)
///           number of rows = (Supercell volume as multiple of the prim) *
///               (prim basis size).
///
///       Example: "disp" values, supercell volume=3, prim basis size=2
///
///           "local_dofs": {
///             "disp": {
///               "values": [
///                 [dx[1], dy[1], dz[1]], // "disp" values on site: sublattice
///                 0, unit cell 0 [dx[2], dy[2], dz[2]], // "disp" values on
///                 site: sublattice 0, unit cell 1 [dx[3], dy[3], dz[3]], //
///                 "disp" values on site: sublattice 0, unit cell 2 [dx[4],
///                 dy[4], dz[4]], // "disp" values on site: sublattice 1, unit
///                 cell 0 [dx[5], dy[5], dz[5]], // "disp" values on site:
///                 sublattice 1, unit cell 1 [dx[6], dy[6], dz[6]], // "disp"
///                 values on site: sublattice 1, unit cell 2
///               ]
///             }
///           }
///
/// - "global_dofs":
///       The global DoF values are represented as a vector of size equal to the
///       dimension of the DoF (i.e. 6 for "GLstrain" in standard basis).
///
///       Example: "GLstrain" values (any supercell volume and prim basis size)
///
///           "global_dofs": {
///             "GLstrain": {
///               "values": [Exx, Eyy, Ezz, sqrt(2)Eyz, sqrt(2)Exz, sqrt(2)Exy]
///             }
///           }
///
jsonParser &to_json(clexulator::ConfigDoFValues const &dof_values,
                    jsonParser &json) {
  json = jsonParser::object();
  if (dof_values.occupation.size()) {
    to_json_array(dof_values.occupation, json["occ"]);
  }
  if (!dof_values.local_dof_values.empty()) {
    for (auto const &local_dof : dof_values.local_dof_values) {
      to_json(local_dof.second.transpose(),
              json["local_dofs"][local_dof.first]["values"]);
    }
  }
  if (!dof_values.global_dof_values.empty()) {
    for (auto const &global_dof : dof_values.global_dof_values) {
      to_json_array(global_dof.second,
                    json["global_dofs"][global_dof.first]["values"]);
    }
  }

  return json;
}

void parse(InputParser<clexulator::ConfigDoFValues> &parser) {
  auto dof_values = notstd::make_unique<clexulator::ConfigDoFValues>();

  if (parser.self.contains("occupation")) {
    // For Backwards compatibility
    parser.require(dof_values->occupation, "occupation");
  } else {
    // Preferred
    parser.require(dof_values->occupation, "occ");
  }

  auto json_it = parser.self.find("local_dofs");
  if (json_it != parser.self.end()) {
    for (auto it = json_it->begin(); it != json_it->end(); ++it) {
      Eigen::MatrixXd tvalues;
      fs::path values_path = fs::path{"local_dofs"} / it.name() / "values";
      parser.require(tvalues, values_path);
      try {
        dof_values->local_dof_values.emplace(it.name(), tvalues.transpose());
      } catch (std::exception const &e) {
        parser.insert_error(values_path, e.what());
      }
    }
  }

  json_it = parser.self.find("global_dofs");
  if (json_it != parser.self.end()) {
    for (auto it = json_it->begin(); it != json_it->end(); ++it) {
      Eigen::VectorXd tvalues;
      fs::path values_path = fs::path{"global_dofs"} / it.name() / "values";
      parser.require(tvalues, values_path);
      try {
        dof_values->global_dof_values.emplace(it.name(), tvalues.transpose());
      } catch (std::exception const &e) {
        parser.insert_error(values_path, e.what());
      }
    }
  }
  if (parser.valid()) {
    parser.value = std::move(dof_values);
  }
}

/// \brief Read ConfigDoF from JSON
///
/// Reminder about standard DoF basis vs prim DoF basis:
/// - This function does not convert ConfigDoFValues between bases, it reads
///   values as they are.
/// - Conversions, if necessary, must be done before calling `to_json` / after
///   calling `from_json`.
void from_json(clexulator::ConfigDoFValues &dof_values,
               jsonParser const &json) {
  InputParser<clexulator::ConfigDoFValues> parser(json);

  auto &log = CASM::log();
  std::runtime_error error_if_invalid{
      "Error reading clexulator::ConfigDoFValues from JSON input"};
  report_and_throw_if_invalid(parser, log, error_if_invalid);

  dof_values = *parser.value;
}

}  // namespace CASM
