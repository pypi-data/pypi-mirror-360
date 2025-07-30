#include "casm/clexulator/version.hh"

using namespace CASM;
using namespace CASM::clexulator;

#ifndef CASM_CLEXULATOR_TXT_VERSION
#define CASM_CLEXULATOR_TXT_VERSION "unknown"
#endif

const std::string &CASM::clexulator::version() {
  static const std::string &ver = CASM_CLEXULATOR_TXT_VERSION;
  return ver;
};
