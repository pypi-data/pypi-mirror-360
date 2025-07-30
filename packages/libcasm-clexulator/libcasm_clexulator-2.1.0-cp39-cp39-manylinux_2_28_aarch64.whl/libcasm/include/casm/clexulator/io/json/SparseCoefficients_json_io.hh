#ifndef CASM_clexulator_SparseCoefficients_json_io
#define CASM_clexulator_SparseCoefficients_json_io

#include <memory>

namespace CASM {

template <typename T>
class InputParser;
class jsonParser;

namespace clexulator {
struct SparseCoefficients;
}

/// \brief Parse clexulator::SparseCoefficients from "eci.json" style JSON
void parse_eci_json(InputParser<clexulator::SparseCoefficients> &parser);

/// \brief Parse clexulator::SparseCoefficients from JSON
void parse(InputParser<clexulator::SparseCoefficients> &parser);

/// \brief Write clexulator::SparseCoefficients to JSON
jsonParser &to_json(clexulator::SparseCoefficients const &coeff,
                    jsonParser &json);

}  // namespace CASM

#endif
