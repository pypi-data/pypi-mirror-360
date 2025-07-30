#ifndef CASM_clexulator_ConfigDoFValues_json_io
#define CASM_clexulator_ConfigDoFValues_json_io

#include <memory>

namespace CASM {

template <typename T>
class InputParser;
template <typename T>
struct jsonConstructor;
template <typename T>
struct jsonMake;
class jsonParser;

namespace clexulator {
struct ConfigDoFValues;
}

template <>
struct jsonMake<clexulator::ConfigDoFValues> {
  static std::unique_ptr<clexulator::ConfigDoFValues> make_from_json(
      jsonParser const &json);
};

template <>
struct jsonConstructor<clexulator::ConfigDoFValues> {
  static clexulator::ConfigDoFValues from_json(jsonParser const &json);
};

/// \brief Insert ConfigDoFValues to JSON
jsonParser &to_json(clexulator::ConfigDoFValues const &dof_values,
                    jsonParser &json);

void parse(InputParser<clexulator::ConfigDoFValues> &parser);

/// \brief Read ConfigDoF from JSON
void from_json(clexulator::ConfigDoFValues &dof_values, jsonParser const &json);

}  // namespace CASM

#endif
