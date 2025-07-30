#include "casm/clexulator/io/json/SparseCoefficients_json_io.hh"

#include "casm/casm_io/json/InputParser_impl.hh"
#include "casm/clexulator/SparseCoefficients.hh"

namespace CASM {

/// \brief Parse clexulator::SparseCoefficients from JSON
///
/// Supports reading coefficients from a CASM v1.2+ style "eci.json" file.
///
/// Expected format:
/// \code
/// {
///   "orbits": [
///     {
///       "cluster_functions": [
///         {
///           "\\Phi_{<linear_function_index>}": <formula>,
///           "eci": <number>,
///           "linear_function_index": <integer>
///         },
///         ...
///       ],
///       ...
///     },
///     ...
///   ],
///   ...
/// }
/// \endcode
void parse_eci_json(InputParser<clexulator::SparseCoefficients> &parser) {
  if (parser.self.find("orbits") == parser.self.end()) {
    std::stringstream msg;
    msg << "Error parsing ECI: 'orbits' array not found";
    parser.error.insert(msg.str());
    return;
  }

  clexulator::SparseCoefficients coeff;

  jsonParser const &orbits_json = parser.self["orbits"];
  fs::path orbits_path{"orbits"};
  Index orbit_index = 0;
  for (auto const &orbit_json : orbits_json) {
    fs::path orbit_path = orbits_path / std::to_string(orbit_index);
    if (!orbit_json.contains("cluster_functions")) {
      parser.insert_error(orbit_path, "Error: missing 'cluster_functions'");
      return;
    }
    jsonParser const &cluster_functions_json = orbit_json["cluster_functions"];
    Index function_index = 0;
    for (auto const &function_json : cluster_functions_json) {
      if (function_json.find("eci") != function_json.end()) {
        fs::path func_path =
            orbit_path / "cluster_functions" / std::to_string(function_index);

        double eci_value;
        parser.require(eci_value, func_path / "eci");
        coeff.value.push_back(eci_value);

        unsigned int linear_function_index;
        parser.require(linear_function_index,
                       func_path / "linear_function_index");
        coeff.index.push_back(linear_function_index);
      }
      ++function_index;
    }
    ++orbit_index;
  }

  if (parser.valid()) {
    parser.value = std::make_unique<clexulator::SparseCoefficients>(coeff);
  }
}

/// \brief Parse clexulator::SparseCoefficients from JSON
///
/// Expected format is an array of (index, value) pairs:
/// \code
/// [
///   [index, value],
///   ...
/// ]
/// \endcode
///
/// Also supported, the CASM v1.2+ `eci.json` format. This format is assumed if
/// the JSON object being parsed contains the attribute "orbits". See
/// `parse_eci_json` for details.
///
void parse(InputParser<clexulator::SparseCoefficients> &parser) {
  if (parser.self.contains("orbits")) {
    auto subparser =
        parser.parse_as_with<clexulator::SparseCoefficients>(parse_eci_json);
    if (subparser->valid()) {
      parser.value = std::move(subparser->value);
    }
  } else if (parser.self.is_array()) {
    clexulator::SparseCoefficients coeff;
    auto it = parser.self.begin();
    auto end = parser.self.end();
    Index i = 0;
    while (it != end) {
      if (!it->is_array() || it->size() != 2) {
        parser.error.insert(
            "Error: clexulator::SparseCoefficients format is not valid");
        break;
      }

      fs::path row(std::to_string(i));

      unsigned int _index;
      parser.require(_index, row / "0");
      coeff.index.push_back(_index);

      double _value;
      parser.require(_value, row / "1");
      coeff.value.push_back(_value);

      ++i;
      ++it;
    }

    if (parser.valid()) {
      parser.value = std::make_unique<clexulator::SparseCoefficients>(coeff);
    }
  } else {
    parser.error.insert(
        "Error: clexulator::SparseCoefficients format is not recognized");
  }
}

/// \brief Write clexulator::SparseCoefficients to JSON
///
/// Expected format is an array of (index, value) pairs:
/// \code
/// [
///   [index, value],
///   ...
/// ]
/// \endcode
jsonParser &to_json(clexulator::SparseCoefficients const &coeff,
                    jsonParser &json) {
  if (coeff.index.size() != coeff.value.size()) {
    throw std::runtime_error(
        "Error writing clexulator::SparseCoefficients to JSON: mismatch "
        "between index.size() and value.size()");
  }
  json.put_array();
  for (Index i = 0; i < coeff.index.size(); ++i) {
    json[i].put_array();
    json[i].push_back(coeff.index[i]);
    json[i].push_back(coeff.value[i]);
  }
  return json;
}

}  // namespace CASM
