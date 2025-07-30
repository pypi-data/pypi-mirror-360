#ifndef CASM_clexulator_Clexulator_json_io
#define CASM_clexulator_Clexulator_json_io

#include <memory>
#include <vector>

#include "casm/global/filesystem.hh"

namespace CASM {
template <typename T>
class InputParser;

namespace clexulator {
class Clexulator;
class PrimNeighborList;

void parse(InputParser<Clexulator> &parser,
           std::shared_ptr<PrimNeighborList> &prim_neighbor_list,
           std::vector<fs::path> search_path = {});

void parse(InputParser<std::vector<Clexulator>> &parser,
           std::shared_ptr<PrimNeighborList> &prim_neighbor_list,
           std::vector<fs::path> search_path = {});

}  // namespace clexulator
}  // namespace CASM

#endif
