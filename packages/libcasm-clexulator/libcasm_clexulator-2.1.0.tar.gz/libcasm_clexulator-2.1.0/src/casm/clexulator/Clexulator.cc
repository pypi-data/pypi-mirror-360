#include "casm/clexulator/Clexulator.hh"

#include <filesystem>

#include "casm/casm_io/Log.hh"
#include "casm/casm_io/container/json_io.hh"
#include "casm/clexulator/ClexParamPack.hh"
#include "casm/system/RuntimeLibrary.hh"

namespace CASM {
namespace clexulator {

/// \brief Construct a Clexulator
Clexulator::Clexulator(std::string _name,
                       std::unique_ptr<clexulator::BaseClexulator> _clex,
                       std::shared_ptr<RuntimeLibrary> _lib)
    : m_name(_name), m_clex(std::move(_clex)), m_lib(_lib) {}

Clexulator::~Clexulator() {
  // ensure Clexulator is deleted before library
  m_clex.reset();
}

namespace Clexulator_impl {

void print_runtime_lib_options_help(std::ostream &sout) {
  sout << "Error compiling clexulator. To fix: \n";
  sout << "  - Check compiler error messages.\n";
  sout << "  - Check compiler options with 'casm settings -l'\n";
  sout << "    - Update compiler options with 'casm settings "
          "--set-compile-options '...options...'\n";
  sout << "    - Make sure the casm headers can be found by including "
          "'-I/path/to/casm'\n";
};

/// Make shared_ptr<RuntimeLibrary>, logging progress and errors
std::shared_ptr<RuntimeLibrary> make_shared_runtime_lib(
    std::string filename_base, std::string compile_options,
    std::string so_options, std::string compile_msg) {
  auto &log = compile_log();
  bool write_status_messages = false;
  if (!fs::exists(filename_base + ".so")) {
    write_status_messages = true;
  }
  if (write_status_messages) {
    log.compiling<Log::standard>(filename_base + ".cc");
    log.begin_lap();
    log << compile_msg << std::endl;
  }
  try {
    std::shared_ptr<RuntimeLibrary> result = std::make_shared<RuntimeLibrary>(
        filename_base, compile_options, so_options);
    if (write_status_messages) {
      log << "compile time: " << log.lap_time() << " (s)\n" << std::endl;
    }
    return result;
  } catch (runtime_lib_compile_error &e) {
    e.print(err_log());
    print_runtime_lib_options_help(log);
    throw;
  } catch (runtime_lib_shared_error &e) {
    e.print(err_log());
    print_runtime_lib_options_help(log);
    throw;
  } catch (std::exception &e) {
    print_runtime_lib_options_help(log);
    throw;
  }
}

}  // namespace Clexulator_impl

/// \brief Clexulator factory function
///
/// \param name Class name for the Clexulator, typically
///     'X_Clexulator_<basis_set_name>', with X referring to the system (i.e.
///     'NiAl'), and `<basis_set_name>` being an identifier that distringuishes
///     different choices of basis set (i.e. `default` or `large`).
/// \param dirpath Directory containing the source code and compiled object
///     file.
/// \param nlist, A PrimNeighborList to be updated to include the neighborhood
///     of this Clexulator. Will be created using parameters written to the
///     Clexulator if empty.
/// \param compile_options Compilation options
/// \param so_options Shared library compilation options
///
/// If 'name' is 'X_Clexulator_<basis_set_name>', and 'dirpath' is '/path/to':
/// - Looks for '/path/to/X_Clexulator_<basis_set_name>.so' and tries to load
///   it.
/// - If not found, looks for 'path/to/X_Clexulator_<basis_set_name>.cc' and
///   tries to compile and load it.
/// - If unsuccesful, will throw std::runtime_error.
///
/// The Clexulator has shared ownership of the loaded library,
/// so it is preferrable to duplicate the Clexulator using it's copy constructor
/// rather than construct another using this constructor which will re-load the
/// library.
///
Clexulator make_clexulator(std::string name, fs::path dirpath,
                           std::shared_ptr<PrimNeighborList> &nlist,
                           std::string compile_options,
                           std::string so_options) {
  // Construct the RuntimeLibrary that will store the loaded clexulator library
  std::shared_ptr<RuntimeLibrary> lib;
  try {
    lib = Clexulator_impl::make_shared_runtime_lib(
        (dirpath / name).string(), compile_options, so_options,
        "compile time depends on how many basis functions are included");
  } catch (std::exception &e) {
    compile_log()
        << "Clexulator construction failed: could not construct runtime "
           "library."
        << std::endl;
    throw;
  }

  // Get the Clexulator factory function
  std::function<clexulator::BaseClexulator *(void)> factory;
  factory =
      lib->get_function<clexulator::BaseClexulator *(void)>("make_" + name);

  // Use the factory to construct the clexulator and store it in m_clex
  std::unique_ptr<clexulator::BaseClexulator> clex(factory());

  // Check nlist has the right weight_matrix
  if (nlist == nullptr) {
    nlist = std::make_shared<PrimNeighborList>(
        clex->weight_matrix(), clex->sublat_indices().begin(),
        clex->sublat_indices().end(), clex->n_sublattices());
  } else {
    if (nlist->weight_matrix() != clex->weight_matrix()) {
      err_log()
          << "Error in Clexulator constructor: weight matrix of neighbor list "
             "does not match the weight matrix used to print the clexulator."
          << std::endl;
      err_log() << "nlist weight matrix: \n"
                << nlist->weight_matrix() << std::endl;
      err_log() << "clexulator weight matrix: \n"
                << clex->weight_matrix() << std::endl;
      throw std::runtime_error(
          "Error in Clexulator constructor: weight matrix of neighbor list "
          "does not match the weight matrix used to print the clexulator.");
    }
    if (nlist->sublat_indices() != clex->sublat_indices()) {
      jsonParser tjson;
      err_log()
          << "Error in Clexulator constructor: sublat_indices of neighbor list "
             "does not match the sublat_indices used to print the clexulator."
          << std::endl;
      err_log() << "nlist sublat_indices: "
                << to_json(nlist->sublat_indices(), tjson) << std::endl;
      err_log() << "clexulator sublat_indices: \n"
                << to_json(clex->sublat_indices(), tjson) << std::endl;
      throw std::runtime_error(
          "Error in Clexulator constructor: sublat_indices of neighbor list "
          "does not match the sublat_indices used to print the clexulator. Try "
          "'casm bset -uf'.");
    }
    if (nlist->n_sublattices() != clex->n_sublattices()) {
      err_log()
          << "Error in Clexulator constructor: n_sublattices of neighbor list "
             "does not match the n_sublattices used to print the clexulator."
          << std::endl;
      err_log() << "nlist n_sublattices: \n"
                << nlist->n_sublattices() << std::endl;
      err_log() << "clexulator n_sublattices: \n"
                << clex->n_sublattices() << std::endl;
      throw std::runtime_error(
          "Error in Clexulator constructor: n_sublattices of neighbor list "
          "does not match the n_sublattices used to print the clexulator. Try "
          "'casm bset -uf'.");
    }
  }

  // Expand the given neighbor list as necessary
  nlist->expand(clex->neighborhood().begin(), clex->neighborhood().end());

  return Clexulator(name, std::move(clex), lib);
}

/// \brief Local Clexulator factory function
///
/// \param name Class name for the Clexulator, typically
///     'X_Clexulator_<basis_set_name>', with X referring to the system (i.e.
///     'NiAl'), and `<basis_set_name>` being an identifier that distringuishes
///     different choices of basis set (i.e. `default` or `large`).
/// \param dirpath Directory containing numbered subdirectories (i.e. '0', '1',
///     '2', ...) containing local Clexulator source files (i.e.
///     'NiAl_Clexulator_<basis_set_name>_<index>.cc')
/// \param nlist, A PrimNeighborList to be updated to include the
///     neighborhood of this Clexulator
/// \param compile_options Compilation options
/// \param so_options Shared library compilation options
///
/// If 'name' is 'X_Clexulator_<basis_set_name>', and 'dirpath' is '/path/to',
/// then for `<i> = 0, 1, ...` for which
/// `path/to/<i>/X_Clexulator_<basis_set_name>_<i>.cc' exists, this method will:
/// - Look for '/path/to/<i>/X_Clexulator_<basis_set_name>_<i>.so' and try to
///   load it.
/// - If not found, look for 'path/to/<i>/X_Clexulator_<basis_set_name>_<i>.cc'
///   and try to compile and load it.
/// - If unsuccesful, will throw std::runtime_error.
///
/// The Clexulator has shared ownership of the loaded library,
/// so it is preferrable to duplicate the Clexulator using it's copy constructor
/// rather than construct another using this constructor which will re-load the
/// library.
///
std::vector<Clexulator> make_local_clexulator(
    std::string name, fs::path dirpath,
    std::shared_ptr<PrimNeighborList> &nlist, std::string compile_options,
    std::string so_options) {
  std::vector<Clexulator> result;
  Index i = 0;
  fs::path equiv_dir = dirpath / fs::path(std::to_string(i));
  while (fs::exists(equiv_dir)) {
    std::string equiv_name = name + "_" + std::to_string(i);
    if (!fs::exists(equiv_dir / (equiv_name + ".cc"))) {
      break;
    }
    result.push_back(make_clexulator(equiv_name, equiv_dir, nlist,
                                     compile_options, so_options));
    ++i;
    equiv_dir = dirpath / fs::path(std::to_string(i));
  }
  return result;
}

}  // namespace clexulator
}  // namespace CASM
