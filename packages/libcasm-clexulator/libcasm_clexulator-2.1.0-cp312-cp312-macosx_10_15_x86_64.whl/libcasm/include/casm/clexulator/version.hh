#ifndef CASM_clexulator_version
#define CASM_clexulator_version

#include <string>

namespace CASM {
namespace clexulator {

const std::string &
version();  // Returns the version defined by the CASM_CLEXULATOR_TXT_VERSION
// macro at compile time

}  // namespace clexulator
}  // namespace CASM

extern "C" {

/// \brief Return the libcasm_clexulator version number
inline const char *casm_clexulator_version() {
  return CASM::clexulator::version().c_str();
}
}

#endif
