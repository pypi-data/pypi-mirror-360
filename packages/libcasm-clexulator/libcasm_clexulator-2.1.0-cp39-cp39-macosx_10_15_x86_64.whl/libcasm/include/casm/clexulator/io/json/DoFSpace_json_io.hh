#ifndef CASM_clexulator_DoFSpace_json_io
#define CASM_clexulator_DoFSpace_json_io

#include <memory>

#include "casm/global/definitions.hh"

namespace CASM {

namespace xtal {
class BasicStructure;
}

namespace clexulator {
struct DoFSpace;
}

template <typename T>
class InputParser;
template <typename T>
struct jsonConstructor;
template <typename T>
struct jsonMake;
class jsonParser;

jsonParser &to_json(clexulator::DoFSpace const &dofspace, jsonParser &json);

void parse(InputParser<clexulator::DoFSpace> &parser,
           std::shared_ptr<xtal::BasicStructure const> const &prim);

// void from_json(clexulator::DoFSpace &dofspace, jsonParser const &json,
//                std::shared_ptr<xtal::BasicStructure const> const &prim);
//
// template <>
// struct jsonConstructor<clexulator::DoFSpace> {
//   static clexulator::DoFSpace from_json(
//       jsonParser const &json,
//       std::shared_ptr<xtal::BasicStructure const> const &prim);
// };

template <>
struct jsonMake<clexulator::DoFSpace> {
  static std::unique_ptr<clexulator::DoFSpace> make_from_json(
      jsonParser const &json,
      std::shared_ptr<xtal::BasicStructure const> const &prim);
};

}  // namespace CASM

#endif
